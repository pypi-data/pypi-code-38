import math
import random
import parmap
import itertools
from itertools import repeat
from scipy.spatial import distance
import operator
from tqdm import tqdm
from functools import reduce
from sklearn import mixture
import statsmodels.stats.multitest as multi
import networkx as nx
import multiprocessing as mp
import numpy as np
from scipy.stats import poisson
import pandas as pd
import pygco as pygco # cut_from_graph # pip install git+git://github.com/amueller/gco_python
import scipy.stats.mstats as ms
from itertools import repeat
from scipy.stats import norm
from scipy.stats import binom
from scipy.stats import skewnorm
from scipy.sparse import issparse
import matplotlib as mpl
import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.path as mplPath
import shapely.geometry
import shapely.ops
from scipy.spatial import Voronoi, voronoi_plot_2d, Delaunay, KDTree, ConvexHull
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection, PatchCollection
from PIL import Image
from matplotlib.backends.backend_pdf import PdfPages
import sklearn.manifold as manifold
import sklearn.decomposition as decomposition 
from sklearn.preprocessing import StandardScaler
from scipy.stats import gaussian_kde
from sklearn.cluster import DBSCAN,KMeans
from scipy.stats import ttest_ind
from sklearn.utils import shuffle
import hdbscan
import seaborn as sns
import sklearn.cluster as cluster
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from scipy import stats
import sys
import os
import time
from scipy.stats import skewnorm
from scipy import stats
from ast import literal_eval



def read_spatial_expression(file,sep='\s+',num_exp_genes=0.01, num_exp_spots=0.01, min_expression=1):
    
    '''
    Read raw data and returns pandas data frame of spatial gene express
    and numpy ndarray for single cell location coordinates; 
    Meanwhile processing raw data.
    
    :param file: csv file for spatial gene expression; 
    :rtype: coord (spatial coordinates) shape (n, 2); data: shape (n, m); 
    '''
    counts = pd.read_csv(file, sep=sep, index_col = 0)
    print('raw data dim: {}'.format(counts.shape))

    num_spots = len(counts.index)
    num_genes = len(counts.columns)
    min_genes_spot_exp = round((counts != 0).sum(axis=1).quantile(num_exp_genes))
#     print("Number of expressed genes a spot must have to be kept " \
#     "({}% of total expressed genes) {}".format(num_exp_genes, min_genes_spot_exp))
    counts = counts[(counts != 0).sum(axis=1) >= min_genes_spot_exp]
#     print("Dropped {} spots".format(num_spots - len(counts.index)))
          
    # Spots are columns and genes are rows
    counts = counts.transpose()
  
    # Remove noisy genes
    min_features_gene = round(len(counts.columns) * num_exp_spots) 
#     print("Removing genes that are expressed in less than {} " \
#     "spots with a count of at least {}".format(min_features_gene, min_expression))
    counts = counts[(counts >= min_expression).sum(axis=1) >= min_features_gene]
#     print("Dropped {} genes".format(num_genes - len(counts.index)))
    
    data=counts.transpose()
    temp = [val.split('x') for val in data.index.values]
    coord = np.array([[float(a[0]), float(a[1])] for a in temp])
    
    return coord,data




def write_result_to_csv(df,fileName):

    '''
    For convenience, user should output and save scGCO result dataframe with this function.
    Meanwhile, output result with scGCO can be resued and readed across platforms 
            with **read_result_to_dataframe()** function.
     More detail can see **read_result_to_dataframe()**.
    '''
    df_=df.copy()
    df_.nodes=df.nodes.apply(conver_list)
    df_.to_csv(fileName)

def read_result_to_dataframe(fileName,sep=','):
    
    '''
    Read and use scGCO output file cross-platform .
    More detail can see **write_result_to_csv()**.
    '''
    converters={"p_value":converter,"nodes":converter}
    df=pd.read_csv(fileName,converters=converters,index_col=0,sep=sep)
    df.nodes=df.nodes.apply(conver_array)
    return df

def conver_list(x):
    return [list(xx) for xx in x ]

def conver_array(x):
    return [np.array(xx) for xx in x] 

def converter(x):
    #define format of datetime
    return literal_eval(x)

 





def normalize_count_cellranger(data):
    '''
    normalize count as in cellranger
    
    :param file: data: A dataframe of shape (m, n);
    :rtype: data shape (m, n);
    '''
    normalizing_factor = np.sum(data, axis = 1)/np.median(np.sum(data, axis = 1))
    data = pd.DataFrame(data.values/normalizing_factor[:,np.newaxis], columns=data.columns, index=data.index)
    return data

def get_gene_high_dispersion(data, n_bins=20, z_cutoff=1.7, min_mean=0.0125, max_mean=3, min_disp=0.5):
    '''
    identify genes with high dispersion as in cellranger
    
    :param file: data (m,n); n_bins=20; z_cutoff=1.7; min_mean=0.0125; max_mean=3; min_disp=0.5.
    :rtype: ndarray (k, ); only index of genes with significant variations are returned
    '''
    mean = np.mean(data, axis=0)
    var = np.var(data, axis=0)
    mean[mean == 0] = 1e-12
    dispersion = var/mean
    temp = np.vstack((np.log1p(mean), np.log(dispersion))).T
    vmd = pd.DataFrame(temp, index=data.columns, columns=['mean', 'disp'])
    
    vmd['bins'] = pd.cut(vmd['mean'], bins=n_bins)
    disp_binned = vmd.groupby('bins')['disp']
    disp_binned_mean = disp_binned.mean()
    disp_binned_std = disp_binned.std()
    disp_binned_mean = disp_binned_mean[vmd['bins']].values
    disp_binned_std = disp_binned_std[vmd['bins']].values
    vmd['disp_norm'] = (vmd['disp'].values - disp_binned_mean) / disp_binned_std
    good_std = ~np.isnan(disp_binned_std)    
    
    mean_sel = np.logical_and(vmd['mean'] > min_mean, vmd['mean'] < max_mean)
    disp_sel = np.logical_and(vmd['disp'] > min_disp, vmd['disp_norm'] > z_cutoff)
    sel_1 = np.logical_and(mean_sel, disp_sel)
    sel = np.logical_and(sel_1, good_std)    

    return np.argwhere(sel).flatten()

def log1p(data):
    '''
    log transform normalized count data
    
    :param file: data (m, n); 
    :rtype: data (m, n);
    '''
    if not issparse(data):
        return np.log1p(data)
    else:
        return data.log1p()

def rotate(origin, point, angle):
    """
    Rotate a point around another points (origin).
    
    :param file: coordiantes of points; angle in radians 
    :rtype: spatial coordinates; 

    """
    ox, oy = origin
    px, py = point

    dx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    dy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return dx, dy


def estimate_smooth_factor(locs, data_norm, start_sf = 10, fdr_cutoff = 0.01, unary_scale_factor=100, 
                      label_cost=10, algorithm='expansion',iterations=None):
    '''
    main function to estimate smooth factor for graph cut
    :param file:locs: spatial coordinates (n, 2); data_norm: normalized gene expression;
        unary_scale_factor=100; label_cost=10; algorithm='expansion' 
    :rtype: factor_df: a dataframe; optim_factor: a scalar, best smooth factor.
    '''       
#    compute_spatial_genomewise_fixed_SF(locs, data_norm, smooth_factor=30, 
#                      unary_scale_factor=100, label_cost=10, algorithm='expansion')
    smooth_factor = start_sf
    iteration=0
    fp = data_norm.shape[0]

    if data_norm.shape[1]>1000:
        fp_cutoff = data_norm.shape[1]/1000
    else:
        fp_cutoff = data_norm.shape[1]/100
        
    num_cores = mp.cpu_count()
    if num_cores > math.floor(data_norm.shape[1]/2):
         num_cores=int(math.floor(data_norm.shape[1]/2))
    ttt = np.array_split(data_norm,num_cores,axis=1)
    while fp > fp_cutoff and fp>10:
        smooth_factor = smooth_factor + 5
        tuples = [(l, d, u, s, c, a) for l, d, u, s, c, a in zip(repeat(locs, num_cores), ttt,                    
                                    repeat(smooth_factor, num_cores),
                                    repeat(unary_scale_factor, num_cores), 
                                    repeat(label_cost, num_cores),
                                    repeat(algorithm, num_cores))] 
                                    
        results = parmap.starmap(compute_spatial_genomewise_fixed_SF, 
                             tuples, pm_processes=num_cores, pm_pbar=True)
#    pool.close()
        ggg = [results[i][0] for i in np.arange(len(results))]
        genes=reduce(operator.add, ggg)    
        ppp = [results[i][1] for i in np.arange(len(results))]
        p_values=reduce(operator.add, ppp)
#    subnet_num = [results[i][2] for i in np.arange(len(results))]
#    nums = reduce(operator.add, subnet_num)
        fdr = multi.multipletests(np.array(p_values), method='fdr_bh')[1]
        fp =  fdr[fdr < fdr_cutoff].shape[0]
        iteration +=1
        print('========iteration{}'.format(iteration))
        print(smooth_factor, fp)
        if iterations !=None:
            if iteration>=iterations:
                break
#    data_array = np.array((genes, p_values, fdr)).T
#    factor_df = pd.DataFrame(data_array[:, 1:], index=data_array[:,0], columns=('p_value', 'fdr'))
#    df_sel = df[df.fdr < 0.0001]
#    factor_df = factor_df.astype('float')

    return smooth_factor




def compute_spatial_genomewise_fixed_SF(locs, data_norm, smooth_factor=10, 
                      unary_scale_factor=100, label_cost=10, algorithm='expansion'):
    '''
    identify spatial genes on genome-scale.
    
    :param points: locs: shape (n, 2) ; data_norm: shape (n, m);  
                unary_scale_factor=100; label_cost=10; algorithm='expansion'.
    :rtype: p_values: list, genes: list, smooth_factors: list, pred_labels: list. 
    
    '''    
    num_sig = 0
#    size_factor=200
    genes = list()
    p_values = list()
#    diff_p_values = list() # add gene expression p values
#    exp_diff = list() # add gene expression diff
#    smooth_factors = list()
#    pred_labels = list()
    unary_scale_factor=unary_scale_factor
    smooth_factor=smooth_factor
    label_cost=label_cost
    algorithm=algorithm
#    alpha_list = compute_alpha_shape(locs)
    data_norm=data_norm
    exp =  data_norm.iloc[:,1]
    exp=(log1p(exp)).values
    cellGraph = create_graph_with_weight(locs, exp)
    seg_count = np.array([1, 2 ,3, 4, 5, 6, 7, 8, 9])
    for i in np.arange(data_norm.shape[1]):
        exp =  data_norm.iloc[:,i]
        if len(np.where(exp > 0)[0]) >= 10:
#            print(data_norm.columns[i])
            exp=(log1p(exp)).values
            newLabels, gmm = cut_graph_general(cellGraph, exp, unary_scale_factor, 
                                               smooth_factor, label_cost, algorithm)
#            t_com, seg_size, com_components = count_component(cellGraph, newLabels, locs)
            p, node, com = compute_p_CSR(locs,newLabels, gmm, exp, cellGraph)
            if len(p) > 0:
#                    diff_p, e_diff = calc_spatial_differential_expression(p, node, exp, cellGraph)
#                    diff_p_values.append(diff_p)
#                    exp_diff.append(e_diff)
                    p_values.append(min(p))
                    genes.append(data_norm.columns[i])
 #                   smooth_factors.append(smooth_factor)
 #                   pred_labels.append(newLabels)

 
    return genes, p_values

def create_graph_with_weight(points, normCount):
    '''
    Returns a graph created from cell coordiantes.
    edge weights set by normalized counts.
    
    :param points: shape (n,2); normCount: shape (n)
    :rtype: ndarray shape (n ,3)
    
    '''
    edges = {}   
    var = normCount.var()
    delauny = Delaunay(points)
