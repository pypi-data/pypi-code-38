
import pandas as pd 
import urllib.request
#from ..classes import TemporalNetwork 
#from .. import __path__ as tenetopath
import os 
import numpy as np
from teneto import TemporalNetwork
from teneto import __path__ as tenetopath
import pickle 

def fetch_dataset(dataset, unit, multiplehits='ignore', spath='default', hdf5=True, hdf5path='./opsahl-socialnetwork.h5'):
    r"""
    Downloads a temporal network dataset

    Parameters
    ----------
    dataset : str
        options: \'opsahl-socialnetwork\'[ds-1]_
    unit : str
        What temporal unit is to be returned. Can be days, hours, seconds, minutes. 
    multiplehits : str
        default is ignore. Can also be \'add\'. When changing the temporal scale, there can 
        be multiple connections that occur. If this is set to \'add\', a weighted network is returned
        where the weights are the number of connections. If \'ignore\' then a binary network
        is returned where the edge means the presense or absence of at least one edge during that time. 
    spath : str 
        string where to save data. If \'default\' data is saved within the teneto directory. 
    
    References
    ----------

    .. [ds-1] Opsahl, T., Panzarasa, P., 2009. Clustering in weighted networks. Social Networks 31 (2), 155-163. [`Link <http://doi.org/10.1016/j.socnet.2009.02.002>`_]
    """   

    availabledatasets = ['opsahl-socialnetwork']
    if dataset not in availabledatasets: 
        raise ValueError('Unknown dataset. Available datasets are: ' + ','.join(availabledatasets))

    if dataset == 'opsahl-socialnetwork': 
        df, starttime = _fetch_opsahl_socialnetwork(unit)

    # If matrix is going to be binary, drop the weight
    if multiplehits != 'add': 
        df = df.drop('weight', axis=1)
        nettype = 'bd'
        extraweighttxt = 'ignored.'
    else: 
        nettype = 'wd'
        extraweighttxt = 'added as weights.'

    if spath == 'default': 
        spath = tenetopath[0] + '/data/datasets/' + dataset + '/'
        extradesctxt = ',' + unit
    else: 
        extradesctxt = ',' + unit + ' , spath=' + spath 

    if not os.path.exists(spath): 
        os.makedirs(spath)

    desc = 'The dataset contains time-stamps from a college social network messanging service from 2004. \
    People are nodes. Edges represent a message being sent. \
    Time-stampes represent time from the first message. \
    Self edges contain time when users joined the service. \
    Time-resolution is in ' + unit + '. If there were multiple edges these are ' + extraweighttxt + '. \n\n\
    More information and dataset source at https://toreopsahl.com/datasets/#online_social_network. \
    Dataset created by Tore Opsahl.\n\n\
    If using data in publication, please cite: Opsahl, T., Panzarasa, P., 2009. \
    Clustering in weighted networks. Social Networks 31 (2), 155-163, \
    doi: 10.1016/j.socnet.2009.02.002 if used in a publicated.\n\n\
    The data has been parsed into a teneto network and is stored in: ' + spath + '\n\n\
    The data can be loaded again by calling: teneto.dataset.load(\'' + dataset + '\'' + extradesctxt + ')'
    
    tnet = TemporalNetwork(from_df=df, nettype=nettype, timeunit=unit, starttime=starttime, desc=desc, diagonal=True, hdf5=True, hdf5path='./opsahl-socialnetwork.h5')
    if spath: 
        print('---Saving---')
        tnet.save_aspickle(spath + dataset + '_' + unit)
    print(tnet.desc)
    return tnet

def load_dataset(dataset, unit='days', spath='default'): 
    r"""
    Loads a downloaded dataset

    Parameters
    ----------
    dataset : str
        options: \'opsahl-socialnetwork\'
    unit : str
        What temporal unit is to be returned. Can be days, hours, seconds, minutes. 
    spath : str 
        string where to save data. If \'default\' data is saved within the teneto directory. 
    """   

    if spath == 'default': 
        spath = tenetopath[0] + '/data/datasets/' + dataset + '/'

    if not os.path.exists(spath + '/' + dataset + '_' + unit + '.pkl'): 
        print('Dataset not found. Call teneto.datasets.fetch_dataset(' + dataset + ')') 
    else: 
        with open(spath + '/' + dataset + '_' + unit + '.pkl','rb') as f:
            tnet = pickle.load(f) 
        return tnet

def _fetch_opsahl_socialnetwork(unit):
    print('---Downloading---')
    response = urllib.request.urlopen('http://opsahl.co.uk/tnet/datasets/OCnodeslinks.txt')
    html = response.read()
    print('---Parsing---')
    html = html.decode('utf-8')
    html = html.split('\n')
    cols = [[' '.join(row.split(' ')[:2])[1:-1]] + row.split(' ')[2:-1] for row in html[:-1]]

    df = pd.DataFrame(cols, columns=['t','i','j'])
    starttime = df['t'].min()
    df['t'] = pd.to_datetime(df['t'])
    df['t'] = df['t'] - df['t'].min()
    if unit == 'days': 
        df['t'] = df['t'].dt.days
    if unit == 'seconds': 
        df['t'] = df['t'].dt.seconds + (df['t'].dt.days * (24*60*60))
    if unit == 'minutes': 
        df['t'] = np.floor(df['t'].dt.seconds/60) + (df['t'].dt.days * (24*60))
    if unit == 'hours': 
        df['t'] = np.floor(df['t'].dt.seconds/60/60) + (df['t'].dt.days * (24))

    # Find dupliate entires 
    df = df.groupby(['i','j','t']).size().reset_index()
    df.columns = ['i', 'j', 't', 'weight']    
    df.sort_values('t', inplace=True)
    df.reset_index(inplace=True, drop=True)
    df['i'] = df['i'].astype('int')
    df['j'] = df['j'].astype('int')
    df['t'] = df['t'].astype('int')
    return df, starttime