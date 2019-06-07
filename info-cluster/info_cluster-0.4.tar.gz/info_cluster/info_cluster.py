import numpy as np
from sklearn.metrics.pairwise import pairwise_kernels
from sklearn.neighbors import kneighbors_graph
from ete3 import Tree
import networkx as nx

from . import psp # [package] principal sequence of partition

class InfoCluster:
    '''Info clustering is a kind of hierarchical clustering method.
    It uses top down approach to build the hierarchical tree.
    
    Parameters
    ----------
    gamma : float, default=1.0
        Kernel coefficient for rbf kernels.
    affinity : string, default 'rbf'
        may be one of 'precomputed', 'rbf', 'laplacian', 'nearest_neighbors'.        
    n_neighbors : integer
        Number of neighbors to use when constructing the affinity matrix using
        the nearest neighbors method. Ignored for ``affinity='rbf'``.        
    n_clusters : integer
        suggested minimum number of clusters required, default is None
    '''
    def __init__(self, gamma=1, affinity='rbf', n_neighbors=10, n_clusters=None):    
        self._gamma = gamma;
        self.affinity = affinity
        self.n_neighbors = n_neighbors     
        self.n_clusters = n_clusters
        self.tree = Tree()
        self.tree_depth = 0
        
    def fit(self, X, use_pdt = False, initialize_tree = True):
        '''Construct an affinity graph from X using rbf kernel function,
        then applies info clustering to this affinity graph.
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            if affinity='precomputed', X is networkx like object or affinity matrix(upper triangle)
           
        '''
        self.tree = Tree() # clear the tree
        if(self.n_clusters is not None and use_pdt == False):
            return self.get_category(self.n_clusters, X)
        self._init_g(X, use_pdt)
        self.g.run()
        
        self.critical_values = to_py_list(self.g.get_critical_values())
        self.partition_num_list = to_py_list(self.g.get_partitions())  
        if(initialize_tree):
            self._get_hierachical_tree()  
            
    def fit_predict(self, X):
        self.fit(X)

    def _add_node(self, root, node_list, num_index):
        label_list = self.get_category(self.partition_num_list[num_index])
        cat_list = []
        for i in node_list:
            if(cat_list.count(label_list[i]) == 0):
                cat_list.append(label_list[i])
        max_cat = len(cat_list)
        label_list_list = [[] for i in range(max_cat)]
        for i in node_list:
            j = cat_list.index(label_list[i])
            label_list_list[j].append(i)
        for node_list_i in label_list_list:
            node_name = ''.join([str(ii) for ii in node_list_i])
            if(node_name != root.name):
                root_i = root.add_child(name= node_name)
            else:
                root_i = root
            if(len(node_list_i)>1):
                self._add_node(root_i, node_list_i, num_index+1)
                
    def _get_hierachical_tree(self):
        max_num = self.partition_num_list[-1]
        node_list = [ i for i in range(0, max_num)]
        self._add_node(self.tree, node_list, 1)
    
    def _set_tree_depth(self, node, depth):
        if(node.is_leaf()):
            if(depth > self.tree_depth):
                self.tree_depth = depth
            return
        for node_i in node.children: # depth first search
            self._set_tree_depth(node_i, depth+1)
            
    def get_tree_depth(self):
        if(self.tree.is_leaf()):
            self._get_hierachical_tree()
        if(self.tree_depth != 0):
            return self.tree_depth
        self._set_tree_depth(self.tree, 0)
        return self.tree_depth
        
    def print_hierarchical_tree(self):
        '''print the hirechical tree of clustering result
        '''
        if(self.tree.is_leaf()):
            self._get_hierachical_tree()
        print(self.tree)
        
    def get_category(self, i, X=None):
        '''get the clustering labels with the number of clusters no smaller than i
        Parameters
        ----------
        i : int, number of cluster threshold
        X : array-like, shape (n_samples, n_features). if provided, recompute the result targeted only at the specified `i`.
            
        Returns
        --------
        list, with each element of the list denoting the label of the cluster.
        '''
        if(X is not None):
            self._init_g(X)
            return to_py_list(self.g.get_labels(i))
        else:
            try:
                self.g
            except AttributeError:
                raise AttributeError('no data provided and category cannot be got')
            return to_py_list(self.g.get_category(i))        
            
    def get_num_cat(self, min_num):
        '''
        return the index of partition whose first element is no smaller than min_num,
        '''
        for i in self.partition_num_list:
            if(i>=min_num):
                return i
        return -1       
        
    def _init_g(self, X, use_pdt = False):
        is_nx_graph = False
        if(type(X) is list):
            n_samples = len(X)
        elif(type(X) is np.ndarray):
            n_samples = X.shape[0]
        elif(type(X) is nx.Graph):
            n_samples = nx.number_of_nodes(X)
            is_nx_graph = True
        else:
            raise TypeError('type(X) must be list, numpy.ndarray or networkx.Graph')
        sim_list = []            
        if not(is_nx_graph):    
            if(self.affinity == 'precomputed'):
                affinity_matrix = X
            elif(self.affinity == 'nearest_neighbors'):
                connectivity = kneighbors_graph(X, n_neighbors=self.n_neighbors,include_self=True)
                affinity_matrix = 0.5 * (connectivity + connectivity.T)        
            elif(self.affinity == 'laplacian'):
                affinity_matrix = pairwise_kernels(X, metric='laplacian', gamma = self._gamma)
            else:
                affinity_matrix = pairwise_kernels(X, metric='rbf', gamma = self._gamma)            
        else:
            sparse_mat = nx.adjacency_matrix(X)
            affinity_matrix = np.asarray(sparse_mat.todense(),dtype=float)
            
        for s_i in range(n_samples):
            for s_j in range(s_i+1, n_samples):
                sim_list.append((s_i, s_j, affinity_matrix[s_i, s_j]))       

        if(use_pdt):
            self.g = psp.PyGraphPDT(n_samples, sim_list)
        else:
            self.g = psp.PyGraph(n_samples, sim_list)    

def to_py_list(L):
    '''
    convert an iterable object (exported from C++ class) to numpy 1d array        
    '''
    return [i for i in L]
