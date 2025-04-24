# **************************************************************************
# *
# * Authors:     J.L. Vilas (jlvilas@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
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
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************
import pyworkflow.utils as pwutils
from pyworkflow.object import Integer
from pyworkflow.protocol.constants import LEVEL_ADVANCED
from pyworkflow.constants import BETA
import pyworkflow.protocol.params as params
from pwem.protocols import ProtExtractParticles
from pwem.protocols import EMProtocol
from afm.objects import AFMImage, SetOfAFMmovies, SetOfAFMImages


class ProtExtractAFMParticles(EMProtocol):
    """Protocol to extract particles from a set of coordinates"""
    _label = 'extract afm particles'
    _devStatus = BETA

    def __init__(self, **args):
        super().__init__(**args)

    #--------------------------- DEFINE param functions ------------------------
    def _defineParams(self, form):

        form.addSection(label=pwutils.Message.LABEL_INPUT)
        form.addParam('inputCoordinates', params.PointerParam, pointerClass='SetOfCoordinates',
                      important=True,
                      label='Coordinates',
                      help='Select a set of picked coordinates.')

        form.addParam('inputAFMs', params.PointerParam, pointerClass='SetOfAFMImages',
                      important=True,
                      label='AFM images',
                      help='Select a set of AFM images.')

        form.addParam('boxSize', params.IntParam,
                      label='Particle box size (px)', default=32,
                      # validators=[params.Positive],
                      help='This is the size of the boxed particles (in pixels). '
                           'Note that if you use downsample option, the '
                           'particles are boxed in a downsampled boxsize conserving the same relation. '
                           'Use the wizard to select a boxSize automatically. '
                           'This is calculated by multiplying 1.5 * box size used for picking.')
        '''
        form.addParam('doBorders', params.BooleanParam, default=False,
                      label='Fill pixels outside borders',
                      help='Xmipp by default skips particles whose boxes fall '
                           'outside of the micrograph borders. Set this '
                           'option to True if you want those pixels outside '
                           'the borders to be filled with the closest pixel '
                           'value available')

        form.addSection(label='Preprocess')

        form.addParam('doRemoveDust', params.BooleanParam, default=True,
                      label='Dust removal (Recommended)', important=True,
                      help='Sets pixels with unusually large values to random '
                           'values from a Gaussian with zero-mean and '
                           'unity-standard deviation.')

        form.addParam('thresholdDust', params.FloatParam, default=5,
                      condition='doRemoveDust', expertLevel=LEVEL_ADVANCED,
                      label='Threshold for dust removal',
                      help='Pixels with a signal higher or lower than this '
                           'value times the standard deviation of the image '
                           'will be affected. For cryo, 3.5 is a good value. '
                           'For high-contrast negative stain, the signal '
                           'itself may be affected so that a higher value may '
                           'be preferable.')

        form.addParam('doInvert', params.BooleanParam, default=True,
                      label='Invert contrast',
                      help='Invert the contrast if your particles are black '
                           'over a white background.  Xmipp, Spider, Relion '
                           'and Eman require white particles over a black '
                           'background. Frealign (up to v9.07) requires black '
                           'particles over a white background')

        form.addParam('doNormalize', params.BooleanParam, default=True,
                      label='Normalize (Recommended)',
                      help='It subtract a ramp in the gray values and '
                           'normalizes so that in the background there is 0 '
                           'mean and standard deviation 1.')
        form.addParam('normType', params.EnumParam,
                      choices=['OldXmipp','NewXmipp','Ramp'], default=2,
                      condition='doNormalize', expertLevel=LEVEL_ADVANCED,
                      display=params.EnumParam.DISPLAY_COMBO,
                      label='Normalization type',
                      help='OldXmipp (mean(Image)=0, stddev(Image)=1). \n'
                           'NewXmipp (mean(background)=0, '
                           'stddev(background)=1) \n  '
                           'Ramp (subtract background+NewXmipp).')
        form.addParam('backRadius', params.IntParam, default=-1,
                      condition='doNormalize',
                      label='Background radius (px)', expertLevel=LEVEL_ADVANCED,
                      help='Pixels outside this circle are assumed to be noise '
                           'and their stddev is set to 1. Radius for '
                           'background circle definition (in pix.). If this '
                           'value is 0, then half the box size is used.')

        form.addParam('patchSize', params.IntParam, default=-1,
                      label='Patch size for the variance filter (px)',
                      expertLevel=LEVEL_ADVANCED,
                      help='Windows size to make the variance filter and '
                           'compute the Gini coeff. A twice of the particle '
                           'size is recommended. Set at -1 applies 1.5*BoxSize.')

        form.addParallelSection(threads=4, mpi=1)
        '''

    #--------------------------- INSERT steps functions ------------------------
    def _insertAllSteps(self):
        inCoords = self.inputCoordinates.get()
        print(self.inputAFMs.get())
        mics = inCoords.getMicrographs()
        for mic in mics:
            coordList = [coord.clone() for coord in inCoords.iterCoordinates(micrograph = mic)]
            self._insertFunctionStep(self.extractParticlesStep, coordList, mic, self.inputAFMs.get()[mic.getObjId()])

    def extractParticlesStep(self, coordList, mic, afmImg):
        import mrcfile
        boxsize = self.boxSize.get()
        halfboxsize = boxsize // 2

        shiftFile = str(afmImg._shiftFile)
        movieFile = str(afmImg._movieFile)
        print(self.parseMovieAlignment2(shiftFile)[0])
        print(self.parseMovieAlignment2(shiftFile)[1])
        print(movieFile)

        with mrcfile.open(mic.getFileName()) as mrc:
            numpyMic = mrc.data

        dims = numpyMic.shape

        
        for m in
        for c in coordList:
            print(c.getX())
            xpos = c.getX()
            ypos = c.getY()
            print(xpos, ypos, halfboxsize)
            if self.validCoordinate(xpos, ypos, halfboxsize, dims):
                particle = self.extract(halfboxsize, numpyMic, xpos, ypos)

    def extract(self, halfboxsize, img, x, y):
        particle = img[x-halfboxsize:x+halfboxsize, y-halfboxsize:y+halfboxsize]
        return particle

    def validCoordinate(self, xpos, ypos, halfboxsize, dims):
        valid = True
        if (xpos - halfboxsize)<0 or (xpos + halfboxsize)>dims[0] or \
            (ypos - halfboxsize)<0 or (ypos + halfboxsize)>dims[1]:
            valid = False
        return valid

    def getAFMImageFromMicId(self):
        inAFM = self.inputAFMs.get()
        for afm in inAFM.iterItems():
            print(afm.getObjId())

    def parseMovieAlignment2(self, logFile):
        """ Get global frame shifts relative to the first frame. """
        first = None
        xshifts = []
        yshifts = []
        with open(logFile, 'r') as f:
            for line in f:
                l = line.strip()
                if '#' not in l and len(l) > 0:
                    parts = l.split()
                    if first is None:  # read the first frame number
                        first = int(parts[0])  # take the id from first column
                    # take the shifts from the last two columns of the line
                    xshifts.append(float(parts[1]))
                    yshifts.append(float(parts[2]))

        xoff, yoff = -xshifts[0], -yshifts[0]
        xshifts = [x + xoff for x in xshifts]
        yshifts = [y + yoff for y in yshifts]

        return xshifts, yshifts

    '''
    def _getExtractArgs(self):
        """ Should be implemented in sub-classes to define the argument
        list that should be passed to the picking step function.
        """
        return [self.doInvert.get(),
                self._getNormalizeArgs(),
                self.doBorders.get()]


    def _getNormalizeArgs(self):
        if not self.doNormalize:
            return ''

        normType = self.getEnumText("normType")
        args = "--method %s " % normType

        if normType != "OldXmipp":
            bgRadius = self.backRadius.get()
            if bgRadius <= 0:
                bgRadius = int(self._getExtractBoxSize() / 2)
            args += " --background circle %d" % bgRadius

        return args

    def _getExtractBoxSize(self):
        if self.boxSize.get() == -1:
            boxSize = int(self.getBoxSize())
        else:
            boxSize = int(self.boxSize.get())

        downFactor =  self._getDownFactor()
        if downFactor > 1:
            newBoxSize = self.getEven(boxSize/downFactor)
        else:
            newBoxSize = boxSize

        return int(newBoxSize)

    def getEven(self, boxSize):
        return Integer(int(int(boxSize)/2+0.75)*2)

    def getBoxSize(self):
        # This function is needed by the wizard and for auto-boxSize selection
        return self.getEven(self.getCoords().getBoxSize()*FACTOR_BOXSIZE)
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
