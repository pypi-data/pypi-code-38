# -*- coding: utf-8 -*-
from hydroinform import DFS
import pandas as pd

class Point(object):
    def __init__(self, x=0.0,y=0.0):
        self.x=x
        self.y=y

class RiverPoint(Point):
    def __init__(self, x = 0, y = 0, chainage=0.0):
        super(RiverPoint, self).__init__(x, y)
        self.chainage = chainage

class GridPoint(RiverPoint):
    def __init__(self, x=0,y=0,chainage=0, z=0.0, type=1):
        super(GridPoint, self).__init__(x,y,chainage)
        self.z=z
        self.type=type
        self.index = -1
        self.itemindex = -1
        self.point_type=''


class Node(Point):
    """description of class"""
    def __init__(self, x=0,y=0,Type=1,name=''):
        super(Node, self).__init__(x,y)
        self.type =Type
        self.name=name

class Reach(object):

    def __init__(self, type, name, topoid, flowdir):
        self.type = type
        self.id=-1
        self.name = name
        self.topo_id = topoid
        self.flow_direction = flowdir
        self.number_of_digi_points=0
        self.number_of_grid_points=0
        self.upstream_node=None
        self.downstream_node =None
        self.digi_points=[]
        self.grid_points=[]
        self.grid_points_h=[]
        self.grid_points_q=[]
        self.xsecs =[]
        self.dataitems={}


class xsecpoint(object):
    def __init__(self, x, z):
        self.x=x
        self.z=z
        self.marker=-1

class xsec(object):
    def __init__(self, name, NumberOfPoints):
        self.name =name
        self.number_of_points = NumberOfPoints
        self.xsec_points=[]
        self.type =-1

class DataItem(object):
    def __init__(self, name):
        self.name = name
        self.chainages =[]
        self.offset=0
        return super(DataItem, self).__init__()

