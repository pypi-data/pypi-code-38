#!/usr/bin/env python 
import numpy as np
import cPickle as pickle 

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
