#================================================================
#IMPORT STATEMENTS
#================================================================

import cartopy.crs as ccrs
import csv
from netCDF4 import Dataset
import datetime as dt
import numpy as np
from matplotlib import colors
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches




color_theme = ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999']



#================================================================
#CALCULATIONS
#================================================================


#Scientific Notation
def sn(x,y):
    return x * 10 **y

#Inverse
def inv(x):
    return 1/x

#================================================================
#DATA IMPORTING
#================================================================

#Import from csv file
def csv_import(fname,delimiter=' '):
    csv_data = []
    with open(fname) as csv_file:
        reader = csv.reader(csv_file,delimiter=delimiter)
        for row in reader:
            csv_data.append(row)
    return csv_data

#================================================================
#NETCDF
#================================================================


#Display the keys, longnames (if available) and units (if available) of a netcdf file.
#Also show the dimensions of the file
def nc_explore(file,retrieve=False,show_all=True):
    if show_all:
        keys = []
        lnames= []
        units = []
        for key in file.variables.keys():
            keys.append(key)
            try:
                name = file.variables[key].long_name
            except:
                name = '--'

            try:
                unit = file.variables[key].units
            except:
                unit = '--'
            lnames.append(name)
            units.append(unit)
        kjust = len(max(keys,key=len))+1
        njust = len(max(lnames,key=len))+1
        ujust = len(max(units,key=len))+1
        string = ''
        str2 = ''
        for i in range(kjust+njust+ujust+4):
            string+='='
            str2+='~'
        print(string)
        print('|'+'KEY'.center(kjust)+'|'+'LONG NAME'.center(njust)+'|'+'UNITS'.center(ujust)+'|')
        print(string)
        for i in range(len(keys)):
            if i%5==0:
                if i !=0:
                    print(str2)
            print('|'+keys[i].ljust(kjust)+'|'+lnames[i].ljust(njust)+'|'+units[i].ljust(ujust)+'|')
        print(string)
    dims = []
    lengths = []
    for dim in file.dimensions.keys():
        dims.append(dim)
        try:
            length = len(file.variables[dim][:])
        except:
            length = '--'
        lengths.append(length)

    str2 = ''
    str3 = ''
    for i in range(len(max(dims,key=len))+len(max(dims,key=len))+5):
        str2+='-'
        str3+='='
    print(str3)
    print('|SHAPE OF DATA'.ljust(len(max(dims,key=len))+len(max(dims,key=len))+4)+'|')
    for i in range(len(dims)):
        if i%3==0:
            print(str2)
        print('|'+str(dims[i]).ljust(len(max(dims,key=len))+1) + ':   '+str(lengths[i]).ljust(len(max(dims,key=len))-2)+'|')
    print(str3)

#Import the values of a netcdf file's dimension
def nc_dim(file,key):
    data = file.variables[key][:]
    return data


#Import the values of a netcdf file variable that is not a dimension
def nc_val(file,key):
    data = file.variables[key]
    return data


#Write data to a netcdf file
def write_netCDF(filename,var_kwrd,var_units,var_lname,var_vals,mode='w',lons='',lats='',levels='',fmat='NETCDF4_CLASSIC',source=''):
    dataset = Dataset(filename,mode,format=fmat)
    if lons == '':
        print('please include latitudes, longitudes, and levels, if applicable')
    else:
        #Create the dimensions of the file
        dataset.source = source
        level_dim = dataset.createDimension('level',np.shape(levels)[0])
        lon_dim = dataset.createDimension('longitude',np.shape(lons)[0])
        lat_dim = dataset.createDimension('latitude',np.shape(lats)[0])
        time_dim = dataset.createDimension('time')

        #Create the coordinate variables of the file
        level = dataset.createVariable('pressure', np.int32, ('level',))
        longitude = dataset.createVariable('longitude', np.float32,('longitude',)) 
        latitude = dataset.createVariable('latitude', np.float32,('latitude',))
        time = dataset.createVariable('time', np.float64, ('time',))

        latitude.long_name = 'Latitude'
        longitude.long_name = 'Longitude'
        level.long_name = 'Pressure Level'
        time.long_name = 'Time'

        latitude.units = 'degree_north'
        longitude.units = 'degree_east'
        level.units = 'hPa'
        time.units = 'hours since 1900-01-01 00:00:00.0'

        longitude[:] = lons
        latitude[:] = lats
        level[:] = levels    
        for i in range(len(var_kwrd)):
            print(var_lname[i])
            #3D Surface/TOA Variable
            if len(np.shape(var_vals[i])) == 3:
                variable = dataset.createVariable(var_kwrd[i], np.float32,\
                                            ('time','latitude','longitude'))
                variable.units = var_units[i]
                variable.long_name = var_lname[i]
                variable[:] = var_vals[i]
            #4D Variable
            else:

                variable = dataset.createVariable(var_kwrd[i], np.float32,\
                                                ('time','level','latitude','longitude'))
                variable.units = var_units[i]
                variable.long_name = var_lname[i]
                variable[:] = var_vals[i]
            del variable
        
    dataset.close()
