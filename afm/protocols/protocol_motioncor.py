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

from pyworkflow.constants import BETA
from motioncorr.protocols.protocol_motioncorr import ProtMotionCorr
from xmipp3.protocols.protocol_flexalign import XmippProtFlexAlign

from pwem.objects.data import Micrograph
import pyworkflow.protocol.params as params
import pyworkflow.utils as pwutils
import pyworkflow.protocol.constants as cons
from pwem.protocols import ProtAlignMovies
from pwem.protocols import EMProtocol


class ProtMotionCorAFMmovies(EMProtocol):
    """
    This protocol imports AFM movies
    """
    _label = 'motioncor AFM'
    _outputClassName = 'AFMImages'
    _devStatus = BETA
    '''
    def __init__(self, **args):
        XmippProtFlexAlign.__init__(self, **args)
    '''

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
        self._insertFunctionStep(self.movieAlignmentStep)
        self._insertFunctionStep(self.createOutputStep)

    def movieAlignmentStep(self):
        import os
        inputMovies = self.inputMovies.get()
        print(inputMovies)

        for movie in inputMovies.iterItems():
            movieFolder = self._getTmpPath('movie_%06d' % movie.getObjId())

            if not os.path.exists(movieFolder):
                os.mkdir(movieFolder)
            #outputMicFn = self._getOutputMicName(movie)

            frame0, frameN = self.alignFrame0.get(), self.alignFrameN.get()
            _, numbOfFrames, _ = inputMovies.getFramesRange()
            if not numbOfFrames:
                numbOfFrames = inputMovies.getFirstItem().getDim()[2]

            args =  ' -InTiff %s ' % movie.getFileName()
            args += ' -Throw %i ' % (frame0 - 1)
            args += ' -Trunc  %i ' % 0
            args += ' -Patch %i %i' %(5, 5)
            args += ' -MaskCent %i %i' % (0, 0)
            args += ' -MaskSize %i %i' % (1, 1)
            args += ' -FtBin %f'  % self.binFactor.get()
            args += ' -Tol %f ' % 0.20
            args += ' -PixSize %f' % inputMovies.getSamplingRate()
            args += ' -kV %f' % 0
            args += ' -Cs %f' % 0
            args += ' -OutStack %i' % (1 if self.doSaveMovie else 0)
            args += ' -Gpu %i' % 0
            args += ' -SumRange %f %f ' % (0.0, 0.0)
            args += ' -LogDir %s ' % './'
            args += ' -OutMrc %s ' % self._getExtraPath('mic_aligned_%06d.mrc' % movie.getObjId())

            program = '/home/vilas/software/software/em/motioncor3-1.1.2/bin/MotionCor3_1.1.2_Cuda118_06-11-2024'
            '''
            argsDict['-OutMrc'] = f'"{outputMicFn}"'

            args = self._getInputFormat(movie.getFileName())
            args += ' '.join(['%s %s' % (k, v)
                              for k, v in argsDict.items()])
            args += ' ' + self.extraParams2.get()
            '''
            print(args)
            self.runJob(program, args)


    def createOutputStep(self):

        micSet = self._createSetOfMicrographs()
        inputMovies = self.inputMovies.get()
        for movie in inputMovies.iterItems():

            outputMic = self._getExtraPath('mic_aligned_%06d.mrc' % movie.getObjId())

            micSet.append(Micrograph(outputMic))
        #micSet.copyInfo(self._getInputMicrographs())

        micSet.setSamplingRate(self.inputMovies.get().getSamplingRate())
        self._defineOutputs(micSet=micSet)
        self._defineSourceRelation(self.inputMovies, micSet)

    '''
    def _insertFinalSteps(self, a= None):
        return True

    def processMovieStep(self, a, b):
        import os
        import shutil
        import time

        time.sleep(10)

        path = '/home/vilas/Downloads/'
        fn = 'afmExample_aligned_mic.mrc'

        # Source path
        source = "/home/vilas/Downloads"
        originPath = os.path.join(source, fn)

        # Destination path
        destination = self._getExtraPath(fn)

        dest = shutil.copyfile(originPath, destination)
        print(dest)
        f = open(self._getExtraPath('DONE', 'all.TXT'), "a")
        f.write("done")
        f.close()



    '''

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
