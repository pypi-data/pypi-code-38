#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 14:13:10 2018

@author: antony
"""

import numpy as np
import pandas as pd
import sys
import matplotlib
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import libplot
import matplotlib.gridspec as gridspec


class ExtGSEA(object):
    def __init__(self, ranked_gene_list, ranked_score, permutations=1000, w=1):
        self.__w = w
        self.__np = permutations
        
        l = len(ranked_gene_list)
        
        rk = np.concatenate((ranked_gene_list, ranked_gene_list))
        rsc = np.concatenate((ranked_score, -ranked_score), axis=0)
        ix = np.argsort(rsc)[::-1]
        
        print(np.sort(rsc)[::-1])
        
        pn = np.concatenate((np.ones(l), -np.ones(l)), axis=0)
        
        self.__rk = ranked_gene_list
        self.__rs = ranked_score
        
        self.__rkc = rk[ix]
        self.__rsc = rsc[ix]
        self.__pn = pn[ix]
        
        # Defaults if nothing found
        self.__es = -1
        self.__nes = -1
        self.__pv = -1
        self.__ledge = []
        self.__bg = {}
        
        self.__gsn1 = 'n1'
        self.__gsn2 = 'n2'
        
        self.__run = False
        
    def enrichment_score(self, gs1):
        l = len(self.__rk)
        
        hits = np.zeros(l)
        
        for i in range(0, l):
            if self.__rk[i] in gs1:
                hits[i] = 1

        # Compute ES
        
        if self.__w != 1:
            score_hit = np.cumsum(np.abs(self.__rs * hits) ** self.__w)
        else:
            score_hit = np.cumsum(np.abs(self.__rs * hits))
                
        score_hit = score_hit / score_hit[-1]
        score_miss = np.cumsum(1 - hits)
        score_miss = score_miss / score_miss[-1]
        
        es_all = score_hit - score_miss
        es = np.max(es_all) + np.min(es_all)
        
        isen = np.zeros(l)
        
        if es < 0:
            ixpk = np.where(es_all == np.min(es_all))[0][0]
            isen[ixpk:] = 1
            ledge = self.__rk[(isen == 1) & (hits == 1)]
            ledge = ledge[::-1]
        else:
            ixpk = np.where(es_all == np.max(es_all))[0][0]
            print(ixpk)
            isen[0:(ixpk + 1)] = 1
            ledge = self.__rk[(isen == 1) & (hits == 1)]    
        
        return es, es_all, hits, ledge
        
    def ext_gsea(self, gs1, gs2, name1='Gene set 1', name2='Gene set 2'):
        self.__gs1 = gs1
        self.__gs2 = gs2
        self.__gsn1 = name1
        self.__gsn2 = name2
        
        l = len(self.__rk)
        
        self.__hits1 = np.zeros(l)
        self.__hits2 = np.zeros(l)
        
        for i in range(0, l):
            if self.__rk[i] in gs1:
                self.__hits1[i] = 1
            
            if self.__rk[i] in gs2:
                self.__hits2[i] = 1
        
        
        l = len(self.__rkc)
        
        self.__isgs = np.zeros(l)
        
        for i in range(0, l):
            if (self.__pn[i] > 0 and self.__rkc[i] in gs1) or (self.__pn[i] < 0 and self.__rkc[i] in gs2):
                self.__isgs[i] = 1
                
            
        
        # Compute ES
        
        if self.__w != 1:
            self.__score_hit = np.cumsum(np.abs(self.__rsc * self.__isgs) ** self.__w)
        else:
            self.__score_hit = np.cumsum(np.abs(self.__rsc * self.__isgs))
                
        self.__score_hit = self.__score_hit / self.__score_hit[-1]
        self.__score_miss = np.cumsum(1 - self.__isgs)
        self.__score_miss = self.__score_miss / self.__score_miss[-1]
        
        self.__es_all = self.__score_hit - self.__score_miss
        self.__es = np.max(self.__es_all) + np.min(self.__es_all)
        
        isen = np.zeros(l)
        
        if self.__es < 0:
            ixpk = np.where(self.__es_all == np.min(self.__es_all))[0][0]
            isen[ixpk:] = 1
            self.__ledge = self.__rkc[(isen == 1) & (self.__isgs == 1)]
            self.__ledge = self.__ledge[::-1]
        else:
            ixpk = np.where(self.__es_all == np.max(self.__es_all))[0][0]
            print(ixpk)
            isen[0:(ixpk + 1)] = 1
            self.__ledge = self.__rkc[(isen == 1) & (self.__isgs == 1)]
            
        if self.__np > 0:
            self.__bg['es'] = np.zeros(self.__np)
            
            for i in range(0, self.__np):
                self.__bg['isgs']  = self.__isgs[np.random.permutation(l)];  
                
                if self.__w != 1:
                    self.__bg['hit'] = np.cumsum((np.abs(self.__rsc * self.__bg['isgs'])) ** self.__w)
                else:
                    self.__bg['hit'] = np.cumsum(np.abs(self.__rsc * self.__bg['isgs']))
                    
                self.__bg['hit'] = self.__bg['hit'] / self.__bg['hit'][-1]
                self.__bg['miss'] = np.cumsum(1 - self.__bg['isgs']);
                self.__bg['miss'] = self.__bg['miss'] / self.__bg['miss'][-1]
                self.__bg['all'] = self.__bg['hit'] - self.__bg['miss'];
                self.__bg['es'][i] = max(self.__bg['all']) + min(self.__bg['all']);

            if self.__es < 0:
                self.__pv  = np.sum(self.__bg['es'] <= self.__es) / self.__np
                self.__nes = self.__es / np.abs(np.mean(self.__bg['es'][self.__bg['es'] < 0]))
            else:
                self.__pv  = np.sum(self.__bg['es'] >= self.__es) / self.__np
                self.__nes = self.__es / np.abs(np.mean(self.__bg['es'][self.__bg['es'] > 0]))
        else:
            self.__pv = -1
            self.__nes = -1
            
        self.__run = True
                
        return self.__es, self.__nes, self.__pv, self.__ledge
                
    @property
    def bg(self):
        return self.__bg
    
    @property
    def score_hit(self):
        return self.__score_hit
    
    @property
    def isgs(self):
        return self.__isgs
    
    @property
    def es(self):
        return self.__es
    
    @property
    def es_all(self):
        return self.__es_all
    
    @property
    def score_miss(self):
        return self.__score_miss
         
    def plot(self, title=None, out=None):
        """
        Replot existing GSEA plot to make it better for publications
        """
        
        if not self.__run:
            return
        
        libplot.setup()
        
        # output truetype
        #plt.rcParams.update({'pdf.fonttype':42,'ps.fonttype':42})
        # in most case, we will have mangy plots, so do not display plots
        # It's also convinient to run this script on command line.
        
        fig = libplot.new_base_fig(w=10, h=7)
        
        # GSEA Plots
        gs = gridspec.GridSpec(16, 1)
        
        
        
        x = np.array(list(range(0, len(self.__rk))))
      
        
        es1, es_all1, hits1, ledge1 = self.enrichment_score(self.__gs1)
        es2, es_all2, hits2, ledge2 = self.enrichment_score(self.__gs2)
        
        
        # Ranked Metric Scores Plot
        
        ix = list(range(0, len(x), 100))
        
        print(ix)
        
        x1 = x[ix]
        y1 = self.__rs[ix]
        
        print(hits1)
        
        ax1 = fig.add_subplot(gs[10:])
        ax1.fill_between(x1, y1=y1, y2=0, color='#2c5aa0')
        ax1.set_ylabel("Ranked list metric", fontsize=14)
            
        ax1.text(.05, .9, self.__gsn1, color='black', horizontalalignment='left', verticalalignment='top',
          transform=ax1.transAxes)
        ax1.text(.95, .05, self.__gsn2, color='red', horizontalalignment='right', verticalalignment='bottom',
          transform=ax1.transAxes)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.set_xlim((0, len(x)))
        
        #
        # Hits
        #
        
        # gene hits
        ax2 = fig.add_subplot(gs[8:9], sharex=ax1)
        
        # the x coords of this transformation are data, and the y coord are axes
        trans2 = transforms.blended_transform_factory(ax2.transData, ax2.transAxes)
        ax2.vlines(np.where(hits1 == 1)[0], 0, 1, linewidth=.5, transform=trans2, color ='black')
        libplot.invisible_axes(ax2)
        
        ax3 = fig.add_subplot(gs[9:10], sharex=ax1)
        
        # the x coords of this transformation are data, and the y coord are axes
        trans3 = transforms.blended_transform_factory(ax3.transData, ax3.transAxes)
        ax3.vlines(np.where(hits2 == 1)[0], 0, 1, linewidth=.5,transform=trans3, color ='red')
        libplot.invisible_axes(ax3)
        
        
        #
        # Enrichment score plot
        #
        
        ax4 = fig.add_subplot(gs[:8], sharex=ax1)
        
        # max es
        y2 = np.max(es_all1)
        x1 = np.where(es_all1 == y2)[0]
        print(x1, y2)
        ax4.vlines(x1, 0, y2, linewidth=.5, color='grey')
        
        y2 = np.min(es_all2)
        x1 = np.where(es_all2 == y2)[0]
        print(x1, y2)
        ax4.vlines(x1, 0, y2, linewidth=.5, color='grey')
        
        y1 = es_all1
        y2 = es_all2
        
        
        ax4.plot(x, y1, linewidth=3, color ='black')
        ax4.plot(x, y2, linewidth=3, color ='red')
        
        
        
        ax4.tick_params(axis='both', which='both', color='dimgray')
        #ax4.spines['left'].set_color('dimgray')
        ax4.spines['bottom'].set_visible(False) #set_color('dimgray')
        
        # the y coords of this transformation are data, and the x coord are axes
        trans4 = transforms.blended_transform_factory(ax4.transAxes, ax4.transData)
        ax4.hlines(0, 0, 1, linewidth=.5, transform=trans4, color='grey')
        
        
        
        ax4.set_ylabel("Enrichment score (ES)", fontsize=14)
        ax4.set_xlim(min(x), max(x))
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.tick_params(axis='both', which='both', bottom='off', top='off', labelbottom='off', right='off')
        ax4.locator_params(axis='y', nbins=5)
        # FuncFormatter need two argment, I don't know why. this lambda function used to format yaxis tick labels.
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda tick_loc,tick_num :  '{:.1f}'.format(tick_loc)) )
        
        
        
        if title is not None:
            fig.suptitle(title)
     
        

        fig.tight_layout(pad=2) #rect=[o, o, w, w])
        
        if out is not None:
            plt.savefig(out, dpi=600)
