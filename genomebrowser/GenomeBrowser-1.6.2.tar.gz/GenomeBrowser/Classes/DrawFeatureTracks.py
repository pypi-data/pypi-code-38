#!/usr/bin/python
# encoding: utf-8

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "1.0.1"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "beta"

##################################################################################
#
#	DrawFeatureTracks.py
#
#
#	Copyright (c) Sander Granneman 2019
#
#	Permission is hereby granted, free of charge, to any person obtaining a copy
#	of this software and associated documentation files (the "Software"), to deal
#	in the Software without restriction, including without limitation the rights
#	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#	copies of the Software, and to permit persons to whom the Software is
#	furnished to do so, subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be included in
#	all copies or substantial portions of the Software.
#
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#	THE SOFTWARE.
#
##################################################################################

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.pyplot import rcParams
from pyCRAC.Methods import numpy_overlap, contigousarray2Intervals
from collections import defaultdict
from operator import itemgetter
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['font.sans-serif'] = ['Arial']
matplotlib.rcParams['lines.linewidth'] = 0.5
matplotlib.rcParams['axes.linewidth'] = 0.75
matplotlib.rc('ytick',labelsize=12)
matplotlib.rc('xtick',labelsize=8)


class DrawGeneFeatures():
	""" class for drawing genes in a genomic ranges. 
	Requires a GTF2 object with gene feature and sequence information """
	def __init__(self):
		self.figure = plt.figure()
		self.figure.clear()
		self.coordinates = []
		self.chromosome = str()
		self.strand = "+"
		self.ranges = 0
		self.bbox = True
		self.plotposition = [0,0,1,0]
		self.axesdict = defaultdict()
		self.numberofaxes = 0
			
	@staticmethod
	def divideCoordinatesOverTracks(data):
		""""
		a = array([
		   [  1,  30],
		   [  5,  40],
		   [ 50,  70],
		   [ 60,  90],
		   [  5,  95],
		   [100, 300],
		   [200, 400]
		   ])
	   
		divideCoordinatesOverTracks(a) should yield:
	
		defaultdict(<type 'list'>, {1: [[1, 30], [50, 70], [100, 300]], 2: [[5, 40], [60, 90], [200, 400]], 3: [[5, 95]]})
		The dictionary key is the track number. The values are the interval coordinates
		
		"""
		trackdict = defaultdict(list)
		numberoftracks = 1
		data = sorted(data, key=itemgetter(0))
		try:
			data = [i for i in data if not i['f2'].startswith(b'INT')]
		except TypeError:
			pass
		while data:
			firstcoord = data.pop(0)
			toremove = list()
			trackdict[numberoftracks].append(firstcoord)
			for coord in data:
				if firstcoord[1] < coord[0]:
					firstcoord = coord
					trackdict[numberoftracks].append(coord)
					toremove.append(coord)
			numberoftracks+=1
			for i in toremove:
				data.remove(i)
		return trackdict

	@staticmethod
	def mergeIntervalCoordinates(a,b):
		""" merges overlapping interval coordinates. Example:
		a = [(3218948, 3219354), (3215871, 3217986)]
		b = [(3218953, 3219006),(3219170, 3219216)]

		mergeIntervalCoordinates(a,b) returns:

		[(3215871, 3217986),(3218948, 3218952),(3219007, 3219169),(3219217, 3219354)]

		"""
		newcoord = list()
		for i in a:
			if i:
				coords = np.arange(i[0],i[1]+1)
				for j in b:
					index = np.where(np.in1d(coords,np.arange(j[0],j[1]+1)))[0]
					coords = np.delete(coords,index)
				newcoord.extend(contigousarray2Intervals(coords))
		newcoord.sort()
		return newcoord

	@staticmethod
	def drawCDS(x,y,width,height=0.6,linewidth=2,fill="ivory"):
		"""to draw a rectangle representing exon or CDS features """
		return patches.Rectangle((x,y),width,height,fc=fill,edgecolor="black",lw=linewidth)
		#return patches.Arrow(x,height,width,0,width=3,fc=fill,edgecolor='black',lw=linewidth)
		#return patches.FancyBboxPatch((x,y),width,0.23,boxstyle="rarrow,pad=0.1",fc=fill,edgecolor='black',lw=linewidth)

	@staticmethod
	def drawUTR(x,y,width,height=0.30,linewidth=2,fill="#ffffff"):
		"""to draw a rectangle representing UTRs"""
		y += 0.15
		return patches.Rectangle((x,y),width,height,fc=fill,edgecolor='black',lw=linewidth)

	@staticmethod
	def drawIntron(x,y,width,linewidth=2):
		"""to draw a line representing an intron """
		height=0.6
		y += float(height)/2
		xend = x+width
		xmid = x+float(xend-x)/2
		ytop = y+0.25
		yend = y
		verts = [
			(x,y),			  # left, bottom
			(xmid,ytop),	  # left, top
			(xend,yend),	  # right, bottom
			]

		codes = [Path.MOVETO,
				 Path.LINETO,
				 Path.LINETO,
				 ]
		return patches.PathPatch(Path(verts,codes),color='k',ls='dashed',lw=linewidth,fill=False)
		
	@staticmethod
	def noSpinesAndTicks(ax):
		""" removes all spines and ticks from axes """
		ax.spines['top'].set_visible(False)
		ax.spines['left'].set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['bottom'].set_visible(False)
		ax.xaxis.set_ticks([])
		ax.yaxis.set_ticks([])
		
	@staticmethod	
	def bottomSpineAndTicks(ax):
		""" with this function only the botom axis will be shown """
		ax.spines['top'].set_visible(False)
		ax.spines['left'].set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['bottom'].set_visible(True)
		ax.spines['bottom'].set_position('center')
		ax.set_yticks([])

	@staticmethod
	def colorNucleotides(ax):
		""" for colouring nucleotide backgrounds """
		color = 'white'
		for nucleotide in ax.get_xticklabels():
			nucleotide.set_fontweight('bold')
			if nucleotide.get_text().upper() == 'A':
				color = 'blue'
			elif nucleotide.get_text().upper() == 'T' or nucleotide.get_text().upper() == 'U':
				color = 'green'
			elif nucleotide.get_text().upper() == 'G':
				color = 'red'
			elif nucleotide.get_text().upper() == 'C':
				color = 'yellow'
			elif nucleotide.get_text().upper() is None:
				continue
			else:
				sys.stderr.write("I don't recognize %s as a nucleotide symbol\n" % nucleotide)	
			nucleotide.set_bbox(dict(facecolor=color,edgecolor=color,pad=0))

	def saveFigure(self,filename="test.pdf",dpi=400,reset=False):
		""" to save the figure to disk. Default is pdf format """
		self.figure.savefig(filename,bbox_inches='tight')
		#self.figure.tight_layout()
		if reset:
			self.figure.clear()
			self.figure = plt.gcf()
			self.plotposition = [0,0,1,0]
			self.axesdict = defaultdict()
			self.numberofaxes = 0
		
	def addFeatureTrack(self,gtf,strand="+",ranges=0,showgenename=True,exon_color="ivory",text_size=6,line_width=0.5):
		""" Adds a track with gene features. Note for this you need a GTF2 object ('gtf') containing the genome annotation information! """
		allowedstrands = ["-","+"]
		assert strand in allowedstrands, "I don't recognize %s as a strand option. Please select from %s\n" % (strand, ",".join(allowedstrands))
		bbox_props = None
		chromstart,chromend = self.coordinates
		tracklength = chromend-chromstart
		count = 0.35
		spacing = 0.06
		height = 0.03
		self.plotposition[-1] = height
		self.plotposition[1] -= 0.10
		feats = gtf.chromosomeGeneCoordIterator(self.chromosome,strand=strand,numpy=True)
		genomicfeats = numpy_overlap(feats,chromstart,chromend,returnall=True)
		if genomicfeats:
			trackdict = self.divideCoordinatesOverTracks(genomicfeats)
			if showgenename:
				if strand == "+":
					bbox_props = dict(boxstyle="rarrow,pad=0.2",fc='w',ec='k',lw=line_width)
				if strand == "-":
					bbox_props = dict(boxstyle="larrow,pad=0.2",fc='w',ec='k',lw=line_width)
			for track in sorted(trackdict):
				self.numberofaxes += 1
				self.axesdict[self.numberofaxes] = self.figure.add_axes(self.plotposition)
				self.plotposition[1] -= spacing
				self.axesdict[self.numberofaxes].set_xlim(self.coordinates)
				self.noSpinesAndTicks(self.axesdict[self.numberofaxes])
				for interval in trackdict[track]:
					genestart,geneend,gene = interval
					genewidth = geneend-genestart
					utrs = gtf.utrCoordinates(gene,ranges=ranges)
					cdss = gtf.cdsCoordinates(gene)
					introns = gtf.intronCoordinates(gene)
					if introns:
						for start,end in introns:
							width = end - start + 1
							self.axesdict[self.numberofaxes].add_patch(self.drawIntron(start,count,width,linewidth=line_width))
					if utrs:
						if introns:
							utrs = self.mergeIntervalCoordinates(utrs,introns)
						try:
							for start,end in utrs:
								width = end - start + 1
								self.axesdict[self.numberofaxes].add_patch(self.drawUTR(start,count,width,linewidth=line_width))
						except:
							pass
					if cdss:
						for start,end in cdss:
							width = end - start + 1
							self.axesdict[self.numberofaxes].add_patch(self.drawCDS(start,count,width,linewidth=line_width,fill=exon_color))
					else:
						exons = gtf.exonCoordinates(gene)
						for start,end in exons:
							width = end - start + 1
							self.axesdict[self.numberofaxes].add_patch(self.drawCDS(start,count,width,linewidth=line_width,fill=exon_color))
					if showgenename:
						textposition = genestart+(genewidth/2)
						if textposition < self.coordinates[1] and textposition > self.coordinates[0]:
							self.axesdict[self.numberofaxes].text(textposition,-0.30,gene, ha="center", va="center",size=text_size,bbox=bbox_props)
		#self.plotposition[1] -= 0.10
						
	def addChromosomeTrack(self,step=None,text_size=12):
		""" Adds an x-axis with chromosome locations """
		if not step:
			if (self.coordinates[1]- self.coordinates[0]) <= 1000: # automatically adjust the step size for x-tics if the region is small
				step = 100
			elif (self.coordinates[1]- self.coordinates[0]) <= 500: # automatically adjust the step size for x-tics if the region is small
				step = 50
			else:
				step = 500
		spacing = 0.25
		height = 0.10
		self.plotposition[1] -= 0.15
		self.plotposition[-1] = height
		self.numberofaxes += 1
		self.axesdict[self.numberofaxes] = self.figure.add_axes(self.plotposition)
		self.axesdict[self.numberofaxes].set_xlabel("%s" % self.chromosome,fontsize=text_size+2)
		self.axesdict[self.numberofaxes].set_xlim(self.coordinates)
		self.axesdict[self.numberofaxes].set_xticks(np.arange(self.coordinates[0],self.coordinates[1],step))
		#self.axesdict[self.numberofaxes].xaxis.set_label_position('top')
		self.axesdict[self.numberofaxes].xaxis.set_tick_params(labelsize=text_size)
		self.bottomSpineAndTicks(self.axesdict[self.numberofaxes])
		self.plotposition[1] -= 0.15
		
	def addSequenceTrack(self,gtf,color=True,text_size=4):
		""" Adds a DNA sequence track. Requires a gtf object with sequence information """
		upstream,downstream = self.coordinates
		if downstream-upstream <= 150:
			sequence = gtf.sequence(self.chromosome,"+",upstream,downstream)
			spacing = 0.010
			height = 0.005
			self.plotposition[1] -= 0.075
			self.numberofaxes += 1
			self.plotposition[1] -= spacing
			self.plotposition[-1] = height
			self.axesdict[self.numberofaxes] = self.figure.add_axes(self.plotposition)
			self.noSpinesAndTicks(self.axesdict[self.numberofaxes])
			self.axesdict[self.numberofaxes].set_xticks(np.arange(len(sequence)))
			self.axesdict[self.numberofaxes].set_xticklabels([i.upper() for i in sequence],fontsize=text_size)
			self.axesdict[self.numberofaxes].tick_params(axis=u'both', which=u'both',length=0)
			self.axesdict[self.numberofaxes].tick_params(axis='x',labeltop=True,labelbottom=False,pad=0)
			self.axesdict[self.numberofaxes].xaxis.set_label_position('top')
			if color is True:
				self.colorNucleotides(self.axesdict[self.numberofaxes])
			self.plotposition[1] -= 0.075
		else:
			sys.stderr.write("The sequence is too long for printing nucleotides. The maximum is 150 nucleotides\nIgnoring this track\n")	