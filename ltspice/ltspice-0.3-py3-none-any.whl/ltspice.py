import os
import struct
import numpy as np
import itertools
import re
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt

class Ltspice:
    filepath = ''
    dsamp = 1
    tags = ['Title:', 'Date:', 'Plotname:', 'Flags:', 'No. Variables:', 'No. Points:' ]
    time_raw = []
    data_raw = []
    time_split_point = []

    title=''
    date=''
    plotname=''
    flags=''

    v_number = 0 # Num of variable(s)
    p_number = 0 # Num of all time point(s)
    c_number = 0 # Num of simulation case(s)

    v_list = [] # Variable name list
    t_list = [] # Variable type list

    def __init__(self, filepath):
        self.filepath = filepath
        self.time_raw = []
        self.data_raw = []
        self.time_split_point = []
        self.v_list = []
        self.t_list = []
    
    def parse(self, dsamp=1, dataframe=False):
        self.__init__(self.filepath)
        self.dsamp = dsamp
        size = os.path.getsize(self.filepath)
        fo = open(self.filepath,'rb')
        tmp = b''
        lines = []
        line = ''
        data = fo.read() # Binary data read
        fo.close()
        i=0

        while 'Binary' not in line:
            tmp = tmp + bytes([data[i]])
            if(bytes([data[i]]) == b'\n'):
                i = i+1
                tmp = tmp + bytes([data[i]])
                line = str(tmp, encoding='UTF16')
                lines.append(line)
                tmp = b''
            i = i+1

        vindex = 0
        for index,l in enumerate(lines):
            if(self.tags[0] in l):
                self.title = l[len(self.tags[0]):]
            if(self.tags[1] in l):
                self.date = l[len(self.tags[1]):]
            if(self.tags[2] in l):
                self.plotname = l[len(self.tags[2]):]
            if(self.tags[3] in l):
                self.flags = l[len(self.tags[3]):]
            if(self.tags[4] in l):
                self.v_number = int(l[len(self.tags[4]):])
            if(self.tags[5] in l):
                self.p_number = int(l[len(self.tags[5]):])
            if('Variables:' in l):
                vindex = index

        for j in range(self.v_number):
            vdata = lines[vindex+j+1].split()
            self.v_list.append(vdata[1])
            self.t_list.append(vdata[2])

        self.data_raw = struct.unpack(str(self.p_number*(self.v_number+1))+'f', data[i:size])

        self.time_raw = [None]*self.p_number
        for i in range(self.p_number):
            self.time_raw[i] = struct.unpack('d', struct.pack('f',self.data_raw[i*(self.v_number+1)]) + struct.pack('f',self.data_raw[1+i*(self.v_number+1)]))
        
        self.time_raw = np.array(self.time_raw).flatten()

        self.c_number = 1
        self.time_split_point.append(0)
        for i in tqdm(range(self.p_number-1)):
            if(self.time_raw[i] > self.time_raw[i+1] and self.time_raw[i+1]==0):
                self.c_number = self.c_number+1
                self.time_split_point.append(i+1) 
        self.time_split_point.append(self.p_number)

        self.data_raw = np.reshape(np.array(self.data_raw), (self.p_number, (self.v_number+1)))
        
        if(dataframe == True):
            self.dataFrame()

    def dataFrame(self):
        time_df_list = []
        data_df_list = []
        case_df_list = []
        var_df_list  = []

        for i in tqdm(range(self.v_number)):
            if i == 0:
                pass
            else:
                v_name = self.v_list[i]
                for j in range(self.c_number):
                    time_df = self.getTime(j)
                    time_df_list += time_df.tolist()
                    data_df_list += (self.getData(v_name, j).tolist())
                    case_df_list += ((j*np.ones(len(time_df)).astype(int)).tolist())
                    var_df_list  += ([v_name]*len(time_df))           
        
        self.df = pd.DataFrame.from_dict(
            {
                'Variable Name': var_df_list,
                'Case': case_df_list,
                'Time': time_df_list,
                'Data': data_df_list
            }
        )
        pass

    def plotData(self, v_names, case = 0):
        if(isinstance(v_names, str)):
            # One string variable is given => plot a variable with time in a case
            fig, axes = plt.subplots(nrows=1, ncols=1)
            d = self.getData(v_names, case)
            t = self.getTime(case)
        elif(isinstance(v_names, list)):
            # List of string variables are given 
            pass
        else:
            print("Unknown type of variable names are given. Please check the parameters")
        pass
    
    def getData(self, v_name, case=0):
        if(',' in v_name):
            v_names = re.split(',|\(|\)',v_name)
            return self.getData('V('+v_names[1]+')', case) - self.getData('V('+v_names[2]+')', case)
        else:
            v_num = 0
            for index,vl in enumerate(self.v_list):
                if(v_name.lower()== vl.lower()):
                    v_num = index+1
            if(v_num == 0):
                return None
            else:
                return self.data_raw[self.time_split_point[case]:self.time_split_point[case+1], v_num]

    def getTime(self, case=0):
        return np.abs(self.time_raw[self.time_split_point[case]:self.time_split_point[case+1]])

    def getVariableNames(self, case=0):
        return self.v_list

    def getVariableTypes(self, case=0):
        return self.t_list

    def getCaseNumber(self):
        return self.c_number

    def getVariableNumber(self):
        return self.v_number

    def plotInteractive(self):
        
        pass
