# -*- coding: utf-8 -*-
import shapefile
import numpy as np

def writeResults(shapefilename, network):
    w=shapefile.Writer(shapefilename, shapeType=shapefile.POINT)
    w.autoBalance=1
    w.field('ReachName', 'C')
    w.field('Chainage', 'F', decimal=4)
    w.field('Discharge', 'F', decimal=10)
    w.field('Level', 'F', decimal=10)

    for r in network.reaches:
        for xsec in r.xss:
            w.record(r.name, xsec.chainage, xsec.flow, xsec.depth)
            w.point(xsec.x, xsec.y)
    w.close()

def writeDetailedLevels(shapefilename, network):
    w=shapefile.Writer(shapefilename,shapeType=shapefile.POINT)
    w.autoBalance=1
    w.field('ReachName', 'C')
    w.field('Chainage', 'F', decimal=4)
    w.field('Level', 'F', decimal=10)

    for r in network.reaches:
        for cv in r.calculated_water_levels:
            w.record(r.name, cv[0], cv[1])
            x= np.interp(cv[0], [p.chainage for p in r.riverPoints], [p.x for p in r.riverPoints]) 
            y= np.interp(cv[0], [p.chainage for p in r.riverPoints], [p.y for p in r.riverPoints]) 
            w.point(x, y)
    w.close()


def writeXsecs(shapefilename, network):
    w=shapefile.Writer(shapefilename, shapeType=shapefile.POINTZ)
    w.autoBalance=1
    w.field('ReachName', 'C')
    w.field('Chainage', 'F', decimal=4)
    w.field('Z', 'F', decimal=10)

    for r in network.reaches:
        for xsec in r.xss:
            for pp in xsec.pps:
                w.record(r.name, xsec.chainage, xsec.z + pp.dz)
                w.pointz(pp.x, pp.y, xsec.z + pp.dz)
    w.close()

def writeRiverpoints(shapefilename, network):
    w=shapefile.Writer(shapefilename,shapeType=shapefile.POINT)
    w.autoBalance=1
    w.field('ReachName', 'C')
    w.field('Chainage', 'F', decimal=4)

    for r in network.reaches:
        for rp in r.riverPoints:
            w.record(r.name, rp.chainage)
            w.point(rp.x, rp.y)
    w.close()