#    cellGraph = np.zeros((delauny.simplices.shape[0]*delauny.simplices.shape[1], 4))
    cellGraph = np.zeros((points.shape[0]*10, 4))

    for simplex in delauny.simplices:
        simplex.sort()
        edge0 = str(simplex[0]) + " " + str(simplex[1])
        edge1 = str(simplex[0]) + " " + str(simplex[2])
        edge2 = str(simplex[1]) + " " + str(simplex[2])
        edges[edge0] = 1
        edges[edge1] = 1
        edges[edge2] = 1
        
    i = 0
    for kk in edges.keys():  
        node0 = int(kk.split(sep=" ")[0])
        node1 = int(kk.split(sep=" ")[1])
        edgeDiff = normCount[node0] - normCount[node1]
        energy = np.exp((0 - edgeDiff**2)/(2*var))
        dist = distance.euclidean(points[node0,:], points[node1,:])
        cellGraph[i] = [node0, node1, energy, dist]       
        i = i + 1
    
    tempGraph = cellGraph[0:i]
    n_components_range = range(1,5)
    best_component = 1
    lowest_bic=np.infty
    temp_data = tempGraph[:,3].reshape(-1,1)
    for n_components in n_components_range:
        gmm = mixture.GaussianMixture(n_components = n_components)
        gmm.fit(temp_data)
        gmm_bic = gmm.bic(temp_data)
        if gmm_bic < lowest_bic:
            best_gmm = gmm
            lowest_bic = gmm_bic
            best_component = n_components  
    
    mIndex = np.where(best_gmm.weights_ == max(best_gmm.weights_))[0]
    cutoff = best_gmm.means_[mIndex] + 2*np.sqrt(best_gmm.covariances_[mIndex])

    for simplex in delauny.simplices:
        simplex.sort()          
        dist0 = distance.euclidean(points[simplex[0],:], points[simplex[1],:])
        dist1 = distance.euclidean(points[simplex[0],:], points[simplex[2],:])
        dist2 = distance.euclidean(points[simplex[1],:], points[simplex[2],:])
        tempArray = np.array((dist0, dist1, dist2))
        badIndex = np.where(tempArray == max(tempArray))[0][0]
        if tempArray[badIndex] > cutoff:
            edge0 = str(simplex[0]) + " " + str(simplex[1])  
            edge1 = str(simplex[0]) + " " + str(simplex[2])       
            edge2 = str(simplex[1]) + " " + str(simplex[2])
            edgeCount = 0
            if edge0 in edges and edge1 in edges and edge2 in edges:
                if badIndex == 0:
                    del edges[edge0]
                elif badIndex == 1:
                    del edges[edge1]
                elif badIndex == 2:
                    del edges[edge2]     

    i = 0
    for kk in edges.keys():  
        node0 = int(kk.split(sep=" ")[0])
        node1 = int(kk.split(sep=" ")[1])
        edgeDiff = normCount[node0] - normCount[node1]
        energy = np.exp((0 - edgeDiff**2)/(2*var))
        dist = distance.euclidean(points[node0,:], points[node1,:])
        cellGraph[i] = [node0, node1, energy, dist]       
        i = i + 1   
      
    tempGraph = cellGraph[0:i]
    temp_data = tempGraph[:,3].reshape(-1,1)    
    gmm = mixture.GaussianMixture(n_components = 1)
    gmm.fit(temp_data)    
    cutoff = gmm.means_[0] + 2*np.sqrt(gmm.covariances_[0])
    finalGraph = tempGraph.copy()
    j=0
    for i in np.arange(tempGraph.shape[0]):    
        if tempGraph[i, 3] < cutoff:
            finalGraph[j] = tempGraph[i]
            j = j + 1
         
    return finalGraph




def cut_graph_general(cellGraph, count, unary_scale_factor=100, 
                      smooth_factor=50, label_cost=10, algorithm='expansion'):
    '''
    Returns new labels and gmm for the cut.
    
    :param points: cellGraph (n,3); count: shape (n,); 
    :unary_scale_factor, scalar; smooth_factor, scalar; 
    :label_cost: scalar; algorithm='expansion'
    :rtype: label shape (n,); gmm object.
    '''
    a = count.copy()
    a = a[a > 0]
    gmm = find_mixture(a)
    smooth_factor = smooth_factor
    unary_scale_factor = unary_scale_factor
    label_cost = label_cost
    algorithm = algorithm
    unary_cost = compute_unary_cost_simple(count, gmm, unary_scale_factor)
    
    pairwise_cost = compute_pairwise_cost(gmm.means_.shape[0], smooth_factor)
    edges = cellGraph[:,0:2].astype(np.int32)
    labels = pygco.cut_from_graph(edges, unary_cost, pairwise_cost, label_cost)
#    energy = compute_energy(unary_cost, pairwise_cost, edges, labels)

    return labels, gmm 

def find_mixture(data):
    '''
    estimate expression clusters
    
    :param file: data (n,); 
    :rtype: gmm object;
    '''

    #n_components_range = range(2,5)
    best_component = 2
    lowest_bic=np.infty
    temp_data = data.reshape(-1,1)

    if len(temp_data)<=2:
        gmm = mixture.GaussianMixture(n_components = 2)
        gmm.fit(temp_data)
        best_gmm=gmm
    else:
        if len(temp_data)<5 and len(temp_data)>2:
            n_components_range=range(2,len(temp_data))

        else:
             n_components_range = range(2,5)

        for n_components in n_components_range:
            gmm = mixture.GaussianMixture(n_components = n_components)
            gmm.fit(temp_data)
            gmm_bic = gmm.bic(temp_data)
            if gmm_bic < lowest_bic:
                best_gmm = gmm
                lowest_bic = gmm_bic
                best_component = n_components      

    return best_gmm
# np.percentile(s, 10)

def find_mixture_2(data):
    '''
    estimate expression clusters, use k=2
    
    :param file: data (n,); 
    :rtype: gmm object;
    '''
    gmm = mixture.GaussianMixture(n_components = 2)
    gmm.fit(data.reshape(-1,1))

    return gmm

def TSNE_gmm(data):
    n_components_range = range(2,10)
    best_component = 2
    lowest_bic=np.infty
    temp_data = data
    for n_components in n_components_range:
        gmm = mixture.GaussianMixture(n_components = n_components)
        gmm.fit(temp_data)
        gmm_bic = gmm.bic(temp_data)
        if gmm_bic < lowest_bic:
            best_gmm = gmm
            lowest_bic = gmm_bic
            best_component = n_components     
    return best_gmm


def compute_unary_cost_simple(count, gmm, scale_factor):
    '''
    Returns unary cost energy.
    
    :param points: count: shape (n,); gmm: gmm object; scale_factor: scalar

    :rtype: unary energy matrix.
    '''    
    labels_pred = gmm.predict(count.reshape(-1,1))
    temp_means = np.sort(gmm.means_, axis=None)
    new_index = np.where(gmm.means_ == temp_means)[1]
    temp_covs = gmm.covariances_.copy()
    for i in np.arange(new_index.shape[0]):
        temp_covs[i] = gmm.covariances_[new_index[i]]
    new_labels = np.zeros(labels_pred.shape[0], dtype=np.int32)
    for i in np.arange(new_index.shape[0]):
        temp_index = np.where(labels_pred == i)[0]
        new_labels[temp_index] = new_index[i]

    mid_points = np.zeros(len(new_index) - 1)
    for i in np.arange(len(mid_points)):
        mid_points[i] = (temp_means[i]*np.sqrt(temp_covs[i+1]) + 
                     temp_means[i+1]*np.sqrt(temp_covs[i])
                    )/(np.sqrt(temp_covs[i]) + np.sqrt(temp_covs[i+1]))
    temp = count[:, np.newaxis] - temp_means.T[1:]
    neg_indices = np.apply_along_axis(first_neg_index, 1, temp)
    ind_count_arr = np.vstack((neg_indices, count)).T        
    return (scale_factor*np.apply_along_axis(calc_u_cost, 1, 
                                    ind_count_arr, mid_points)).astype(np.int32)


def compute_pairwise_cost(size, smooth_factor):
    '''
    Returns pairwise energy.
    
    :param points: size: scalar; smooth_factor: scalar

    :rtype: pairwise energy matrix.
    '''
    pairwise_size = size
    pairwise = -smooth_factor * np.eye(pairwise_size, dtype=np.int32)
    step_weight = -smooth_factor*np.arange(pairwise_size)[::-1]
    for i in range(pairwise_size): 
        pairwise[i,:] += np.roll(step_weight,i) 
    temp = np.triu(pairwise).T + np.triu(pairwise)
    np.fill_diagonal(temp, np.diag(temp)/2)
    return temp


def compute_p_CSR(locs,newLabels, gmm, exp, cellGraph): 
    '''
    Returns p_value of the cut.
    
    :param points: newLabels: shape (n,); gmm: gmm object
                   exp: ndarray shape (n ,3); cellGraph: shape (n,3)

    :rtype: p_value.
    '''
    com_factor = 9
    p_values = list()
    node_lists = list()
    gmm_pred = gmm.predict(exp.reshape(-1,1))
    unique, counts = np.unique(gmm_pred,return_counts=True)
    t_com, seg_size, con_components = count_component(locs,cellGraph, newLabels)

    for j in np.arange(len(con_components)):
        node_list = con_components[j]
        com_size = len(node_list)
        if com_size >= com_factor:
            gmm_pred_com = gmm.predict(exp[np.array(list(node_list))].reshape(-1,1))
            unique_com, counts_com = np.unique(gmm_pred_com, return_counts=True)
            major_label = unique_com[np.where(counts_com == counts_com.max())[0][0]]
            label_count = counts[np.where(unique == major_label)[0]]
            count_in_com =  counts_com.max()
            
            prob = poisson.sf(count_in_com, com_size*(label_count/exp.shape[0]))[0]

            p1 = poisson.pmf(count_in_com, com_size*(label_count/exp.shape[0]))[0]
 #           print(prob, count_in_com, com_size, com_size*(label_count/exp.shape[0]))
            p = prob + p1
            p_values.append(p)
            node_lists.append(np.array(list(node_list)))
    return p_values, node_lists, con_components


def count_component(locs, cellGraph, newLabels):
    '''
    Returns number of subgraphs.
    
    :param points: cellGraph: shape (n,3); newLabels: ndarray shape (n,); locs: shape (n, 2) 

    :rtype: scalar. 
    
    '''
    
    G=nx.Graph()
    tempGraph = cellGraph.copy()
    tempGraph = np.apply_along_axis(remove_egdes, 1, tempGraph, newLabels)
    G.add_edges_from(tempGraph[np.where(tempGraph[:,2] == 1)[0],0:2].astype(np.int32))
    com = sorted(nx.connected_components(G), 
                                  key = len, reverse=True)   
    sum_nodes = 0
    seg_size = np.zeros(9)
    for cc in com:
        sum_nodes = sum_nodes + len(cc)
        if len(cc) == 2:
            seg_size[1] = seg_size[1] + 1
        elif len(cc) == 3:
            seg_size[2] = seg_size[2] + 1   
        elif len(cc) == 4:
            seg_size[3] = seg_size[3] + 1  
        elif len(cc) == 5:
            seg_size[4] = seg_size[4] + 1      
        elif len(cc) == 6:
            seg_size[5] = seg_size[5] + 1  
        elif len(cc) == 7:
            seg_size[6] = seg_size[6] + 1  
        elif len(cc) == 8:
            seg_size[7] = seg_size[7] + 1  
        elif len(cc) == 9:
            seg_size[8] = seg_size[8] + 1              
#    t_com = len(com) + locs.shape[0] - sum_nodes 
    t_com = locs.shape[0] - sum_nodes 
    seg_size[0] = t_com
    return len(com) + t_com, seg_size, com


def remove_egdes(edges, newLabels):
    '''
    Mark boundary of the cut.
    
    :param points: edges: shape (n,); newLabels: shape(k,)

    :rtype: marked edges.
    '''
    if newLabels[int(edges[0])] != newLabels[int(edges[1])]:
        edges[2] = 0
    else:
        edges[2] = 1
    return edges


def calc_spatial_differential_expression(p, node, exp, cellGraph):
    '''
    Returns the expression difference p value and fold change between adjcent segments.
    
    :param points: p: shape (m,); node: shape (k,); exp: shape (n,); cellGraph: shape (n,3); 

    :rtype: two scalar. 
    
    '''
    minp = np.argmin(p)
    min_node = node[minp]
    min_node_edge_index0 = np.where(np.isin(cellGraph[:,0], min_node))[0]
    min_node_link0 = np.unique(cellGraph[min_node_edge_index0, 1])

    min_node_edge_index1 = np.where(np.isin(cellGraph[:,1], min_node))[0]
    min_node_link1 = np.unique(cellGraph[min_node_edge_index1, 0])

    min_p_link = np.setdiff1d(np.unique(np.concatenate([min_node_link0, min_node_link1])), min_node)

    best_match = 0
    best_diff = 0
    best_node = node[np.argmax(p)]
    for nn in node:
        m_size = np.intersect1d(nn, min_p_link).shape[0]
        temp_exp_diff = abs(np.mean(exp[min_node]) - np.mean(exp[nn]))
#        print(m_size, temp_exp_diff)
        if m_size > 0 and temp_exp_diff > best_diff:
            best_match = m_size
            best_diff = temp_exp_diff
            best_node = nn    
    t, p = ttest_ind((exp[min_node]), (exp[best_node]))
    exp_diff = np.mean(exp[min_node]) - np.mean(exp[best_node])
    return p, exp_diff



def identify_spatial_genes(locs, data_norm, smooth_factor=30, fdr_cutoff=0.01,
                           unary_scale_factor=100, label_cost=10, algorithm='expansion'):
