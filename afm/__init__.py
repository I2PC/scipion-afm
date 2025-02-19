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
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os
from os.path import join
from motioncorr import V1_1_2
import pyworkflow.utils as pwutils
import pwem
from .constants import *

__version__ = "0.1"  # plugin version
_logo = "icon.png"
_references = ['you2019']


class Plugin(pwem.Plugin):
    _homeVar = AFM_HOME
    _pathVars = [AFM_HOME, AFM_MOTIONCOR_HOME, AFM_MOTIONCOR_CUDA_LIB]
    _url = "https://github.com/scipion-em/scipion-afm"
    _supportedVersions = [V1]  # binary version

    @classmethod
    def _defineVariables(cls):
        cls._defineVar(AFM_BINARY, "program")
        cls._defineEmVar(AFM_HOME, f"afm-{V1}")
        cls._defineVar(AFM_MOTIONCOR_CUDA_LIB, pwem.Config.CUDA_LIB)
        cudaVersion = cls.guessCudaVersion(AFM_MOTIONCOR_CUDA_LIB,
                                           default="12.1")
        cls._defineEmVar(AFM_MOTIONCOR_HOME, f'motioncor3-{V1_1_2}')
        cls._defineVar(AFM_MOTIONCOR_BIN, 'MotionCor3_1.1.2_Cuda%s%s_06-11-2024' % (
            cudaVersion.major, cudaVersion.minor))


    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch my program. """
        environ = pwutils.Environ(os.environ)

        # ...

        return environ

    @classmethod
    def getDependencies(cls):
        """ Return a list of dependencies. """
        neededProgs = []

        return neededProgs

    @classmethod
    def defineBinaries(cls, env):
        installCmds = [("make -j 4", "")]  # replace the target "" with e.g. "bin/myprogram"
        env.addPackage('afm', version=V1,
                       tar='void.tgz',
                       commands=installCmds,
                       neededProgs=cls.getDependencies(),
                       default=True)

    @classmethod
    def getAfmMotioncorrProgram(cls):
        return join(cls.getVar(AFM_MOTIONCOR_HOME), 'bin', cls.getVar(AFM_MOTIONCOR_BIN))
