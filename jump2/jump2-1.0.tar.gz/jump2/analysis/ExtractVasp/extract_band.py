# coding: utf-8
# Copyright (c) JUMP2 Development Team.
# Distributed under the terms of the JLU License.


#=================================================================
# This file is part of JUMP2.
#
# Copyright (C) 2017 Jilin University
#
#  Jump2 is a platform for high throughput calculation. It aims to 
#  make simple to organize and run large numbers of tasks on the 
#  superclusters and post-process the calculated results.
#  
#  Jump2 is a useful packages integrated the interfaces for ab initio 
#  programs, such as, VASP, Guassian, QE, Abinit and 
#  comprehensive workflows for automatically calculating by using 
#  simple parameters. Lots of methods to organize the structures 
#  for high throughput calculation are provided, such as alloy,
#  heterostructures, etc.The large number of data are appended in
#  the MySQL databases for further analysis by using machine 
#  learning.
#
#  Jump2 is free software. You can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published 
#  by the Free sofware Foundation, either version 3 of the License,
#  or (at your option) and later version.
# 
#  You should have recieved a copy of the GNU General Pulbic Lincense
#  along with Jump2. If not, see <https://www.gnu.org/licenses/>.
#=================================================================

"""
Module for extract data from vasp output: data for band structure. 
"""


__author__ = ""
import numpy as np
import matplotlib.pyplot as plt
import os,sys
import math
from matplotlib.font_manager import FontProperties
from jump2.analysis.ExtractVasp.basics import BasicParam


class BandStructure():

    """
    Get basic data associated with band structure

    tribute:
        vbm::tuple, (40,(a,b,c), -0.5)
        cbm::tuple, (41,(a,b,c),  0.5)
        ispin::integer, 1 or 2
        nelect:: integer, total number of electron; 
        symbols:: high symmetrized symbols;
        eigenvalue:: list, eigenvalues at each band;
        kpoints:: list, organized kpoints;
        gap:: dict, {'direct':{'x':(0.,0.0.),'value':1.0},
                     'indirect':{'x':(0.,0.,0.), 'value':0.5}}
        projected_bands:: dict of projected orbitals;
    """

    def __init__(self, path=None, symmetry_path=None, projected=False, *args, **kwargs):

        if path is None:
            path = os.getcwd()
        self.path = path
        self.symmetry_path = symmetry_path

    @property
    def vbm(self):
        """
        eigenvalue of valence band maximum.

        return::
            tuple(num,         # the num of points %    
                 [0., 0., 0.], # coordination %
                 -1.5)         # eigenvalue % 
        """
        VBMtop = -100
        kpoint = 0
        bands = self.eigenvalue
        for i in range(0, bands.shape[0]):
            for j in range(0, bands.shape[1]):
                if bands[i][j] <= 0.5:
                    if bands[i][j] > VBMtop:
                        VBMtop = bands[i][j]
                        kpoint = j

        coordination = self.kpoints[kpoint]

        return (kpoint, coordination, VBMtop)

    @property
    def cbm(self):
        """
        eigenvalue of conduction band minimum.

        return::
            tuple(num,         # the num of points %    
                 [0., 0. 0.],  # coordination %  
                 -1.5)         # eigenvalue % 
        """
        CBMbottom = 100
        kpoint = 0
        bands = self.eigenvalue
        for i in range(0, bands.shape[0]):
            for j in range(0, bands.shape[1]):
                if bands[i][j] > 0.5:
                    if bands[i][j] < CBMbottom:
                        CBMbottom = bands[i][j]
                        kpoint = j

        coordination = self.kpoints[kpoint]

        return (kpoint, coordination, CBMbottom)

    @property
    def ispin(self):
        """spin==1 or 2"""
        temp = os.popen("grep 'ISPIN' scf/OUTCAR").readline()
        ispin = int(temp.split()[2])
        return ispin

    @property
    def efermi(self):
        #fermi_level %
        temp = os.popen("grep 'E-fermi' scf/OUTCAR").readline()
        efermi = float(temp.split()[2])
        return efermi

    @property
    def gap(self):
        # direct gap value %

        direct_gap = 0.0
        direct_kpoint = []
        indirect_gap = 0.0

        cbm = self.cbm
        vbm = self.vbm

        if cbm[2] - vbm[2] > 10E-2:
            bands = self.eigenvalue
            direct_gap = 100.0
            for i in xrange(0, bands.shape[1]):
                vmaxer = -100.0
                cminer = 100.0
                for j in xrange(1, bands.shape[0]):
                    temp = bands[j][i]
                    if temp >= 0.0:
                        if temp < cminer:
                            cminer = temp
                    else:
                        if temp > vmaxer:
                            vmaxer = temp
                gap = cminer - vmaxer

                if gap < direct_gap:
                    direct_gap = gap
                    direct_kpoint = i

            indirect_gap = cbm[2] - vbm[2]
            if (cbm[1] == vbm[1]).all():
                isdirect =True

        return {'direct': {'x': self.kpoints[direct_kpoint], 'value': direct_gap},
                'indirect': {'x': self.kpoints[self.cbm[0]], 'value': indirect_gap}}

    @property
    def nelect(self):
        """the total number of electrons"""
        temp = os.popen("grep 'NELECT' scf/OUTCAR").readline()
        nelect = int(float(temp.split()[2]))
        return nelect

    @property
    def symbols(self):
        # symbols of high symmetrized points %
        symbols = []

        for p in self.symmetry_path:
            if symbols == []:
                symbols.append(p.split('-')[0])
            symbols.append(p.split('-')[1])

        return symbols


    @property 
    def eigenvalue(self, path=None):
        # eigenvalues of all the bands %

        Efermi = self.efermi
        eigenvalue = []
        for p in self.symmetry_path:

            infile = open("band/" + p + "/EIGENVAL")

            # comment lines
            for i in range(0, 5):
                infile.readline()
            # get total number of kpints and bands
            string = infile.readline()
            totalKpoints = int(string.split()[1])
            totalBands = int(string.split()[2])

            # read bands
            bands = []
            for i in range(0, totalKpoints):
                infile.readline()  # blank line
                infile.readline()  # kpoint line

                # get band value
                bk = []  # bands of a kpoint
                for j in range(0, totalBands):
                    string = infile.readline()
                    temp = np.array(float(string.split()[1]) - Efermi)
                    if (bk == []):
                        bk = temp
                    else:
                        bk = np.vstack([bk, temp])

                # bk->bands
                if (bands == []):
                    bands = bk
                else:
                    bands = np.hstack([bands, bk])

            if eigenvalue == []:
                eigenvalue = bands
            else:
                eigenvalue = np.hstack([eigenvalue, np.delete(bands, 0, axis=1)])

        return eigenvalue

    @property
    def kpoints(self):
        # kponts along high symmetrized pathway %
        kpoints = []
        for p in self.symmetry_path:
            infile = open("band/" + p + "/EIGENVAL")

            # comment lines
            for i in range(0, 5):
                infile.readline()
            # get total number of kpints and bands
            string = infile.readline()
            totalKpoints = int(string.split()[1])
            totalBands = int(string.split()[2])

            # read bands
            kpoint = []
            for i in range(0, totalKpoints):
                infile.readline()  # blank line

                # get kpoint coordinate
                string = infile.readline()
                kp = np.array([float(s0) for s0 in string.split()[:3]])
                if (kpoint == []):
                    kpoint = kp
                else:
                    kpoint = np.vstack([kpoint, kp])

                for j in range(0, totalBands):
                    infile.readline()

            if kpoints == []:
                kpoints = kpoint
            else:
                kpoints = np.vstack([kpoints, kpoint[1:]])

        return kpoints

    @property
    def projected_bands(self):
        # projected bands %
        ions = []
        for p in self.symmetry_path:
            infile = open("band/" + p + "/PROCAR")
            # comment lines
            infile.readline()
            # get total number of kpints and bands
            string = infile.readline()
            totalKpoints = int(string.split()[3])
            totalBands = int(string.split()[7])
            natom = int(string.split()[11])
            norbit = len(os.popen("grep -w ion band/" + p + "/PROCAR").readline().split()) -2

            # read bands
            ion = np.zeros((totalBands, totalKpoints, natom, norbit+1))
            for i in range(0, totalKpoints):  # kpoint
                # skip blank line
                infile.readline()
                # skip kpoint line
                infile.readline()
                # get band value
                for j in range(0, totalBands):  # band
                    # skip blank line
                    infile.readline()
                    # skip band line
                    infile.readline()
                    # skip blank line
                    infile.readline()
                    # skip comment line
                    infile.readline()
                    for k in range(0, natom):  # atom
                        string = infile.readline()
                        temp = np.array([s0 for s0 in string.split()])
                        for l in xrange(0, norbit+1):
                            ion[j][i][k][l] = float(temp[l + 1])
                    # skip "tot..."
                    infile.readline()
                    if (j == totalBands - 1):
                        # skip blank line, enter next kpoint
                        infile.readline()

            if ions == []:
                ions = ion
            else:
                ions = np.hstack([ions, np.delete(ion, 0, axis=1)])

        return ions

    @property
    def reverse(self):
        kpoints = self.kpoints[::-1]
        eigenvalue = self.eigenvalue[::-1]

        return kpoints, eigenvalue

    def __iterm_path__(self):
        return None 