#    pool = mp.Pool()
    '''
    main function to identify spatially variable genes
    :param file:locs: spatial coordinates (n, 2); data_norm: normalized gene expression;
        smooth_factor=10; unary_scale_factor=100; label_cost=10; algorithm='expansion' 
    :rtype: prediction: a dataframe
    '''    
    
    num_cores = mp.cpu_count()
    if num_cores > math.floor(data_norm.shape[1]/2):
         num_cores=int(math.floor(data_norm.shape[1]/2))
    ttt = np.array_split(data_norm,num_cores,axis=1)
    tuples = [(l, d, u, s, c, a) for l, d, u, s, c, a in zip(repeat(locs, num_cores), ttt,
                                    repeat(smooth_factor, num_cores),
                                    repeat(unary_scale_factor, num_cores), 
                                    repeat(label_cost, num_cores),
                                    repeat(algorithm, num_cores))] 
                                    
    results = parmap.starmap(compute_spatial_genomewise, tuples,
                             pm_processes=num_cores, pm_pbar=True)
#    pool.close()
# p_values, genes, diff_p_values, exp_diff, smooth_factors, pred_labels
    nnn = [results[i][0] for i in np.arange(len(results))]
    nodes = reduce(operator.add, nnn)
    ppp = [results[i][1] for i in np.arange(len(results))]
    p_values=reduce(operator.add, ppp)
    ggg = [results[i][2] for i in np.arange(len(results))]
    genes = reduce(operator.add, ggg)
    exp_ppp = [results[i][3] for i in np.arange(len(results))]
    exp_pvalues = reduce(operator.add, exp_ppp)  
    exp_ddd = [results[i][4] for i in np.arange(len(results))]
    exp_diffs = reduce(operator.add, exp_ddd)      
    fff = [results[i][5] for i in np.arange(len(results))]
    s_factors = reduce(operator.add, fff)
    lll = [results[i][6] for i in np.arange(len(results))]
    pred_labels = reduce(operator.add, lll)

    best_p_values=[min(i) for i in p_values]
    fdr = multi.multipletests(np.array(best_p_values), method='fdr_bh')[1]
    exp_fdr = multi.multipletests(np.array(exp_pvalues), method='fdr_bh')[1]    
    
    labels_array = np.array(pred_labels).reshape(len(genes), pred_labels[0].shape[0])
    data_array = np.array((genes, p_values, fdr, exp_pvalues, exp_fdr, exp_diffs, s_factors, nodes), dtype=object).T
    t_array = np.hstack((data_array, labels_array))
    c_labels = ['p_value', 'fdr', 'exp_p_value', 'exp_fdr', 'exp_diff', 'smooth_factor', 'nodes']
    for i in np.arange(labels_array.shape[1]) + 1:
        temp_label = 'label_cell_' + str(i)
        c_labels.append(temp_label)
    result_df = pd.DataFrame(t_array[:,1:], index=t_array[:,0], 
                      columns=c_labels)
    
    #optimize boundary
    opt_df = result_df[result_df.fdr < fdr_cutoff*2].sort_values(by=['fdr'])
    if opt_df.shape[0] <= num_cores*10:
        nodes, p_values, genes, exp_pvalues, exp_diffs, s_factors, pred_labels = optimize_boundary(locs, data_norm, opt_df,smooth_factor,unary_scale_factor,label_cost,algorithm)
    else:
        ttt = np.array_split(opt_df,num_cores,axis=0)
        tuples = [(l, d, t, s, u, c, a) for l, d, t, s, u, c, a in zip(repeat(locs, num_cores),
                                    repeat(data_norm, num_cores),
                                    ttt,
                                    repeat(smooth_factor, num_cores),
                                    repeat(unary_scale_factor, num_cores), 
                                    repeat(label_cost, num_cores),
                                    repeat(algorithm, num_cores))]
                                    
        results = parmap.starmap(optimize_boundary, tuples,
                                pm_processes=num_cores, pm_pbar=True)
    #    pool.close()
    # p_values, genes, diff_p_values, exp_diff, smooth_factors, pred_labels
        nnn = [results[i][0] for i in np.arange(len(results))]
        nodes = reduce(operator.add, nnn)
        ppp = [results[i][1] for i in np.arange(len(results))]
        p_values=reduce(operator.add, ppp)
        ggg = [results[i][2] for i in np.arange(len(results))]
        genes = reduce(operator.add, ggg)
        exp_ppp = [results[i][3] for i in np.arange(len(results))]
        exp_pvalues = reduce(operator.add, exp_ppp)  
        exp_ddd = [results[i][4] for i in np.arange(len(results))]
        exp_diffs = reduce(operator.add, exp_ddd)      
        fff = [results[i][5] for i in np.arange(len(results))]
        s_factors = reduce(operator.add, fff)
        lll = [results[i][6] for i in np.arange(len(results))]
        pred_labels = reduce(operator.add, lll)

    best_p_values=[min(i) for i in p_values]
    if len(best_p_values)>=1:
        fdr = multi.multipletests(np.array(best_p_values), method='fdr_bh')[1]
        exp_fdr = multi.multipletests(np.array(exp_pvalues), method='fdr_bh')[1]    

        labels_array = np.array(pred_labels).reshape(len(genes), pred_labels[0].shape[0])
        data_array = np.array((genes, p_values, fdr, exp_pvalues, exp_fdr, exp_diffs, s_factors, nodes), dtype=object).T
        t_array = np.hstack((data_array, labels_array))
        c_labels = ['p_value', 'fdr', 'exp_p_value', 'exp_fdr', 'exp_diff', 'smooth_factor', 'nodes']
        for i in np.arange(labels_array.shape[1]) + 1:
            temp_label = 'label_cell_' + str(i)
            c_labels.append(temp_label)
        opt_df = pd.DataFrame(t_array[:,1:], index=t_array[:,0], 
                            columns=c_labels)

        for geneID in opt_df.index:
            result_df.loc[geneID] = opt_df.loc[geneID]
        best_p_values=[min(i) for i in result_df['p_value']]
        fdr = multi.multipletests(np.array(best_p_values), method='fdr_bh')[1]
        exp_fdr = multi.multipletests(np.array(result_df['exp_p_value']), method='fdr_bh')[1]
        result_df['fdr'] = fdr
        result_df['exp_fdr'] = exp_fdr
    return result_df


def compute_spatial_genomewise(locs, data_norm, smooth_factor=30, 
                      unary_scale_factor=100, label_cost=10, algorithm='expansion'):
    '''
    identify spatial genes on genome-scale.
    
    :param points: locs: shape (n, 2) ; data_norm: shape (n, m);  
                unary_scale_factor=100; label_cost=10; algorithm='expansion'.
    :rtype: p_values: list, genes: list, smooth_factors: list, pred_labels: list. 
    
    '''    
    seg_cutoff = 1
    num_sig = 0
#    size_factor=200
    genes = list()
    nodes = list()
    p_values = list()
    diff_p_values = list() # add gene expression p values
    exp_diff = list() # add gene expression diff
    smooth_factors = list()
    pred_labels = list()
    unary_scale_factor=unary_scale_factor
    smooth_factor=smooth_factor
    final_factor = smooth_factor
    label_cost=label_cost
    algorithm=algorithm
#    alpha_list = compute_alpha_shape(locs)
    data_norm=data_norm
    exp =  data_norm.iloc[:,1]
    exp=(log1p(exp)).values
    cellGraph = create_graph_with_weight(locs, exp)
#    seg_count = np.array([1, 2 ,3, 4, 5, 6, 7, 8, 9])
    count_gmm = 0
    for i in np.arange(data_norm.shape[1]):
        exp =  data_norm.iloc[:,i]
        if len(np.where(exp > 0)[0]) >= 10:
            temp_factor = smooth_factor #int(smooth_factor/2)
            exp=(log1p(exp)).values
            newLabels, gmm = cut_graph_general(cellGraph, exp, unary_scale_factor, 
                                               temp_factor, label_cost, algorithm)
            t_com, seg_size, com_components = count_component(locs,cellGraph, newLabels)
            p, node, com = compute_p_CSR(locs,newLabels, gmm, exp, cellGraph)
            final_factor = temp_factor
#            if float(abs(max(gmm.means_) - min(gmm.means_))) >= 1 and t_com == 1:
#                temp_factor = max(10, smooth_factor - 20)
#                while temp_factor < smooth_factor: 
#                    newLabels, gmm = cut_graph_general(cellGraph, exp, unary_scale_factor, 
#                                               temp_factor, label_cost, algorithm)
#                    t_com, seg_size, com_components = count_component(cellGraph, newLabels, locs)
#                    if t_com >= 2 and np.sum(seg_size) <= seg_cutoff:
#                        break
#                    else:
#                        temp_factor = temp_factor + 5
#                final_factor = temp_factor
#                p, node, com = compute_p_CSR(locs,newLabels, gmm, exp, cellGraph)

            if len(p) > 0:
                    diff_p, e_diff = calc_spatial_differential_expression(p, node, exp, cellGraph)
                    diff_p_values.append(diff_p)
                    exp_diff.append(e_diff)
                    p_values.append(p)
                    nodes.append(node)
                    genes.append(data_norm.columns[i])
                    smooth_factors.append(final_factor)
                    pred_labels.append(newLabels)
                    
    return nodes, p_values, genes, diff_p_values, exp_diff, smooth_factors, pred_labels


def optimize_boundary(locs, data_norm, opt_df,smooth_factor,
                           unary_scale_factor, label_cost, algorithm):
    seg_cutoff = 1
    genes = list()
    nodes = list()
    p_values = list()
    diff_p_values = list() # add gene expression p values
    exp_diff = list() # add gene expression diff
    smooth_factors = list()
    pred_labels = list()    
    exp =  data_norm.iloc[:,1]
    exp=(log1p(exp)).values
    cellGraph = create_graph_with_weight(locs, exp)
    for geneID in opt_df.index:
        exp =  data_norm.loc[:,geneID]
        exp=(log1p(exp)).values
        if opt_df.loc[geneID].smooth_factor == smooth_factor:
            temp_factor = max(10, smooth_factor - 20)
            while temp_factor < smooth_factor: 
                newLabels, gmm = cut_graph_general(cellGraph, exp, unary_scale_factor, 
                                               temp_factor, label_cost, algorithm)
                t_com, seg_size, com_components = count_component(locs, cellGraph, newLabels)
                if t_com >= 2 and np.sum(seg_size) <= seg_cutoff:
                    final_factor = temp_factor
                    p, node, com = compute_p_CSR(locs,newLabels, gmm, exp, cellGraph)  
                    diff_p, e_diff = calc_spatial_differential_expression(p, node, exp, cellGraph)
                    diff_p_values.append(diff_p)
                    exp_diff.append(e_diff)
                    p_values.append(p)
                    nodes.append(node)
                    genes.append(geneID)
                    smooth_factors.append(final_factor)
                    pred_labels.append(newLabels)
                    break
                else:
                    temp_factor = temp_factor + 5
    return nodes, p_values, genes, diff_p_values, exp_diff, smooth_factors, pred_labels


# create function to do graph cuts on profile

def generate_cluster_center_mat(locs, data_norm, fdr_opt, 
                             cluster_size = 5, perplexity = 30):

    '''
    Gene cluster
    '''

    tsne_proj = spatial_pca_tsne(data_norm, fdr_opt.index, perplexity = perplexity)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=cluster_size, gen_min_span_tree=True)
    clusterer.fit(tsne_proj) 
    labels = clusterer.fit_predict(tsne_proj)
    final_labels = labels
    final_tsne = np.c_[tsne_proj, final_labels]
    palette = sns.color_palette('deep', final_labels.max() + 1)
    colors = [palette[x] if x >= 0 else (0.0, 0.0, 0.0) for x in final_tsne[:,2].astype(int)]
    plt.scatter(final_tsne[:,0], final_tsne[:,1], c=colors, s=28)
    plt.xlabel('TSNE component 1')
    plt.ylabel('TSNE component 2')
    for i in final_labels:
        position = np.max(final_tsne[ final_tsne[:,2]== i], axis=0)
        plt.gcf().gca().text(position[0], position[1]-1,str(i), fontsize=12)
    plt.show()
    uniq, count = np.unique(labels, return_counts=True)
    if len(uniq) == 1:
        uniq = np.array([0])
        labels = np.zeros(len(labels))
        count = np.array([len(labels)])
    cluster_center_vec_list = list()
    exp =  data_norm.iloc[:,1]
    exp=(log1p(exp)).values
    cellGraph = create_graph_with_weight(locs, exp)    
    for uu in uniq[uniq >= 0]:
        gene_subset = fdr_opt.index[np.where(labels == uu)]
        X=log1p(data_norm.loc[:,gene_subset])
        kmeans=KMeans(n_clusters=2,random_state=0).fit(X)
        hmrf_labels = cut_graph_profile(cellGraph, kmeans.labels_, unary_scale_factor=100, 
                      smooth_factor=35)
        uniq, count = np.unique(hmrf_labels, return_counts = True)

        if np.max(count)/np.min(count) <=1.2:
            for uu in uniq:
                temp_label = uu
                temp_vec = np.zeros(hmrf_labels.shape[0])
                temp_vec[np.where(hmrf_labels == temp_label)[0]] = 1    
                cluster_center_vec_list.append(temp_vec)        
        else:
            temp_label = uniq[np.argmin(count)]
            temp_vec = np.zeros(hmrf_labels.shape[0])
            temp_vec[np.where(hmrf_labels == temp_label )[0]] = 1    
            cluster_center_vec_list.append(temp_vec)

    return np.array(cluster_center_vec_list)


