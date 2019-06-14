# -*- coding: utf-8 -*-
import codecs
import numpy as np
from hydroinform import DFS
from hydroinform import Mike_river
from hydroinform import hymod
from operator import attrgetter


class Res1DReader(object):
    """This class reads data from a Res1d file and returns a Hymod reach network"""
    def __init__(self, Res1DFileName):
        self.res1d=Mike_river.River_setup()
        self.res1d.read_res1d(Res1DFileName)
        self.number_of_time_steps = self.res1d.res.number_of_time_steps

    def getHymodNetwork(self):
        """
        Gets a hymod reach network from the res1d file
        """
        reach_network = hymod.Reach_network()

        reach_dic={}

        for r in self.res1d.reaches:
            #We only create a new reach if we do not already have a reach with that name. Otherwise we merge. TODO: Make TopoID count
            if r.name not in reach_dic:
                reach_dic[r.name]= hymod.Reach(r.name)
                reach_network.reaches.append(reach_dic[r.name])
            reach = reach_dic[r.name]
            reach.description = r.topo_id
            for xs in r.xsecs:
                if not any(x.chainage==-xs.Gridpoint.chainage for x in reach.xss): #We can only add one xsecs at the same chainage
                    xsec = hymod.Xs(name=xs.name)
                    xsec.radius_type = 'resistance radius'
                    xsec.chainage = -xs.Gridpoint.chainage
                    xsec.x = xs.Gridpoint.x
                    xsec.y = xs.Gridpoint.y
                    xsec.z= min(xs.xsec_points, key=attrgetter('z')).z
                    for pp in xs.xsec_points:
                        xsec.pps.append(hymod.Pp(pp.x, pp.z-xsec.z))
                    reach.xss.append(xsec)
                    reach.riverPoints.append(hymod.RiverPoint(xsec.chainage, xs.Gridpoint.x, xs.Gridpoint.y))
            for dp in r.digi_points:
                reach.riverPoints.append(hymod.RiverPoint(-dp.chainage, dp.x, dp.y))
           
            downstreamReaches = (dr for dr in self.res1d.reaches if dr.upstream_node==r.downstream_node)
            for dr in downstreamReaches:
                if(dr.name != r.name):
                    reach_network.connections.append(hymod.Connection(r.name, dr.name, -dr.grid_points[0].chainage))

        #Sort and remove duplicate points in reaches
        for hr in reach_network.reaches:
            hr.riverPoints = list(set(hr.riverPoints)) #To remove duplicate points
            hr.riverPoints.sort(key=lambda rp: rp.chainage) #Now sort
            hr.xss.sort(key=lambda rp: rp.chainage) #Also sort xsecs
            hr.update_perimeter_points_xy_coords(rotate180=True)

        hymod.Tools.RemoveUnnecessaryPerimeterPoints(reach_network)

        return reach_network

    def setQandH(self, reaches=[], Time=1):
        """
        Takes a list of hymod reaches and sets Q and H. Matches on reach name and interpolates on chainage
        H is added to the observations. Clear observations first if necessary.
        """
        qitem = next(i for i in self.res1d.DataItems if i.name =='Discharge')
        hitem = next(i for i in self.res1d.DataItems if i.name =='Water level' and i.grouptype==2)
        
        #Reads the data from the res1d-file
        Hdata=self.res1d.getvalues(hitem.ItemIndex+1, Time)
        Qdata=self.res1d.getvalues(qitem.ItemIndex+1, Time)

        for r in reaches:
            del r.observations[:]
            if r.name in Hdata:
                for chainageH in Hdata[r.name]:
                    r.observations.append((-chainageH[0], chainageH[1]))

            if r.name in Qdata:
                chains = [c[0] for c in Qdata[r.name]]
                qs = [c[1] for c in Qdata[r.name]]
                for xs in r.xss:
                    xs.flow =np.interp(-xs.chainage, chains, qs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes the res1d-file
        """
        self.res1d.dispose()