#================================================================
#GRID CONSIDERATIONS
#================================================================

#Find the index in an array for the argument closest to the given value
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

#find the index of the values closest to the specified values in an array
def indices(lats,lons,lat1,lat2,lon1,lon2):
    i2 = find_nearest(lats,lat1)
    i1 = find_nearest(lats,lat2)
    j1 = find_nearest(lons,lon1)
    j2 = find_nearest(lons,lon2)
    return i1,i2,j1,j2

#Simple printour of longitudes and latitudes
def print_latlon(lon,lat,wt,ht,i=''):
    print('==================================')
    if i !='':
        print('|Region ' + str(i+1)+ ': ')
    print('|Longitude       ' + str(lon) + ' : ' + str(lon+wt))
    print('|Latitude        ' + str(lat) + ' : ' + str(lat+ht))


#================================================================
#FIELD MANIPULATIONS
#================================================================

#Average a field along the two horizontal dimensions
def region_avg(field):
    return np.nanmean(field,axis=(-1,-2))

#Compute the sounding of a field by averaging over the latitude and longitude dimensions
def sounding(field):
    shape = len(np.shape(field))
    if shape == 4:
        return np.nanmean(field,axis=(2,3))
    elif shape == 3:
        return np.nanmean(field,axis=(1,2))
    else:
        print('Incorrect Format')

#Isolate the data in a rectangular (lat-lon) region from a netcdf field
def isolate_region(field,lons,lats,lon1,lon2,lat1,lat2,latlon=True):
    i1,i2,j1,j2 = indices(lats,lons,lat1,lat2,lon1,lon2)
    
    #Depending on the dimensions of the data, isolate the lat/lon region of
    #interest, preserving data along other axes (e.g. height, time)
    if len(np.shape(field)) == 4:
        region_field = field[:,:,i1:i2+1,j1:j2+1]
    elif len(np.shape(field)) == 3:
        region_field = field[:,i1:i2+1,j1:j2+1]
    else:
        region_field = field[i1:i2+1,j1:j2+1]

    #Updated latitude and longitudes based on the user-input    
    new_lats = lats[i1:i2+1]
    new_lons = lons[j1:j2+1]
    print_latlon(new_lons[0],new_lats[0],new_lons[-1]-new_lons[0],new_lats[-1]-new_lats[0])
    if latlon:
        return region_field, new_lons,new_lats
    else:
        return region_field

#Convert a temperature field to potential temperature given pressure levels
def potential_temp(temps,plevels,p_0=1000,OK_4D=False):
    #Dim: Time, Level, lat/lon
    #Convert a 4D temperature field(1 Time, 3 spatial) into potential temperature
    if len(np.shape(temps)) == 4:
        if OK_4D:
            all_ptemps = []
            for temp in temps:
                cp = 1005.7
                R = 287.058
                factor = (p_0/plevels)**(R/cp)
                ptemps = np.zeros(np.shape(temp))
                for i in range(len(plevels)):
                    factor = (p_0/plevels[i])**(R/cp)
                    ptemps[i,:,:] = factor*temp[i,:,:]
                all_ptemps.append(ptemps)
            return np.array(all_ptemps)
            print('Conversion Complete.')
        else:
            print('Length to large: Only attempt for 3D Fields or small 4D Fields')
            print('For override, enter \"OK_4D = True\"')
    #Dim: Level, lat/lon
    elif len(np.shape(temps)) == 3:
    #Convert a 3D temperature field to a potential temperature field
        cp = 1005.7
        R = 287.058
        factor = (p_0/plevels)**(R/cp)
        ptemps = np.zeros(np.shape(temps))
        for i in range(len(plevels)):
            factor = (p_0/plevels[i])**(R/cp)
            ptemps[i,:,:] = factor*temps[i,:,:]
        return np.array(ptemps)
        print('Conversion Complete.')
    #Dim Level
    #Convert a temperature sounding to a potential temperature sounding
    elif len(np.shape(temps)) == 1:
        cp = 1005.7
        R = 287.058
        temps = np.array(temps)
        plevels = np.array(plevels)
        theta = temps*(p_0/plevels)**(R/cp)
        return theta
        print('Conversion Complete.')


#================================================================
#PLOTTING
#================================================================

