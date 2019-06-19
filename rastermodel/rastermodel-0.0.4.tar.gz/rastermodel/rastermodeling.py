"""
Functionalities related to modeling on rasters
"""

###### Library used in this script
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.cm as cm
#import matplotlib.colors as colors
#import seaborn as sns
import rasterio
import subprocess
import pandas as pd
import os, glob
from rasterio import plot
import geopandas as gpd
import georasters as gr
import gdal
import rasterio
import descartes
import pysal as ps
from cartopy import crs as ccrs
from pyproj import Proj
from osgeo import osr
#from shapely.geometry import Point
#from collections import OrderedDict
#import webcolors
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
#debugusing pdb
import pdb
from sklearn.ensemble import RandomForestRegressor
from sklearn import svm
from sklearn.neural_network import MLPRegressor
from itertools import repeat

def rasterPredict(mod,rast_in,dtype_val=None,out_filename=None,out_dir=None):
    
    out_filename = os.path.join(out_dir,out_filename)
    
    ## Check for type:
    if(type(rast_in)==list):
        src_RP1 = rasterio.open(rast_in[0])
        src_RP =  list(map(lambda x: rasterio.open(x) , rast_in))
        n_layers = len(src_RP)
    else:
        src_RP1 = rasterio.open(rast_in)
        n_layers = 1
        
    #Add multiband support:
    if(src_RP1.count >1):
        n_layers= src_RP1.count
           
    ## Option  to set the dtype from the predicted val??     
    ## Check if file exists first, still a problem here
    
    exists = os.path.isfile(out_filename)
    
    if exists:
        print("File already exists, removing file")
        os.remove(out_filename)
        
        out_profile = src_RP1.profile.copy()
        
        if dtype_val!= None:
            nodata_val = rasterio.dtypes.dtype_ranges[dtype_val][0] #take min val of range

            out_profile['dtype']=dtype_val
            out_profile['nodata']=nodata_val
            
        dst = rasterio.open(out_filename, 
                        'w', 
                        **out_profile)        
    else:
        print("creating file")
        out_profile = src_RP1.profile.copy()
        if dtype_val!= None:
            nodata_val = rasterio.dtypes.dtype_ranges[dtype_val][0] #take min val of range

            out_profile['dtype']=dtype_val
            out_profile['nodata']=nodata_val
        dst = rasterio.open(out_filename, 
                        'w', 
                        **out_profile)
        

    for block_index, window in src_RP1.block_windows(1):
        RP1_block = src_RP1.read(window=window, masked=True)

        if(n_layers>1):
            RP_block =  list(map(lambda x,window: x.read(window=window, masked=True) , src_RP,repeat(window)))
            RP_block =  list(map(lambda x: x.ravel() , RP_block))            
            RP_block =  np.stack(RP_block, axis=1)
        else:
            RP_block = RP1_block
            RP_block = RP_block.ravel() #only sample of the form (20,), missing feature
            RP_block = RP_block.reshape(-1,1)

        shape_block = RP1_block.shape #need with and heigt
        
        if dtype_val!= None:
            RP_block = RP_block.astype(dtype_val)

        result_block = mod.predict(RP_block) # Note this is a fit!
        result_block = result_block.reshape(shape_block)
        
        dst.write(result_block, window=window)
            
    src_RP1.close()
    out_close = list(map(lambda x: x.close(), src_RP))    
    dst.close()
        
    return(out_filename)


