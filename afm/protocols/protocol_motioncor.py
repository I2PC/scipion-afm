# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     you (you@yourinstitution.email)
# *
# * your institution
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'you@yourinstitution.email'
# *
# **************************************************************************


"""
Describe your python module here:
This module will provide the traditional Hello world example
"""
from enum import Enum
from os.path import join

from afm import Plugin
from afm.objects import AFMImage, SetOfAFMmovies
from motioncorr.convert import parseMovieAlignment2
from pyworkflow.constants import BETA
from pwem.objects.data import Micrograph
import pyworkflow.protocol.params as params
import pyworkflow.utils as pwutils
import pyworkflow.protocol.constants as cons
from pwem.protocols import EMProtocol
from pyworkflow.object import Set
from pyworkflow.utils import makePath


class AfmMCOutputs(Enum):
    afmMovies = SetOfAFMmovies


class ProtMotionCorAFMmovies(EMProtocol):
    """
    This protocol imports AFM movies
    """
    _label = 'motioncor AFM'
    _outputClassName = 'AFMImages'
    _possibleOutputs = AfmMCOutputs
    _devStatus = BETA

    def __init__(self, **args):
        super().__init__(**args)
        self.inMovies = None


    def _defineParams(self, form):
        form.addSection(label=pwutils.Message.LABEL_INPUT)
        form.addParam('inputMovies', params.PointerParam, pointerClass='SetOfMovies',
                      important=True,
                      label=pwutils.Message.LABEL_INPUT_MOVS,
                      help='Select a set of previously imported movies.')

        form.addHidden('doSaveAveMic', params.BooleanParam,
                       default=True)
        form.addHidden('useAlignToSum', params.BooleanParam,
                       default=True)

        group = form.addGroup('Alignment')
        line = group.addLine('Frames to ALIGN and SUM',
                             help='Frames range to ALIGN and SUM on each movie. The '
                                  'first frame is 1. If you set 0 in the final '
                                  'frame to align, it means that you will '
                                  'align until the last frame of the movie. '
                                  'When using EER, this option is IGNORED!')
        line.addParam('alignFrame0', params.IntParam, default=1,
                      label='from')
        line.addParam('alignFrameN', params.IntParam, default=0,
                      label='to')

        group.addParam('binFactor', params.FloatParam, default=1.,
                       label='Binning factor',
                       help='1x or 2x. Bin stack before processing.')

        form.addParam('doSaveMovie', params.BooleanParam, default=True,
                      label="Save aligned movie?")

        form.addParam('doComputePSD', params.BooleanParam, default=False,
                      expertLevel=cons.LEVEL_ADVANCED,
                      label="Compute PSD?",
                      help="If Yes, the protocol will compute for each "
                           "aligned micrograph the PSD using EMAN2.")

    def _insertAllSteps(self):
        self.inMovies = self.inputMovies.get()
        for movie in self.inMovies.iterItems():
            objId = movie.getObjId()
            self._insertFunctionStep(self.movieAlignmentStep, objId)
            self._insertFunctionStep(self.createOutputStep, objId)
        self._insertFunctionStep(self._closeOutputSet)

    def movieAlignmentStep(self, objId: int):
        movie = self._getCurrentMovie(objId)
        movieFolder = self._getTmpPath('movie_%06d' % movie.getObjId())
        makePath(movieFolder)

        frame0, frameN = self.alignFrame0.get(), self.alignFrameN.get()
        args =  ' -InTiff %s ' % movie.getFileName()
        args += ' -Throw %i ' % (frame0 - 1)
        args += ' -Trunc  %i ' % 0
        args += ' -Patch %i %i' %(5, 5)
        args += ' -MaskCent %i %i' % (0, 0)
        args += ' -MaskSize %i %i' % (1, 1)
        args += ' -FtBin %f'  % self.binFactor.get()
        args += ' -Tol %f ' % 0.20
        args += ' -PixSize %f' % movie.getSamplingRate()
        args += ' -kV %f' % 0
        args += ' -Cs %f' % 0
        args += ' -OutStack %i' % (1 if self.doSaveMovie else 0)
        args += ' -Gpu %i' % 0
        args += ' -SumRange %f %f ' % (0.0, 0.0)
        args += ' -LogDir %s ' % movieFolder
        args += ' -OutMrc %s ' % self._getExtraPath('mic_aligned_%06d.mrc' % movie.getObjId())

        program = Plugin.getAfmMotioncorrProgram()
        self.runJob(program, args)

        # Move output log to extra dir
        movieLog = self._getMovieLogFile(movie)
        logFn = join(movieFolder, movieLog)
        logFnExtra = self._getExtraPath(movieLog)
        pwutils.moveFile(logFn, logFnExtra)

    def createOutputStep(self, objId: int):
        micSet = getattr(self, self._possibleOutputs.afmMovies.name, None)
        if micSet:
            micSet.enableAppend()
        else:
            micSet = self._createSetOfMicrographs()
            micSet.setSamplingRate(self.inMovies.getSamplingRate())
            micSet.setStreamState(Set.STREAM_OPEN)
            self._defineOutputs(**{self._possibleOutputs.afmMovies.name: micSet})
            self._defineSourceRelation(self.inputMovies, micSet)

        movie = self._getCurrentMovie(objId)
        xshifts, yshifts = parseMovieAlignment2(self._getMovieLogFile(movie))
        outputMic = self._getExtraPath('mic_aligned_%06d.mrc' % movie.getObjId())
        micSet.append(Micrograph(outputMic))

    # --------------------------- INFO functions -----------------------------------
    def _validate(self):
        errors = []
        return errors

    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []
        return summary

    def _methods(self):
        methods = []
        return methods

    # --------------------------- UTILS functions -----------------------------------
    def _getCurrentMovie(self, objId: int) -> AFMImage:
        return self.inMovies.getItem('_objId', objId)

    @staticmethod
    def _getMovieLogFile(movie: AFMImage):
        return '%s-Patch-Full.log' % pwutils.removeBaseExt(movie.getFileName())