#Sample autocorrelation plot of a timeseries, only showing values 'to the right' of the midpoint. Includes lag-1 value.
def auto_corrrelation_plot(timeseries):
    corr = np.correlate(timeseries,timeseries,'same')
    midpt = np.size(corr)//2
    corr_positive = corr[midpt:]/corr[midpt]
    fig, ax = plot(corr_positive)
    ax.scatter(1,corr_positive[1],color=color_theme[0])
    ax.annotate('Lag-1 = ' + str(round(corr_positive[1],3)),xy=(1,corr_positive[1]),xytext=(15,corr_positive[1]-0.025))
    return corr_positive[1]

#Normalizes midpoint based on a given value
class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

#Basic plot. If one input array, plots as the y value. If two input arrays, the first is x, the second is y.
def plot(x,y='',colors=color_theme,xlabel = '',ylabel = '',title ='',labels='',legendloc='upper right'\
         ,xmin='',xmax='',ymin='',ymax='',xscale='linear',yscale='linear',\
        xticks = '',yticks = '',save = ''):
    fig, ax = plt.subplots()
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    i = 0
    if y == '':
        t = np.arange(0,len(x),1)
        y = x
        x = t
    if np.shape(x)!=np.shape(y):
        if np.shape(y)[0]>np.shape(colors)[0]:
            for yi in y:
                ax.plot(x,yi)
                i+=1
        else:
            for yi in y:
                ax.plot(x,yi,color=colors[i])
                i+=1            
    else:
        ax.plot(x,y,color=colors[i])
    if xmin !='':
        ax.set_xlim(xmin,xmax)
    if ymin !='':
        ax.set_ylim(ymin,ymax)
    if xticks!='':
        ax.set_xticks(xticks)
    if yticks!='':
        ax.set_yticks(yticks)
    if labels !='':
        ax.legend(labels,loc=legendloc)
    if save !='':
        plt.savefig(save,bbox_inches='tight')
    return fig, ax

#Generate a continuous sequence of datetime objects, convenient for plotting
#timeseries over a specified period
import datetime as dt
def plot_datetimes(start_yr,stop_yr):
    #Months ranging from  1 - 12
    months = np.arange(1,13,1)
    
    #Years ranging from start_yr to stop_yr
    years = np.arange(start_yr,stop_yr+1,1)
    
    
    plot_dts = np.array([])
    for year in years:
        for month in months:
            date = dt.datetime(year,month,1)
            plot_dts = np.append(plot_dts,date)
    return plot_dts

#Find the nearest coordinate in an array to a specified value
def reconcile_coord(spatial_array,point):
    idx = find_nearest(spatial_array,point)
    new_point = spatial_array[idx]
    return new_point

#Visualize 'rectangular' (lat/lon) regions on a map 
#based on given latitude and longitude bounds
def region_map(lon0,lat0,wt,ht,lons='',lats='',center=180,colors=color_theme,save=''):
    if type(lon0) in [float,int]:
        lon0 = [lon0]
        lat0 = [lat0]
        wt = [wt]
        ht = [ht]
    #Reshape all spatial quantaties as numpy arrays
    lon0 = np.array(lon0)
    lat0 = np.array(lat0)
    wt = np.array(wt)
    ht = np.array(ht)
    lon1 = lon0 + wt
    lat1 = lat0 + ht
    
    
    
    #Generate cartopy projection with coastlines and gridlines
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=center))
    ax.coastlines()
    ax.set_global()
    ax.gridlines()
    
    
    
    #Print out user-input coordinates
    print('==================================')
    print('|Input Coordinates')
    for i in range(len(lon0)):
        print_latlon(lon0[i],lat0[i],wt[i],ht[i],i)
    print('==================================')
    
    #Convert the user-input lat/lon into the closest values
    #found in the lons/lats arrays included
    #E.g. x=30S -> x=29.75
    if lons !='':
        new_lon0 = np.array([])
        new_lat0 = np.array([])
        new_lon1 = np.array([])
        new_lat1 = np.array([])
        for i in range(len(lon0)):
            new_lon0 = np.append(new_lon0,reconcile_coord(lons,lon0[i]))
            new_lat0 = np.append(new_lat0,reconcile_coord(lats,lat0[i]))
            new_lon1 = np.append(new_lon1,reconcile_coord(lons,lon1[i]))
            new_lat1 = np.append(new_lat1,reconcile_coord(lats,lat1[i]))
        lon0 = new_lon0
        lon1 = new_lon1
        lat0 = new_lat0
        lat1 = new_lat1
        wt = new_lon1-new_lon0
        ht = new_lat1-new_lat0
        
        
        print('|Updated Coordinates')
        for i in range(len(lon0)):
            print_latlon(lon0[i],lat0[i],wt[i],ht[i],i)
        print('==================================')
        wt = lon1-lon0
        ht = lat1-lat0
    for i in range(len(lon0)):
        ax.add_patch(patches.Rectangle(xy=(lon0[i],lat0[i]),width=wt[i],height=ht[i]\
                           ,fill=True,transform=ccrs.PlateCarree()\
                          ,linewidth =1,color=colors[i],alpha=0.35))
    if save != '':
        plt.savefig(save,bbox_inches='tight')

