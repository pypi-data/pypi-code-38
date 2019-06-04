# **************************************************************************
# *
# * Authors:     Josue Gomez Blanco (josue.gomez-blanco@mcgill.ca)
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

# ------------------ Program common names --------------------------------------
CTFFIND = 'CTFFIND'
CTFFIND4 = 'CTFFIND4'
UNBLUR = 'UNBLUR'
SUMMOVIE = 'SUMMOVIE'
CTFTILT = 'CTFTILT'

# Frealign programs
FREALIGN = 'FREALIGN'
CALC_OCC = 'CALC_OCC'
RSAMPLE = 'RSAMPLE'

# Magdist
MAGDIST = 'MAGDIST'
MAGDISTEST = 'MAGDISTEST'
MAGDISTCORR = 'MAGDISTCORR'


V4_0_15 = '4.0.15'
V4_1_10 = '4.1.10'

MAGDIST_HOME = 'MAGDIST_HOME'
SUMMOVIE_HOME = 'SUMMOVIE_HOME'
UNBLUR_HOME = 'UNBLUR_HOME'
FREALIGN_HOME = 'FREALIGN_HOME'
CTFFIND4_HOME = 'CTFFIND4_HOME'
CTFFIND_HOME = 'CTFFIND_HOME'

CTFFIND_BIN = 'ctffind3.exe'
CTFFINDMP_BIN = 'ctffind3_mp.exe'
CTFFIND4_BIN = 'ctffind'
CTFTILT_BIN = 'ctftilt.exe'
CTFTILTMP_BIN = 'ctftilt_mp.exe'
FREALIGN_BIN = 'frealign_v9.exe'
FREALIGNMP_BIN = 'frealign_v9_mp.exe'
MAGDISTEST_BIN = 'mag_distortion_estimate_openmp.exe'
MAGDISTCORR_BIN = 'mag_distortion_correct_openmp.exe'
CALC_OCC_BIN = 'calc_occ.exe'
RSAMPLE_BIN = 'rsample.exe'
UNBLUR_BIN = 'unblur_openmp.exe'
SUMMOVIE_BIN = 'sum_movie_openmp.exe'

# ------------------ Constants values --------------------------------------

# Modes of search/refinement/reconstruction
MOD_RECONSTRUCTION = 0
MOD_REFINEMENT = 1
MOD_RANDOM_SEARCH_REFINEMENT = 2
MOD_SIMPLE_SEARCH_REFINEMENT = 3
MOD_SEARCH_REFINE_RANDOMISE = 4

# Modes for the first iteration
MOD2_SIMPLE_SEARCH_REFINEMENT = 0
MOD2_SEARCH_REFINE_RANDOMISE = 1

# Methods to correct the Ewald sphere
EWA_DISABLE = 0
EWA_SIMPLE = 1
EWA_REFERENCE = 2
EWA_SIMPLE_HAND = 3
EWA_REFERENCE_HAND = 4

# FSC calculation
FSC_CALC = 0
FSC_3DR_ODD = 1
FSC_3DR_EVEN = 2
FSC_3DR_ALL = 3

# Memory Usage
MEM_0 = 0
MEM_1 = 1
MEM_2 = 2
MEM_3 = 3

# Interpolation
INTERPOLATION_0 = 0
INTERPOLATION_1 = 1

# Parameters to Refine
REF_ALL = 0
REF_ANGLES = 1
REF_SHIFTS = 2
REF_NONE = 3
