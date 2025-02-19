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
import os
import re

from pyworkflow.constants import BETA
import pyworkflow.protocol.params as params

from pwem.protocols import EMProtocol
from afm.objects import SetOfAFMmovies, AFMmovie, AFMAcquisition


class ProtImportAFMmovies(EMProtocol):
    """
    This protocol imports AFM movies
    """
    _label = 'import AFM movies'
    _outputClassName = 'SetOfAFMmovies'
    _devStatus = BETA

    def __init__(self, **args):
        EMProtocol.__init__(self, **args)

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputFile', params.FileParam,
                      label='Files to import')

        form.addParam('samplingRate', params.FloatParam,
                      label='Pixel size [Å/pix]',
                      allowsNull=False)

        form.addParam('scanningTime', params.FloatParam,
                      label='Scanning time per image [s]',
                      default=1.0)

        form.addParam('scanningFreq', params.FloatParam,
                      label='Scanning Frequency [s⁻1]',
                      default=1.0)


    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep(self.importStep)

    def findFiles(self, inputRegEx, searchPath=None):
        """
        This function searches files that matche with a specific regular expresion in a
        searching folder

        Args:
            inputRegEx: Regular expression to find the files
            searchPath: This is the searching folder, current workind dir as default

        Returns:
            A list with the files that verify the regular expression.

        Raises:
             TypeError: If the input is not a string
        """
        import glob
        inputRegEx_str = str(inputRegEx)
        print('aa')
        partes_patron = inputRegEx_str.split(os.sep) # Separamos por el separador del sistema operativo
        print(partes_patron)
        ruta_base = os.sep.join(partes_patron[:-1]) # Unimos todas las partes menos la última para la ruta
        patron_archivo = partes_patron[-1]

        # Si la ruta base está vacía, se asume el directorio actual
        if not ruta_base:
            print('A filename was introduced not a path with a pattern')
            ruta_base = "."

        # Usamos glob para obtener todos los archivos que coinciden con el patrón de archivo en la ruta base.
        archivos_en_ruta = glob.glob(os.path.join(ruta_base, patron_archivo))

        print('archivos en ruta')
        print(archivos_en_ruta)
        archivos_coincidentes = []
        if archivos_en_ruta:
            archivos_coincidentes = archivos_en_ruta
            return archivos_coincidentes, ruta_base
        else:
            return None

    def importStep(self):

        filesPath = self.inputFile.get()
        print(filesPath)

        listOfFiles, basePath = self.findFiles(filesPath)

        print(listOfFiles)
        sampling = self.samplingRate.get()
        scanningTime = self.scanningTime.get()
        scanningFreq = self.scanningFreq.get()

        outputSetOfAFMmovies = SetOfAFMmovies.create(self._getPath(), template='setOfAFMmovies%s.sqlite')

        acqInfo = AFMAcquisition(sampling=sampling, scanningTime=scanningTime, scanningFreq=scanningFreq)

        outputSetOfAFMmovies.setSamplingRate(sampling)
        outputSetOfAFMmovies.setAFMAcquisition(acqInfo)
        for f in listOfFiles:
            movie = AFMmovie(location=f)
            outputSetOfAFMmovies.append(movie)
            outputSetOfAFMmovies.update(movie)

        self._defineOutputs(outputSetOfTiltSeries=outputSetOfAFMmovies)

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