#Sample plot of a sounding with log-y scaling
def sounding_plot(pressure,field,color=color_theme[1],label=''):
    fig, ax = plt.subplots()
    ax.plot(field,pressure,label=label,color=color)
    ax.set_yscale('log')
    ax.get_yaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
    ax.axis([min(field),max(field),1000,1])
    ax.set_yticks([1000,100,10,1])
    ax.set_ylabel('Pressure (hPa)')
    if label != '':
        ax.legend()
    return fig, ax

#================================================================
#SYNTHETIC DATA
#================================================================


#Generate a red noise time series of length n
def red_noise(alpha,n,syntax=False):
    if syntax:
        print('red_noise(alpha,n)')
    else:
        beta = np.sqrt(1-alpha*alpha)
        x = np.zeros(n)
        x[0] = beta*np.random.randn()
        for i in np.arange(1,n):
            x[i] = alpha*x[i-1] + beta*np.random.randn()
        return x

#Generate a red noise time series of length n with underlying sinusoidal oscillations
def RN_oscillation(alpha,n,freqs,mags=1,periods=0,rads=False):
    x = red_noise(alpha,n)
    t = np.arange(0,n)
    waves = np.zeros(n)
    if mags == 1:
        mags = np.ones(n)
    if periods == 0:
        periods = np.zeros(n)
    elif rads == False:
        periods = np.radians(periods)
    for i in range(len(freqs)):
        freq = freqs[i]
        period = periods[i]
        mag = mags[i]
        wave = mag*np.sin(freq*t + period)
        waves = waves+wave
    x = x + waves
    return x-np.mean(x)


#================================================================
#TRENDS
#================================================================


#Wrapper to compute various best fit lines
def best_fit(x_values,y_values, mode='ordinary',delta=''):
    if mode == 'ordinary':
        return ordinary_least_squares(x_values,y_values)
    if mode == 'orthogonal':
        return deming_least_squares(x_values,y_values,delta=1)
    if mode == 'deming':
        if delta == '':
            print('Ratio of variances calculated from sample variances' )
        return deming_least_squares(x_values,y_values,delta = np.var(y_values)/np.var(x_values))


#Ordinary lest squares regression
def ordinary_least_squares(x_values,y_values):
    x_mean = np.mean(x_values)
    y_mean = np.mean(y_values)
    x_deviations = np.array([x-x_mean for x in x_values])
    y_deviations = np.array([y-y_mean for y in y_values])
    xy_deviations = x_deviations*y_deviations
    xy_dev_mean = np.mean(xy_deviations)
    xy_mean = x_mean*y_mean+xy_dev_mean
    x_dev_squared = [x**2 for x in x_deviations]
    x_square_mean = x_mean**2 + np.mean(x_dev_squared)
    a1 = (xy_mean-x_mean*y_mean)/(x_square_mean-x_mean**2)
    a0 = y_mean-a1*x_mean
    return (a0,a1)

#Deming least squares regression minizing error in both x and y. For standardized data, reduces to an orthogonal least squares regression.
def deming_least_squares(x_values,y_values,delta):
    n = len(x_values)
    x_mean = np.mean(x_values)
    y_mean = np.mean(y_values)
    x_deviations = np.array([x-x_mean for x in x_values])
    y_deviations = np.array([y-y_mean for y in y_values])
    s_xx = np.sum(x_deviations**2)/(n-1)
    s_yy = np.sum(y_deviations**2)/(n-1)
    s_xy = np.sum(x_deviations*y_deviations)/(n-1)  
    b1 = (s_yy-delta*s_xx+np.sqrt((s_yy-delta*s_xx)*(s_yy-delta*s_xx)+4*delta*s_xy*s_xy))/(2*s_xy)
    b0 = y_mean - b1*x_mean
    return (b0,b1)

#Remove the best fit trend from a timeseries. Defaults to ordinary least squares
def remove_trend(timeseries,mode='ordinary'):
    x = np.arange(0,len(timeseries),1)
    a0, a1 = mf.best_fit(x,timeseries,mode)
    trend_adjusted = timeseries - (a0+a1*x)
    return np.array(trend_adjusted)

#================================================================
#STATISTICS
#================================================================

#Subtract the mean from a timeseries
def anomaly(timeseries,i1=0,i2=''):
    if i2 == '':
        mean = np.mean(timeseries[i1:])
    else:
        mean = np.mean(timeseries[i1:i2])
    return timeseries - mean

#Standardize a dataset by subtracting the mean and dividing by the SD
def standardize(data):
    data = np.array(data)
    mean = np.mean(data)
    std = np.std(data)
    return (data-mean)/std











