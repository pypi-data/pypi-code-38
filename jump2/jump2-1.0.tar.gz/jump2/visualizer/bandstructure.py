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
This module defines the classes relating to visualize the band structure.
"""
#

__contributors__ = 'xingang zhao'

from basic_plot import BasicPlot
import numpy as np

class PlotBandStructure(BasicPlot):

    """
    Class to aim to show the band structure according to eigenvalues and 
    high symmetrized kpoints pathway.

    args:
        band:: object of VasExtract.bandstructure,
                         other data from other results;
    """
    
    def __init__(self, band=None, *args, **kwargs):

        from ..analysis.ExtractVasp.extract_band import BandStructure
        
        super(PlotBandStructure, self).__init__()

        if isinstance(band, BandStructure):
            self.bands = band # an object of data extract from
                              # band structure calculation %
        else:
            raise ModuleError ("incorrect object %s")

    @staticmethod
    def refine_bands(eigenvalues, ymin, ymax, scale=2.0):
        
        """ 
        Static method to redefine the shape of eigenvalues within (y_min - scale) 
            to (y_max + scale) eV.

        args::
            y_min: the minium value of scale you focus on;
            y_max: the maximum value of scale you focus on;
            scale: the broading range of the energy scale.

        Returns a array contained band eigenvalues.
        """
        
        nc = 0  # count index number of conduction band % 
        nv = 0  # count index number of valence band % 

        eigen = eigenvalues.T[0] # reshape the eigenvalue to get eigenvalues
                                 # along the first kpoint %

        # assume the broading of each band less than 2.0 eV %
        for v in eigen: 
            if v <= ymin - scale: nv += 1
            if v <= ymax + scale: nc += 1

        return eigenvalues[nv:nc]
    
    @staticmethod
    def vc_band_edges(eigenvalues, ispin, gap, nelect):

        """
        Static method to get the vbm/cbm band just for semiconductors.

        args:
            eigenvalues: eigenvalues of each band at different kpoint;
            ispin: electronic spin;
            gap: band gap value;  
            nelect: total number of electrons;

        Returns array of band eigenvalues.
        """

        if gap < 0.0:
            raise DATAError ("Warning:: filled color just for semiconductors")
        else:
            nc = 0
            # get the conduction band index by using the total electrons %
            if ispin == 2:
                nc = int(nelect/1.0)  # nc the conduction index due to 
            if ispin == 1:            # python index initized from zero.    
                nc = int(nelect/2.0)  
            
            return eigenvalues[nc-1:nc]

    @staticmethod
    def projected_band(num_band, ispin, nelect):
        """
        Static method for get the projected bands index.
        
        args:
            num_band: int/list band index for projected fat bands;
            ispin: electronic spin;
            gap: band gap value;  
            nelect: total number of electrons;

        Returns a list contained the band index.
        """
        
        band_index =[]
        
        if type(num_band) is list:
            band_index= num_band
        
        if type(num_band) is int:
                
            for i in xrange(0, num_band*2):
                if ispin == 1:
                    band_index.append(int(nelect/2.0)-num_band+i)
                if ispin == 2:
                    band_index.append(int(nelect/1.0)-num_band+i)

        return band_index

    def plot(self, ax, ymin=-4.0, ymax=4.0, edges=True, filled=False, surface_color='m', 
                   projected=False, nbands=5, line_color='k', shift=0.0, broad=4.0, *args, **kwargs):

        """
        script for aiming to plot the bandstructure.

        args:
            ymin & ymax:: 
                   real, the visualized y scale, default -4.0~4.0 eV;
            edges:: 
                   bool, show the VBM/CBM points in the figure, default is True;
            filled:: 
                   bool, fill color of the valance/conduction bands, dfault is false;
            surface_color:: 
                   string, filled color, default is purple;
            projected:: 
                   bool, whether to project the fat bands, default is false;
            nbands:: 
                  integer(0 or >0) or list, show the fat bands at the band edges, default is 5;
            line_color:: 
                  string, color of each bands, defaults is black;
            shift:: 
                  real, up-/down-shift the conductor bands, default is zero;
            broad::
                  real,assumed broading of each band, default is 4.0eV;
                
        """
        vbm = self.bands.vbm 
        cbm = self.bands.cbm
        ispin = self.bands.ispin
        nelect = self.bands.nelect

        symbols = self.bands.symbols # symbols of high symmetrized points % 
        eigenvalues = self.bands.eigenvalue # eigenvalues of all the bands %
        kpoints = self.bands.kpoints # kponts along high symmetrized pathway % 
        direct_gap = self.bands.gap['direct']['value'] # direct gap value %
        indirect_gap = self.bands.gap['indirect']['value'] # indirect gap value %
        proband = self.bands.projected_bands # projected bands % 

        projected_color = ['r','g','b','m','y','c','grey', 'k']
        # normal band structure % 
        if filled is False:
            eigenv = self.refine_bands(eigenvalues, ymin, ymax)
            
            count = 0 
            for eigen in eigenv:
                if ispin == 1: 
                    if count > int(nelect/2.0) and indirect_gap >= 0.0:
                        eigen += shift
                else:
                    if count > int(nelect) and indirect_gap >=0.0:
                        eigen += shift
                ax.plot(kpoints, eigen, color=line_color)

                # fat bands % 
                if projected is True and proband:
                    if isinstance(nbands, list):
                        bands = nbands
                    if isinstance(nbands, int):
                        bands = self.projected_band(nbands, ispin, nelect)

                    if (count+1) in nbands:
                        for pro in proband[count]:  # loop the projected categery% 
                            ax.scatter(kpoints, eigen, s=proband[count][pro]['value'], 
                                color=projected_color[proband[count].index(pro)], 
                                label=proband[count][pro]['label'],alpha=0.5) 
                        
                count += 1  # band count % 
            
        # filled color band structure % 
        if filled is True:
            eigenv = self.vc_band_edges(eigenvalues, ispin, indirect_gap, nelect)
            ax.fill_between(kpoints, [ymin]*len(kpoints), eigenv[0], color=surface_color, alpha=0.5)
            ax.fill_between(kpoints, eigenv[1], [ymax]*len(kpoints), color=surface_color, alpha=0.5)

        # show band edges % 
        if edges is True and indirect_gap > 0.0:
            ax.plot(kpoints[vbm['x']], vbm['y'], 'o', color='r')
            ax.plot(kpoints[vbm['x']], vbm['y']+direct_gap['value'], 'o', color='r')
            ax.plot(kpoints[cbm['x']], cbm['y'], 'o', color='g')
            ax.text(kpoints[vbm['x']], vbm['y']+direct_gap['value']*0.5, 
                                      str(direct_gap['value'])+'eV', color='k')
            ax.text(kpoints[int((vbm['x']+cbm['x'])/2)], vbm['y']+indirect_gap['value']*0.5, 
                                      str(indirect_gap['value'])+'eV', color='k')
            # add the arrows %
            ax.annotate('', xy=(kpoints[cbm['x']], cbm['y']),
                            xytext=(kpoints[vbm['x']], vbm['y']), 
                            arrowprops=dict(arrowstyle='->', color='r')) 
            ax.annotate('', xy=(kpoints[vbm['x']], vbm['y']+direct_gap['value']),
                            xytext=(kpoints[vbm['x']], vbm['y']), 
                            arrowprops=dict(arrowstyle='->', color='r')) 

        ax.set_ylim(ymin, ymax)
        ax.set_xlim(kpoints[0],kpoints[-1]) 
        ax.set_xticks(symbols['coord'], symbols['label'])
        ax.set_ylabel("$\mathregular{E \ (eV)}$", fontsize=12)
       
        self.plot = ax

        del self.bands
