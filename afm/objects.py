# -*- coding: utf-8 -*-
#  **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se) [1]
# *
# * [1] SciLifeLab, Stockholm University
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
import logging
from os.path import exists
from sqlite3 import OperationalError
from typing import Dict, Tuple, Any, Optional, Union

import mrcfile

from pwem import ALIGN_NONE

logger = logging.getLogger(__name__)

import csv
import math
import os
import threading
from collections import OrderedDict
from datetime import datetime

import numpy as np
import pwem.objects.data as data
import pyworkflow.utils.path as path
import tomo.constants as const
from pwem.convert.transformations import euler_matrix
from pwem.emlib.image import ImageHandler
from pwem.objects import Transform
from pyworkflow.object import Integer, Float, String, Pointer, Boolean, CsvList, PointerList, Scalar


class AFMAcquisition(data.Acquisition):
    """ Tomography acquisition metadata object"""

    def __init__(self, sampling=None, exposureTime=None, scanningFreq=None, **kwargs):
        super().__init__()
        self._samplingRate = Float(sampling)
        self._exposureTime = Float(exposureTime)
        self._scanningFreq = Float(scanningFreq)
        self._opticsGroupInfo = String()

    def setSamplingRate(self, value):
        self._samplingRate = value

    def getSamplingRate(self):
        return self._samplingRate.get()

    def setExposureTime(self, value):
        self._exposureTime = value

    def getExposureTime(self):
        return self._exposureTime.get()

    def setScanningFreq(self, value):
        self._scanningFreq = value

    def getScanningFreq(self):
        return self._scanningFreq.get()


class AFMmovie(data.Movie):
    """ Tilt movie. """

    def __init__(self, location=None, **kwargs):
        data.Movie.__init__(self, location, **kwargs)

    def copyInfo(self, other):
        data.Movie.copyInfo(self, other)


class SetOfAFMmovies(data.SetOfMovies):
    ITEM_TYPE = AFMmovie

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._afmAcquisition = AFMAcquisition()

    def setAFMAcquisition(self, value):
        self._afmAcquisition = value

    def getAFMAcquisition(self):
        return self._afmAcquisition

    def __str__(self):
        """ String representation of a set of coordinates. """
        return "%s (%d items, %s, %0.2f Å/px)" % (
        'SetOfAFMmovies', self.getSize(), self._dimStr(), self.getSamplingRate())


class AFMImage(data.Micrograph):
    def __init__(self, location=None, movieFile=None, shiftFile=None, **kwargs):
        super().__init__(location, **kwargs)
        self._movieFileName = String(movieFile)
        self._shiftsFile = String(shiftFile)

    def setMovieFileName(self, value):
        self._movieFileName.set(value)

    def getMovieFileName(self):
        return self._movieFileName.get()

    def setShiftsFile(self, fn):
        self._shiftsFile.set(fn)

    def getShiftsFile(self):
        return self._shiftsFile.get()


class SetOfAFMImages(data.SetOfMicrographs):
    ITEM_TYPE = AFMImage

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._afmAcquisition = AFMAcquisition()

    def setAFMAcquisition(self, value):
        self._afmAcquisition = value

    def getAFMAcquisition(self):
        return self._afmAcquisition

    def __str__(self):
        """ String representation of a SetOfAFMImages. """
        return "%s (%d items, %s, %0.2f Å/px)" % (
        'SetOfAFMimages', self.getSize(), self._dimStr(), self.getAFMAcquisition().getSamplingRate())

