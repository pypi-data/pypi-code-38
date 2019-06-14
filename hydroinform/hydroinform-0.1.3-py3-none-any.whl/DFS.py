# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 22:50:46 2015

@author: Jacob
"""


from ctypes import byref, WinDLL, c_int, c_float, c_double, c_char_p, c_byte, cast, c_long, c_wchar_p, POINTER,c_uint,c_longlong, c_short
from datetime import date, datetime, timedelta, time
from enum import Enum
import os
from pathlib import Path
import numpy as np
import pandas as pd
import math

hllDll=None
MikeZeroBinDIR=r'D:\Programs\DHI\2019\bin\x64'

class DFSDLLWrapper(object):

#Open/close
    @staticmethod
    def dfsFileClose(HeaderPointer, FilePointer):
      return hllDll['dfsFileClose'](HeaderPointer, byref(FilePointer))
    @staticmethod
    def dfsFileEdit(FileName, HeaderPointer, FilePointer):
        file = os.path.abspath(FileName).encode(encoding='UTF-8')
        return hllDll['dfsFileEdit'](file, byref(HeaderPointer), byref(FilePointer))
    @staticmethod
    def dfsFileRead(FileName, HeaderPointer, FilePointer):
        file = os.path.abspath(FileName).encode(encoding='UTF-8')
        return hllDll['dfsFileRead'](file, byref(HeaderPointer), byref(FilePointer))
    @staticmethod
    def dfsFileCreate(FileName, HeaderPointer, FilePointer):
        file = os.path.abspath(FileName).encode(encoding='UTF-8')
        return hllDll['dfsFileCreate'](file, HeaderPointer, byref(FilePointer))
    @staticmethod
    def dfsHeaderCreate(FileType, NumberOfItems, StatType, HeaderPointer):
        title="Title"#.encode(encoding='UTF-8')
        desc="HydroNumerics"#.encode(encoding='UTF-8')
        hllDll.dfsHeaderCreate.argtypes=[c_int,c_wchar_p,c_wchar_p,c_int,c_int,c_int, POINTER(c_longlong)]
        hllDll.dfsHeaderCreate.restype =c_int
 
        
        return  hllDll.dfsHeaderCreate(FileType.value, title, desc, c_int(1), c_int(NumberOfItems),StatType.value, byref(HeaderPointer))
      
#Read/Write/Spool
    @staticmethod
    def dfsReadItemTimeStep(HeaderPointer, FilePointer, Time, Data):
        return hllDll['dfsReadItemTimeStep'](HeaderPointer, FilePointer, byref(Time), Data)
    @staticmethod
    def dfsStaticRead(HeaderPointer, fioError):
        hllDll.dfsStaticRead.argtypes=[c_longlong, POINTER(c_int)]
        hllDll.dfsStaticRead.restype = c_longlong
        return hllDll.dfsStaticRead(HeaderPointer, byref(fioError))
    @staticmethod
    def dfsWriteItemTimeStep(HeaderPointer, FilePointer, Time, Data):
        return hllDll['dfsWriteItemTimeStep'](HeaderPointer, FilePointer, c_double(Time), Data)
    @staticmethod
    def dfsFindItemDynamic(HeaderPointer, FilePointer, TimeStep, ItemNumber):
        return hllDll['dfsFindItemDynamic'](HeaderPointer, FilePointer, TimeStep, ItemNumber)
    @staticmethod
    def dfsFindItemStatic(HeaderPointer, FilePointer, ItemNumber):
        return hllDll['dfsFindItemStatic'](HeaderPointer, FilePointer, ItemNumber)
    @staticmethod
    def dfsStaticGetData(ItemPointer, StaticData):
        return hllDll['dfsStaticGetData'](ItemPointer, StaticData)

    
    @staticmethod
    def dfsSkipItem(HeaderPointer, FilePointer):
        return hllDll['dfsSkipItem'](HeaderPointer, FilePointer)

#ItemInfo
    @staticmethod
    def dfsGetNoOfItems(HeaderPointer):
      return hllDll['dfsGetNoOfItems'](HeaderPointer)
    @staticmethod
    def dfsGetItemElements(ItemPointer):
        hllDll.dfsGetItemElements.argtypes=[c_longlong]
        hllDll.dfsGetItemElements.restype = c_uint
        return hllDll.dfsGetItemElements(ItemPointer)
    @staticmethod
    def dfsGetItemInfo(ItemPointer, ItemType, Name, Eum, Data_Type):
        hllDll.dfsGetItemInfo.argtypes =[c_longlong, POINTER(c_int), c_char_p, POINTER(c_char_p), POINTER(c_char_p),c_char_p(), POINTER(c_int)]
        return hllDll['dfsGetItemInfo'](ItemPointer, byref(ItemType), c_char_p(), byref(Name), byref(Eum), c_char_p(), byref(Data_Type))
    @staticmethod
    def dfsSetItemInfo(HeaderPointer, ItemPointer, ItemType, Name, Eum, Data_Type):
#        hllDll.dfsSetItemInfo.argtypes =[c_longlong, c_longlong, c_int, c_wchar_p, c_int, c_int]
        utfname =Name.encode(encoding='UTF-8')
        return hllDll.dfsSetItemInfo(HeaderPointer, ItemPointer, ItemType.value, utfname, Eum.value, Data_Type.value)
    @staticmethod
    def dfsItemD(HeaderPointer, ItemNumber): #Returns a pointer to the item
        hllDll.dfsItemD.argtypes = [c_longlong, c_int]
        hllDll.dfsItemD.restype = c_longlong
        v= hllDll.dfsItemD(HeaderPointer, c_int(ItemNumber))
        return c_longlong(v)
    @staticmethod
    def dfsGetItemValueType(ItemPointer, ValueType):
        return hllDll['dfsGetItemValueType'](ItemPointer, byref(ValueType))
    @staticmethod
    def dfsSetItemValueType(ItemPointer, ValueType):
        return hllDll['dfsSetItemValueType'](ItemPointer, ValueType.value)
        
    
#TimeAxis
    @staticmethod
    def dfsGetTimeAxisType(HeaderPointer):
      return hllDll['dfsGetTimeAxisType'](HeaderPointer)
      
    @staticmethod
    def dfsGetEqTimeAxis(HeaderPointer, TimeStepUnit, EumUnit, TStart, TStep, NumberOfTimeSteps,TIndex): 
        return hllDll['dfsGetEqTimeAxis'](HeaderPointer, byref(TimeStepUnit), byref(EumUnit), byref(TStart), byref(TStep), byref(NumberOfTimeSteps), byref(TIndex))

    @staticmethod
    def dfsGetEqCalendarAxis(HeaderPointer, DateStart, TimeStart, TimeStepUnit, EumUnit, TStart, TStep, NumberOfTimeSteps,TIndex): 
        return hllDll.dfsGetEqCalendarAxis(HeaderPointer, byref(DateStart), byref(TimeStart), byref(TimeStepUnit), byref(EumUnit), byref(TStart), byref(TStep), byref(NumberOfTimeSteps), byref(TIndex))

    @staticmethod
    def dfsSetEqCalendarAxis(HeaderPointer, StartTime, TimeStepUnit, TStep): 
        start_date = StartTime.strftime('%Y-%m-%d')
        start_time= StartTime.strftime('%H:%M:%S')
        tstep=0        
        if TimeStepUnit is TimeInterval.Second:
            tstep = TStep.seconds
        elif TimeStepUnit  is TimeInterval.Minute:
            tstep = TStep.minutes
        return hllDll.dfsSetEqCalendarAxis(HeaderPointer, start_date.encode(encoding='UTF-8'), start_time.encode(encoding='UTF-8'), TimeStepUnit.value,0, c_double (tstep),0)
    
    @staticmethod
    def dfsGetNeqCalendarAxis(HeaderPointer, DateStart, TimeStart, TimeStepUnit, EumUnit, TStart, TStep, NumberOfTimeSteps,TIndex): 
        return hllDll.dfsGetNeqCalendarAxis(HeaderPointer, byref(DateStart), byref(TimeStart), byref(TimeStepUnit), byref(EumUnit), byref(TStart), byref(TStep), byref(NumberOfTimeSteps), byref(TIndex))    
   
    @staticmethod
    def dfsSetNeqCalendarAxis(HeaderPointer, StartTime, TimeStepUnit): 
        start_date = StartTime.strftime('%Y-%m-%d')
        start_time= StartTime.strftime('%H:%M:%S')
        return hllDll.dfsSetNeqCalendarAxis(HeaderPointer, start_date.encode(encoding='UTF-8'), start_time.encode(encoding='UTF-8'), c_int(TimeStepUnit.value), c_double(0), c_int(0))


#SpaceAxis
    @staticmethod
    def dfsGetItemAxisType(ItemPointer):
        return hllDll['dfsGetItemAxisType'](ItemPointer)
        
    @staticmethod
    def dfsSetItemAxisEqD0(ItemPointer):
        return hllDll['dfsSetItemAxisEqD0'](ItemPointer, 1000)

    @staticmethod
    def dfsGetItemAxisEqD2(ItemPointer, ItemType, EumUnit, NumberOfColumns, NumberOfRows, X, Y, dx,dy):
        return hllDll['dfsGetItemAxisEqD2'](ItemPointer, ItemType, EumUnit, byref(NumberOfColumns), byref(NumberOfRows), byref(X), byref(Y), byref(dx),byref(dy))

    @staticmethod
    def dfsSetItemAxisEqD2(ItemPointer, NumberOfColumns, NumberOfRows, X, Y, dx,dy):
        return hllDll['dfsSetItemAxisEqD2'](ItemPointer, 1000, NumberOfColumns, NumberOfRows, X, Y, c_float(dx), c_float(dy))

    @staticmethod
    def dfsGetItemAxisEqD3(ItemPointer, ItemType, EumUnit, NumberOfColumns, NumberOfRows, NumberOfLayers, X, Y, Z, dx,dy, dz):
        return hllDll['dfsGetItemAxisEqD3'](ItemPointer, ItemType, EumUnit, byref(NumberOfColumns), byref(NumberOfRows), byref(NumberOfLayers), byref(X), byref(Y), byref(Z), byref(dx),byref(dy), byref(dz))

    @staticmethod
    def dfsSetItemAxisEqD3(ItemPointer, NumberOfColumns, NumberOfRows, NumberOfLayers, X, Y, dx, dy):
        return hllDll['dfsSetItemAxisEqD3'](ItemPointer, 1000, NumberOfColumns, NumberOfRows, NumberOfLayers, X, Y, 0, c_float(dx), c_float(dy), c_float(dy))
       


#GeoInfo
    @staticmethod
    def dfsGetGeoInfoUTMProj(HeaderPointer, Name, XOrigin, YOrigin, Orientation): 
        return hllDll['dfsGetGeoInfoUTMProj'](HeaderPointer, byref(Name), byref(XOrigin), byref(YOrigin), byref(Orientation))
    @staticmethod
    def dfsSetGeoInfoUTMProj(HeaderPointer, projection, XOrigin, YOrigin, Orientation):
      return hllDll['dfsSetGeoInfoUTMProj'](HeaderPointer, projection.encode(encoding='UTF-8'), c_double(XOrigin), c_double(YOrigin), c_double(Orientation))
      
      
      #EncodeKeys
    @staticmethod
    def dfsIsFileCompressed(HeaderPointer): 
        return hllDll['dfsIsFileCompressed'](HeaderPointer)

    @staticmethod
    def dfsGetEncodeKeySize(HeaderPointer): 
        return hllDll['dfsGetEncodeKeySize'](HeaderPointer)

    @staticmethod
    def dfsGetEncodeKey(HeaderPointer, xKey, yKey, zKey):
      return hllDll['dfsGetEncodeKey'](HeaderPointer, xKey, yKey, zKey)

    @staticmethod
    def dfsSetEncodeKey(HeaderPointer, xKey, yKey, zKey, en):
        return hllDll['dfsSetEncodeKey'](HeaderPointer, xKey, yKey, zKey, c_int(en))

        
class DFSItem(object):
    def __init__(self, ItemPointer, ItemNumber):
        self.item_pointer = ItemPointer
        self.eum_unit = c_int()
        self.eum_item = c_int()
        self.data_type = c_int(1)
        self.value_type = c_int()
        self.name=c_char_p()

    def __str__(self):
        return self.name
        
    def read_item(self):
        self.number_of_elements = DFSDLLWrapper().dfsGetItemElements((self.item_pointer))
        self.ok=DFSDLLWrapper().dfsGetItemInfo((self.item_pointer), self.eum_item, self.name, self.eum_unit, self.data_type)
        self.data_type = DfsSimpleType(self.data_type.value)
        self.eum_item = EumItem(self.eum_item.value)
        self.ok=DFSDLLWrapper().dfsGetItemValueType((self.item_pointer), self.value_type)
        self.value_type =DataValueType(self.value_type.value)
        self.name = self.name.value.decode('UTF-8', 'ignore')
        self.eum_unit = EumUnit(self.eum_unit.value)


    def read_data(self):
        if self.data_type== DfsSimpleType.Int or self.data_type== DfsSimpleType.UInt:
            _staticDataType = c_int*self.number_of_elements
        elif self.data_type== DfsSimpleType.Float:
            _staticDataType = c_float*self.number_of_elements
        elif self.data_type== DfsSimpleType.Double:
            _staticDataType = c_double*self.number_of_elements
        elif self.data_type== DfsSimpleType.Byte:
            _staticDataType = c_byte*self.number_of_elements
            _staticData= _staticDataType()
            DFSDLLWrapper().dfsStaticGetData(self.item_pointer, _staticData)
            return bytearray(_staticData).decode('UTF-8', 'ignore')
            return bytearray(_staticData).decode(encoding='ISO-8859-1').encode('UTF-8')

        _staticData= _staticDataType()
        DFSDLLWrapper().dfsStaticGetData(self.item_pointer, _staticData)
        return np.array(_staticData)
        
 
class DFSBase(object):     
    def __init__(self, file_name):
        global hllDll
        if hllDll is None:
            mz=MikeZeroBinDIR
            import clr
            try:
                clr.AddReference(r'C:\Windows\Microsoft.NET\assembly\GAC_MSIL\DHI.DHIfl\v4.0_16.0.0.0__c513450b5d0bf0bf\DHI.DHIfl.dll')
                from DHI.DHIfl import DHIRegistry, DHIProductAreas
                key = DHIRegistry(DHIProductAreas.COMMON_COMPONNETS, False)
                mzbin=''
                exist, mz = key.GetHomeDirectory(mzbin)
                if not exist:
                    raise Exception("Could not find MikeZero-installation")
            except:
                try:
                    clr.AddReference(r'C:\Windows\Microsoft.NET\assembly\GAC_MSIL\DHI.Mike.Install\v4.0_1.0.0.0__c513450b5d0bf0bf\DHI.Mike.Install.dll')
                    from DHI.Mike.Install import MikeImport
                    p = MikeImport.InstalledProducts()
                    mz = os.path.join(p[0].InstallRoot,'bin','x64');
                except:
                    pass

            # os.chdir(r'D:\Programs\DHI\2016\bin\x64')
            if not os.path.exists(os.path.join(mz,"ufs.dll")):
                raise Exception("Could not find MikeZero-installation at: " + mz + "\nSet the attribute DFS.MikeZeroBinDIR to the correct path to the MikeZero bin directory containing the file ufs.dll" )

            CurrentDirectory = os.getcwd()
            os.chdir(mz)    
            hllDll = WinDLL("ufs.dll")
            os.chdir(CurrentDirectory) #Reset to current directory


        self._currentTimeStep = 0
        self._currentItem= 1
        self._numberOfTimeStepsWritten=0
        self._header_pointer = c_longlong()
        self._file_pointer = c_longlong()
        self._initialized_for_writing=False
        self.file_name = os.path.abspath(file_name)
        self.items=[]
        #Intialize reference variables
        self.number_of_columns =c_int(1) # Lowest value is one
        self.number_of_rows =c_int(1)
        self.number_of_layers =c_int(1)
        self.x_origin = 0
        self.y_origin = 0
        self.dx = c_float(0)
        self.dy = c_float(0)
        self.dz =c_float(0)
        self.orientation = 0
        self.space_axis = SpaceAxisType.undefined
        self.time_axis = TimeAxisType.Undefined
        #Intialize reference variables
        self.time_step_size=timedelta()        
        self.time_step_unit = c_int(0)
        self.number_of_time_steps = c_int()
        self.start_time = datetime(2002,1,1)
        self.time_steps=[]
        self.delete_value=-1e-035
        self.projection_WKT = 'NON-UTM'
        self._needs_saving=False
    
    @classmethod
    def open_file(cls, file_name):
        if not os.path.isfile(file_name):
            raise FileNotFoundError(file_name)
        ext=Path(file_name).suffix.lower()

        if(ext == '.dfs0'):
            cls = DFS0(file_name)
        elif(ext == '.dfs2'):
            cls =DFS2(file_name)
        elif(ext == '.dfs3'):
            cls =DFS3(file_name)
        elif(ext == '.res1d'):
            cls = RES(file_name)
        elif(ext == '.res11'):
            cls =RES(file_name)
        cls.__open_for_reading()
        return cls


    def __open_for_reading(self):
        #Open the file for reading
        self.error=DFSDLLWrapper().dfsFileRead(self.file_name, self._header_pointer, self._file_pointer)
        
        #read the items
        self.number_of_items =DFSDLLWrapper().dfsGetNoOfItems(self._header_pointer)
        for i in range(self.number_of_items):
            self.items.append(DFSItem(DFSDLLWrapper().dfsItemD(self._header_pointer, i + 1),i+1))
            self.items[i].read_item()
        
        #Read the projection
        xor = c_double(0)
        yor = c_double(0)
        orient = c_double(0)
        proj = c_char_p() #added by rs
        self.ok=DFSDLLWrapper().dfsGetGeoInfoUTMProj(self._header_pointer, proj, xor, yor, orient)
        if self.ok==0: #Not all dfs files have projections
            self.x_origin = xor.value
            self.y_origin = yor.value
            self.orientation = orient.value
            self.projection_WKT = proj.value.decode('UTF-8', 'ignore') #added by rs

        #Now Read the space axis
        self.space_axis = SpaceAxisType(DFSDLLWrapper().dfsGetItemAxisType(self.items[0].item_pointer))
        if self.space_axis is SpaceAxisType.EqD2: #DFS2
            DFSDLLWrapper().dfsGetItemAxisEqD2(self.items[0].item_pointer, c_int(), c_int(), self.number_of_columns, self.number_of_rows, c_float(), c_float(), self.dx, self.dy)
        if self.space_axis is SpaceAxisType.EqD3: #DFS3
            DFSDLLWrapper().dfsGetItemAxisEqD3(self.items[0].item_pointer, c_int(), c_int(), self.number_of_columns, self.number_of_rows, self.number_of_layers, c_float(), c_float(), c_float(), self.dx, self.dy,self.dz)

        #Convert from c-types
        self.number_of_columns = self.number_of_columns.value
        self.number_of_rows = self.number_of_rows.value
        self.number_of_layers = self.number_of_layers.value
        self.dx = self.dx.value
        self.dy = self.dy.value
        self.dz = self.dz.value
                
        #Read the time axis
        self.time_axis= TimeAxisType(DFSDLLWrapper().dfsGetTimeAxisType(self._header_pointer))
        
        if self.time_axis is TimeAxisType.TimeEquidistant: #Some .dfs2 goes here
            DFSDLLWrapper().dfsGetEqTimeAxis(self._header_pointer, self.time_step_unit, c_char_p(), c_float(), c_float(), self.number_of_time_steps, c_int())
        else:
            starttime = c_char_p()
            startdate = c_char_p()
            tstep = c_double()
            if self.time_axis is TimeAxisType.CalendarEquidistant: #Most dfs2 and dfs3 goes here
                DFSDLLWrapper().dfsGetEqCalendarAxis(self._header_pointer, startdate, starttime, self.time_step_unit, c_char_p(), c_float(), tstep, self.number_of_time_steps, c_int())
                self.time_step_unit = TimeInterval(self.time_step_unit.value)
                tstep = tstep.value
                if self.time_step_unit is TimeInterval.Second:
                    self.time_step_size = timedelta(seconds = tstep)
                elif self.time_step_unit is TimeInterval.Minute:
                    self.time_step_size = timedelta(minutes =tstep)
                elif self.time_step_unit is TimeInterval.Hour:
                    self.time_step_size = timedelta(hours=tstep)

            elif self.time_axis is TimeAxisType.CalendarNonEquidistant: #Dfs0 can have varying timestep
                DFSDLLWrapper().dfsGetNeqCalendarAxis(self._header_pointer, startdate, starttime, self.time_step_unit, c_char_p(), c_float(), tstep, self.number_of_time_steps, c_int())
                
            self.start_time = datetime.strptime(startdate.value.decode(encoding='UTF-8')+starttime.value.decode(encoding='UTF-8'), "%Y-%m-%d%H:%M:%S")
            self.time_step_unit = TimeInterval(self.time_step_unit.value)

        self.number_of_time_steps = self.number_of_time_steps.value
        self.time_steps=[]
        
        for i in range(self.number_of_time_steps):
            self.time_steps.append(self.get_time_of_timestep(i))

    def new_file(self, FileName, NumberOfItems):
        self._initialized_for_writing=True
        self.number_of_items = NumberOfItems
        self.number_of_time_steps=0
        self.time_step_unit = TimeInterval.Second
        for i in range(self.number_of_items):
            self.items.append(DFSItem(DFSDLLWrapper().dfsItemD(self._header_pointer, i + 1),i+1))
        self._needs_saving=True


    def get_asc_header(self):
        """
        Gets a header that can be used to write an ascii grid file. Only use with dfs2 and dfs3.
        """
        return 'ncols '+str(self.number_of_columns)+'\nnrows '+str(self.number_of_rows)+'\nxllcorner '+str(self.x_origin)+'\nyllcorner '+str(self.y_origin)+'\ncellsize '+str(self.dx)+'\nnodata_value ' + str(self.delete_value)


    def _copy_item_info(self, TemplateDFS):
        for i in range(self.number_of_items):
            self.items[i].name = TemplateDFS.items[i].name
            self.items[i].eum_item = TemplateDFS.items[i].eum_item
            self.items[i].eum_unit = TemplateDFS.items[i].eum_unit
            self.items[i].value_type = TemplateDFS.items[i].value_type
            self.items[i].data_type = TemplateDFS.items[i].data_type


    def copy_from_template(self, dfs):
      self.time_axis = dfs.time_axis
      if dfs.time_axis is TimeAxisType.CalendarEquidistant or dfs.time_axis is TimeAxisType.TimeEquidistant:
        self.start_time = dfs.start_time
        self.time_step_size = dfs.time_step_size
        self.time_step_unit = dfs.time_step_unit
      self.delete_value = dfs.delete_value;
      self.time_steps.append(self.start_time)

      if DFSDLLWrapper().dfsIsFileCompressed(dfs._header_pointer):
        en = DFSDLLWrapper().dfsGetEncodeKeySize(dfs._header_pointer)
        EncodeKeyArrayType=c_int*en

        xkey = EncodeKeyArrayType()
        ykey = EncodeKeyArrayType()
        zkey = EncodeKeyArrayType()

        DFSDLLWrapper().dfsGetEncodeKey(dfs._header_pointer, xkey, ykey, zkey);
        #Adjust z-count if we go from dfs3 to dfs2
        if self.number_of_layers == 1 and dfs.number_of_layers > 1:
            en = en / dfs.number_of_layers
            xkey = xkey[:en]
            ykey = ykey[:en]
            zkey = zkey[:en]
            for i in range(en):
                zkey[i] = 0;

        DFSDLLWrapper().dfsSetEncodeKey(self._header_pointer, xkey, ykey, zkey, en);

    #Gets the time of a particular timestep
    def get_time_of_timestep(self, TimeStep):
        if TimeStep<len(self.time_steps): #TimeStep have been read or created
            return self.time_steps[TimeStep]
        else:
            if self.time_axis is TimeAxisType.CalendarNonEquidistant:
                self.read_item_time_step(TimeStep,1)
                return self._currentTime
            else:
                return self.start_time + self.time_step_size*TimeStep 
    
    # Returns the zero-based index of the TimeStep closest to the TimeStamp. If the timestamp falls exactly between two timestep the smallest is returned.
    # If the TimeStamp is before the first timestep 0 is returned.
    # If the TimeStamp is after the last timestep the index of the last timestep is returned
    def get_time_step(self, TimeStamp):
        if TimeStamp < self.start_time or self.number_of_time_steps == 1:
            return 0
        #fixed timestep
        TimeStep=0
        if self.time_axis is TimeAxisType.CalendarEquidistant:
            TimeStep = round((TimeStamp-self.start_time).total_seconds() / self.time_step_size.total_seconds(), 0)
        #Variable timestep
        else:
        #Last timestep is known
            if TimeStamp >= self.time_steps[self.number_of_time_steps - 1]:
                return self.number_of_time_steps - 1

            i = 1
            #Loop the timesteps
            while TimeStamp > self.time_steps[i]:
                i=i+1
            #Check if last one was actually closer
            if self.time_steps[i] -TimeStamp < TimeStamp -self.time_steps[i - 1]:
                return i
            else:
                return i - 1
        return int(min(self.number_of_time_steps-1, TimeStep))
    

    #Reads an item and a timestep and returns data in multidimensional list
    def read_item_time_step(self, TimeStep, Item):
        if TimeStep != self._currentTimeStep or Item != self._currentItem:
            self.__move_to_item_timestep(TimeStep, Item)

        #Prepare the array to read data
        if self.space_axis is SpaceAxisType.EqD2:
            dataArrayType=c_float*self.number_of_columns *self.number_of_rows
        elif self.space_axis is SpaceAxisType.EqD3:
            dataArrayType=c_float*self.number_of_columns *self.number_of_rows*self.number_of_layers
        else:
            dataArrayType=c_float*self.items[Item-1].number_of_elements


        dfsdata =dataArrayType()
        time = c_double(0)

        self.error = DFSDLLWrapper().dfsReadItemTimeStep(self._header_pointer, self._file_pointer, time, dfsdata)
        if self.time_step_unit is TimeInterval.Second:
            self._currentTime = self.start_time + timedelta(seconds = time.value)
        elif self.time_step_unit is TimeInterval.Minute:
            self._currentTime = self.start_time + timedelta(minutes = time.value)
        elif self.time_step_unit is TimeInterval.Hour:
            self._currentTime = self.start_time + timedelta(hours = time.value)
 
            #self.IncrementItemTimeStep()
        return dfsdata
    
    #Moves to the item and timestep, so it can be read or written       
    #Note that it is not possible to move backwards into something that has been written
    def __move_to_item_timestep(self, TimeStep, Item):
        TimeStep = min(TimeStep, self.number_of_time_steps)
        Item=min(Item, self.number_of_items)
        if TimeStep != self._currentTimeStep or Item != self._currentItem:
            self._currentTimeStep = TimeStep
            self._currentItem = Item
            if TimeStep == self.number_of_time_steps:
                #Spools to last item
                self.ok=DFSDLLWrapper().dfsFindItemDynamic(self._header_pointer, self._file_pointer, c_int(TimeStep - 1), c_int(self.number_of_items))  
                #Skip Item to get to end                
                self.ok=DFSDLLWrapper().dfsSkipItem(self._header_pointer, self._file_pointer) 
                self._currentItem = 1
            else:
                #Spools to the correct Item and TimeStep
                DFSDLLWrapper().dfsFindItemDynamic(self._header_pointer, self._file_pointer, c_int(TimeStep), c_int(Item))

    #Closes the file and opens it again as writeable
    def __initialize_for_writing(self):
        self.dispose()
        DFSDLLWrapper().dfsFileEdit(self.file_name, self._header_pointer, self._file_pointer);
        self._initialized_for_writing = True;

        for i in range(self.number_of_items):
            ip = DFSDLLWrapper().dfsItemD(self._header_pointer, i + 1)
            self.items[i].item_pointer = ip;
      
    
    def __create_file(self):
        self.save_changes()
        self.error=DFSDLLWrapper().dfsFileCreate(self.file_name, self._header_pointer, self._file_pointer)
    
    
    def __increment_item_time_step(self):
        self._currentItem=self._currentItem+1
        if  self._currentItem > self.number_of_items:
            self._currentItem = 1
            self._currentTimeStep=self._currentTimeStep+1

    def append_time_step(self, Time):
        if self.time_axis is TimeAxisType.CalendarNonEquidistant:
            if self.number_of_time_steps==0:
                self.start_time = Time
            self.time_steps.append(Time)
            self.number_of_time_steps+=1;

    def __end_of_file(self):
        return self._currentTimeStep == self.number_of_time_steps
    

    def write_item_timestep(self, TimeStep, Item, data):
      if not self._initialized_for_writing:
        self.__initialize_for_writing()

      if self._file_pointer.value == 0:
        self.__create_file()

      self.__move_to_item_timestep(TimeStep, Item)

        # Get the time of the timestep in double
      time = 0
      if self.time_axis is TimeAxisType.CalendarNonEquidistant and self._currentTimeStep > 0 :
        ts = self.time_steps[TimeStep] - self.start_time
        if self.time_step_unit is TimeInterval.Second:
            time = ts.total_seconds()
        elif self.time_step_unit is TimeInterval.Minute:
            time = ts.total_minutes()
        elif self.time_step_unit is TimeInterval.Hour:
            time = ts.total_hours()

      
      #Do we need to also add a new timestep
      if self.__end_of_file():
        if self._currentItem == self.number_of_items:
          self.number_of_time_steps=self.number_of_time_steps+1
#        self.AppendTimeStep(self.TimeSteps[self.NumberOfTimeSteps-1] + self.TimeStepSize)
      
      #Writes the data
      self.error = DFSDLLWrapper().dfsWriteItemTimeStep(self._header_pointer, self._file_pointer, time, data);
      
      #Increment current timestep/item
      self.__increment_item_time_step()
      self._needs_saving=True


    def get_column_index(self, UTMX):
        """
        Gets the Column index for this coordinate. Lower left is (0,0). 
        Returns -1 if UTMY is left of the grid and -2 if it is right.
        """
        #Calculate as a double to prevent overflow errors when casting 
        ColumnD = max(-1, math.floor((UTMX - (self.x_origin - self.dx / 2)) / self.dx))

        if (ColumnD > self.number_of_columns):
            return -2;
        return int(ColumnD);
    
    def get_row_index(self, UTMY):
        """
        Gets the Row index for this coordinate. Lower left is (0,0). 
        Returns -1 if UTMY is below the grid and -2 if it is above.
        """
        #Calculate as a double to prevent overflow errors when casting 
        RowD = max(-1, math.floor((UTMY - (self.y_origin - self.dy / 2)) / self.dy));

        if (RowD > self.number_of_rows):
            return -2
        return int(RowD)
    

    def __write_geo_info(self):
      if not self._initialized_for_writing:
        self.__initialize_for_writing()

      self.error =DFSDLLWrapper().dfsSetGeoInfoUTMProj(self._header_pointer, self.projection_WKT, self.x_origin, self.y_origin, self.orientation)
      for i in range(self.number_of_items):
          self.__write_item_info(self.items[i])
          if self.space_axis is SpaceAxisType.EqD2:
              self.error = DFSDLLWrapper().dfsSetItemAxisEqD2(self.items[i].item_pointer, self.number_of_columns, self.number_of_rows, 0, 0, self.dx, self.dy)
          elif self.space_axis is SpaceAxisType.EqD3:
               self.error = DFSDLLWrapper().dfsSetItemAxisEqD3(self.items[i].item_pointer, self.number_of_columns, self.number_of_rows, self.number_of_layers, 0, 0, self.dx, self.dy)
          elif self.space_axis is SpaceAxisType.EqD0:
               self.error = DFSDLLWrapper().dfsSetItemAxisEqD0(self.items[i].item_pointer)

    def __write_item_info(self, Item):
      if not self._initialized_for_writing:
        self.__initialize_for_writing()
      self.error =DFSDLLWrapper().dfsSetItemInfo(self._header_pointer, Item.item_pointer, Item.eum_item, Item.name, Item.eum_unit, Item.data_type);
      self.error =DFSDLLWrapper().dfsSetItemValueType(Item.item_pointer, Item.value_type)
      
    #Writes timestep and starttime
    def __write_time(self):
        if not self._initialized_for_writing:
            self.__initialize_for_writing()
        if self.time_axis is TimeAxisType.CalendarEquidistant:
            self.error =DFSDLLWrapper().dfsSetEqCalendarAxis(self._header_pointer, self.start_time, self.time_step_unit, self.time_step_size)
        elif self.time_axis is TimeAxisType.CalendarNonEquidistant:
            self.error =DFSDLLWrapper().dfsSetNeqCalendarAxis(self._header_pointer, self.start_time, self.time_step_unit)
    
    def save_changes(self):
        self.__write_geo_info()
        self.__write_time()


    def dispose(self):
        if self._needs_saving==True:
            self.save_changes()

        if (self._header_pointer != c_int()):
            self.error = DFSDLLWrapper().dfsFileClose(self._header_pointer, self._file_pointer)


#DFS0
class DFS0(DFSBase):
    def __init__(self, file_name):
        super(DFS0, self).__init__(file_name)
        self.__data_read=False

    @classmethod
    def from_file(cls, file_name):
        ext=Path(file_name).suffix.lower()
        if ext!='.dfs0':
            raise SyntaxError("Cannot open file with extension: " + ext + ' as DFS0')
        return super().open_file(file_name)
        
    @classmethod
    def new_file(cls, file_name, NumberOfItems):
        cls = DFS0(file_name)
        cls.ok = DFSDLLWrapper().dfsHeaderCreate(FileType.NeqtimeFixedspaceAllitems, NumberOfItems, StatType.NoStat, cls._header_pointer)
        super(DFS0, cls).new_file(file_name, NumberOfItems)
        cls.time_axis = TimeAxisType.CalendarNonEquidistant
        cls.space_axis = SpaceAxisType.EqD0

        return cls
    
    @classmethod
    def from_template_file(cls, FileName, TemplateFile):
        cls = super().new_file(FileName, TemplateFile.NumberOfItems)
        cls.CopyItemInfo(TemplateFile)
        cls.copy_from_template(TemplateFile)
        return cls

    def get_data(self, TimeStep, Item):
        return super(DFS0, self).read_item_time_step(TimeStep, Item)[0]

    def set_data(self, TimeStep, Item, Data):
        dataArrayType=c_float*1
        dfsdata =dataArrayType()
        dfsdata[0]=Data
        super(DFS0, self).write_item_timestep(TimeStep, Item, dfsdata)

    def get_timeseries(self, Item):
#   Gets all data for a particular item as a Pandas series
        if not self.__data_read:
            for I in self.items:
                I.data = []
            for t in range(0, self.number_of_time_steps):
                for inumber in range(1, self.number_of_items):
                    self.items[inumber-1].data.append(self.get_data(t, inumber))
            self.__data_read = True
        return pd.Series(self.items[Item].data, index=self.time_steps)

#DFS2
class DFS2(DFSBase):
    def __init__(self, file_name):
        super(DFS2, self).__init__(file_name)
    
    @classmethod
    def from_file(cls, file_name):
        ext=Path(file_name).suffix.lower()
        if ext!='.dfs2':
            raise SyntaxError("Cannot open file with extension: " + ext + ' as DFS2')
        return super().open_file(file_name)

    @classmethod
    def new_file(cls, file_name, NumberOfItems):
        cls = DFS2(file_name)
        DFSDLLWrapper().dfsHeaderCreate(FileType.EqtimeFixedspaceAllitems, NumberOfItems, StatType.NoStat, cls._header_pointer)
        super(DFS2, cls).new_file(file_name, NumberOfItems)
        cls.time_axis = TimeAxisType.CalendarEquidistant
        cls.space_axis = SpaceAxisType.EqD2
        return cls
    
    @classmethod
    def from_template_file(cls, file_name, TemplateFileName):
        TemplateFile = DFS2.from_file(TemplateFileName)
        cls = DFS2.new_file(file_name, TemplateFile.number_of_items)
        cls._copy_item_info(TemplateFile)
        cls.copy_from_template(TemplateFile)
        return cls

    def copy_from_template(self, TemplateFile):
        super(DFS2, self).copy_from_template(TemplateFile)
        self.number_of_columns = TemplateFile.number_of_columns;
        self.number_of_rows = TemplateFile.number_of_rows;
        self.dx = TemplateFile.dx
        self.dy = TemplateFile.dy
        self.x_origin = TemplateFile.x_origin
        self.y_origin = TemplateFile.y_origin
        self.orientation = TemplateFile.orientation
        
    def get_data(self, TimeStep, Item):
        return np.array(super(DFS2,self).read_item_time_step(TimeStep, Item))

    def to_asc(self, file_name, time_step, item):
        dtpm = np.flipud(self.get_data(time_step, item))
        np.savetxt(file_name, dtpm, fmt = '%10.5E', header= self.get_asc_header(), comments='')
        
       
    def set_data(self, TimeStep, Item, Data):
        super(DFS2, self).write_item_timestep(TimeStep, Item, Data.ctypes)
       
#DFS3
class DFS3(DFSBase):
    def __init__(self, file_name):
        super(DFS3, self).__init__(file_name)
    
    @classmethod
    def from_file(cls, file_name):
        ext=Path(file_name).suffix.lower()
        if ext!='.dfs3':
            raise SyntaxError("Cannot open file with extension: " + ext + ' as DFS3')
        return super().open_file(file_name)

    @classmethod
    def new_file(cls, file_name, NumberOfItems):
        cls = DFS3(file_name)
        DFSDLLWrapper().dfsHeaderCreate(FileType.EqtimeFixedspaceAllitems, NumberOfItems, StatType.NoStat, cls._header_pointer)
        super(DFS3, cls).new_file(file_name, NumberOfItems)
        cls.time_axis = TimeAxisType.CalendarEquidistant
        cls.space_axis = SpaceAxisType.EqD3
        return cls
    
    @classmethod
    def from_template_file(cls, FileName, TemplateFileName):
        TemplateFile = DFS3.from_file(TemplateFileName)
        cls = DFS3.new_file(FileName, TemplateFile.number_of_items)
        cls._copy_item_info(TemplateFile)
        cls.copy_from_template(TemplateFile)
        return cls

    def copy_from_template(self, TemplateFile):
        super(DFS3, self).copy_from_template(TemplateFile)
        self.number_of_columns = TemplateFile.number_of_columns
        self.number_of_rows = TemplateFile.number_of_rows
        self.number_of_layers = TemplateFile.number_of_layers
        self.dx = TemplateFile.dx
        self.dy = TemplateFile.dy
        self.x_origin = TemplateFile.x_origin
        self.y_origin = TemplateFile.y_origin
        self.orientation = TemplateFile.orientation
        
    def get_data(self, TimeStep, Item):
        data =super(DFS3, self).read_item_time_step(TimeStep, Item)
        toreturn =[]
        for i in range(self.number_of_layers):
            toreturn.append(np.array(data[:][:][i]))
        return toreturn
        
    def set_data(self, TimeStep, Item, Data):
        dataArrayType=c_float*self.number_of_columns *self.number_of_rows*self.number_of_layers
        dfsdata =dataArrayType()

        for k in range(self.number_of_layers):
            for i in range(self.number_of_rows):
                for j in range(self.number_of_columns):
                    d=Data[k][i,j]
                    dfsdata[k][i][j]=d 
            
        super(DFS3, self).write_item_timestep(TimeStep, Item, dfsdata)

    def to_asc(self, file_name, time_step, item, layer):
        dtpm = np.flipud(self.get_data(time_step, item)[:][:][layer])
        np.savetxt(file_name, dtpm, fmt = '%10.5E', header= self.get_asc_header(), comments='')


#RES1D
class RES(DFSBase):
    def __init__(self, file_name):
        super(RES, self).__init__(file_name)
        self.__data_read=False

    @classmethod
    def from_file(self, file_name):
        ext=Path(file_name).suffix.lower()
        if ext!='.res1d' and ext!='.res11':
            raise SyntaxError("Cannot open file with extension: " + ext + ' as RES')
        self = super().open_file(file_name)

        fioerror = c_int( 0)
        i = 1
        self.StaticItems=[]
        DFSDLLWrapper().dfsFindItemStatic(self._header_pointer, self._file_pointer, i)
        while True: 
            si = DFSDLLWrapper().dfsStaticRead(self._file_pointer, fioerror)
            if si==0:
                break;
            item = DFSItem(c_longlong(si), i)
            item.read_item()
            self.StaticItems.append(item)
            i+=1

        return self

    def get_data(self, TimeStep, Item):
        return super(RES, self).read_item_time_step(TimeStep, Item)

    def get_timeseries(self, Item, index):
#   Gets all data for a particular item as a Pandas series
        if not self.__data_read:
            for I in self.items:
                I.data = []
            for t in range(0, self.number_of_time_steps):
                for inumber in range(1, self.number_of_items+1):
                    self.items[inumber-1].data.append(self.get_data(t, inumber))
            self.__data_read = True
        return pd.Series( [i[index] for i in self.items[Item-1].data], index=self.time_steps)



#Enumeration section
class SpaceAxisType(Enum):
    undefined=0
    EqD0 = 1
    EqD1 = 2
    NeqD1 = 3
    EqD2 = 5
    NeqD2 = 6
    EqD3 = 8
    NeqD3 = 9
    CurveLinearD2 = 12
    CurveLinearD3 = 13
    
class TimeAxisType(Enum):
    Undefined = 0
    TimeEquidistant = 1
    TimeNonEquidistant = 2
    CalendarEquidistant = 3
    CalendarNonEquidistant = 4
    
class TimeInterval(Enum):
    Second = 1400
    Minute =1401
    Hour=1402
    Day=1403
    Month=1404
    Year=1405  
    
class DataValueType(Enum):
    Instantaneous = 0
    Accumulated = 1
    StepAccumulated = 2
    MeanStepBackward = 3
    MeanStepForward = 4
    
class DfsSimpleType(Enum):
    Float = 1
    Double = 2
    Byte = 3
    Int = 4
    UInt = 5
    Short = 6
    UShort = 7

class FileType(Enum):
    Undefined = 0
    EqtimeFixedspaceAllitems = 1
    EqtimeTvarspaceAllitems = 2
    NeqtimeFixedspaceAllitems = 4
    NeqtimeFixedspaceVaritems = 8
    NeqtimeTvarspaceVaritems = 16

class StatType(Enum):
    Undefined = 0
    NoStat = 1
    RegularStat = 2
    LargevalStat = 3

class EumItem(Enum):
    eumIItemUndefined = 999
    eumIWaterLevel = 100000
    eumIDischarge = 100001
    eumIWindVelocity = 100002
    eumIWindDirection = 100003
    eumIRainfall = 100004
    eumIEvaporation = 100005
    eumITemperature = 100006
    eumIConcentration = 100007
    eumIBacteriaConc = 100008
    eumIResistFactor = 100009
    eumISedimentTransport = 100010
    eumIBottomLevel = 100011
    eumIBottomLevelChange = 100012
    eumISedimentFraction = 100013
    eumISedimentFractionChange = 100014
    eumIGateLevel = 100015
    eumIFlowVelocity = 100016
    eumIDensity = 100017
    eumIDamBreachLevel = 100018
    eumIDamBreachWidth = 100019
    eumIDamBreachSlope = 100020
    eumISunShine = 100021
    eumISunRadiation = 100022
    eumIRelativeHumidity = 100023
    eumISalinity = 100024
    eumISurfaceSlope = 100025
    eumIFlowArea = 100026
    eumIFlowWidth = 100027
    eumIHydraulicRadius = 100028
    eumIResistanceRadius = 100029
    eumIManningsM = 100030
    eumIManningsn = 100031
    eumIChezyNo = 100032
    eumIConveyance = 100033
    eumIFroudeNo = 100034
    eumIWaterVolume = 100035
    eumIFloodedArea = 100036
    eumIWaterVolumeError = 100037
    eumIAccWaterVolumeError = 100038
    eumICompMass = 100039
    eumICompMassError = 100040
    eumIAccCompMassError = 100041
    eumIRelCompMassError = 100042
    eumIRelAccCompMassError = 100043
    eumICompDecay = 100044
    eumIAccCompDecay = 100045
    eumICompTransp = 100046
    eumIAccCompTransp = 100047
    eumICompDispTransp = 100048
    eumIAccCompDispTransp = 100049
    eumICompConvTransp = 100050
    eumIAccCompConvTransp = 100051
    eumIAccSedimentTransport = 100052
    eumIDuneLength = 100053
    eumIDuneHeight = 100054
    eumIBedSedimentLoad = 100055
    eumISuspSedimentLoad = 100056
    eumIIrrigation = 100057
    eumIRelMoistureCont = 100058
    eumIGroundWaterDepth = 100059
    eumISnowCover = 100060
    eumIInfiltration = 100061
    eumIRecharge = 100062
    eumIOF1_Flow = 100063
    eumIIF1_Flow = 100064
    eumICapillaryFlux = 100065
    eumISurfStorage_OF1 = 100066
    eumISurfStorage_OF0 = 100067
    eumISedimentLayer = 100068
    eumIBedLevel = 100069
    eumIRainfallIntensity = 100070
    eumIproductionRate = 100071
    eumIsedimentMass = 100072
    eumIprimaryProduction = 100073
    eumIprodPerVolume = 100074
    eumIsecchiDepth = 100075
    eumIAccSedimentMass = 100076
    eumISedimentMassPerM = 100077
    eumISurfaceElevation = 100078
    eumIBathymetry = 100079
    eumIFlowFlux = 100080
    eumIBedLoadPerM = 100081
    eumISuspLoadPerM = 100082
    eumISediTransportPerM = 100083
    eumIWaveHeight = 100084
    eumIWavePeriod = 100085
    eumIWaveFrequency = 100086
    eumIPotentialEvapRate = 100087
    eumIRainfallRate = 100088
    eumIWaterDemand = 100089
    eumIReturnFlowFraction = 100090
    eumILinearRoutingCoef = 100091
    eumISpecificRunoff = 100092
    eumIMachineEfficiency = 100093
    eumITargetPower = 100094
    eumIWaveDirection = 100095
    eumIAccSediTransportPerM = 100096
    eumISignificantWaveHeight = 100097
    eumIShieldsParameter = 100098
    eumIAngleBedVelocity = 100099
    eumIProfileNumber = 100100
    eumIClimateNumber = 100101
    eumISpectralDescription = 100102
    eumISpreadingFactor = 100103
    eumIRefPointNumber = 100104
    eumIWindFrictionFactor = 100105
    eumIWaveDisturbanceCoefficient = 100106
    eumITimeFirstWaveArrival = 100107
    eumISurfaceCurvature = 100108
    eumIRadiationStress = 100109
    eumISpectralDensity = 100120
    eumIFreqIntegSpectralDensity = 100121
    eumIDirecIntegSpectralDensity = 100122
    eumIEddyViscosity = 100123
    eumIDSD = 100124
    eumIBeachPosition = 100125
    eumITrenchPosition = 100126
    eumIGrainDiameter = 100127
    eumIFallVelocity = 100128
    eumIGeoDeviation = 100129
    eumIBreakingWave = 100130
    eumIDunePosition = 100131
    eumIContourAngle = 100132
    eumIFlowDirection = 100133
    eumIBedSlope = 100134
    eumISurfaceArea = 100135
    eumICatchmentArea = 100136
    eumIRoughness = 100137
    eumIActiveDepth = 100138
    eumISedimentGradation = 100139
    eumIGroundwaterRecharge = 100140
    eumISoluteFlux = 100141
    eumIRiverStructGeo = 100142
    eumIRiverChainage = 100143
    eumINonDimFactor = 100144
    eumINonDimExp = 100145
    eumIStorageDepth = 100146
    eumIRiverWidth = 100147
    eumIFlowRoutingTimeCnst = 100148
    eumIFstOrderRateAD = 100149
    eumIFstOrderRateWQ = 100150
    eumIEroDepoCoef = 100151
    eumIShearStress = 100152
    eumIDispCoef = 100153
    eumIDispFact = 100154
    eumISedimentVolumePerLengthUnit = 100155
    eumIKinematicViscosity = 100156
    eumILatLong = 100157
    eumISpecificGravity = 100158
    eumITransmissionCoefficient = 100159
    eumIReflectionCoefficient = 100160
    eumIFrictionFactor = 100161
    eumIRadiationIntensity = 100162
    eumIDuration = 100163
    eumIRespProdPerArea = 100164
    eumIRespProdPerVolume = 100165
    eumISedimentDepth = 100166
    eumIAngleOfRespose = 100167
    eumIHalfOrderRateWQ = 100168
    eumIRearationConstant = 100169
    eumIDepositionRate = 100170
    eumIBODAtRiverBed = 100171
    eumICropDemand = 100172
    eumIIrrigatedArea = 100173
    eumILiveStockDemand = 100174
    eumINumberOfLiveStock = 100175
    eumITotalGas = 100176
    eumIGroundWaterAbstraction = 100177
    eumIMeltingCoefficient = 100178
    eumIRainMeltingCoefficient = 100179
    eumIElevation = 100180
    eumICrossSectionXdata = 100181
    eumIVegetationHeight = 100182
    eumIGeographicalCoordinate = 100183
    eumIAngle = 100184
    eumIItemGeometry0D = 100185
    eumIItemGeometry1D = 100186
    eumIItemGeometry2D = 100187
    eumIItemGeometry3D = 100188
    eumITemperatureLapseRate = 100189
    eumICorrectionOfPrecipitation = 100190
    eumITemperatureCorrection = 100191
    eumIPrecipitationCorrection = 100192
    eumIMaxWater = 100193
    eumILowerBaseflow = 100194
    eumIMassFlux = 100195
    eumIPressureSI = 100196
    eumITurbulentKineticEnergy = 100197
    eumIDissipationTKE = 100198
    eumISaltFlux = 100199
    eumITemperatureFlux = 100200
    eumIConcentration1 = 100201
    eumILatentHeat = 100202
    eumIHeatFlux = 100203
    eumISpecificHeat = 100204
    eumIVisibility = 100205
    eumIIceThickness = 100206
    eumIStructureGeometryPerTime = 100207
    eumIDischargePerTime = 100208
    eumIFetchLength = 100209
    eumIRubbleMound = 100210
    eumIGridSpacing = 100211
    eumITimeStep = 100212
    eumILenghtScale = 100213
    eumIErosionCoefficientFactor = 100214
    eumIFrictionCoeffient = 100215
    eumITransitionRate = 100216
    eumIDistance = 100217
    eumITimeCorrectionAtNoon = 100218
    eumICriticalVelocity = 100219
    eumILightExtinctionBackground = 100220
    eumIParticleProductionRate = 100221
    eumIFirstOrderGrazingRateDependance = 100222
    eumIResuspensionRate = 100223
    eumIAdsorptionCoefficient = 100224
    eumIDesorptionCoefficient = 100225
    eumISedimentationVelocity = 100226
    eumIBoundaryLayerThickness = 100227
    eumIDiffusionCoefficient = 100228
    eumIBioconcentrationFactor = 100229
    eumIFcoliConcentration = 100230
    eumISpecificDischarge = 100231
    eumIPrecipitation = 100232
    eumISpecificPrecipitation = 100233
    eumIPower = 100234
    eumIConveyanceLoss = 100235
    eumIInfiltrationFlux = 100236
    eumIEvaporationFlux = 100237
    eumIGroundWaterAbstractionFlux = 100238
    eumIFraction = 100239
    eumIYieldfactor = 100240
    eumISpecificSoluteFluxPerArea = 100241
    eumICurrentSpeed = 100242
    eumICurrentDirection = 100243
    eumICurrentMagnitude = 100244
    eumIPistonPosition = 100245
    eumISubPistonPosition = 100246
    eumISupPistonPosition = 100247
    eumIFlapPosition = 100248
    eumISubFlapPosition = 100249
    eumISupFlapPosition = 100250
    eumILengthZeroCrossing = 100251
    eumITimeZeroCrossing = 100252
    eumILengthLoggedData = 100253
    eumIForceLoggedData = 100254
    eumISpeedLoggedData = 100255
    eumIVolumeFlowLoggedData = 100256
    eumI2DSurfaceElevationSpectrum = 100257
    eumI3DSurfaceElevationSpectrum = 100258
    eumIDirectionalSpreadingFunction = 100259
    eumIAutoSpectrum = 100260
    eumICrossSpectrum = 100261
    eumICoherenceSpectrum = 100262
    eumICoherentSpectrum = 100263
    eumIFrequencyResponseSpectrum = 100264
    eumIPhaseSpectrum = 100265
    eumIFIRCoefficient = 100266
    eumIFourierACoefficient = 100267
    eumIFourierBCoefficient = 100268
    eumIuVelocity = 100269
    eumIvVelocity = 100270
    eumIwVelocity = 100271
    eumIBedThickness = 100272
    eumIDispersionVelocityFactor = 100273
    eumIWindSpeed = 100274
    eumIShoreCurrentZone = 100275
    eumIDepthofWind = 100276
    eumIEmulsificationConstantK1 = 100277
    eumIEmulsificationConstantK2 = 100278
    eumILightExtinction = 100279
    eumIWaterDepth = 100280
    eumIReferenceSettlingVelocity = 100281
    eumIPhaseError = 100282
    eumILevelAmplitudeError = 100283
    eumIDischargeAmplitudeError = 100284
    eumILevelCorrection = 100285
    eumIDischargeCorrection = 100286
    eumILevelSimulated = 100287
    eumIDischargeSimulated = 100288
    eumISummQCorrected = 100289
    eumITimeScale = 100290
    eumISpongeCoefficient = 100291
    eumIPorosityCoefficient = 100292
    eumIFilterCoefficient = 100293
    eumISkewness = 100294
    eumIAsymmetry = 100295
    eumIAtiltness = 100296
    eumIKurtosis = 100297
    eumIAuxiliaryVariableW = 100298
    eumIRollerThickness = 100299
    eumILineThickness = 100300
    eumIMarkerSize = 100301
    eumIRollerCelerity = 100302
    eumIEncroachmentOffset = 100303
    eumIEncroachmentPosition = 100304
    eumIEncroachmentWidth = 100305
    eumIConveyanceReduction = 100306
    eumIWaterLevelChange = 100307
    eumIEnergyLevelChange = 100308
    eumIParticleVelocityU = 100309
    eumIParticleVelocityV = 100310
    eumIAreaFraction = 100311
    eumICatchmentSlope = 100312
    eumIAverageLength = 100313
    eumIPersonEqui = 100314
    eumIInverseExpo = 100315
    eumITimeShift = 100316
    eumIAttenuation = 100317
    eumIPopulation = 100318
    eumIIndustrialOutput = 100319
    eumIAgriculturalArea = 100320
    eumIPopulationUsage = 100321
    eumIIndustrialUse = 100322
    eumIAgriculturalUsage = 100323
    eumILayerThickness = 100324
    eumISnowDepth = 100325
    eumISnowCoverPercentage = 100326
    eumIPressureHead = 100353
    eumIKC = 100354
    eumIAroot = 100355
    eumIC1 = 100356
    eumIC2 = 100357
    eumIC3 = 100358
    eumIIrrigationDemand = 100359
    eumIHydrTransmissivity = 100360
    eumIDarcyVelocity = 100361
    eumIHydrLeakageCoefficient = 100362
    eumIHydrConductance = 100363
    eumIHeightAboveGround = 100364
    eumIPumpingRate = 100365
    eumIDepthBelowGround = 100366
    eumICellHeight = 100367
    eumIHeadGradient = 100368
    eumIGroundWaterFlowVelocity = 100369
    eumIIntegerCode = 100370
    eumIDrainageTimeConstant = 100371
    eumIHeadElevation = 100372
    eumILengthError = 100373
    eumIElasticStorage = 100374
    eumISpecificYield = 100375
    eumIExchangeRate = 100376
    eumIVolumetricWaterContent = 100377
    eumIStorageChangeRate = 100378
    eumISeepage = 100379
    eumIRootDepth = 100380
    eumIRillDepth = 100381
    eumILogical = 100382
    eumILAI = 100383
    eumIIrrigationRate = 100384
    eumIIrrigationIndex = 100385
    eumIInterception = 100386
    eumIETRate = 100387
    eumIErosionSurfaceLoad = 100388
    eumIErosionConcentration = 100389
    eumIEpsilonUZ = 100390
    eumIDrainage = 100391
    eumIDeficit = 100392
    eumICropYield = 100393
    eumICropType = 100394
    eumICropStress = 100395
    eumICropStage = 100396
    eumICropLoss = 100397
    eumICropIndex = 100398
    eumIAge = 100399
    eumIHydrConductivity = 100400
    eumIPrintScaleEquivalence = 100401
    eumIConcentration_1 = 100402
    eumIConcentration_2 = 100403
    eumIConcentration_3 = 100404
    eumIConcentration_4 = 100405
    eumISedimentDiameter = 100406
    eumIMeanWaveDirection = 100407
    eumIFlowDirection_1 = 100408
    eumIAirPressure = 100409
    eumIDecayFactor = 100410
    eumISedimentBedDensity = 100411
    eumIDispersionCoefficient = 100412
    eumIFlowVelocityProfile = 100413
    eumIHabitatIndex = 100414
    eumIAngle2 = 100415
    eumIHydraulicLength = 100416
    eumISCSCatchSlope = 100417
    eumITurbidity_FTU = 100418
    eumITurbidity_MgPerL = 100419
    eumIBacteriaFlow = 100420
    eumIBedDistribution = 100421
    eumISurfaceElevationAtPaddle = 100422
    eumIUnitHydrographOrdinate = 100423
    eumITransferRate = 100424
    eumIReturnPeriod = 100425
    eumIConstFallVelocity = 100426
    eumIDepositionConcFlux = 100427
    eumISettlingVelocityCoef = 100428
    eumIErosionCoefficient = 100429
    eumIVolumeFlux = 100430
    eumIPrecipitationRate = 100431
    eumIEvaporationRate = 100432
    eumICoSpectrum = 100433
    eumIQuadSpectrum = 100434
    eumIPropagationDirection = 100435
    eumIDirectionalSpreading = 100436
    eumIMassPerUnitArea = 100437
    eumIIncidentSpectrum = 100438
    eumIReflectedSpectrum = 100439
    eumIReflectionFunction = 100440
    eumIBacteriaFlux = 100441
    eumIHeadDifference = 100442
    eumIenergy = 100443
    eumIDirStdDev = 100444
    eumIRainfallDepth = 100445
    eumIGroundWaterAbstractionDepth = 100446
    eumIEvaporationIntesity = 100447
    eumILongitudinalInfiltration = 100448
    eumIPollutantLoad = 100449
    eumIPressure = 100450
    eumICostPerTime = 100451
    eumIMass = 100452
    eumIMassPerTime = 100453
    eumIMassPerAreaPerTime = 100454
    eumIKd = 100455
    eumIPorosity = 100456
    eumIHalfLife = 100457
    eumIDispersivity = 100458
    eumIFrictionCoeffientcfw = 100459
    eumIWaveamplitude = 100460
    eumISedimentGrainDiameter = 100461
    eumIViscosity = 100462
    eumISedimentSpill = 100463
    eumINumberOfParticles = 100464
    eumIEllipsoidalHeight = 100500
    eumICloudiness = 100501
    eumIProbability = 100502
    eumIDispersantActivity = 100503
    eumIDredgeRate = 100504
    eumIDredgeSpill = 100505
    eumIClearnessCoefficient = 100506
    eumIProfileOrientation = 100507
    eumIReductionFactor = 100508
    eumIActiveBeachHeight = 100509
    eumIUpdatePeriod = 100510
    eumIAccumulatedErosion = 100511
    eumIErosionRate = 100512
    eumINonDimTransport = 100513
    eumIDiverteddischarge = 110001
    eumIDemandcarryoverfraction = 110002
    eumIGroundwaterdemand = 110003
    eumIDamcrestlevel = 110004
    eumISeepageflux = 110005
    eumISeepagefraction = 110006
    eumIEvaporationfraction = 110007
    eumIResidencetime = 110008
    eumIOwnedfractionofinflow = 110009
    eumIOwnedfractionofvolume = 110010
    eumIReductionlevel = 110011
    eumIReductionthreshold = 110012
    eumIReductionfraction = 110013
    eumITotalLosses = 110014
    eumICountsPerLiter = 110015
    eumIAssimilativeCapacity = 110016
    eumIStillWaterDepth = 110017
    eumITotalWaterDepth = 110018
    eumIMaxWaveHeight = 110019
    eumIIceConcentration = 110020
    eumIWindFrictionSpeed = 110021
    eumIRoughnessLength = 110022
    eumIWindDragCoefficient = 110023
    eumICharnockConstant = 110024
    eumIBreakingParameterGamma = 110025
    eumIThresholdPeriod = 110026
    eumICourantNumber = 110027
    eumITimeStepFactor = 110028
    eumIElementLength = 110029
    eumIElementArea = 110030
    eumIRollerAngle = 110031
    eumIRateBedLevelChange = 110032
    eumIBedLevelChange = 110033
    eumISedimentTransportDirection = 110034
    eumIWaveActionDensity = 110035
    eumIZeroMomentWaveAction = 110036
    eumIFirstMomentWaveAction = 110037
    eumIBedMass = 110038
    eumIEPANETWaterQuality = 110039
    eumIEPANETStatus = 110040
    eumIEPANETSetting = 110041
    eumIEPANETReactionRate = 110042
    eumIFRDischarge = 110043
    eumISRDischarge = 110044
    eumIAveSediTransportPerLengthUnit = 110045
    eumIValveSetting = 110046
    eumIWaveEnergyDensity = 110047
    eumIWaveEnergyDistribution = 110048
    eumIWaveEnergy = 110049
    eumIRadiationMeltingCoefficient = 110050
    eumIRainMeltingCoefficientPerDegree = 110051
    eumIEPANETFriction = 110052
    eumIWaveActionDensityRate = 110053
    eumIElementAreaLongLat = 110054
    eumIElectricCurrent = 110100
    eumIHeatFluxResistance = 110200
    eumIAbsoluteHumidity = 110210
    eumILength = 110220
    eumIVolume = 110230
    eumIElementVolume = 110231
    eumIWavePower = 110232
    eumIMomentOfInertia = 110233
    eumITopography = 110234
    eumIScourDepth = 110235
    eumIScourWidth = 110236
 
class EumUnit(Enum):
    eumUUnitUndefined = 0
    eumUmeter = 1000
    eumUkilometer = 1001
    eumUmillimeter = 1002
    eumUfeet = 1003
    eumUinch = 1004
    eumUmile = 1005
    eumUyard = 1006
    eumUcentimeter = 1007
    eumUmicrometer = 1008
    eumUnauticalmile = 1009
    eumUmillifeet = 1010
    eumULiterPerM2 = 1011
    eumUMilliMeterD50 = 1012
    eumUinchUS = 1013
    eumUfeetUS = 1014
    eumUyardUS = 1015
    eumUmileUS = 1016
    eumUkilogram = 1200
    eumUgram = 1201
    eumUmilligram = 1202
    eumUmicrogram = 1203
    eumUton = 1204
    eumUkiloton = 1205
    eumUmegaton = 1206
    eumUPound = 1207
    eumUtonUS = 1208
    eumUsec = 1400
    eumUminute = 1401
    eumUhour = 1402
    eumUday = 1403
    eumUyear = 1404
    eumUmonth = 1405
    eumUm3 = 1600
    eumUliter = 1601
    eumUmilliliter = 1602
    eumUft3 = 1603
    eumUgal = 1604
    eumUmgal = 1605
    eumUkm3 = 1606
    eumUacft = 1607
    eumUMegaGal = 1608
    eumUMegaLiter = 1609
    eumUTenTo6m3 = 1610
    eumUm3PerCurrency = 1611
    eumUgalUK = 1612
    eumUMegagalUK = 1613
    eumUydUS3 = 1614
    eumUYard3 = 1615
    eumUm3PerSec = 1800
    eumUft3PerSec = 1801
    eumUMlPerDay = 1802
    eumUMgalPerDay = 1803
    eumUacftPerDay = 1804
    eumUm3PerYear = 1805
    eumUGalPerDayPerHead = 1806
    eumULiterPerDayPerHead = 1807
    eumUm3PerSecPerHead = 1808
    eumUliterPerPersonPerDay = 1809
    eumUm3PerDay = 1810
    eumUGalPerSec = 1811
    eumUGalPerDay = 1812
    eumUGalPerYear = 1813
    eumUft3PerDay = 1814
    eumUft3PerYear = 1815
    eumUm3PerMinute = 1816
    eumUft3PerMin = 1817
    eumUGalPerMin = 1818
    eumUliterPerSec = 1819
    eumUliterPerMin = 1820
    eumUm3PerHour = 1821
    eumUgalUKPerDay = 1822
    eumUMgalUKPerDay = 1823
    eumUft3PerDayPerHead = 1824
    eumUm3PerDayPerHead = 1825
    eumUGalUKPerSec = 1826
    eumUGalUKPerYear = 1827
    eumUGalUKPerDayPerHead = 1828
    eumUydUS3PerSec = 1829
    eumUyard3PerSec = 1830
    eumUftUS3PerSec = 1831
    eumUftUS3PerMin = 1832
    eumUftUS3PerDay = 1833
    eumUftUS3PerYear = 1834
    eumUyardUS3PerSec = 1835
    eumUmeterPerSec = 2000
    eumUmillimeterPerHour = 2001
    eumUfeetPerSec = 2002
    eumUliterPerSecPerKm2 = 2003
    eumUmillimeterPerDay = 2004
    eumUacftPerSecPerAcre = 2005
    eumUmeterPerDay = 2006
    eumUft3PerSecPerMi2 = 2007
    eumUmeterPerHour = 2008
    eumUfeetPerDay = 2009
    eumUmillimeterPerMonth = 2010
    eumUinchPerSec = 2011
    eumUmeterPerMinute = 2012
    eumUfeetPerMinute = 2013
    eumUinchPerMinute = 2014
    eumUfeetPerHour = 2015
    eumUinchPerHour = 2016
    eumUmillimeterPerSecond = 2017
    eumUcmPerHour = 2018
    eumUknot = 2019
    eumUmilePerHour = 2020
    eumUkilometerPerHour = 2021
    eumUAcreFeetPerDayPerAcre = 2022
    eumUCentiMeterPerSecond = 2023
    eumUCubicFeetPerSecondPerAcre = 2024
    eumUCubicMeterPerDayPerHectar = 2025
    eumUCubicMeterPerHourPerHectar = 2026
    eumUCubicMeterPerSecondPerHectar = 2027
    eumUGallonPerMinutePerAcre = 2028
    eumULiterPerMinutePerHectar = 2029
    eumULiterPerSecondPerHectar = 2030
    eumUMicroMeterPerSecond = 2031
    eumUMillionGalPerDayPerAcre = 2032
    eumUMillionGalUKPerDayPerAcre = 2033
    eumUMillionLiterPerDayPerHectar = 2034
    eumUinchUSPerSecond = 2035
    eumUfeetUSPerSecond = 2036
    eumUfeetUSPerDay = 2037
    eumUinchUSPerHour = 2038
    eumUinchUSPerMinute = 2039
    eumUMeterPerSecondPerSecond = 2100
    eumUFeetPerSecondPerSecond = 2101
    eumUkiloGramPerM3 = 2200
    eumUmicroGramPerM3 = 2201
    eumUmilliGramPerM3 = 2202
    eumUgramPerM3 = 2203
    eumUmicroGramPerL = 2204
    eumUmilliGramPerL = 2205
    eumUgramPerL = 2206
    eumUPoundPerCubicFeet = 2207
    eumUtonPerM3 = 2208
    eumUPoundPerSquareFeet = 2209
    eumUtonPerM2 = 2210
    eumUmicroGramPerM2 = 2211
    eumUPoundPerydUS3 = 2212
    eumUPoundPeryard3 = 2213
    eumUPoundPerCubicFeetUS = 2214
    eumUPoundPerSquareFeetUS = 2215
    eumUKiloGramPerMeterPerSecond = 2300
    eumUPascalSecond = 2301
    eumUradian = 2400
    eumUdegree = 2401
    eumUDegreeNorth50 = 2402
    eumUdegreesquared = 2403
    eumUperDay = 2600
    eumUpercentPerDay = 2601
    eumUhertz = 2602
    eumUperHour = 2603
    eumUcurrencyPerYear = 2604
    eumUperSec = 2605
    eumUbillionPerDay = 2606
    eumUtrillionPerYear = 2607
    eumUSquareMeterPerSecondPerHectar = 2608
    eumUSquareFeetPerSecondPerAcre = 2609
    eumURevolutionPerMinute = 2610
    eumUpercentPerHour = 2611
    eumUpercentPerMinute = 2612
    eumUpercentPerSecond = 2613
    eumUdegreeCelsius = 2800
    eumUdegreeFahrenheit = 2801
    eumUdegreeKelvin = 2802
    eumUperDegreeCelsius = 2850
    eumUperDegreeFahrenheit = 2851
    eumUdeltaDegreeCelsius = 2900
    eumUdeltaDegreeFahrenheit = 2901
    eumUmillPer100ml = 3000
    eumUPer100ml = 3001
    eumUperLiter = 3002
    eumUperM3 = 3003
    eumUperMilliliter = 3004
    eumUSecPerMeter = 3100
    eumUm2 = 3200
    eumUm3PerM = 3201
    eumUacre = 3202
    eumUft2 = 3203
    eumUha = 3204
    eumUkm2 = 3205
    eumUmi2 = 3206
    eumUft3PerFt = 3207
    eumUftUS2 = 3208
    eumUydUS2 = 3209
    eumUmiUS2 = 3210
    eumUacreUS = 3211
    eumUydUS3PeryardUS = 3212
    eumUYard3PerYard = 3213
    eumUftUS3PerftUS = 3214
    eumUEPerM2PerDay = 3400
    eumUThousandPerM2PerDay = 3401
    eumUPerM2PerSec = 3402
    eumUMeter2One3rdPerSec = 3600
    eumUFeet2One3rdPerSec = 3601
    eumUSecPerMeter2One3rd = 3800
    eumUSecPerFeet2One3rd = 3801
    eumUMeter2OneHalfPerSec = 4000
    eumUFeet2OneHalfPerSec = 4001
    eumUFeetUS2OneHalfPerSec = 4002
    eumUkilogramPerSec = 4200
    eumUmicrogramPerSec = 4201
    eumUmilligramPerSec = 4202
    eumUgramPerSec = 4203
    eumUkilogramPerHour = 4204
    eumUkilogramPerDay = 4205
    eumUgramPerDay = 4206
    eumUkilogramPerYear = 4207
    eumUGramPerMinute = 4208
    eumUKiloGramPerPersonPerDay = 4209
    eumUKilogramPerMinute = 4210
    eumUPoundPerDay = 4212
    eumUPoundPerHour = 4213
    eumUPoundPerMinute = 4214
    eumUPoundPerSecond = 4215
    eumUPoundPerPersonPerDay = 4216
    eumUPoundPerYear = 4217
    eumUTonPerYear = 4218
    eumUTonPerDay = 4219
    eumUTonPerSec = 4220
    eumUgramPerM2 = 4400
    eumUkilogramPerM = 4401
    eumUkilogramPerM2 = 4402
    eumUkilogramPerHa = 4403
    eumUmilligramPerM2 = 4404
    eumUPoundPerAcre = 4405
    eumUgramPerM2PerDay = 4500
    eumUgramPerM2PerSec = 4501
    eumUkilogramPerHaPerHour = 4502
    eumUkilogramPerM2PerSec = 4503
    eumUKiloGramPerHectarPerDay = 4504
    eumUPoundPerAcrePerDay = 4505
    eumUkilogramPerM2PerDay = 4506
    eumUPoundPerFt2PerSec = 4507
    eumUgramPerM3PerHour = 4600
    eumUgramPerM3PerDay = 4601
    eumUgramPerM3PerSec = 4602
    eumUMilliGramPerLiterPerDay = 4603
    eumUm3PerSecPerM = 4700
    eumUm3PerYearPerM = 4701
    eumUm2PerSec = 4702
    eumUTen2Minus6m2PerSec = 4703
    eumUft2PerSec = 4704
    eumUTen2Minus6ft2PerSec = 4705
    eumUm3PerSecPer10mm = 4706
    eumUft3PerSecPerInch = 4707
    eumUm2PerHour = 4708
    eumUm2PerDay = 4709
    eumUft2PerHour = 4710
    eumUft2PerDay = 4711
    eumUGalUKPerDayPerFeet = 4712
    eumUGalPerDayPerFeet = 4713
    eumUGalPerMinutePerFeet = 4714
    eumULiterPerDayPerMeter = 4715
    eumULiterPerMinutePerMeter = 4716
    eumULiterPerSecondPerMeter = 4717
    eumUft3PerSecPerFt = 4718
    eumUTen2Minus5ft2PerSec = 4719
    eumUft2PerSec2 = 4720
    eumUcm3PerSecPerCm = 4721
    eumUmm3PerSecPerMm = 4722
    eumUftUS3PerSecPerFtUS = 4723
    eumUin3PerSecPerIn = 4724
    eumUinUS3PerSecPerInUS = 4725
    eumUydUS3PerSecPerydUS = 4726
    eumUyard3PerSecPeryard = 4727
    eumUyard3PerYearPeryard = 4728
    eumUydUS3PerYearPerydUS = 4729
    eumUmmPerDay = 4801
    eumUinPerDay = 4802
    eumUm3PerKm2PerDay = 4803
    eumUwatt = 4900
    eumUkwatt = 4901
    eumUmwatt = 4902
    eumUgwatt = 4903
    eumUHorsePower = 4904
    eumUperMeter = 5000
    eumUpercentPer100meter = 5001
    eumUpercentPer100feet = 5002
    eumUperFeet = 5003
    eumUperInch = 5004
    eumUperFeetUS = 5005
    eumUperInchUS = 5006
    eumUm3PerS2 = 5100
    eumUm2SecPerRad = 5200
    eumUm2PerRad = 5201
    eumUm2Sec = 5202
    eumUm2PerDegree = 5203
    eumUm2Sec2PerRad = 5204
    eumUm2PerSecPerRad = 5205
    eumUm2SecPerDegree = 5206
    eumUm2Sec2PerDegree = 5207
    eumUm2PerSecPerDegree = 5208
    eumUft2PerSecPerRad = 5209
    eumUft2PerSecPerDegree = 5210
    eumUft2Sec2PerRad = 5211
    eumUft2Sec2PerDegree = 5212
    eumUft2SecPerRad = 5213
    eumUft2SecPerDegree = 5214
    eumUft2PerRad = 5215
    eumUft2PerDegree = 5216
    eumUft2Sec = 5217
    eumUmilliGramPerL2OneHalfPerDay = 5300
    eumUmilliGramPerL2OneHalfPerHour = 5301
    eumUNewtonPerSqrMeter = 5400
    eumUkiloNewtonPerSqrMeter = 5401
    eumUPoundPerFeetPerSec2 = 5402
    eumUNewtonPerM3 = 5500
    eumUkiloNewtonPerM3 = 5501
    eumUkilogramM2 = 5550
    eumUJoule = 5600
    eumUkiloJoule = 5601
    eumUmegaJoule = 5602
    eumUgigaJoule = 5603
    eumUteraJoule = 5604
    eumUKiloWattHour = 5605
    eumUWattSecond = 5606
    eumUKileJoulePerM2PerHour = 5700
    eumUKileJoulePerM2PerDay = 5701
    eumUmegaJoulePerM2PerDay = 5702
    eumUm2mmPerKiloJoule = 5710
    eumUm2mmPerMegaJoule = 5711
    eumUMilliMeterPerDegreeCelsiusPerDay = 5800
    eumUMilliMeterPerDegreeCelsiusPerHour = 5801
    eumUInchPerDegreeFahrenheitPerDay = 5802
    eumUInchPerDegreeFahrenheitPerHour = 5803
    eumUPerDegreeCelsiusPerDay = 5900
    eumUPerDegreeCelsiusPerHour = 5901
    eumUPerDegreeFahrenheitPerDay = 5902
    eumUPerDegreeFahrenheitPerHour = 5903
    eumUDegreeCelsiusPer100meter = 6000
    eumUDegreeCelsiusPer100feet = 6001
    eumUDegreeFahrenheitPer100meter = 6002
    eumUDegreeFahrenheitPer100feet = 6003
    eumUPascal = 6100
    eumUhectoPascal = 6101
    eumUkiloPascal = 6102
    eumUpsi = 6103
    eumUMegaPascal = 6104
    eumUMetresOfWater = 6105
    eumUFeetOfWater = 6106
    eumUBar = 6107
    eumUmilliBar = 6108
    eumUPSU = 6200
    eumUPSUM3PerSec = 6300
    eumUDegreeCelsiusM3PerSec = 6301
    eumUConcNonDimM3PerSec = 6302
    eumUPSUft3PerSec = 6303
    eumUDegreeFahrenheitFt3PerSec = 6304
    eumUm2PerSec2 = 6400
    eumUm2PerSec3 = 6401
    eumUft2PerSec3 = 6402
    eumUm2PerSec3PerRad = 6403
    eumUft2PerSec3PerRad = 6404
    eumUJoulePerKilogram = 6500
    eumUWattPerM2 = 6600
    eumUJouleKilogramPerKelvin = 6700
    eumUm3PerSec2 = 6800
    eumUft3PerSec2 = 6801
    eumUAcreFeetPerDayPerSecond = 6802
    eumUMillionGalUKPerDayPerSecond = 6803
    eumUMillionGalPerDayPerSecond = 6804
    eumUGalPerMinutePerSecond = 6805
    eumUCubicMeterPerDayPerSecond = 6806
    eumUCubicMeterPerHourPerSecond = 6807
    eumUMillionLiterPerDayPerSecond = 6808
    eumULiterPerMinutePerSecond = 6809
    eumULiterPerSecondSquare = 6810
    eumUm3Pergram = 6900
    eumULiterPergram = 6901
    eumUm3PerMilligram = 6902
    eumUm3PerMicrogram = 6903
    eumUNewton = 7000
    eumUm2PerHertz = 7100
    eumUm2PerHertzPerDegree = 7101
    eumUm2PerHertzPerRadian = 7102
    eumUft2PerHertz = 7103
    eumUft2PerHertzPerDegree = 7104
    eumUft2PerHertzPerRadian = 7105
    eumUm2PerHertz2 = 7200
    eumUm2PerHertz2PerDegree = 7201
    eumUm2PerHertz2PerRadian = 7202
    eumUKilogramPerS2 = 8100
    eumUm2Perkilogram = 9100
    eumUPerMeterPerSecond = 9200
    eumUMeterPerSecondPerHectar = 9201
    eumUFeetPerSecondPerAcre = 9202
    eumUPerSquareMeter = 9300
    eumUPerAcre = 9301
    eumUPerHectar = 9302
    eumUPerCubicMeter = 9350
    eumUCurrencyPerCubicMeter = 9351
    eumUCurrencyPerCubicFeet = 9352
    eumUSquareMeterPerSecond = 9400
    eumUSquareFeetPerSecond = 9401
    eumUPerWatt = 9600
    eumUNewtonMeter = 9700
    eumUNewtonMeterSecond = 9800
    eumUNewtonPerMeterPerSecond = 9900
    eumUOnePerOne = 99000
    eumUPerCent = 99001
    eumUPerThousand = 99002
    eumUHoursPerDay = 99003
    eumUPerson = 99004
    eumUGramPerGram = 99005
    eumUGramPerKilogram = 99006
    eumUMilligramPerGram = 99007
    eumUMilligramPerKilogram = 99008
    eumUMicrogramPerGram = 99009
    eumUKilogramPerKilogram = 99010
    eumUM3PerM3 = 99011
    eumULiterPerM3 = 99012
    eumUintCode = 99013
    eumUMeterPerMeter = 99014
    eumUperminute = 99015
    eumUpermonth = 99016
    eumUperyear = 99017
    eumUampere = 99100
    eumUMilliAmpere = 99101
    eumUWattPerMeter = 99200
    eumUkiloWattPerMeter = 99201
    eumUmegaWattPerMeter = 99202
    eumUgigaWattPerMeter = 99203
    eumUkiloWattPerFeet = 99204