class River_setup(object):
    def __init__(self):
        self.nodes=[]
        self.reaches=[]
        return super(River_setup, self).__init__()

    @classmethod
    def from_file(cls, file_name):
        import os
        from pathlib import Path
        if not os.path.isfile(file_name):
            raise FileNotFoundError(file_name)
        ext=Path(file_name).suffix.lower()
        cls = River_setup()
        if(ext == '.res1d'):
            cls.read_res1d(file_name)
        elif(ext == '.res11'):
            cls.read_res11(file_name)
        return cls;


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.dispose()

    def dispose(self):
        self.res.dispose()

    def getvalues(self, Item=2, TimeStep=0):
        """
        Returns the values for a particular time step and item in a double dictionary with first river name and then chainage
        """
        toreturn={}
        for reach in self.reaches:
            if Item-1 in reach.dataitems:
                values = self.res.get_data(TimeStep,Item)[reach.dataitems[Item-1].offset: reach.dataitems[Item-1].offset + len(reach.dataitems[Item-1].chainages)]
                for i in range(0, len (values)):
                    if reach.name not in toreturn:
                        toreturn[reach.name] ={}
                    toreturn[reach.name][reach.dataitems[Item-1].chainages[i]]=values[i]
        for reach, val in toreturn.items():
            toreturn[reach]= sorted(val.items(), key=lambda x: x[0])
        return toreturn


    def read_res1d(self, Filename):
        """
        Reads a res1D file and builds the network
        """
        self.res= DFS.RES.from_file(Filename)
        nodestart=1

        NumberOfDynamicItems = self.res.StaticItems[nodestart].read_data()[0]
        self.DataItems =[]

        names = self.res.StaticItems[nodestart+1].read_data()
        names=names.split(';')
        for i in range(0, NumberOfDynamicItems):
            self.DataItems.append(DataItem(names[i].replace("\"", "")))
            self.DataItems[i].grouptype =self.res.StaticItems[nodestart+2].read_data()[i]
            self.DataItems[i].ItemIndex=i

        listlength = self.res.StaticItems[nodestart+5].read_data()
        nodestart+=6
        for i in range(0, NumberOfDynamicItems):
            if listlength[i]!=0:
                self.DataItems[i].ReachIndeces=self.res.StaticItems[nodestart].read_data()
                nodestart+=1

        for i in range(0, NumberOfDynamicItems):
            if self.DataItems[i].grouptype==2:
                self.DataItems[i].ReachNoVals=self.res.StaticItems[nodestart].read_data()
                self.DataItems[i].chainages=self.res.StaticItems[nodestart+1].read_data()
                nodestart+=2

        #Read nodes
        while self.res.StaticItems[nodestart].name!='NoNodes':
            nodestart+=1

        numberofnodes = self.res.StaticItems[nodestart].read_data()[0]
        xs =self.res.StaticItems[nodestart+3].read_data()
        ys =self.res.StaticItems[nodestart+4].read_data()
        types =self.res.StaticItems[nodestart+1].read_data()
        names = self.res.StaticItems[nodestart+2].read_data().split(';')
        for i in range(0,numberofnodes):
            self.nodes.append(Node(xs[i],ys[i],types[i], names[i]))

        #Read reaches
        reachstart= nodestart + 5
        numberofreaches = self.res.StaticItems[reachstart].read_data()[0]
        reachtypes = self.res.StaticItems[reachstart+1].read_data();
        allnames= self.res.StaticItems[reachstart+2].read_data()
        reachnames = allnames.split(';')
        topoids = self.res.StaticItems[reachstart+3].read_data().split(';')
        ups = self.res.StaticItems[reachstart+4].read_data()
        dws = self.res.StaticItems[reachstart+5].read_data()
        dir = self.res.StaticItems[reachstart+6].read_data()
        nodigipoints = self.res.StaticItems[reachstart+7].read_data()
        nogridpoints = self.res.StaticItems[reachstart+8].read_data()
        for i in range(0,numberofreaches):
            r = Reach(reachtypes[i], reachnames[i].replace("\"", ""), topoids[i].replace("\"", ""), dir[i])
            r.upstream_node = self.nodes[ups[i]]
            r.downstream_node = self.nodes[dws[i]]
            r.number_of_digi_points=nodigipoints[i]
            r.number_of_grid_points=nogridpoints[i]
            self.reaches.append(r)

        for di in self.DataItems:
            if di.grouptype==2:
                if not hasattr(di, 'ReachIndeces'):
                    di.ReachIndeces=range(0,numberofreaches)
                lcount=0
                for i in di.ReachIndeces:
                    ldi =DataItem(di.name)
                    ldi.ItemIndex =di.ItemIndex
                    ldi.offset =di.offset
                    ldi.chainages = di.chainages[di.offset:di.offset+di.ReachNoVals[lcount]]
                    di.offset +=di.ReachNoVals[lcount]
                    lcount+=1
                    self.reaches[i].dataitems[di.ItemIndex]=ldi


        #Now build each individual reach
        Hindex=0
        Qindex=0
        rcount=0
        offset = reachstart + 9
        for r in self.reaches:
            if self.res.StaticItems[offset].name!='dpChainages':
                k=1

            #The digipoints
            dpChainages = self.res.StaticItems[offset].read_data()
            dpXs = self.res.StaticItems[offset+1].read_data()
            dpYs = self.res.StaticItems[offset+2].read_data()
            for i in range(0, r.number_of_digi_points):
                dp = RiverPoint(dpXs[i],dpYs[i], dpChainages[i])
                r.digi_points.append(dp)

            #The gridpoints
            gpType = self.res.StaticItems[offset+3].read_data()
            gpChainages = self.res.StaticItems[offset+4].read_data()
            gpXs = self.res.StaticItems[offset+5].read_data()
            gpYs = self.res.StaticItems[offset+6].read_data()
            gpZs = self.res.StaticItems[offset+7].read_data()
            for i in range(0, r.number_of_grid_points):
                dg = GridPoint(gpXs[i],gpYs[i], gpChainages[i], gpZs[i], gpType[i])
                r.grid_points.append(dg)
                if dg.type==1025:
                    r.grid_points_h.append(dg)
                    dg.index = Hindex
                    dg.itemindex=1
                    dg.point_type='H'
                    Hindex+=1
                    r.grid_points_q.append(dg)
                    dg.index=Qindex
                    dg.itemindex=2
                    dg.point_type='Q'
                    Qindex+=1
                else:
                    r.grid_points_q.append(dg)
                    dg.index=Qindex
                    dg.itemindex=2
                    dg.point_type='Q'
                    Qindex+=1
                   
            #Some structures
            if self.res.StaticItems[offset+8].name=='structureNumberOfSubTypes':
                offset +=3
            
            #We may already be at the next reach
            if self.res.StaticItems[offset+10].name=='dpChainages':
                offset+=10
            elif self.res.StaticItems[offset+8].name=='dpChainages':
                offset+=8
            else: #Now for xsecs
                csIDs = self.res.StaticItems[offset+8].read_data().split(';')
                csnopoints= self.res.StaticItems[offset+10].read_data()

                cstypes= self.res.StaticItems[offset+9].read_data()
                csXs = self.res.StaticItems[offset+11].read_data()
                csZs = self.res.StaticItems[offset+12].read_data()
                csNoMarkers = self.res.StaticItems[offset+13].read_data()
                csMarkers = self.res.StaticItems[offset+14].read_data()
                csMarkersIndices = self.res.StaticItems[offset+15].read_data()
                csstart=0
                csmarkstart =0
                gpoffset=0
                for i in range(0, len(csnopoints)):
                    if cstypes[i+gpoffset] == 1000:
                        gpoffset+=1
                    cs = xsec(csIDs[i+gpoffset].replace("\"", ""), csnopoints[i])
                    cs.type = cstypes[i]
                    for n in range(csstart, csstart+ cs.number_of_points):
                        cs.xsec_points.append(xsecpoint(csXs[n],csZs[n]))
                    r.xsecs.append(cs);
                    csstart+=cs.number_of_points
                    for k in range(csmarkstart, csmarkstart + csNoMarkers[i]):
                        cs.xsec_points[csMarkersIndices[k]].marker=csMarkers[k]
                    csmarkstart += csNoMarkers[i]
                    cs.Gridpoint = r.grid_points_h[i+gpoffset]

                offset+=16

    def read_res11(self, Filename):
        """
        Reads a res11 file and builds the network
        """
        self.res= DFS.RES.from_file(Filename)
        nodestart=0

        NumberOfstaticItemsPrBranch = self.res.StaticItems[0].read_data()[0]
        NumberOfBranches = self.res.StaticItems[1].read_data()[0]
        self.DataItems =[]

        nitems = len(self.res.items);

        nodestart =4
        while len(self.reaches)<NumberOfBranches:
            name = self.res.StaticItems[nodestart].read_data();
            topoid = self.res.StaticItems[nodestart+1].read_data();
            r = Reach(1, name, topoid, 1)
            self.reaches.append(r)
            gpChainages =self.res.StaticItems[nodestart+2].read_data()
            r.number_of_grid_points = len(gpChainages)
            gpXs =self.res.StaticItems[nodestart+3].read_data()
            gpYs =self.res.StaticItems[nodestart+4].read_data()
            gpZs =self.res.StaticItems[nodestart+5].read_data()
            gpRightBanks =self.res.StaticItems[nodestart+6].read_data()
            gpLeftBanks =self.res.StaticItems[nodestart+7].read_data()
            gptypes = self.res.StaticItems[nodestart+8].read_data()

            dpChainages =self.res.StaticItems[nodestart+9].read_data()
            r.number_of_digi_points = len(dpChainages)
            dpXs =self.res.StaticItems[nodestart+10].read_data()
            dpYs =self.res.StaticItems[nodestart+11].read_data()


            gpNumberOfRawdata = self.res.StaticItems[nodestart+13].read_data()
            connections = self.res.StaticItems[nodestart+12].read_data()
            # crosssections
            nodestart+=14
            while self.res.StaticItems[nodestart].name =='Cross section ID':
                crosssectionid = self.res.StaticItems[nodestart].read_data()
                rawXs = self.res.StaticItems[nodestart+1].read_data()
                rawZs = self.res.StaticItems[nodestart+2].read_data()
                nodestart+=4
            nodestart+=9

            #now build the reach
            Hindex=0
            Qindex=0
            for i in range(0, r.number_of_grid_points):
                dg = GridPoint(gpXs[i],gpYs[i], gpChainages[i], gpZs[i], gptypes[i])
                r.grid_points.append(dg)
                if dg.type==2:
                    r.grid_points_q.append(dg)
                    dg.index=Qindex
                    dg.itemindex = len(self.reaches) + int(nitems/2)
                    dg.point_type='Q'
                    Qindex+=1
                else:
                    r.grid_points_h.append(dg)
                    dg.index = Hindex
                    dg.itemindex = len(self.reaches)
                    dg.point_type='H'
                    Hindex+=1

            for i in range(0, r.number_of_digi_points):
                dp = RiverPoint(dpXs[i],dpYs[i], dpChainages[i])
                r.digi_points.append(dp)

    def get_timeseries(self, grid_point):
        return self.res.get_timeseries(grid_point.itemindex, grid_point.index)

    def to_csv(self, filename, ItemNumber, TimeStep=1):
        """
        Writes a csv file with reach name, chainage and Item value. Items counts from 1, TimeStep from 0
        """
        with codecs.open(filename, encoding='utf-8', mode='w') as file:
            datadic=self.getvalues(ItemNumber, TimeStep)
            for name, chainlist in datadic.items():
                for cv in chainlist:
                    file.write(name + '\t' + str(cv[0]) + '\t' + str(cv[1]) + '\n')

    def to_shape(self, shape_file_name):
        import shapefile
        with shapefile.Writer(shape_file_name, shapeType=shapefile.POINT) as w:
                w.field('Branch', 'C')
                w.field('TopoID', 'C')
                w.field('Chainage', 'F', decimal=4)
                w.field('X', 'F', decimal=10)
                w.field('Y', 'F', decimal=10)
                w.field('PointType', 'C')
                for r in self.reaches:
                    for p in r.grid_points:
                        w.record(r.name, r.topo_id, p.chainage,  p.x, p.y, p.point_type)
                        w.point(p.x, p.y)