###############################
sym ={
'R-T': '      0.50000000       0.50000000       0.50000000 ! R+\n      0.00000000       0.50000000       0.50000000 ! T',
'S-Y': '      0.50000000       0.50000000       0.00000000 ! S+\n      0.00000000       0.50000000       0.00000000 ! Y',
'U-R': '      0.50000000       0.00000000       0.50000000 ! U+\n      0.50000000       0.50000000       0.50000000 ! R',
'Gamma-Z': '      0.00000000       0.00000000       0.00000000 ! \\Gamma+\n      0.00000000       0.00000000       0.50000000 ! Z',
'T-Z': '      0.00000000       0.50000000       0.50000000 ! T+\n      0.00000000       0.00000000       0.50000000 ! Z',
'Gamma-X': '      0.00000000       0.00000000       0.00000000 ! \\Gamma+\n      0.50000000       0.00000000       0.00000000 ! X',
'X-S': '      0.50000000       0.00000000       0.00000000 ! X+\n      0.50000000       0.50000000       0.00000000 ! S',
'Y-Gamma': '      0.00000000       0.50000000       0.00000000 ! Y+\n      0.00000000       0.00000000       0.00000000 ! \\Gamma',
'Z-U': '      0.00000000       0.00000000       0.50000000 ! Z+\n      0.50000000       0.00000000       0.50000000 ! U'}

#sym_keys = sym.keys()
#kpoints = {}
#eigenvalue = {}
#for k in sym_keys:
#    band = BandStructure(path=os.getcwd()+'/'+str(k))
#    kpoints.update({k:band.kpoints})
#    eigenvalue.update({k:band.eigenvalue})

#print kpoints.keys()
#print eigenvalue.keys()