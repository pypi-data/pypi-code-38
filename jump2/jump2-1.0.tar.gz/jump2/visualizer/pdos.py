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
import numpy as np
import cPickle as pickle 

from basic_plot import BasicPlot

class PlotPDOS(BaiscPlot):

    """
    Aiming the plot the projected density of states.

    method:
        project_per_elements:
            projected integrated s,p,d,f orbital;
        project_per_formula: 
            projected s,p,d,f for per formula;
        project_per_atoms:
            projected s,p,d,f for per atom;
        project_per_volume
            projected s,p,d,f for per volume;
        
    """

    def __init__(self, dos=None, *args, **kwargs):
        
        pass

        if isinstance(dos, VaspPDOS):
            self.dos = dos
        else:
            raise ModuleError("Not correct object!")

        
    def project_per_elements(self, element=None, orbital=None, *args, **kwargs):
        
        pass

    def project_per_formula(self, nformula=None, orbital=None, *args, **kwargs):

        pass

    def project_per_atoms(self, atoms=None, orbital=None, *args, **kwargs):
        pass

    def project_per_volume(self):
        
        pass

    def project_DIY_classify(self):
        
        pass

def ElmPDOS(ax,name,element=None,linewidth=2.0,colors=None,**kwargs):

         
        if (element and colors) and len(element) == len(colors):
            
            tags = zip(element.keys(),colors)
         
        labels = []   
        (energy,elementPDOS,elements,volume) = pickle.load(open(name,'rb'))
        if kwargs.has_key('perfu'):
            perfu = kwargs['perfu']
        else:
            perfu = 1.0
        orbital = ['s','p','d','f']
        if not colors: colors = ['r','g','b','k','y','gray','c','m']
        if not element: 
            element = elements
        linestyle = '-'    
        ax.axvline(x=0, linestyle="--", color="b",linewidth=0.5)
        n = 0 
        for elm , orbt in element.iteritems():
            y = None 
            label = None
            if len(orbt) > 1:
                
                label = elm+'-{\it'+'/'.join(orbt)+'}'
                for o in orbt:
                   if y is None: 
                        y = elementPDOS[elements.index(elm)][orbital.index(o)] 
                   else:
                        y += elementPDOS[elements.index(elm)][orbital.index(o)]
            else:
              
                label = elm+'-{\it{'+orbt[0]+'}}'
                print label
                o  =  orbt[0]
                y  = elementPDOS[elements.index(elm)][orbital.index(o)]
            ax.plot(energy, np.array(y)/perfu, linestyle=linestyle,linewidth=linewidth, 
            color=tags[n][1], label='$\mathregular{'+label+'}$')
            n += 1
            labels.append('$\mathregular{'+label+'}$')
        return ax, labels 
