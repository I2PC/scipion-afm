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
import time

from pyworkflow.constants import BETA
from xmipp3.protocols.protocol_particle_pick import XmippProtParticlePicking
import pyworkflow.utils as pwutils
import pyworkflow.protocol.params as params


class ProtManualPickingAFM(XmippProtParticlePicking):
    """
    This protocol imports AFM movies
    """
    _label = 'manual picking'
    _outputClassName = 'AFMImages'
    _devStatus = BETA

    def __init__(self, **args):
        XmippProtParticlePicking.__init__(self, **args)
        self.saveDiscarded = False

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputMicrographs', params.PointerParam,
                      pointerClass='SetOfAFMImages',
                      label='Set of AFM Images', important=True,
                      help='Select the SetOfAFMImages to be used during '
                           'picking.')

    def _insertAllSteps(self):

        """The Particle Picking process is realized for a set of micrographs"""
        # Get pointer to input micrographs

        self.afmImages = self.inputMicrographs.get()
        micFn = self.afmImages.getFileName()

        # Launch Particle Picking GUI
        if not self.importFolder.hasValue():
            self._insertFunctionStep(self.launchParticlePickGUIStep, micFn,
                                     interactive=True)
        else:  # This is only used for test purposes
            self._insertFunctionStep(self._importFromFolderStep)
            # Insert step to create output objects
            self._insertFunctionStep(self.createOutputStep)

    # --------------------------- INFO functions -----------------------------------
    def getInputMicrographs(self):
        return self.inputMicrographs.get()


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