def spatial_pca_tsne(data_norm, gene_lists, perplexity = 30):
    '''
    perform standard PCA + tsne
    :param file: data_norm: normalized gene expression; gene_lists: list shape(k,)
        perplexity = 30 
    :rtype: tsne_proj: shape (m, 2)
    '''           
    data_s = StandardScaler().fit_transform(data_norm.loc[:, gene_lists])  ## Input matrix (n_sample,n_feature)
    pca = decomposition.PCA()
    pca.fit(data_s.T)
    pca_proj = pca.fit_transform(data_s.T)
    num_comp = np.where(np.cumsum(pca.explained_variance_)/np.sum(pca.explained_variance_) 
                    > 0.9)[0][0]

#    RS=20180824
    tsne=manifold.TSNE(n_components=2, perplexity=perplexity)
    tsne_proj = tsne.fit_transform(pca_proj[:,0:num_comp])
    return tsne_proj


def cut_graph_profile(cellGraph, Kmean_labels, unary_scale_factor=100, 
                      smooth_factor=50, label_cost=10, algorithm='expansion'):
    '''
    Returns new labels and gmm for the cut.
    
    :param points: cellGraph (n,3); count: shape (n,); 
    :unary_scale_factor, scalar; smooth_factor, scalar; 
    :label_cost: scalar; algorithm='expansion'
    :rtype: label shape (n,); gmm object.
    '''

    smooth_factor = smooth_factor
    unary_scale_factor = unary_scale_factor
    label_cost = label_cost
    algorithm = algorithm
    uniq, count = np.unique(Kmean_labels, return_counts = True)  
    unary_cost = compute_unary_cost_profile(Kmean_labels, unary_scale_factor)
    pairwise_cost = compute_pairwise_cost(len(uniq), smooth_factor)
    edges = cellGraph[:,0:2].astype(np.int32)
    labels = pygco.cut_from_graph(edges, unary_cost, pairwise_cost, label_cost)
#    energy = compute_energy(unary_cost, pairwise_cost, edges, labels)

    return labels
                                          
def compute_unary_cost_profile(Kmean_labels, scale_factor):
    '''
    Returns unary cost energy.
    
    :param points: count: shape (n,); gmm: gmm object; scale_factor: scalar

    :rtype: unary energy matrix.
    '''    
    labels_pred = Kmean_labels
    uniq, count = np.unique(Kmean_labels, return_counts = True)    
    uninary_mat = np.zeros((len(labels_pred), len(uniq)))
    for i in np.arange(uninary_mat.shape[0]):
        for j in np.arange(len(uniq)):
            if uniq[j] == labels_pred[i]:
                uninary_mat[i, j] = -1
            else:
                uninary_mat[i, j] = 1   
    return (scale_factor*uninary_mat).astype(np.int32)

def count_neighbors(a, b, cellGraph):
    idx0 = np.in1d(cellGraph[:,0], a).nonzero()[0]
    idx1 = np.in1d(cellGraph[:,1], a).nonzero()[0]
    neighbor0 = cellGraph[idx0, 1]
    neighbor1 = cellGraph[idx1, 0]
    neighbors = set(neighbor0.tolist() + neighbor1.tolist())   
    return len(neighbors.intersection(set(b)))


def compute_overlap_new(u, v):
#    if len(np.where((u+v) == 2)[0]) == 0:
#        return len(np.where(abs(u-v) == 1)[0])
#    else:
        return len(np.where((u+v) == 2)[0])

def compute_inclusion_new(u, v):
#    if len(np.where((u+v) == 2)[0]) == 0:
#        return len(np.where(abs(u-v) == 1)[0])
#    else:
        return len(np.where((u+v) == 2)[0])/sum(v)

def compute_norm_hamming(u, v):
    return len(np.where((u-v) != 0)[0])/min(sum(u), sum(v))

def compute_diff_vs_common_new(u, v):
    return len(np.where((u+v) == 1)[0])/(2*len(np.where((u+v) == 2)[0]) + 10)

def first_neg_index(a):
    '''
    deprecated
    '''
    for i in np.arange(a.shape[0]):
        if a[i] < 0:
            return i
    return a.shape[0] - 1                

def calc_u_cost(a, mid_points):
    '''
    deprecated
    '''
    neg_index = int(a[0])
    x = a[1]
    m_arr = np.concatenate((0 - mid_points[0:neg_index+1], 
                            mid_points[neg_index:]), axis=0)
    x_arr = np.concatenate((np.repeat(x, neg_index+1), 
                0 - np.repeat(x, mid_points.shape[0] - neg_index)), axis=0)
    return m_arr+x_arr   

def powerset(seq):
    """
    Returns all the subsets of this set. This is a generator.
    """
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]]+item
            yield item


def identify_pattern_conserved_genes(locs, data_norm, fdr_opt, similarity_cutoff = 0.3,
                             cluster_size = 10, perplexity = 30):

    '''
    Based on genes cluster to compare conserved pattern
    '''
    
    seed_mat = generate_cluster_center_mat(locs, data_norm, fdr_opt, 
                             cluster_size = cluster_size, perplexity = perplexity)
    target_df, missed_gene = generate_target_shape_amtrix_for_hamming(data_norm, fdr_opt, fdr_opt.index)  ## always fdr01
    # now match eact target to seed, require all seed seg are matched
    sim_cutoff = similarity_cutoff
    hamming_df = computer_norm_hamming_to_tissue(seed_mat,target_df, fdr_opt)           
    target_passed_shape_filter = hamming_df[hamming_df.hamming < sim_cutoff].index
    return fdr_opt.loc[target_passed_shape_filter]



## cell cluster

def generate_cluster_tissue_mat(locs, data_norm, fdr_opt,
                             cluster_size = 5,sf = 10, perplexity = 30,fixed_k=None,
                             seg_min=8,seg_max=135):

    '''
    cell cluster for get tissue mat by automatically learning.
    you can set the parameters of 'fixed_k' to decide the number of cluster by leraning or manual setting.
    
    '''
    
    if fixed_k==None:    ## Not giving cluster number in advance; need learning
              
        cluster_kk=[]
        final_tsne_mat=list()
        for kk in range(5):
            tsne_proj = spatial_pca_tsne_cell(data_norm, fdr_opt.index, perplexity = perplexity)
            clusterer = hdbscan.HDBSCAN(min_cluster_size=cluster_size, gen_min_span_tree=True)
            clusterer.fit(tsne_proj) 
            labels = clusterer.fit_predict(tsne_proj)
            final_labels = labels    
            final_tsne_ = np.c_[tsne_proj, final_labels]
            final_tsne_mat.append(final_tsne_)
            uniq,count=np.unique(labels,return_counts=True)
            
            if len(uniq) == 1:
                uniq = np.array([0])
                labels = np.zeros(len(labels))
                count = np.array([len(labels)])
            cluster_k0=np.sum(uniq>=0)
            cluster_kk.append(cluster_k0)

        uniq,count=np.unique(cluster_kk,return_counts=True)
        #cluster_k=uniq[np.argmax(count)]   ## frequence max
        cluster_k=max(uniq)   ## cluster max
        #print(cluster_kk)
        #print('KMeans cluster size is {} by automatically learning'.format(cluster_k))

        #if do_plot:
        cluster_index=np.where(cluster_kk==cluster_k)[0][0]
        final_tsne=final_tsne_mat[cluster_index]

        palette = sns.color_palette('deep', final_tsne[:,2].astype(int).max() + 1)
        colors = [palette[x] if x >= 0 else (0.0, 0.0, 0.0) for x in final_tsne[:,2].astype(int)]
        plt.scatter(final_tsne[:,0], final_tsne[:,1], c=colors, s=28)
        plt.xlabel('TSNE component 1')
        plt.ylabel('TSNE component 2')
        for i in final_tsne[:,2]:
            position = np.max(final_tsne[ final_tsne[:,2]== i], axis=0)
            plt.gcf().gca().text(position[0], position[1]-1,str(i), fontsize=12)
        plt.show()
        
            
        bool_k=input("We have got KMeans cluster number is equal to {} by automatically learning , \n Do you use the number of cluster by learning?: Y/N :".format(cluster_k))
        if bool_k=='Y' or bool_k=='y':
            cluster_k=cluster_k
        elif bool_k=='N' or bool_k=='n':
            cluster_k=input('Please input your desired cluster number:')
        else:
            sys.exit("ERROR! Please input 'Y'/'y' or 'N'/'n' as warning message.")        
    
    else:    ## fixed_k !=None, user give a fixed_k 
        cluster_k=fixed_k
    
    exp =  data_norm.iloc[:,1]
    exp=(log1p(exp)).values
    cellGraph = create_graph_with_weight(locs, exp) 
    X=log1p(data_norm.loc[:,fdr_opt.index])
    
    print(cluster_k)
    cluster_k=int(cluster_k) 
    if cluster_k<2:
        sys.exit('ERROR! Please input more than two clsuter number for KMeans.')    
    else:
        tissue_mat_list= list()
        for n_cluster in np.arange(2,cluster_k+1):
            kmeans=KMeans(n_clusters=n_cluster,random_state=0).fit(X)
            hmrf_labels = cut_graph_profile(cellGraph, kmeans.labels_, unary_scale_factor=100,
                          smooth_factor=sf)
         #   print(hmrf_labels.shape)

            
#             colors=['green','purple','coral','cyan','yellow','blue','black','hotpink','lime','dimgrey']
#             plt.scatter(locs[:,0], locs[:,1], c=hmrf_labels,
#              cmap=matplotlib.colors.ListedColormap(colors) ,s=15)
#             plt.title('#Cluster{}'.format(n_cluster))
#             plt.show()
            uniq, count = np.unique(kmeans.labels_, return_counts = True)

            for tm_index in np.arange(len(uniq)):
                temp_vec=np.zeros(kmeans.labels_.shape[0])
                temp_vec[np.where(kmeans.labels_==uniq[tm_index])[0]]=1
                temp_vec_inv=abs(1-temp_vec)
                if max(sum(temp_vec_inv),sum(temp_vec))/min(sum(temp_vec_inv),sum(temp_vec))<1.2:
                    if np.sum(temp_vec_inv)>seg_min and np.sum(temp_vec_inv)<seg_max:
                        tissue_mat_list.append(temp_vec_inv)
                    if np.sum(temp_vec)>seg_min and np.sum(temp_vec)<seg_max:    ## control pattern size 
                        tissue_mat_list.append(temp_vec)
                else:
                    if sum(temp_vec_inv) > sum(temp_vec):
                        if np.sum(temp_vec)>seg_min and np.sum(temp_vec)<seg_max:    ## control pattern size 
                            tissue_mat_list.append(temp_vec)  
                    else:
                        if np.sum(temp_vec_inv)>seg_min and np.sum(temp_vec_inv)<seg_max:
                            tissue_mat_list.append(temp_vec_inv)  
    tissue_mat=np.array(tissue_mat_list)
    print(np.sum(tissue_mat,axis=1))
    return tissue_mat,cluster_k






def spatial_pca_tsne_cell(data_norm, gene_lists, perplexity = 30):  

    '''
    perform standard PCA + tsne for cell cluster to get tissue mat
    :param file: data_norm: normalized gene expression; gene_lists: list shape(k,)
        perplexity = 30 
    :rtype: tsne_proj: shape (m, 2)
    '''           
    data_s = StandardScaler().fit_transform(data_norm.loc[:, gene_lists])   ## (n_sample,n_feature)
    pca = decomposition.PCA()
    pca.fit(data_s)
    pca_proj = pca.fit_transform(data_s)
    num_comp = np.where(np.cumsum(pca.explained_variance_)/np.sum(pca.explained_variance_) 
                    > 0.9)[0][0]

    tsne=manifold.TSNE(n_components=2, perplexity=perplexity)
    tsne_proj = tsne.fit_transform(pca_proj[:,0:num_comp])
    return tsne_proj



