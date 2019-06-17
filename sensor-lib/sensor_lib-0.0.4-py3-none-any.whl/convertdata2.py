# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 22:20:12 2019

@author: andi-
"""
import numpy as np 
import matplotlib.pyplot as plt
import csv

#with open("E:/xethru_baseband_iq_20190208_132418.dat", "rb") as f:
with open("xethru_datafloat_20190614_141837.dat", "rb") as f:
    #dt=np.dt    ype([np.uint32, np.unint32, ])

    data = np.fromfile(f, dtype=np.float32)
    #matrix=1j*np.ones([len(data)//363-1, 180])
    
    
    for i in range(0, len(data)//363-1):
        temp=data[3*(i+1)+360*i:3*(i+1)+360*(i+1)]
        iqdata=[]
        for j in range(0, 180):
            if(temp[j+180]>0):
                iqdata.append(str(round(temp[j], 4))+"+"+str(round(temp[j+180], 4))+"j")
            else:
                iqdata.append(str(round(temp[j], 4))+str(round(temp[j+180], 4))+"j")
                
        with open ('nohex.csv', 'a', newline="") as csvFile:
            writer=csv.writer(csvFile)
            writer.writerow(iqdata)
       # iqdata=np.array(temp[0:180])+1j*np.array(temp[180:360])
    
        #matrix[i,:]=iqdata
        
#    x=5.25/100*np.arange(180)
#    i=500
#    plt.plot(x, np.abs(matrix[i,:]))
#    #First peak at range bin 4
#    #Second peak at range bin 12
#    plt.plot(x[8], np.abs(matrix[i,8]), '*')
#    plt.show()
    f.close()
    csvFile.close()
    
#np.savetxt("Nothing5.csv", matrix, fmt='%.4f', delimiter=',')


'''
What this code does:
    Takes a read-only binary file and stores the data into an array called 'data' as float values. The array is sliced and the sliced array appends its elements to a array called iqdata.
    Opens a csv file and writes all te iqdata elements into this csv file row by row.
'''
