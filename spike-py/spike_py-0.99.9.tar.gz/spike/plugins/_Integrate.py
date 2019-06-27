#!/usr/bin/env python
# encoding: utf-8

"""A set of tools for computing Integrals for 1D  NMR spectra

If present, it can guess integral zones from an existing peak-list
Add .integzones .integcurves and .integvalues  into NPKDataset

First version by DELSUC Marc-André on May-2019.

"""

from __future__ import print_function
import numpy as np
import unittest
from spike.NPKData import NPKData_plugin, parsezoom
from spike.NPKError import NPKError

def delintegrals(data):
    "horrible hack to remove integrals - everything should be rewritten OOP!"
    try:
        del data.integzones
        del data.integcurves
        del data.integvalues
    except:
        pass
    return data

def compzones(data, separation = 3, wings = 5):
    """
    computes integral zones from peak list, 
    return a list [(star,end)...] in index unit
    separation : if two peaks are less than separation x width n they are aggregated, default = 3
    wings : integrals sides are extended by wings x width, default = 5
    """
    try:
        if len(data.peaks) == 0:
            return []                   # return [] if empty peaklist
    except AttributeError:
        data.pp().centroid()            # create one if missing
    # then build integral list
    integrals = []
    prev = data.peaks[0]    # initialize
    start = prev.pos - wings*prev.width
    for pk in data.peaks[1:]: # then through remaining
        # extending or creating a new zone
        if (pk.pos - separation*pk.width) > (prev.pos + separation*prev.width): # we're done
            end = prev.pos + wings*prev.width
            integrals.append([start,end])
            start = pk.pos - wings*pk.width
        prev = pk
    end = data.peaks[-1].pos + wings*data.peaks[-1].width
    integrals.append([start,end])
    data.integzones = integrals
    return data

def compsums(data, bias=0.0, calib=None):
    "from integral lists, computes curves and values, sets integcurves and integvalues"
    curves = []
    buff = (data.get_buffer().real-bias)/data.cpxsize1
    for (a,b) in data.integzones:
        curves.append(buff[int(a):int(b)].cumsum())
    data.integcurves = curves
    data.integvalues = np.array( [c[-1] for c in curves] )
    # then calibrate
    sumax = max(data.integvalues)
    if calib is None:
        data.integvalues *= 100/sumax   # max at 100
    else:
        data.integvalues *= calib
    return data

def display(data, integoff=0.3, integscale=0.5, color='red', label=False, 
    labelposition=None, regions=False, zoom=None, figure=None):
    "displays integrals"
    import matplotlib.transforms as transforms
    from spike.Display import testplot
    plt = testplot.plot()
    if figure is None:
        ax = plt.subplot(111)
    else:
        ax = figure
    trans = transforms.blended_transform_factory( ax.transData, ax.transAxes )
    z1, z2 = parsezoom(data, zoom)
    sumax = max([c[-1] for c in data.integcurves])
    for ((a,b),c,v) in zip(data.integzones, data.integcurves, data.integvalues):
#        print(a,b,max(c)/sumax)
        if a>z2 or b<z1:
            continue   # we're outside
        xinteg = data.axis1.itoc( np.linspace(a,b,len(c)) )
        yinteg = integoff + integscale*c/sumax
        ax.plot(xinteg, yinteg, transform=trans, color=color)
        if label:
            if labelposition:
                xl = xinteg[0] 
                yl = labelposition
            else:
                xl = xinteg[-1]
                yl = yinteg[-1]
            ax.text(xl,yl,"%.2f"%v, transform=trans, color=color, fontsize=7)
        if regions:
            ax.plot([xinteg[0],xinteg[0]], [0,1], transform=trans, color=color, alpha=0.1)
            ax.plot([xinteg[-1],xinteg[-1]], [0,1], transform=trans, color=color, alpha=0.1 )

class Integralitem(object):
    def __init__(self, start, end, curve, value):
        """
        the elemental integral item - used by Integrals
        start, end : the delimited zone, in pixels
        curve : the cumsum over the zone (eventually modified)
        value : the calibrated value
        """
        self.start = start
        self.end = end
        self.curve = curve
        self.value = value
    def _report(self):
        return "%d - %d : %f  on %d points\n"%(self.start, self.end, self.value, len(self.curve))
    def __str__(self):
        return self._report()
    def __repr__(self):
        return "Integralitem %s"%self._report()