def generate_target_shape_amtrix_for_hamming(data_norm, result_df, gene_list):
    
    '''
    Generating target mat from these genes that needed comparing pattern.
    
    ''' 
    
    target_gene_list = list()
    target_mat_list = list()
    missed_gene = list() # save genes that are not in data_norm; and just extract from origianl data
    for geneID in gene_list:
        if geneID in result_df.index:
            p = result_df.loc[geneID].p_value
            node = result_df.loc[geneID].nodes
            target_gene_list.append(geneID)
            target_list = list()
            for p_index in np.arange(len(p)): 
#                if len(node[p_index]) < fdr_opt.shape[1]/2:
                temp_vec = np.zeros(data_norm.shape[0])
                temp_vec[node[p_index]] = 1  
                target_list.append(temp_vec)    
            target_mat = np.asarray(target_list)      
            target_mat_list.append(target_mat)
        else:
            missed_gene.append(geneID)
    target_df = pd.DataFrame([target_gene_list, target_mat_list]).T        
    target_df.columns = ['geneID', 'mat']
    target_df.index =  target_df.geneID     
        
    return target_df, missed_gene

# def computer_norm_hamming_to_tissue(tissue_mat, target_df,fdr_opt):

#     '''
#     old versions computer hamming distance
#     '''
#     hamming_result = list()
#     for geneID in target_df.index:
#         if geneID in fdr_opt.index:
#             temp_mat = target_df.loc[geneID].mat
#             overlap_hdist = cdist(tissue_mat, temp_mat, compute_inclusion_new)
#             mapping_index_c = np.argmax(overlap_hdist, axis=0)
#     #        mapping_index_r = np.argmax(overlap_hdist, axis=1)
#             if temp_mat.shape[0] == 1: # use small tissue cluster for no cuts
#                 hamming_val = list()    
#                 ts_index = np.argmin(np.sum(tissue_mat, axis=1))
#                 temp_vec= np.ones(tissue_mat.shape[1])
#                 temp_hamming = compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)# temp_hamming = 10 #random.uniform(2.5, 4)   #compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)
#                 hamming_val.append(temp_hamming)
#             elif temp_mat.shape[0] == 2: # use small size of node for 2 segments cuts
#                 hamming_val = list()    
#                 #p = fdr_opt.loc[geneID].p_value
#                 node = fdr_opt.loc[geneID].nodes

#                 temp_vec= np.zeros(tissue_mat.shape[1])
#                 size=[len(node[i]) for i in range(len(node))]
#                 temp_vec[node[np.argmin(size)]] = 1
                
#                 for ts_index in np.arange(tissue_mat.shape[0]):
#                     temp_hamming = compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)
#                     hamming_val.append(temp_hamming)
#             else:
#                 hamming_val = list()
#                 for ts_index in np.arange(tissue_mat.shape[0]):
#                     match_index = np.where(overlap_hdist[ts_index] > 0.6)[0]

#                     if len(match_index) > 0:
#                         temp_vec= np.zeros(tissue_mat.shape[1])
#                         for m_index in match_index:
#                             if m_index != np.argmax(np.sum(temp_mat, axis=1)):
#                                 temp_vec = temp_vec + temp_mat[m_index]
#                         temp_hamming = compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)
#                         hamming_val.append(temp_hamming)         
#                 p = fdr_opt.loc[geneID].p_value
#                 node = fdr_opt.loc[geneID].nodes
#                 temp_vec= np.zeros(tissue_mat.shape[1])
#                 temp_vec[node[np.argmin(p)]] = 1
#                 for ts_index in np.arange(tissue_mat.shape[0]):
#                     temp_hamming = compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)
#                     hamming_val.append(temp_hamming)                
    
#             hamming_result.append(min(hamming_val))
#     hamming_df = pd.DataFrame([target_df.index, hamming_result]).T        
#     hamming_df.columns = ['geneID', 'hamming']
#     hamming_df.index =  target_df.index
#     return hamming_df
## this is old function to calculate hamming; 387 SV genes from this function


## now this is the newest function to calculate hamming. 
def computer_norm_hamming_to_tissue(tissue_mat, target_df, fdr_opt):
    hamming_result = list()
    temp_result_df = fdr_opt[fdr_opt.fdr < 0.01].sort_values(by=['fdr'])
    p_cutoff = min(temp_result_df.iloc[temp_result_df.shape[0]-1].p_value)
#    p_cutoff = min(fdr_opt.p_value[int(np.where(fdr_opt.fdr == max(fdr_opt.fdr))[0])])
    for geneID in target_df.index:
        temp_mat = target_df.loc[geneID].mat
        overlap_hdist = cdist(tissue_mat, temp_mat, compute_inclusion_new)
        mapping_index_c = np.argmax(overlap_hdist, axis=0)
#        mapping_index_r = np.argmax(overlap_hdist, axis=1)
        if temp_mat.shape[0] == 1: # use small tissue cluster for no cuts
            hamming_val = list()    
            ts_index = np.argmin(np.sum(tissue_mat, axis=1))
            temp_vec= np.zeros(tissue_mat.shape[1])
            one_index = random.sample(range(0, tissue_mat.shape[1]-1), sum(tissue_mat[ts_index]).astype(np.int))
            temp_vec[one_index] = 1
            temp_hamming = compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)# temp_hamming = 10 #random.uniform(2.5, 4)   #compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)
            hamming_val.append(temp_hamming)
        elif temp_mat.shape[0] == 2: # use small p for 2 segments cuts
            hamming_val = list()    
            p = fdr_opt.loc[geneID].p_value
            node = fdr_opt.loc[geneID].nodes
            sizes=list()
            for nn in node:
                sizes.append(len(nn))

            temp_vec= np.zeros(tissue_mat.shape[1])
            temp_vec[node[np.argmin(sizes)]] = 1
            for ts_index in np.arange(tissue_mat.shape[0]):
                temp_hamming = compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)
                hamming_val.append(temp_hamming)
        else:
            hamming_val = list()
            for ts_index in np.arange(tissue_mat.shape[0]):
                match_index = np.where(overlap_hdist[ts_index] > 0.6)[0]
                # use small seg first, use same number of seg as seed:
                # until seize match
                if len(match_index) > 0:
                    temp_vec= np.zeros(tissue_mat.shape[1])
                    for m_index in match_index:
                        if sum(temp_vec) < 1.2*sum(tissue_mat[ts_index]):
                            temp_vec = temp_vec + temp_mat[m_index]
                    temp_hamming = compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)
                    hamming_val.append(temp_hamming)         
            p = fdr_opt.loc[geneID].p_value
            node = fdr_opt.loc[geneID].nodes
            if geneID == 'Fgfr1':
                print(p_cutoff, p)
            for p_index in np.arange(len(p)):
                if p[p_index] <= p_cutoff:
                    temp_vec= np.zeros(tissue_mat.shape[1])
                    temp_vec[node[p_index]] = 1
                    for ts_index in np.arange(tissue_mat.shape[0]):
                        temp_hamming = compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)
                        hamming_val.append(temp_hamming)  
                        if geneID == 'Fgfr1':
                            print(p_cutoff, p)
                            print(p_index, ts_index, sum(temp_vec), sum(tissue_mat[ts_index]), temp_hamming)

                        
        if len(hamming_val) == 0:
            ts_index = np.argmin(np.sum(tissue_mat, axis=1))
            temp_vec= np.zeros(tissue_mat.shape[1])
            one_index = random.sample(range(0, tissue_mat.shape[1]-1), sum(tissue_mat[ts_index]).astype(np.int))
            temp_vec[one_index] = 1
            temp_hamming = compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)# temp_hamming = 10 #random.uniform(2.5, 4)   #compute_diff_vs_common_new(tissue_mat[ts_index], temp_vec)
            hamming_val.append(temp_hamming)
        hamming_result.append(min(hamming_val))
    hamming_df = pd.DataFrame([target_df.index, hamming_result]).T        
    hamming_df.columns = ['geneID', 'hamming']
    hamming_df.index =  target_df.index
    return hamming_df


def identify_pattern_conserved_genes_fixed(locs, data_norm, fdr_opt,cluster_size=5, similarity_cutoff = 0.7,
                                           smooth_factor = 10, perplexity = 30,fixed_k=None,seg_min=8,seg_max=135):
    '''
    Based on cells cluster to compare conserved pattern.
    
    identify similarilty pattern by fixed_k #cluster in KMeans
    '''
    
    tissue_mat,cluster_k = generate_cluster_tissue_mat(locs, data_norm, fdr_opt,
                             cluster_size = cluster_size,
                                             sf = smooth_factor, perplexity = perplexity,
                                             fixed_k=fixed_k,seg_min=seg_min,seg_max=seg_max)
    
    target_df, missed_gene = generate_target_shape_amtrix_for_hamming(data_norm, fdr_opt, fdr_opt.index)
    # now match eact target to seed, require all seed seg are matched
    sim_cutoff = similarity_cutoff
    hamming_df = computer_norm_hamming_to_tissue(tissue_mat,target_df, fdr_opt)           
    target_passed_shape_filter = hamming_df[hamming_df.hamming < sim_cutoff].index
    return fdr_opt.loc[target_passed_shape_filter], tissue_mat,cluster_k,target_df, hamming_df



def identify_pattern_conserved_genes_iteration(locs, data_norm, fdr_df,
                                similarity_cutoff=0.7,cluster_size=5,smooth_factor=10, 
                                perplexity=30,fixed_k=None,seg_min=8,seg_max=135):

    '''
    Compare tissue mat to optimate similarity pattern genes with iteration methods by fixed #cluster in KMeans
    
    '''
    
    iteration=0
    fdr_opt=fdr_df  ## fdr_df=fdr01
    sim_cutoff=similarity_cutoff
    
    temp_df,tissue_mat,cluster_k, target_df, _ = identify_pattern_conserved_genes_fixed(
        locs, data_norm, fdr_opt,cluster_size=cluster_size, similarity_cutoff = similarity_cutoff,
                                           smooth_factor = smooth_factor, perplexity = perplexity,
                                                    fixed_k=fixed_k,seg_min=seg_min,seg_max=seg_max)
   # temp_exp=temp_df[abs(temp_df.exp_diff)>exp_cutoff]
    print(temp_df.shape)

    while len(set(fdr_opt.index)&set(temp_df.index))/max(len(fdr_opt.index),len(temp_df.index))<0.9:
       # temp_exp=pattern_conserved_df.loc[abs(pattern_conserved_df.exp_diff)>exp_cutoff,]
        iteration +=1
        print('================iteration{}'.format(iteration))
        fdr_opt=temp_df
        fixed_k=cluster_k
        print('k:',fixed_k)
        tissue_mat,_ = generate_cluster_tissue_mat(locs, data_norm, fdr_opt,
                             cluster_size = cluster_size,
                                             sf = smooth_factor, perplexity = perplexity,
                                             fixed_k=fixed_k,seg_min=seg_min,seg_max=seg_max)
        
        hamming_df = computer_norm_hamming_to_tissue(tissue_mat,target_df, fdr_df)
        target_passed_shape_filter = hamming_df[hamming_df.hamming < sim_cutoff].index
        temp_df=fdr_df.loc[target_passed_shape_filter]
       # temp_exp=temp_df[abs(temp_df.exp_diff)>exp_cutoff]
        print(temp_df.shape)
       # print(temp_exp.shape)
        if iteration>=50:
            break
    return temp_df,tissue_mat, target_df, hamming_df



def simulate_hamming(locs,data_norm,fdr_opt, cutoff = 0.0001):
    '''
    Estimate hamming cutoff
    ''' 
#    p_cutoff = min(fdr_opt.iloc[fdr_opt.shape[0]-1].p_value)
    hamming_p = cutoff
    target_list = list()    
    # generate seed mat
    # use top genes

    for geneID in fdr_opt.index:
        if True:
            p = fdr_opt.loc[geneID].p_value
            node = fdr_opt.loc[geneID].nodes                     
            sizes = list()
            for nn in node:
                sizes.append(len(nn))
            temp_df = pd.DataFrame([p, node, sizes]).T        
            temp_df.columns = ['p', 'node', 'size']
            temp_df_sorted = temp_df.sort_values('size') 
            for p_index in np.arange(len(p)): 
                temp_sorted_p = temp_df_sorted.iloc[p_index].p
                temp_sorted_node = np.array(temp_df_sorted.iloc[p_index].node)
                if len(temp_sorted_node) < data_norm.shape[0]/2:
                    temp_vec = np.zeros(data_norm.shape[0])
                    temp_vec[temp_sorted_node] = 1  
                    target_list.append(temp_vec)    
                    break  
                       
    target_mat = np.asarray(target_list)      
    # run simulation to check the p of selected cutoff
    # tissue_mat_rand = shuffle(tissue_mat.T).T
    sample = list()
    for rr in np.arange(10): 
       # tissue_mat_rand = shuffle(tissue_mat.T).T
        target_mat_rand1 = shuffle(target_mat.T).T
        target_mat_rand2 = shuffle(target_mat.T).T    
        hdist_rand = cdist(target_mat_rand1, target_mat_rand2, compute_diff_vs_common_new)
        sample.append(hdist_rand.flatten())
    flattened  = [val for sublist in sample for val in sublist]
    ae, loce, scalee = stats.skewnorm.fit(flattened)
    hamming_cutoff = skewnorm.ppf(hamming_p, ae, loce,scalee)
    return flattened, hamming_cutoff

