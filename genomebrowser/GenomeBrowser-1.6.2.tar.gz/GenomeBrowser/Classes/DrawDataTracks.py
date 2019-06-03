#!/usr/bin/python

__author__		= "Sander Granneman"
__copyright__	= "Copyright 2019"
__version__		= "1.0.1"
__credits__		= ["Sander Granneman"]
__maintainer__	= "Sander Granneman"
__email__		= "sgrannem@ed.ac.uk"
__status__		= "beta"

##################################################################################
#
#	DrawDataTracks.py
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

from GenomeBrowser.Classes.DrawFeatureTracks import *
import matplotlib.cm as cm
import matplotlib.colors as colors

class MakeGenomeBrowserTracks(DrawGeneFeatures):
	""" Class for making genome browser snapshots of your data """ 
	def __init__(self):
		DrawGeneFeatures.__init__(self)
		self.ylim = None
		self.xgrid = False
		self.ygrid = True

	@staticmethod
	def readBedGraph(filename):
		""" takes a bedgraph file and converts it into a pandas dataframe """
		df = pd.read_csv(filename,sep="\t",comment="#",index_col=None,header=None,names=["chromosome","start","end","score"])
		return df
		
	@staticmethod
	def readBedFile(filename):
		""" takes a bed6 (!) file and converts it into a pandas dataframe """
		df = pd.read_csv(filename,sep="\t",comment="#",index_col=None,header=None,names=["chromosome","start","end","name","score","strand"])
		return df
		
	@staticmethod		
	def readGTFfile(filename):
		""" takes a GTF file and converts it into a pandas dataframe """
		df = pd.read_csv(filename,sep="\t",comment="#",index_col=None,header=None,names=["chromosome","feature","source","start","end","score","strand","frame","group"])
		return df
		
	@staticmethod
	def loadSGRfile(filename):
		df = pd.read_csv(filename,sep="\t",comment="#",names=['chromosome', 'position','score'],header=None,index_col=[0,1])
		return df
		
	@staticmethod
	def loadWigFile(filename):
		df = pd.read_csv(filename,sep="\t",skiprows=2,comment="#",names=['position','score'],header=None,index_col=0)
		return df
			
	@staticmethod
	def makeCumulativeDataFrame(df):
		""" Takes start and end coordinates from a dataframe and makes pileups for the region """
		datapoints = np.arange(min(df['start']),max(df['end']))
		newdf = pd.DataFrame(0,index=datapoints,columns=['score'])
		newdf.index.name = 'position'
		for i in df.index:
			start = df.loc[i,'start']
			end = df.loc[i,'end']
			score = df.loc[i,'score']
			if int(start) == int(end):
				sys.stderr.write("ERROR! The start and end coordinates of the nucleotide are the same. Please change the bedGraph file at position %s\n" % i)
				continue
			if score == ".":
				score = 1
			newdf.loc[np.arange(start,end),'score'] += score
		return newdf
		
	def getRegionData(self,df,strand=None):
		assert self.coordinates, "You forgot to set the coordinates that you would like to analyze\n"
		start,end = self.coordinates
		if 'chromosome' in df.columns and 'strand' in df.columns and 'start' in df.columns:					### in the case of GTF and bed6 files:
			assert self.chromosome, "You forgot to set the chromosome variable\n"
			selecteddata = df[(df['chromosome'] == self.chromosome) & (df['start'] >= start) & (df['start'] <= end) & (df['strand'] == strand)]
		elif 'chromosome' in df.columns and not 'strand' in df.columns and 'position' in df.columns:		### in the case of sgr files:
			assert self.chromosome, "You forgot to set the chromosome variable\n"
			selecteddata = df[(df.index.get_level_values('chromosome') == self.chromosome) & \
				(df.index.get_level_values('position') >= start) & (df.index.get_level_values('position') <= end)]
		elif 'chromosome' in df.columns and not 'strand' in df.columns and 'start' in df.columns:			### in the case of bedgraph files
			assert self.chromosome, "You forgot to set the chromosome variable\n"
			selecteddata = df[(df['chromosome'] == self.chromosome) & (df['start'] >= start) & (df['start'] <= end)]
		elif not 'chromosome' in df.columns and not 'strand' in df.columns:									### in the case of wig files:
			selecteddata = df[(df.index.get_level_values('position') >= start) & (df.index.get_level_values('position') <= end)]
		return selecteddata
	
	def formatAxes(self,ax,text_size=10,ylim=None,xlabel="Coordinates",ylabel=None,showaxis=False):
		""" to tweak the plotting of the axes as well as the fontsize """
		for loc,spine in list(ax.spines.items()):
			if loc == 'left':	# settings for the y-axis
				spine.set_visible(True)
				spine.set_position(("outward",10))
				spine.set_smart_bounds(True)
				if ylim:
					ax.set_yticks(ylim) 
					ax.set_ylim(ylim)
					ax.set_yticklabels(ylim,fontsize=text_size)
				if ylabel:
					ax.set_ylabel(ylabel,fontsize=text_size,rotation=0)
				ax.yaxis.set_ticks_position('left')
				ax.get_yaxis().set_tick_params(which='both',direction='out')
			elif loc == 'bottom':	# settings for x-axis
				spine.set_visible(True)
				ax.set_xlim(self.coordinates)
				if xlabel:
					ax.set_xlabel(xlabel,fontsize=text_size)
				if showaxis:
					ax.get_xaxis().set_tick_params(which='bottom',direction='out')
					ax.get_xaxis().tick_bottom()
					ax.set_xticks(np.arange(self.coordinates[0],self.coordinates[1],500))
				else:
					ax.set_xticks([])
			else:
				spine.set_visible(False)
				
		ax.patch.set_visible(False)
	
	def addDataTrack(self,dataset,color="blue",colormap=None,ygrid=False,xgrid=False,ylim=None,xlabel="Coordinates",ylabel="RPM",plottype="line",datatype="bedgraph",showaxis=False,text_size=12,line_width=0.5):
		""" creates a genomebrowser track with ngs data as a line or bar plot """
		plotoptions = ["line","bar","interval"]
		datatypes = ["sgr","wig","bedgraph","gtf"]
		assert plottype	in plotoptions, "please choose from %s when selecting type\n" % ",".join(plotoptions)
		assert datatype in datatypes, "I don't know how to handle %s data. Please choose from the following:\t%s" % (datatype,",".join(datatypes))
		if datatype in datatypes[:2] and plottype == "interval":
			sys.stderr.write("I cannot combine the interval plot type with wig data files. Please select 'line' as plot type\n")
			return None
		spacing = 0.20	# spacing between each track
		height = 0.15	# height of track
		lim = []
		self.plotposition[-1] = height
		self.plotposition[1] -= spacing
		self.numberofaxes += 1
		self.axesdict[self.numberofaxes] = self.figure.add_axes(self.plotposition)
				
		if plottype == 'line' or plottype == 'bar':
			if datatype == 'wig' or datatype == 'sgr':
				cumulativedata = dataset
			elif datatype == 'bedgraph' or datatype == 'gtf':
				cumulativedata = self.makeCumulativeDataFrame(dataset)
			if ygrid: self.axesdict[self.numberofaxes].yaxis.grid(b=True, which='major', color='grey', linestyle='--')
			if xgrid: self.axesdict[self.numberofaxes].xaxis.grid(b=True, which='major', color='grey', linestyle='--')

			if not ylim:
				ymin = 0
				ymax = round(max(cumulativedata.values)[0],2)
				lim = [ymin,ymax]
			else:
				lim = ylim
			
			x = cumulativedata.index.get_level_values('position')
			y = cumulativedata[cumulativedata.columns[0]]
			
			if plottype == 'line':
				self.axesdict[self.numberofaxes].plot(x,y,c='k',lw=line_width)
				self.axesdict[self.numberofaxes].fill_between(x,y,facecolor=color,interpolate=True,alpha=0.6)
			elif plottype == 'bar':
				self.axesdict[self.numberofaxes].bar(x,y,lw=line_width)
				#self.axesdict[self.numberofaxes].fill_between(x,y,facecolor=color,interpolate=True,alpha=0.6)				

		elif plottype == 'interval':
			numberoflines = len(dataset.index)
			scores = dataset['score']
			colorvalues = []
			if colormap:
				colorvalues = self.getTrackColors(scores,colormap)					
			else:
				colorvalues = len(scores)*['k']
			intervalcoordinates = list(zip(dataset['start'],dataset['end'],colorvalues))
			intervaltrackdict = self.divideCoordinatesOverTracks(intervalcoordinates)
			totaltracks = len(intervaltrackdict.keys())
			if not ylim:
				lim = [0,totaltracks]
			else:
				lim = ylim
			for y in sorted(intervaltrackdict.keys()):
				for j in intervaltrackdict[y]:
					xmin,xmax,colorvalue = j
					self.axesdict[self.numberofaxes].hlines(y,xmin,xmax,lw=line_width,color=colorvalue)

		self.formatAxes(self.axesdict[self.numberofaxes],text_size,lim,xlabel,ylabel,showaxis)		### Tweaking the settings for the axes, as well as font size