import numpy as np
from multiprocessing.pool import Pool
from threading import Event, Lock, Semaphore

#import collections
import igraph
import pandas as pd
import timeit
#import graphs_aux
from sklearn.neighbors.kde import KernelDensity
from numpy import linalg as LA
from sklearn import svm, datasets
from scipy import stats
#from pathlib2 import Path
import os
import sys

class graph_partition:
    def __init__(self, id_part = 0, num_parts = 1, paths = None, work_dir = ''):
        self.id_part = id_part
        self.num_parts = num_parts
        if paths is None:
            paths = [''] * num_parts
            for i in range(num_parts):
                paths[i] = 'graph_id_part_' + str(i) + '.npz'
        else:
            assert(len(paths) == num_parts)
        for i in range(num_parts):
            paths[i] = os.path.join(work_dir, paths[i])
        self.paths = paths
        self.path = paths[id_part]
        self.fit(0)
    
    def fit(self, num_vertices):
        cnt = num_vertices * (num_vertices - 1) // 2
        lens = np.tile(cnt // self.num_parts, (self.num_parts, 1))
        lens[:(cnt % self.num_parts)] += 1
        clens = np.concatenate([[0], np.cumsum(lens)])
        self.be = clens[self.id_part]
        self.en = clens[self.id_part + 1] - 1
        self.num_vertices = num_vertices
        self.length = int(np.asscalar(lens[self.id_part]))
        return self

    def get_path(self):
        return self.partition_path

    def get_paths(self):
        return self.partition_paths
        
    def __iter__(self):
        cur = 0
        for i in range(self.num_vertices):
            l = self.num_vertices - i - 1
            if (cur <= self.be and self.be < cur + l) or (cur <= self.en and self.en < cur + l) or (self.be <= cur and cur <= self.en):
                for j in range(self.num_vertices):
                    if i >= j: continue
                    cur_id = i * self.num_vertices + j
                    if self.be <= cur and cur <= self.en:
                        yield i, j
                    cur += 1
            else:        
                cur += l
    
    def __len__(self):
        return self.length


class classifier_kernel:
    def __init__(self, distance_threshold = 0, min_score = 0.75, by_group = False, dtype = np.float32, \
                 clf = svm.LinearSVC(C = 1, class_weight = "balanced"), distance_method = 'decision_function', \
                 score_method = 'score'):
        self.distance_threshold = distance_threshold
        self.min_score = min_score
        self.by_group = by_group
        self.dtype = dtype
        self.clf = clf
        self.distance_method = getattr(self.clf, distance_method)
        self.score_method = getattr(self.clf, score_method)
        self.G = None
        self.D = None
        #clf = svm.SVC(kernel = 'linear', C = 1, class_weight = "balanced")
    
    def fit(self, X_i, X_j, y, mask):
        #data = stats.zscore(np.array([X_i, X_j]).T)
        data = np.array([X_i, X_j]).T
        
        if self.by_group:
            classes = np.unique(y)
            G = np.zeros((len(y), ), np.bool)
            D = np.zeros((len(y), ), self.dtype)
            for c in classes:
                fit_mask = (y == c) | (mask == 1)
                if len(np.unique(y[fit_mask])) == 1:
                    continue
                self.clf.fit(data[fit_mask], y[fit_mask] == c)
                score = self.score_method(data[fit_mask], y[fit_mask] == c)
                
                G[y == c] = self.clf.predict(data[y == c]) == 1
                D[y == c] = self.distance_method(data[y == c])
                if score < self.min_score:
                    G[fit_mask] = False
                    
            G = G.reshape((1, len(G)))
        else:
            fit_mask = (mask == 0) | (mask == 1)
            
            self.clf.fit(data[fit_mask], y[fit_mask] == 0)
            G = self.clf.predict(data) == 1
            score = self.score_method(data[fit_mask], y[fit_mask] == 0)
                
            if score < self.min_score:
                G[:] = False
            G = G.reshape((1, len(G)))
            D = np.array(self.distance_method(data), dtype = self.dtype)
        self.G = G
        self.D = D
        return self
        
    def get_edges(self, thr_d = None):
        return self.G, self.D        
    
class pdf_kernel:
    def __init__(self, num_points = 10000, linearity_eps = 1.0e-9, dtype = np.float32, thr_p = 0.9):
        self.num_points = num_points
        self.linearity_eps = linearity_eps
        self.dtype = dtype
        self.thr_p = thr_p
        self.G = None
        self.D = None
        self.p = None
        self.pr = None
    
    def fit(self, X_i, X_j, y, mask):
        X_prob_i, X_prob_j = X_i[mask], X_j[mask]
        data = np.array([X_prob_i, X_prob_j])
        det = np.linalg.det(np.corrcoef(data))

        if abs(det) < self.linearity_eps:
            self.pr = np.zeros((self.num_points), dtype=np.dtype)
            self.p = np.zeros((X_i.shape[0]), dtype=np.dtype)
            self.D = np.zeros((X_i.shape[0]), dtype=np.bool)
            return self
        kde = stats.gaussian_kde(data)
        
        data = np.array([X_i, X_j])
        p = np.array(kde(data))
        
        points = kde.resample(self.num_points)
        pr = np.array(kde(points))
        pr.sort()

        self.pr = pr
        self.p = p
        self.D = np.array(p, dtype = self.dtype)
        return self

    def get_edges(self, thr_p = None):
        if thr_p is None:
            thr_p = self.thr_p
        ind = int(thr_p * self.num_points)
        if ind < len(self.pr):
            q = self.pr[ind]
            self.G = self.p < q
        else:
            self.G = np.ones((len(self.p)), dtype=np.bool)
        return self.G, self.D



class parenclitic:
    def __init__(self, partition = graph_partition(), kernel = classifier_kernel(), verbose = 0):
        self.partition = partition
        self.kernel = kernel
        
        self.M = None
        self.D = None
        self.E = None
        self.is_fitted = False
        self.is_loaded = False
        self.graph_paths = None
        self.graphs = None
        self.parenclitics = None
        self.verbose = verbose
        #self.max_edges = max_edges

    def fit(self, X, y, mask, num_workers = 1, queue_len = 10):
        """Fit the model according to the given training data.
        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vector, where n_samples in the number of samples and
            n_features is the number of features.
        y : array-like, shape = [n_samples]
            Target vector relative to X
        mask : array-like, shape = [n_samples]
            Control group mask vector relative to X, 
            where True (1) - control, False (0) - test
        sample_weight : array-like, shape = [n_samples], optional
            Array of weights that are assigned to individual
            samples. If not provided,
            then each sample is given unit weight.
        Returns
        -------
        self : object
        """
        
        self.X_shape = X.shape
        assert(len(self.X_shape) == 2)
        self.num_samples = self.X_shape[0]
        self.num_features = self.X_shape[1]

        if self.verbose == 1:
            print('parenclitic_graphs')
            sys.stdout.flush()

        self.partition.fit(self.num_features)
        
        global num_done, num_pairs
        num_done = 0
        num_pairs = len(self.partition)
            
        M, D, E = [], [], []
        
        need_parallel = num_workers > 1
        if need_parallel:
            pool = Pool(num_workers)
            global done_tasks, ready
            done_tasks = 0
            ready = Semaphore(num_workers * queue_len)

        start = timeit.default_timer()
        each_progress = int(np.sqrt(num_pairs + 0.5))
        for i, j in self.partition:
            def upd_graph(kernel, i = i, j = j):
                global num_done, done_tasks, ready
                m, d = kernel.get_edges()
                if m.any():
                    M.append(m)
                    D.append(d)
                    E.append([i, j])
            
                if need_parallel:
                    done_tasks += 1
                    ready.release()

                num_done += 1
                if num_done % each_progress == 0 or num_done == num_pairs:
                    stop = timeit.default_timer()
                    if self.verbose == 1:
                        print('Graph for', num_done, 'pairs calculated in', stop - start)
                        sys.stdout.flush()

            if need_parallel:
                ready.acquire()
                pool.apply_async(self.kernel.fit, args = (self.kernel, X[:, i], X[:, j], y, mask), callback = upd_graph)
            else:
                upd_graph(self.kernel.fit(X[:, i], X[:, j], y, mask))

        if need_parallel:
            while done_tasks < num_pairs:
                ready.acquire()

            pool.close()
            pool.join()
    
        if self.verbose == 1:
            sys.stdout.flush()
        if M == []:
            self.M = np.zeros((self.num_samples, 0), dtype = np.bool)
            self.D = np.zeros((self.num_samples, 0), dtype = np.float32)
            self.E = np.zeros((2, 0), dtype = np.float32)
        else:    
            self.M = np.array(M).T
            self.D = np.array(D).T
            self.E = np.array(E)
        self.is_fitted = True
        return self
        
    def save_part_graphs(self):
        np.savez_compressed(self.partition.get_path(), G = self.G, D = self.D, IDS = self.IDS, \
                            num_samples = self.num_samples, num_features = self.num_features)
        
    def load_part_graphs(self):
        if self.is_loaded:
            return
            
        if self.partition.num_parts > 1 or not self.is_fitted:
            E, D, IDS = [], [], []
            for part_path in self.partition.get_paths():
                data = np.load(part_path)
                mcur, dcur, ecur = data['M'], data['D'], data['E']
                num_samples, num_features = data['num_samples'], data['num_features']
                
                M.extend(mcur.tolist())
                D.extend(dcur.tolist())
                E.extend(ecur.tolist())

            self.M = np.array(M).T
            self.D = np.array(D).T
            self.E = np.array(E)
            self.num_samples = num_samples
            self.num_features = num_features
        
        self.is_loaded = True
        
    def make_graph(self, edges, weights, mask, num_features, features_names = None):
        mask = mask.flatten()
        weights = weights.flatten()
        edges = edges[mask, :]
        weights = weights[mask]
        
        g = igraph.Graph(n = num_features, edges = list(zip(*edges.T)))
        g.es["weight"] = weights
            
        if not features_names is None:
            g.vs["name"] = features_names
            g.vs["label"] = features_names
        return g
        
    def get_graph(self, id_sample, features_names = None):
        if self.graphs is None or self.graphs[id_sample] is None:
            if self.M is None:
                M, D, E, num_samples, num_features = self.load_graph(id_sample)
                self.num_samples = num_samples
                self.num_features = num_features
            else:
                M = self.M[id_sample, :]
                D = self.D[id_sample, :]
                E = self.E
            if self.graphs is None:
                self.graphs = [None] * self.num_samples
            self.graphs[id_sample] = self.make_graph(E, D, M, self.num_features, features_names = features_names)
        return self.graphs[id_sample]

    def make_paths(paths, num_paths, work_dir, pref, suf):
        if paths is None:
            paths = [''] * self.num_samples
            for i in range(self.num_samples):
                paths[i] = pref + str(i) + suf
        assert(len(paths) == num_paths)
        
        for i in range(paths):
            paths[i] = os.path.join(work_dir, paths[i])
        return paths

    
    def set_graph_paths(self, paths = None, work_dir = 'graphs'):
        self.graph_paths = make_paths(paths, num_samples, work_dir, 'graph_id_sample_', '.npz')

    def set_parenclitic_paths(self, paths = None, work_dir = 'parenclitics'):
        self.parenclitic_paths = make_paths(paths, num_samples, work_dir, 'parenclitic_id_sample_', '.pkl')
        
    def get_graph_paths(self):
        return self.graph_paths        

    def get_parenclitic_paths(self):
        return self.parenclitic_paths
        
    def save_graphs(self):
        if self.graph_paths is None:
            self.set_graph_paths()
        for i, graph_path in enumerate(self.graph_paths):
            np.savez_compressed(graph_path, M = self.M[i, :], D = self.D[i, :], E = self.E, \
                                num_samples = self.num_samples, num_features = self.num_features)

    def load_graph(self, id_sample = 0):
        graph_path = self.graph_paths[id_sample]
        data = np.load(graph_path)
        M, D, E = data['M'], data['D'], data['E']
        num_samples, num_features = data['num_samples'], data['num_features']
        return M, D, E, num_samples, num_features
            
    def get_graphs(self, features_names = None):
        self.load_part_graphs()
        for id_sample in range(self.num_samples):
            self.get_graph(id_sample = id_sample, features_names = features_names)
        return self.graphs
        
    def calc_parenclitic(self, id_sample = None, need_weights = True, get_big = True):
        if id_sample is None:
            for id_sample in range(self.num_samples):
                self.calc_parenclitic(id_sample)
        else:
            g = self.get_graph(id_sample)
            if self.parenclitics is None:
                self.parenclitics = [None] * self.num_samples
            self.parenclitics[id_sample] = self.calculate_metrics(g.copy(), need_weights = need_weights, get_big = get_big)
        return self
            
    def get_parenclitic(self):
        if self.parenclitics is None:
            self.calc_parenclitic()
                        
        return pd.concat(self.parenclitics, ignore_index=True, sort=True)
        
    def save_parenclitic(self, id_sample = None):
        if self.parenclitic_paths is None:
            self.set_parenclitic_paths()
        if id_sample is None:
            for id_sample, parenclitic_path in enumerate(self.parenclitic_paths):
                if not self.parenclitics[id_sample] is None:
                    self.parenclitics[id_sample].to_pickle(parenclitic_path, compression = "gzip")
        else:
            if not self.parenclitics[id_sample] is None:
                self.parenclitics[id_sample].to_pickle(parenclitic_paths[id_sample], compression = "gzip")
            
    def robustness(self, g, weights = None):
        cnt = 0
        while g.ecount() > 0:
            degrees = np.array(g.strength(weights = weights))
            g.delete_vertices(np.argmax(degrees))
            cnt = cnt + 1
        return cnt
                
    def calculate_metrics(self, g, need_weights = True, get_big = True):
        if self.verbose == 1:
            print('Metrics')
            sys.stdout.flush()

        if need_weights:
            weights = 'weight'
        else:
            weights = None
            
        if g.ecount() == 0:
            weights = None

        parenclitic = pd.DataFrame(index=[0])
        start = timeit.default_timer()

        degrees = np.array(g.strength(weights = weights))
        if get_big: 
            parenclitic['degrees'] = [degrees]
        parenclitic['min_degrees'] = np.min (degrees)
        parenclitic['max_degrees'] = np.max (degrees)
        parenclitic['mean_degrees'] = np.mean(degrees)
        parenclitic['std_degrees'] = np.std (degrees)
        degrees = None

        stop = timeit.default_timer()
        if self.verbose == 1:
            print('Parenclitic 1', stop - start)
            sys.stdout.flush()
            
        start = timeit.default_timer()

        shortest_paths = np.array(g.shortest_paths(weights = weights))
        shortest_paths = shortest_paths[(shortest_paths > 0) & (shortest_paths != np.inf)]
        sys.stdout.flush()

        efficiency = 0
        if len(shortest_paths) > 0:
            efficiency = (1.0 / shortest_paths).sum() / (g.vcount() * (g.vcount() - 1))
        # In paper Latora V., Marchiori M.: Efficient behavior of small-world networks. Phys. Rev. Lett. 87 (Article No. 198701) (2001)
        # suggested to normalize by efficiency for threshold_p = 0 (cause graph has all edges when thr_p = 0)
        parenclitic['efficiency'] = efficiency
        shortest_paths = None

        stop = timeit.default_timer()
        if self.verbose == 1:
            print('Parenclitic 2', stop - start)
            sys.stdout.flush()
            
        start = timeit.default_timer()

        betweenness = g.betweenness(weights = weights)
        if get_big: 
            parenclitic['betweenness'] = [np.array(betweenness)]
        parenclitic['min_betweenness'] = np.min (betweenness)
        parenclitic['max_betweenness'] = np.max (betweenness)
        parenclitic['mean_betweenness'] = np.mean(betweenness)
        parenclitic['std_betweenness'] = np.std (betweenness)
        betweenness = None

        stop = timeit.default_timer()
        if self.verbose == 1:        
            print('Parenclitic 3', stop - start)
            sys.stdout.flush()
            
        
        start = timeit.default_timer()

        closeness = g.closeness(weights = weights)
        if get_big: 
            parenclitic['closeness'] = [np.array(closeness)]
        parenclitic['min_closeness'] = np.min (closeness)
        parenclitic['max_closeness'] = np.max (closeness)
        parenclitic['mean_closeness'] = np.mean(closeness)
        parenclitic['std_closeness'] = np.std (closeness)
        closeness = None

        stop = timeit.default_timer()
        if self.verbose == 1:
            print('Parenclitic 4', stop - start)
            sys.stdout.flush()

        start = timeit.default_timer()

        pagerank = g.pagerank(weights = weights)
        if get_big: 
            parenclitic['pagerank'] = [np.array(pagerank)]
        parenclitic['min_pagerank'] = np.min (pagerank)
        parenclitic['max_pagerank'] = np.max (pagerank)
        parenclitic['mean_pagerank'] = np.mean(pagerank)
        parenclitic['std_pagerank'] = np.std (pagerank)
        pagerank = None

        stop = timeit.default_timer()
        if self.verbose == 1:
            print('Parenclitic 5', stop - start)
            sys.stdout.flush()
            
        start = timeit.default_timer()

        # alpha centrality with alpha = 1
        
        eigenvector_centrality = g.eigenvector_centrality(weights = weights)
        if get_big: 
            parenclitic['eigenvector_centrality'] = [np.array(eigenvector_centrality)]
        parenclitic['min_eigenvector_centrality'] = np.min(eigenvector_centrality)
        parenclitic['max_eigenvector_centrality'] = np.max(eigenvector_centrality)
        parenclitic['mean_eigenvector_centrality'] = np.mean(eigenvector_centrality)
        parenclitic['std_eigenvector_centrality'] = np.std(eigenvector_centrality)
        eigenvector_centrality = None

        stop = timeit.default_timer()
        if self.verbose == 1:
            print('Parenclitic centrality', stop - start)
            sys.stdout.flush()
            
        start = timeit.default_timer()
        
        largest = g.clusters().giant()    
        m = np.array(largest.get_adjacency().data)
        sys.stdout.flush()

        eigenvalues, eigenvectors = LA.eig(m)
        #Suppose symmetric matrix
        eigenvalues = np.real(eigenvalues)
        eigenvectors = np.real(eigenvectors)
        if self.verbose == 1:
            print('Eigenvectors', stop - start)
            sys.stdout.flush()

        eigenvalues_intervals = np.diff(np.sort(eigenvalues)) 
        if self.verbose == 1:
            print('intervals', stop - start)
            sys.stdout.flush()

        eigenvalues_intervals_normalized = eigenvalues_intervals / np.mean(eigenvalues_intervals)

        if self.verbose == 1:
            print('normalized', stop - start)
            sys.stdout.flush()
        
        if get_big: 
            parenclitic['eigenvalues'] = [np.array(eigenvalues)]
            parenclitic['eigenvalues_intervals'] = [np.array(eigenvalues_intervals)]
            parenclitic['eigenvalues_intervals_normalized'] = [np.array(eigenvalues_intervals_normalized)]

        stop = timeit.default_timer()
        if self.verbose == 1:
            print('Parenclitic: eigenvalues', stop - start)
            sys.stdout.flush()
        
        IPR = np.sum(np.power(eigenvectors, 4), axis=0) / np.power(np.sum(np.power(eigenvectors, 2), axis=0), 2)
        if get_big: 
            parenclitic['IPR'] = [np.array(IPR)]
        parenclitic['max_IPR'] = np.max(IPR)
        parenclitic['mean_IPR'] = np.mean(IPR)

        stop = timeit.default_timer()
        if self.verbose == 1:
            print('Parenclitic 7', stop - start)
            sys.stdout.flush()

        eigenvectors = None
        eigenvalues = None
        IPR = None
        eigenvalues_intervals = None
        eigenvalues_intervals_normalized = None
        
        start = timeit.default_timer()
        parenclitic['num_edges'] = g.ecount()

        if g.ecount() > 0:
            weights = np.array(g.es["weight"])
            if get_big: 
                parenclitic['weights'] = [np.array(weights)]
            parenclitic['sum_weights'] = np.sum (weights)
            parenclitic['min_weights'] = np.min (weights)
            parenclitic['max_weights'] = np.max (weights)
            parenclitic['mean_weights'] = np.mean(weights)
            parenclitic['std_weights'] = np.std (weights)
            weights = None

        stop = timeit.default_timer()
        if self.verbose == 1:
            print('Parenclitic 8', stop - start)
            sys.stdout.flush()

        start = timeit.default_timer()
    #    parenclitic['community_edge_betweenness_optimal'] = g.community_edge_betweenness().optimal_count
        stop = timeit.default_timer()
        if self.verbose == 1:
            print('Parenclitic 9', stop - start)
            sys.stdout.flush()
            
        start = timeit.default_timer()
        parenclitic['robustness'] = self.robustness(g, weights)
        stop = timeit.default_timer()
        if self.verbose == 1:
            print('Parenclitic 10', stop - start)
            sys.stdout.flush()

        return parenclitic
        
    @staticmethod
    def metric_names():
        metric_names = {}
        metric_names['degrees'] = 'Degrees'
        metric_names['min_degrees'] = 'Min degrees'
        metric_names['max_degrees'] = 'Max degrees'
        metric_names['mean_degrees'] = 'Mean degrees'
        metric_names['std_degrees'] = 'Std degrees'
        
        metric_names['efficiency'] = 'Efficiency'
        metric_names['betweenness'] = 'Betweenness'
        metric_names['min_betweenness'] = 'Min betweenness'
        metric_names['max_betweenness'] = 'Max betweenness'
        metric_names['mean_betweenness'] = 'Mean betweenness'
        metric_names['std_betweenness'] = 'Std betweenness'
        
        metric_names['closeness'] = 'Closeness'
        metric_names['min_closeness'] = 'Min closeness'
        metric_names['max_closeness'] = 'Max closeness'
        metric_names['mean_closeness'] = 'Mean closeness'
        metric_names['std_closeness'] = 'Std closeness'
        
        metric_names['pagerank'] = 'Pagerank'
        metric_names['min_pagerank'] = 'Min pagerank'
        metric_names['max_pagerank'] = 'Max pagerank'
        metric_names['mean_pagerank'] = 'Mean pagerank'
        metric_names['std_pagerank'] = 'Std pagerank'
        
        metric_names['eigenvalues'] = 'Eigenvalues'
        metric_names['min_eigenvector_centrality'] = 'Min eigenvector centrality'
        metric_names['max_eigenvector_centrality'] = 'Max eigenvector centrality'
        metric_names['mean_eigenvector_centrality'] = 'Mean eigenvector centrality'
        metric_names['std_eigenvector_centrality'] = 'Std eigenvector centrality'
        metric_names['num_edges'] = 'Number of edges'

        metric_names['eigenvalues_intervals'] = 'Eigenvalues intervals'
        metric_names['eigenvalues_intervals_normalized'] = 'Eigenvalues intervals normalized'

        metric_names['IPR'] = 'IPR'
        metric_names['max_IPR'] = 'Max IPR'
        metric_names['mean_IPR'] = 'Mean IPR'

        metric_names['weights'] = 'Weights'
        metric_names['sum_weights'] = 'Sum weights'
        metric_names['min_weights'] = 'Min weights'
        metric_names['max_weights'] = 'Max weights'
        metric_names['mean_weights'] = 'Mean weights'
        metric_names['std_weights'] = 'Std weights'
        
        metric_names['community_edge_betweenness_optimal'] = 'Community edge betweenness: optimal count'
            
        metric_names['robustness'] = 'Robustness'
        return metric_names    