def generate_random_target_mat(data_norm, result_df, gene_list):
    # generate target mat
    # use all genes    
    target_gene_list = list()
    target_mat_list = list()
    missed_gene = list() # save genes that are not in data_norm; and just extract from origianl data
    for geneID in gene_list:
        if geneID in result_df.index:
            p = result_df.loc[geneID].p_value
            node = result_df.loc[geneID].nodes
            target_gene_list.append(geneID)
            target_list = list()
            for p_index in np.arange(len(p)): 
#                if len(node[p_index]) < fdr_opt.shape[1]/2:
                temp_vec = np.zeros(data_norm.shape[0])
                temp_vec[node[p_index]] = 1  
                temp_vec = shuffle(temp_vec)
                target_list.append(temp_vec)    
            target_mat = np.asarray(target_list)      
            target_mat_list.append(target_mat)
        else:
            missed_gene.append(geneID)
    target_df = pd.DataFrame([target_gene_list, target_mat_list]).T        
    target_df.columns = ['geneID', 'mat']
    target_df.index =  target_df.geneID     
        
    return target_df, missed_gene





def estimate_exp_diff_cutoff(new_result_df,cutoff=0.01,q=0.95):

    '''
    Estimating exp_diff cutoff for third filter.
    '''
    df=new_result_df
    fdr1 = df[df.fdr>cutoff]
    fdr1_exp = np.abs(list(fdr1.exp_diff))
    #fdr1_exp = fdr1_exp[fdr1_exp < 5]
    
    ae, loce, scalee = stats.skewnorm.fit(fdr1_exp)
    exp_cutoff = skewnorm.ppf(q, ae, loce,scalee)

    return exp_cutoff


def recalc_exp_diff(data_norm,result_df,fdr_cutoff=0.01,cluster_k=3):

    '''
    For estimating exp_diff cutoff, recalculating zero exp_diff with gmm.
    '''
    
    zero_exp_genes=result_df.index[result_df.exp_diff==0].values
    new_result_df=result_df.copy()
    
    df=result_df[result_df.fdr<fdr_cutoff]
    x=log1p(data_norm.loc[:,df.index])
    k=cluster_k
    kmeans=KMeans(k,random_state=0).fit(x)

    
    #for geneID in zero_exp_genes:
    new_exp=[]
    for i in np.arange(k-1):
        for j in np.arange(k)+1:
            if j<k and i !=j:
                temp_exp=abs(np.mean(log1p(data_norm[kmeans.labels_==i].loc[:,zero_exp_genes]))-np.mean(log1p(data_norm[kmeans.labels_==j].loc[:,zero_exp_genes])))
                new_exp.append(temp_exp)
                
    new_exp_array=np.asarray(new_exp)
    max_exp=np.max(new_exp_array,axis=0)
    new_result_df.loc[zero_exp_genes,'exp_diff']=max_exp
    
    return new_result_df,zero_exp_genes


def compare_tissue_mat_hamming_fixed(data_norm, tissue_mat,result_df,geneList, similarity_cutoff = 0.7):
    '''
    Calculate hamming df between final tissue mat and target geneList.
    '''
    
#     tissue_mat = generate_cluster_tissue_mat_fixed(locs, data_norm, fdr_opt, 
#                              sf = smooth_factor, fixed_k=fixed_k)
    target_df, missed_gene = generate_target_shape_amtrix_for_hamming(data_norm, result_df, geneList)
    # now match eact target to seed, require all seed seg are matched
    sim_cutoff = similarity_cutoff
    hamming_df = computer_norm_hamming_to_tissue(tissue_mat,target_df, result_df)           
    target_passed_shape_filter = hamming_df[hamming_df.hamming < sim_cutoff].index
    return result_df.loc[target_passed_shape_filter], hamming_df


### Visualize
def reverse_newLabel(newLabels,cellGraph,com_factor=5): 
   
    '''
    optimate graph cuts.
    
    :param points: newLabels: shape (n,); gmm: gmm object
                   ndarray shape (n ,3); cellGraph: shape (n,)

    :rtype: p_value.
    '''
    node_lists = list()
    components_nodes=list()
    nodes_set=set(range(len(newLabels)))
    com_factor = com_factor
    G=nx.Graph()
    tempGraph = cellGraph.copy()
    Labels=newLabels.copy()
    tempGraph = np.apply_along_axis(remove_egdes, 1, tempGraph, newLabels)
    G.add_edges_from(tempGraph[np.where(tempGraph[:,2] == 1)[0],0:2].astype(np.int32))
    con_components_old = sorted(nx.connected_components(G), 
                                  key = len, reverse=True)   
#    G = remove_single_link(G)
    con_components = sorted(nx.connected_components(G), 
                                  key = len, reverse=True)

    for j in np.arange(len(con_components)):
        node_list = con_components[j]
        components_nodes+=node_list
        com_size = len(node_list)
#         for k in node_list:
#                 print (newLabels[k],end=" ",flush=True)
#         print("\n")
#         print (node_list)
        if com_size <=com_factor:
#             print (node_list)
            for k in node_list:
                if Labels[k]==0:
                    Labels[k]=1
                else:
                    Labels[k]=0

            node_lists.append(np.array(list(node_list)))
            
    single_nodes=nodes_set-set(components_nodes)
    for n in single_nodes:
        if Labels[n]==0:
            Labels[n]=1
        else:
            Labels[n]=0

    return Labels,node_lists


def visualize_tsne_density(tsne_proj, threshold=0.001, bins=100, fileName=None,title=None,ax=None,fig=None):

   
    '''
    perform kde density estimationg for tsne projection to visualize genes clusters.
    :param file: tsne_proj: shape (m, 2)
    threshold=0.001, bins=100, fileName=None
    '''  
   # fig,ax=plt.subplots()
    tsne_proj=tsne_proj.copy()
    kde = gaussian_kde(tsne_proj.T, bw_method = 'scott')
    z = kde(tsne_proj.T)    
    x = np.ma.masked_where(z > threshold, tsne_proj[:,0])
    y = np.ma.masked_where(z > threshold, tsne_proj[:,1])

    # plot unmasked points
    ax.scatter(list(tsne_proj[:,0]), list(tsne_proj[:,1]), c='black', marker='o', s=5)

    # get bounds from axes
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    # prepare grid for density map
    xedges = np.linspace(xmin, xmax, bins)
    yedges = np.linspace(ymin, ymax, bins)
    xx, yy = np.meshgrid(xedges, yedges)
    gridpoints = np.array([xx.ravel(), yy.ravel()])

    # compute density map
    zz = np.reshape(kde(gridpoints), xx.shape)

    # plot density map
    im = ax.imshow(zz, cmap='Spectral_r', interpolation='nearest',
               origin='lower', extent=[xmin, xmax, ymin, ymax],
                  aspect='auto')
    # plot threshold contour
    cs = ax.contour(xx, yy, zz, levels=[threshold], colors='black', line_width=10)
    # show
    fig.colorbar(im,ax=ax)   
    if title !=None:
        ax.set_title(title,fontsize=12)

    if fileName != None:
        plt.savefig(fileName)
   # plt.show()
    return z
     
def dbScan(tsne_proj, z, threshold, eps=1):
    '''
    deprecated
    '''      
    fig, ax = plt.subplots(figsize = (6, 6))
    tsne_proj_sel = tsne_proj[z > threshold]
    db = DBSCAN(eps=eps, min_samples=5).fit(tsne_proj_sel)
    ax.scatter(tsne_proj_sel[:,0], tsne_proj_sel[:,1], c=db.labels_, marker='.')
    n_clusters_ = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
    for i in np.arange(n_clusters_):
        position = np.max(tsne_proj_sel[db.labels_ == i], axis=0)
        plt.gcf().gca().text(position[0], position[1]-1,str(i), fontsize=12)
    plt.show()
    return tsne_proj_sel, db.labels_


def spatial_pca_tsne_kmeans_cluster_gene(data_norm, gene_lists,marker_genes, perplexity = 30,fileName=None):

    '''
    perform standard PCA + tsne
    :param file: data_norm: normalized gene expression; gene_lists: list shape(k,)
        perplexity = 30
    :rtype: tsne_proj: shape (m, 2)
    '''          
    data_s = StandardScaler().fit_transform(data_norm.loc[:, gene_lists])
    pca = decomposition.PCA()
    pca.fit(data_s.T)
    pca_proj = pca.fit_transform(data_s.T)
    num_comp = np.where(np.cumsum(pca.explained_variance_)/np.sum(pca.explained_variance_)
                    > 0.9)[0][0]

#    RS=20180824
    tsne=manifold.TSNE(n_components=2, perplexity=perplexity)
    tsne_proj = tsne.fit_transform(pca_proj[:,0:num_comp])
    print(tsne_proj.shape)
#    tsne_proj = tsne.fit_transform(pca_proj[:,0:num_comp])
    tsne_proj_df=pd.DataFrame(index=gene_lists)
    tsne_proj_df["TSNE1"]=tsne_proj[:,0]
    tsne_proj_df["TSNE2"]=tsne_proj[:,1]
    init = tsne_proj_df.loc[marker_genes].values
    num_clusters=len(marker_genes)
    kmeans=KMeans(n_clusters=num_clusters,init = init, random_state=0).fit(tsne_proj)

    tsne_proj_df["cluster"]=kmeans.labels_
    gene_subset_lists=list()
    for geneID in marker_genes:
        gene_subset = tsne_proj_df.index[np.where(tsne_proj_df.cluster == tsne_proj_df.loc[geneID,"cluster"])]
        gene_subset_lists.append(gene_subset)

    for i ,gene_subset in enumerate(gene_subset_lists):
        tsne_proj_df.loc[gene_subset,"cluster"]=i
        
    final_labels = tsne_proj_df.cluster.values
    final_tsne = np.c_[tsne_proj, final_labels]
    palette = sns.color_palette('deep', final_labels.max() + 1)
    colors = [palette[x] if x >= 0 else (0.0, 0.0, 0.0) for x in final_tsne[:,2].astype(int)]
    plt.scatter(final_tsne[:,0], final_tsne[:,1], c=colors, s=28)
    plt.xlabel('TSNE component 1')
    plt.ylabel('TSNE component 2')
    for i in final_labels:
        position = np.max(final_tsne[ final_tsne[:,2]== i], axis=0)
        plt.gcf().gca().text(position[0], position[1]-1,str(i), fontsize=12)
    if fileName != None:
        plt.savefig(fileName,format="pdf",dpi=300)
    plt.show()
    return tsne_proj_df

def plot_tsne(tsne_locs,tsne_labels,fileName=None):
    palette = sns.color_palette('deep', tsne_labels.max() + 1)
    colors = [palette[x] if x >= 0 else (0.0, 0.0, 0.0) for x in tsne_labels.astype(int)]
    plt.scatter(tsne_locs[:,0],tsne_locs[:,1], c=colors, s=28)
    plt.xlabel('TSNE component 1')
    plt.ylabel('TSNE component 2')
    for i in tsne_labels:
        position = np.max(tsne_locs[tsne_labels== i], axis=0)
        plt.gcf().gca().text(position[0], position[1]-1,str(i), fontsize=12)

    if fileName !=None:
        plt.savefig(fileName)
    plt.show()


def visualize_spatial_genes(df, locs, data_norm, point_size= 0.5):
    '''
    plot Voronoi tessellation of cells, highlight boundaries of graph cut
    
    :param file: df: dataframe of graph cut results; locs: spatial coordinates (n, 2);
    data_norm: normalized count: shape (n, m); 
    point_size = 0.5; 
    '''    
#    for i in (np.arange(df.shape[0])):

    i = 0
    while i < df.shape[0]:
        plt.figure(figsize=(6,2.5), dpi=300)
        p1 = plt.subplot(121)
        p2 = plt.subplot(122)

        geneID = df.index[i]
        exp =  data_norm.loc[:,geneID]
        exp=(log1p(exp)).values
        best_Labels = df.loc[geneID,][7:].values.astype(int)
        subplot_voronoi_boundary(geneID, locs, exp, best_Labels,
                                 df.loc[geneID,].fdr, ax=p1, 
                                 fdr=True, point_size = point_size, class_line_width=2)
        i = i + 1
        if i < df.shape[0]:
            geneID = df.index[i]
            exp =  data_norm.loc[:,geneID]
            exp=(log1p(exp)).values
            best_Labels = df.loc[geneID,][7:].values.astype(int)
            subplot_voronoi_boundary(geneID, locs, exp, best_Labels,
                                 df.loc[geneID,].fdr, ax=p2, fdr=True, 
                                     point_size = point_size)    
        else:
            p2.axis('off')
        plt.show()
        i= i + 1