class Integrals(list):
    """
    the class to hold a list of Integral

    an item is [start, end, curve as np.array(), value]
    start and end are in index !
    """
    def __init__(self, data, *arg, **kwds): #compute=True, source=None):
        super(Integrals, self).__init__(*arg, **kwds)
        # I can't figure out how to explictly specify a keyword arg with *args:
        #   def __init__(self, *arg, threshold=None, source=None): ...
        # so I use **kwds and sqauwk if something unexpected is passed in.
        # code taken from   lib/python2.7/pstats.py
        #
        # additional kw are source: the originating dataset, compute: initialize values
        self.source = data
        if "compute" in kwds:
            self.source = kwds["compute"]
            del kwds["compute"]
        else:
            self.compute = True
        if kwds:
            keys = kwds.keys()
            keys.sort()
            extras = ", ".join(["%s=%s" % (k, kwds[k]) for k in keys])
            raise(ValueError, "unrecognized keyword args: %s" % extras)
        self.calibration = None  # global calibration
        self.bias = 0.0          # global bias
        self.frompeaks()

    def _report(self):
        ll = ['calibration: %d\n'%self.calibration]
        for i,ii in enumerate(self):
            ll.append( "%d: %s"(i,ii._report()) )
        return "\n".join(ll)
    def report(self):
        for ii in self:
            print(ii)
    def to_pandas(self):
        "export extract of current integrals list to pandas Dataframe"
        import pandas as pd
        I1 = pd.DataFrame({
            'Start': [self.source.axis1.itoc(ii.start) for ii in self],
            'End': [self.source.axis1.itoc(ii.end) for ii in self],
            'Value': [ii.curve[-1] for ii in self],
            'Calibration': [ii.value for ii in self]
        })
        return I1
    def frompeaks(self, separation = 3, wings = 5):
        """
        computes integrals zones from peak list, 
        separation : if two peaks are less than separation x width n they are aggregated, default = 3
        wings : integrals sides are extended by wings x width, default = 5
        """
        data = self.source
        try:
            pk = data.peaks
        except AttributeError:
            data.pp().centroid()            # create one if missing
            pk = data.peaks
        # then build integral list
        if len(pk) == 0:
                return []                   # return [] if empty peaklist
        prev = data.peaks[0]    # initialize
        start = prev.pos - wings*prev.width
        for pk in data.peaks[1:]: # then through remaining
            # extending or creating a new zone
            if (pk.pos - separation*pk.width) > (prev.pos + separation*prev.width): # we're done
                end = prev.pos + wings*prev.width
                self.append(   Integralitem(start, end, [], 0.0)  )
                start = pk.pos - wings*pk.width
            prev = pk
        end = data.peaks[-1].pos + wings*data.peaks[-1].width
        self.append(   Integralitem(start, end, [], 0.0)  )
    def zone2curves(self):
        "from integral lists, computes curves and values"
        curves = []
        buff = (self.source.get_buffer().real-self.bias)/self.source.cpxsize1
        intmax = 0.0
        for iint in self:
            curves = buff[int(iint.start):int(iint.end)].cumsum()
            iint.curve = curves
            iint.value = curves[-1]
            intmax = max(intmax,iint.value)
        # then calibrate
        self.calibrate()
    def calibrate(self, calibration=None):
        """computes integration values from curves
        either use calibration value as a scale, or put the largest to 100.0 is calibration is None
        """
        if calibration:
            self.calibration = calibration
        intmax = 0.0
        for iint in self:
            iint.value = iint.curve[-1]
            intmax = max(intmax,iint.value)
        if self.calibration is None:   # set max at 100
            calib = 100/intmax
        else:
            calib = self.calibration
        for iint in self:
            iint.value *= calib


def calibrate(npkd, entry, value):
    """
    on a dataset alreat integrated, the integrals are adapted so that
    the given entry is set to the given value.
    """
    try:
        vals = npkd.integvalues
    except:
        raise NPKError('data set should be integrated with .integrate() first!',data=npkd)
    npkd.integvalues *= value/vals[entry]
    return npkd
def integrate(npkd, separation=3, wings=5, bias=0.0, calibration=None):
    """
    computes integral zones and values from peak list, 

    separation : if two peaks are less than separation x width n they are aggregated, default = 3
    wings : integrals sides are extended by wings x width, default = 5
    bias: this value is substracted to data before integration
    calibration: a coefficient to multiply all integrals / if None (default) largest is set at 100
    """
    compzones(npkd, separation=separation, wings=wings)
    compsums(npkd, bias=bias, calib=calibration)
    return npkd
#-------------------------------------------------------
def int2pandas(npkd):
    "export extract of current integrals list to pandas Dataframe"
    import pandas as pd
    I1 = pd.DataFrame({
        'Start': [npkd.axis1.itoc(ii[0]) for ii in npkd.integzones],
        'End': [npkd.axis1.itoc(ii[1]) for ii in npkd.integzones],
        'Value': [c[-1] for c in npkd.integcurves],
        'Calibration': npkd.integvalues
    })
    return I1

NPKData_plugin("integrate", integrate)
NPKData_plugin("calibrate", calibrate)
NPKData_plugin("display_integrals", display)
NPKData_plugin("int2pandas", int2pandas)
NPKData_plugin("delintegrals", delintegrals)