def plot_voronoi_boundary(geneID, coord, count, classLabel, p, fdr=False, 
                            fileName=None, point_size=5,
                          line_colors="k", class_line_width=2.5,
                          line_width=0.5, line_alpha=1.0,**kw):
    '''
    plot spatial expression as voronoi tessellation
    highlight boundary between classes
    
    :param file: geneID; spatial coordinates shape (n, 2); normalized count: shape (n);
                predicted cell class calls shape (n); prediction p-value.
                fdr=False; line_colors = 'k'; class_line_width = 3; 
                line_width = 0.5; line_alpha = 1.0
    '''
    points = coord
    count = count
    newLabels =classLabel

    # first estimate mean distance between points--
    p_dist = cdist(points, points)    
    p_dist[p_dist == 0] = np.max(p_dist, axis = 0)[0]
    norm_dist = np.mean(np.min(p_dist, axis = 0))

    # find points at edge, add three layers of new points 
    x_min = np.min(points, axis = 0)[0] - 3*norm_dist
    y_min = np.min(points, axis = 0)[1] - 3*norm_dist
    x_max = np.max(points, axis = 0)[0] + 3*norm_dist
    y_max = np.max(points, axis = 0)[1] + 3*norm_dist

    n_x = int((x_max - x_min)/norm_dist) + 1
    n_y = int((y_max - y_min)/norm_dist) + 1

    # create a mesh
    x = np.linspace(x_min, x_max, n_x)
    y = np.linspace(y_min, y_max, n_y)
    xv, yv = np.meshgrid(x, y)
    # now select points outside of hull, and merge
    hull = Delaunay(points)
    grid_points = np.hstack((xv.reshape(-1,1), yv.reshape(-1,1)))
    pad_points = grid_points[np.where(hull.find_simplex(grid_points)< 0)[0]]
    pad_dist = cdist(pad_points, points)   
    pad_points = pad_points[np.where(np.min(pad_dist, axis = 1) > norm_dist)[0]]
    all_points = np.vstack((points, pad_points))

    ori_len = points.shape[0]
    vor = Voronoi(all_points)

    if kw.get("show_points",True):
        plt.plot(points[0:ori_len,0], points[0:ori_len,1], ".", markersize=point_size)     
    patches = []
    # but we onl use the original points fot plotting
    for i in np.arange(ori_len):
        good_ver = vor.vertices[vor.regions[vor.point_region[i]]]
        polygon = Polygon(good_ver, True)
        patches.append(polygon)

    pc = PatchCollection(patches, cmap=cm.PiYG, alpha=1)

    pc.set_array(np.array(count))

    plt.gca().add_collection(pc)
    # for loop for plotting is slow, consider to vectorize to speedup
    # doesn;t mater for now unless you have many point or genes
    finite_segments=[]
    boundary_segments=[]
    for kk, ii in vor.ridge_dict.items():
        if kk[0] < ori_len and kk[1] < ori_len:
            if newLabels[kk[0]] !=  newLabels[kk[1]]:
                boundary_segments.append(vor.vertices[ii])
            else:
                finite_segments.append(vor.vertices[ii])

    plt.gca().add_collection(LineCollection(boundary_segments,
                                            colors="k",           
                                            lw=class_line_width,
                                            alpha=1,
                                            linestyles="solid"))
    plt.gca().add_collection(LineCollection(finite_segments,
                                            colors=line_colors,
                                            lw=line_width,
                                            alpha=line_alpha,
                                            linestyle="solid"))
    plt.xlim(x_min + 1*norm_dist, x_max - 1*norm_dist)
    plt.ylim(y_min + 1*norm_dist, y_max - 1*norm_dist)

    # also remember to add color bar
    plt.colorbar(pc)
    

    if fdr:
            titleText = geneID + '\n' + 'fdr: ' + str("{:.2e}".format(p))
    else:
            titleText = geneID + '\n' + 'p_value: ' + str("{:.2e}".format(p))
    
    titleText=kw.get("set_title",titleText)
    fontsize=kw.get("fontsize",12)
    plt.title(titleText, fontname="Arial", fontsize=fontsize)
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    if fileName!=None:
        plt.savefig(fileName)
    plt.show() 



def pdf_voronoi_boundary(geneID, coord, count, classLabel, p ,fileName, fdr=False, point_size=5,
                          line_colors="k", class_line_width=2.5,
                          line_width=0.5, line_alpha=1.0,**kw):
    '''
    save spatial expression as voronoi tessellation to pdf
    highlight boundary between classes.
    
    :param file: geneID; spatial coordinates shape (n, 2); normalized count: shape (n);
                predicted cell class calls shape (n); prediction p-value; pdf fileName;
                fdr=False; line_colors = 'k'; class_line_width = 3; 
                line_width = 0.5; line_alpha = 1.0
    '''

    points = coord
    count = count
    newLabels =classLabel

    # first estimate mean distance between points--
    p_dist = cdist(points, points)    
    p_dist[p_dist == 0] = np.max(p_dist, axis = 0)[0]
    norm_dist = np.mean(np.min(p_dist, axis = 0))

    # find points at edge, add three layers of new points 
    x_min = np.min(points, axis = 0)[0] - 3*norm_dist
    y_min = np.min(points, axis = 0)[1] - 3*norm_dist
    x_max = np.max(points, axis = 0)[0] + 3*norm_dist
    y_max = np.max(points, axis = 0)[1] + 3*norm_dist

    n_x = int((x_max - x_min)/norm_dist) + 1
    n_y = int((y_max - y_min)/norm_dist) + 1

    # create a mesh
    x = np.linspace(x_min, x_max, n_x)
    y = np.linspace(y_min, y_max, n_y)
    xv, yv = np.meshgrid(x, y)
    # now select points outside of hull, and merge
    hull = Delaunay(points)
    grid_points = np.hstack((xv.reshape(-1,1), yv.reshape(-1,1)))
    pad_points = grid_points[np.where(hull.find_simplex(grid_points)< 0)[0]]
    pad_dist = cdist(pad_points, points)   
    pad_points = pad_points[np.where(np.min(pad_dist, axis = 1) > norm_dist)[0]]
    all_points = np.vstack((points, pad_points))

    ori_len = points.shape[0]
    vor = Voronoi(all_points)

    if kw.get("show_points",True):
        plt.plot(points[0:ori_len,0], points[0:ori_len,1], ".", markersize=point_size)     
    patches = []
    # but we onl use the original points fot plotting
    for i in np.arange(ori_len):
        good_ver = vor.vertices[vor.regions[vor.point_region[i]]]
        polygon = Polygon(good_ver, True)
        patches.append(polygon)

    pc = PatchCollection(patches, cmap=cm.PiYG, alpha=1)

    pc.set_array(np.array(count))

    plt.gca().add_collection(pc)
    # for loop for plotting is slow, consider to vectorize to speedup
    # doesn;t mater for now unless you have many point or genes
    finite_segments=[]
    boundary_segments=[]
    for kk, ii in vor.ridge_dict.items():
        if kk[0] < ori_len and kk[1] < ori_len:
            if newLabels[kk[0]] !=  newLabels[kk[1]]:
                boundary_segments.append(vor.vertices[ii])
            else:
                finite_segments.append(vor.vertices[ii])

    plt.gca().add_collection(LineCollection(boundary_segments,
                                            colors="k",           
                                            lw=class_line_width,
                                            alpha=1,
                                            linestyles="solid"))
    plt.gca().add_collection(LineCollection(finite_segments,
                                            colors=line_colors,
                                            lw=line_width,
                                            alpha=line_alpha,
                                            linestyle="solid"))
    plt.xlim(x_min + 1*norm_dist, x_max - 1*norm_dist)
    plt.ylim(y_min + 1*norm_dist, y_max - 1*norm_dist)

    # also remember to add color bar
    plt.colorbar(pc)
    

    if fdr:
            titleText = geneID + '\n' + 'fdr: ' + str("{:.2e}".format(p))
    else:
            titleText = geneID + '\n' + 'p_value: ' + str("{:.2e}".format(p))
    
    titleText=kw.get("set_title",titleText)
    fontsize=kw.get("fontsize",12)
    plt.title(titleText, fontname="Arial", fontsize=fontsize)
    plt.axis('off')
#    plt.xlabel('X coordinate')
#    plt.ylabel('Y coordinate')
    if fileName != None:
        plt.savefig(fileName)
    else:
        print('ERROR! Please supply a file name.')



def subplot_voronoi_boundary(geneID, coord, count, classLabel, p  ,ax ,fdr=False, point_size=5,
                          line_colors="k", class_line_width=2.5,
                          line_width=0.5, line_alpha=1.0,**kw):
    '''
    plot spatial expression as voronoi tessellation
    highlight boundary between classes
    
    :param file: geneID; spatial coordinates (n, 2); normalized gene expression: count;
            predicted cell class calls (n); p_value; ax number;
    '''
    points = coord
    count = count
    newLabels =classLabel

    # first estimate mean distance between points--
    p_dist = cdist(points, points)    
    p_dist[p_dist == 0] = np.max(p_dist, axis = 0)[0]
    norm_dist = np.mean(np.min(p_dist, axis = 0))

    # find points at edge, add three layers of new points 
    x_min = np.min(points, axis = 0)[0] - 3*norm_dist
    y_min = np.min(points, axis = 0)[1] - 3*norm_dist
    x_max = np.max(points, axis = 0)[0] + 3*norm_dist
    y_max = np.max(points, axis = 0)[1] + 3*norm_dist

    n_x = int((x_max - x_min)/norm_dist) + 1
    n_y = int((y_max - y_min)/norm_dist) + 1

    # create a mesh
    x = np.linspace(x_min, x_max, n_x)
    y = np.linspace(y_min, y_max, n_y)
    xv, yv = np.meshgrid(x, y)
    # now select points outside of hull, and merge
    hull = Delaunay(points)
    grid_points = np.hstack((xv.reshape(-1,1), yv.reshape(-1,1)))
    pad_points = grid_points[np.where(hull.find_simplex(grid_points)< 0)[0]]
    pad_dist = cdist(pad_points, points)   
    pad_points = pad_points[np.where(np.min(pad_dist, axis = 1) > norm_dist)[0]]
    all_points = np.vstack((points, pad_points))

    ori_len = points.shape[0]
    vor = Voronoi(all_points)

    if kw.get("show_points",True):
        ax.plot(points[0:ori_len,0], points[0:ori_len,1], ".", markersize=point_size)  

    ## plt.full(color)   
    patches = []
    # but we onl use the original points fot plotting
    for i in np.arange(ori_len):
        good_ver = vor.vertices[vor.regions[vor.point_region[i]]]
        polygon = Polygon(good_ver, True)
        patches.append(polygon)

    pc = PatchCollection(patches, cmap=cm.PiYG, alpha=1)

    pc.set_array(np.array(count))

    ax.add_collection(pc)


    # for loop for plotting is slow, consider to vectorize to speedup
    # doesn;t mater for now unless you have many point or genes
    finite_segments=[]
    boundary_segments=[]
    for kk, ii in vor.ridge_dict.items():
        if kk[0] < ori_len and kk[1] < ori_len:
            if newLabels[kk[0]] !=  newLabels[kk[1]]:
                boundary_segments.append(vor.vertices[ii])
            else:
                finite_segments.append(vor.vertices[ii])

    ax.add_collection(LineCollection(boundary_segments,
                                            colors="k",           
                                            lw=class_line_width,
                                            alpha=1,
                                            linestyles="solid"))
    ax.add_collection(LineCollection(finite_segments,
                                            colors=line_colors,
                                            lw=line_width,
                                            alpha=line_alpha,
                                            linestyle="solid"))
    ax.set_xlim(x_min + 1*norm_dist, x_max - 1*norm_dist)
    ax.set_ylim(y_min + 1*norm_dist, y_max - 1*norm_dist)

    # also remember to add color bar
    #plt.colorbar(pc)
    

    if fdr:
            titleText = geneID + '\n' + 'fdr: ' + str("{:.2e}".format(p))
    else:
            titleText = geneID + '\n' + 'p_value: ' + str("{:.2e}".format(p))
    
    titleText=kw.get("set_title",titleText)
    fontsize=kw.get("fontsize",8)
    ax.set_title(titleText, fontname="Arial", fontsize=fontsize)
    
def subplot_voronoi_boundary_12x18(geneID, coord, count, 
                          classLabel, p, ax, fdr=False, point_size = 0.5,  
                          line_colors = 'k', class_line_width = 0.8, 
                          line_width = 0.05, line_alpha = 1.0,**kw):
    '''
    plot spatial expression as voronoi tessellation
    highlight boundary between classes
    
    :param file: geneID; coord: spatial coordinates (n, 2); count: normalized gene expression;
        predicted cell class calls (n); p: graph cut p-value. 
    '''
    points = coord
    count = count
    newLabels =classLabel


    p_dist = cdist(points, points)    
    p_dist[p_dist == 0] = np.max(p_dist, axis = 0)[0]
    norm_dist = np.mean(np.min(p_dist, axis = 0))

    # find points at edge, add three layers of new points 
    x_min = np.min(points, axis = 0)[0] - 3*norm_dist
    y_min = np.min(points, axis = 0)[1] - 3*norm_dist
    x_max = np.max(points, axis = 0)[0] + 3*norm_dist
    y_max = np.max(points, axis = 0)[1] + 3*norm_dist

    n_x = int((x_max - x_min)/norm_dist) + 1
    n_y = int((y_max - y_min)/norm_dist) + 1

    # create a mesh
    x = np.linspace(x_min, x_max, n_x)
    y = np.linspace(y_min, y_max, n_y)
    xv, yv = np.meshgrid(x, y)
    # now select points outside of hull, and merge
    hull = Delaunay(points)
    grid_points = np.hstack((xv.reshape(-1,1), yv.reshape(-1,1)))
    pad_points = grid_points[np.where(hull.find_simplex(grid_points)< 0)[0]]
    pad_dist = cdist(pad_points, points)   
    pad_points = pad_points[np.where(np.min(pad_dist, axis = 1) > norm_dist)[0]]
    all_points = np.vstack((points, pad_points))

    ori_len = points.shape[0]
    vor = Voronoi(all_points)
    if kw.get("show_points",True):
        ax.plot(points[0:ori_len,0], points[0:ori_len,1], ".", markersize=point_size)     
    patches = []
    # but we onl use the original points fot plotting
    for i in np.arange(ori_len):
        good_ver = vor.vertices[vor.regions[vor.point_region[i]]]
        polygon = Polygon(good_ver, True)
        patches.append(polygon)

    pc = PatchCollection(patches, cmap=cm.PiYG, alpha=1)

    pc.set_array(np.array(count))

    ax.add_collection(pc)
    # for loop for plotting is slow, consider to vectorize to speedup
    # doesn;t mater for now unless you have many point or genes
    finite_segments=[]
    boundary_segments=[]
    for kk, ii in vor.ridge_dict.items():
        if kk[0] < ori_len and kk[1] < ori_len:
            if newLabels[kk[0]] !=  newLabels[kk[1]]:
                boundary_segments.append(vor.vertices[ii])
            else:
                finite_segments.append(vor.vertices[ii])

    ax.add_collection(LineCollection(boundary_segments,   ### boundary
                                            colors="k",           
                                            lw=class_line_width,
                                            alpha=1,
                                            linestyles="solid"))
    ax.add_collection(LineCollection(finite_segments,               ## other line in loop
                                            colors=line_colors,
                                            lw=line_width,
                                            alpha=line_alpha,
                                            linestyle="solid"))
    ax.set_xlim(x_min + 1*norm_dist, x_max - 1*norm_dist)
    ax.set_ylim(y_min + 1*norm_dist, y_max - 1*norm_dist)

    # also remember to add color bar
    #plt.colorbar(pc)

    if fdr:
        titleText = geneID + ' ' + '' + str("{0:.1e}".format(p))
    else:
        titleText = geneID + ' ' + 'p_value: ' + str("{0:1e}".format(p))
    titleText=kw.get("set_title",titleText)
    fontsize=kw.get("fontsize",3.5)
    ax.set_title(titleText, fontname="Arial", fontsize=fontsize, y = 0.85)


def multipage_pdf_visualize_spatial_genes(df, locs, data_norm, fileName, 
                     point_size=0.,**kw):
    '''
    save spatial expression as voronoi tessellation to pdf highlight boundary between classes
    format: 12 by 18.
    :param file: df: graph cuts results; locs: spatial coordinates (n, 2); data_norm: normalized gene expression;
        pdf filename; point_size=0.5. 
    '''    
    
    geneID = df.index[0]
    points = locs
    exp =  data_norm.loc[:,geneID]
    exp=(log1p(exp)).values
    cellGraph = create_graph_with_weight(locs, exp)
    count = exp
    vor = Voronoi(points)

    nb_plots = int(df.shape[0])
    numCols = 12  
    numRows = 18
    nb_plots_per_page =  numCols*numRows
    t_numRows = int(df.shape[0]/numCols) + 1
    
    with PdfPages(fileName) as pdf:    
#    fig, axs = plt.subplots(numRows, numCols, figsize = (15, fsize), constrained_layout=True)
        for i in np.arange(df.shape[0]):
            if i % nb_plots_per_page == 0:
                fig, axs = plt.subplots(numRows, numCols, # 8 11
                                    figsize = (8,11))   
                fig.subplots_adjust(hspace=0.3, wspace=0.3,
                                top=0.925, right=0.925, bottom=0.075, left = 0.075)
                  
            geneID = df.index[i]
            exp =  data_norm.loc[:,geneID]
            exp=(log1p(exp)).values
            if np.isnan(df.loc[geneID,].fdr):
                best_Labels = np.zeros(data_norm.shape[0])
            else:
                best_Labels = df.loc[geneID,][7:].values.astype(int)
            m = int(i/numCols) % numRows
            n = i % numCols 
            ax = axs[m,n]
            subplot_voronoi_boundary_12x18(geneID, locs, exp, best_Labels,
                                 df.loc[geneID,].fdr, ax=ax, fdr=True,
                                 point_size = point_size,**kw)

            if (i + 1) % nb_plots_per_page == 0 or (i + 1) == nb_plots:
                for ii in np.arange(numRows):
                    for jj in np.arange(numCols):        
                        axs[ii,jj].axis('off')

            # if (i + 1) % nb_plots_per_page == 0 or (i + 1) == nb_plots:
            #      for ii in np.arange(nb_plots,nb_box):        
            #         ax[int(ii/ncols),ii%ncols].axis('off')

                pdf.savefig(fig)
                fig.clear()
                plt.close()


def add_HE_image(image,ax):
    img=Image.open(image)
    extent_size = [1,33,1,35]
    img_transpose=img.transpose(Image.FLIP_TOP_BOTTOM)
    ax.imshow(img_transpose,extent=extent_size)

def subplot_boundary(geneID, coord, count, classLabel, p  , ax=None,
                    fdr=False, point_size=5,
                    class_line_width=2.5,
                    **kw):
    '''
    plot spatial expression as voronoi tessellation
    
    :param file: geneID; spatial coordinates (n, 2); normalized count: shape (n); 
    '''
    points = coord
    count = count
    newLabels =classLabel

    # first estimate mean distance between points--
    p_dist = cdist(points, points)    
    p_dist[p_dist == 0] = np.max(p_dist, axis = 0)[0]
    norm_dist = np.mean(np.min(p_dist, axis = 0))

    # find points at edge, add three layers of new points 
    x_min = np.min(points, axis = 0)[0] - 3*norm_dist
    y_min = np.min(points, axis = 0)[1] - 3*norm_dist
    x_max = np.max(points, axis = 0)[0] + 3*norm_dist
    y_max = np.max(points, axis = 0)[1] + 3*norm_dist

    n_x = int((x_max - x_min)/norm_dist) + 1
    n_y = int((y_max - y_min)/norm_dist) + 1

    # create a mesh
    x = np.linspace(x_min, x_max, n_x)
    y = np.linspace(y_min, y_max, n_y)
    xv, yv = np.meshgrid(x, y)
    # now select points outside of hull, and merge
    hull = Delaunay(points)
    grid_points = np.hstack((xv.reshape(-1,1), yv.reshape(-1,1)))
    pad_points = grid_points[np.where(hull.find_simplex(grid_points)< 0)[0]]
    pad_dist = cdist(pad_points, points)   
    pad_points = pad_points[np.where(np.min(pad_dist, axis = 1) > norm_dist)[0]]
    all_points = np.vstack((points, pad_points))

    ori_len = points.shape[0]
    vor = Voronoi(all_points)

    if kw.get("show_points",False):
        ax.plot(points[0:ori_len,0], points[0:ori_len,1], ".", markersize=point_size)
    
    # for loop for plotting is slow, consider to vectorize to speedup
    # doesn;t mater for now unless you have many point or genes
    boundary_segments=[]
    for kk, ii in vor.ridge_dict.items():
        if kk[0] < ori_len and kk[1] < ori_len:
            if newLabels[kk[0]] !=  newLabels[kk[1]]:
                boundary_segments.append(vor.vertices[ii])

    ax.add_collection(LineCollection(boundary_segments,
                                            colors="k",           
                                            lw=class_line_width,
                                            alpha=1,
                                            linestyles="solid"))
    
    ax.set_xlim(x_min + 1*norm_dist, x_max - 1*norm_dist)
    ax.set_ylim(y_min + 1*norm_dist, y_max - 1*norm_dist)
    
    if fdr:
            titleText = geneID + '\n' + 'fdr: ' + str("{:.2e}".format(p))
    else:
            titleText = geneID + '\n' + 'p_value: ' + str("{:.2e}".format(p))
    
    titleText=kw.get("set_title",titleText)
    fontsize=kw.get("fontsize",8)
    ax.set_title(titleText, fontname="Arial", fontsize=8)






def plot_tissue_pattern(locs,data_norm,tissue_mat,image,colors,title,nrows=4,ncols=5,s=15):
        ## Task2: Tissue mat
    
    nb_plots=tissue_mat.shape[0]
    nrows=nrows
    ncols=ncols
    nb_box=nrows*ncols

    
    fig,ax=plt.subplots(nrows,ncols,figsize=(ncols*3,nrows*3),dpi=180)
    fig.subplots_adjust(hspace=0.3, wspace=0.3,
                                    top=0.925, right=0.925, bottom=0.075, left = 0.075)
    
    for i in range(tissue_mat.shape[0]):
        x=int(i/ncols)
        y=i%ncols

        axes=ax[x,y]
        
        add_HE_image(image,axes)
        axes.scatter(locs[:,0], locs[:,1], c=tissue_mat[i],
                     cmap=matplotlib.colors.ListedColormap(colors) ,s=s)
        
        axes.set_title(title,fontsize=8)


        points=locs
        p_dist = cdist(points, points)    
        p_dist[p_dist == 0] = np.max(p_dist, axis = 0)[0]
        norm_dist = np.mean(np.min(p_dist, axis = 0))

        # find points at edge, add three layers of new points 
        x_min = np.min(points, axis = 0)[0] - 3*norm_dist
        y_min = np.min(points, axis = 0)[1] - 3*norm_dist
        x_max = np.max(points, axis = 0)[0] + 3*norm_dist
        y_max = np.max(points, axis = 0)[1] + 3*norm_dist

        axes.set_xlim(x_min + 1*norm_dist, x_max - 1*norm_dist)
        axes.set_ylim(y_min + 1*norm_dist, y_max - 1*norm_dist)

        if (i + 1) == nb_plots:
            for ii in np.arange(nb_plots,nb_box):        
                    ax[int(ii/ncols),ii%ncols].axis('off')


def create_labels(locs,data_norm,geneList,cluster_size=5,unary_scale_factor=100,smooth_factor=10,rs=0):
    
    exp =  data_norm.iloc[:,1]
    exp=(log1p(exp)).values
    cellGraph = create_graph_with_weight(locs, exp) 
    X=log1p(data_norm.loc[:,geneList])
    
    cluster_KM=cluster_size
    kmeans=KMeans(n_clusters=cluster_KM,random_state=rs).fit(X)
    hmrf_labels = cut_graph_profile(cellGraph, kmeans.labels_, unary_scale_factor=unary_scale_factor,
                  smooth_factor=smooth_factor) ## smooth_factor can adjust
    return kmeans.labels_,hmrf_labels

def subplot_HE_with_labels(locs,labels,image,ax,colors,title,s=30,**kw):
    
   # import matplotlib
    add_HE_image(image,ax)  
    ax.scatter(locs[:,0], locs[:,1], c=labels,
                 cmap=matplotlib.colors.ListedColormap(colors) ,s=s)
    
    fontsize=kw.get("fontsize",8)
    ax.set_title(title,fontsize=fontsize)

    points=locs
    p_dist = cdist(points, points)    
    p_dist[p_dist == 0] = np.max(p_dist, axis = 0)[0]
    norm_dist = np.mean(np.min(p_dist, axis = 0))
    x_min = np.min(points, axis = 0)[0] - 3*norm_dist
    y_min = np.min(points, axis = 0)[1] - 3*norm_dist
    x_max = np.max(points, axis = 0)[0] + 3*norm_dist
    y_max = np.max(points, axis = 0)[1] + 3*norm_dist

    ax.set_xlim(x_min + 1*norm_dist, x_max - 1*norm_dist)
    ax.set_ylim(y_min + 1*norm_dist, y_max - 1*norm_dist)