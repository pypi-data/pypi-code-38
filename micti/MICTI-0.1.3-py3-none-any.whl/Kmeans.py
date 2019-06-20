import numpy as np
import pandas as pa
import time
from sklearn.metrics import pairwise_distances
from scipy.sparse import csr_matrix

class Kmeans:
    def __init__(self,data,k,geneNames,cellNames,cluster_label=None,seed=None):
        self.data=data
        self.k=k
        self.geneNames=geneNames
        self.cellNames=cellNames
        self.seed=seed
        self.centroids=None
        self.cluster_assignment=None
        self.cluster_label=cluster_label
        self.heterogeneity=0.0
        self.get_initial_centroids()
        self.heterogeneities=None

        
    def getCentroids(self):
        return self.centroids
        
    def getCluster_assignment(self):
        return self.cluster_assignment

    def getHeterogenity(self):
        return self.heterogeneity
    
    def getHetrogenities(self):
        return self.heterogeneities
 
    def get_initial_centroids(self):
        '''Randomly choose k data points as initial centroids'''
        if self.seed is not None: # useful for obtaining consistent results
            np.random.seed(self.seed)
        n = self.data.shape[0] # number of data points
        
        # Pick K indices from range [0, N).
        rand_indices = np.random.randint(0, n, self.k)
    
        # Keep centroids as dense format, as many entries will be nonzero due to averaging.
        # As long as at least one document in a cluster contains a word,
        # it will carry a nonzero weight in the TF-IDF vector of the centroid.
        centroids = self.data[rand_indices,:].toarray()
        self.centroids=centroids
        return centroids
    
    def smart_initialize(self):
        '''Use k-means++ to initialize a good set of centroids'''
        if self.seed is not None: # useful for obtaining consistent results
            np.random.seed(self.seed)
        centroids = np.zeros((self.k, self.data.shape[1]))
        # Randomly choose the first centroid.
        # Since we have no prior knowledge, choose uniformly at random
        idx = np.random.randint(self.data.shape[0])
        centroids[0] = self.data[idx,:].toarray()
        # Compute distances from the first centroid chosen to all the other data points
        squared_distances = pairwise_distances(self.data, centroids[0:1], metric='euclidean').flatten()**2
        for i in range(1, self.k):
            # Choose the next centroid randomly, so that the probability for each data point to be chosen
            # is directly proportional to its squared distance from the nearest centroid.
            # Roughtly speaking, a new centroid should be as far as from ohter centroids as possible.
            idx = np.random.choice(self.data.shape[0], 1, p=squared_distances/sum(squared_distances))
            centroids[i] = self.data[idx,:].toarray()
            # Now compute distances from the centroids to all data points
            squared_distances = np.min(pairwise_distances(self.data, centroids[0:i+1], metric='euclidean')**2,axis=1)
        self.centroids=centroids
        return centroids
        
    def assign_clusters(self):
    
        # Compute distances between each data point and the set of centroids:
        # Fill in the blank (RHS only)
        distances_from_centroids = pairwise_distances(self.data,self.centroids,metric='euclidean')
    
        # Compute cluster assignments for each data point:
        # Fill in the blank (RHS only)
        cluster_assignment = np.apply_along_axis(np.argmin, 1, distances_from_centroids)
        self.cluster_assignment=cluster_assignment
        return cluster_assignment
    
    def revise_centroids(self):
        new_centroids = []
        for i in range(self.k):
            # Select all data points that belong to cluster i. Fill in the blank (RHS only)
            member_data_points = self.data[self.cluster_assignment==i]
            # Compute the mean of the data points. Fill in the blank (RHS only)
            centroid = member_data_points.mean(axis=0)
        
            # Convert numpy.matrix type to numpy.ndarray type
            centroid = centroid.A1
        
            new_centroids.append(centroid)
        new_centroids = np.array(new_centroids)
        self.centroids=new_centroids
        return new_centroids
    
    def kmeans(self, maxiter, record_heterogeneity=None, verbose=False):
        '''This function runs k-means on given data and initial set of centroids.
           maxiter: maximum number of iterations to run.
           record_heterogeneity: (optional) a list, to store the history of heterogeneity as function of iterations
                             if None, do not store the history.
           verbose: if True, print how many data points changed their cluster labels in each iteration'''
        centroids = self.centroids[:]
        prev_cluster_assignment = None
        for itr in range(int(maxiter)):        
            if verbose:
                print(itr)
            # 1. Make cluster assignments using nearest centroids
            # YOUR CODE HERE
            cluster_assignment = self.assign_clusters() 
            # 2. Compute a new centroid for each of the k clusters, averaging all data points assigned to that cluster.
            # YOUR CODE HERE
            centroids = self.revise_centroids()  
            # Check for convergence: if none of the assignments changed, stop
            if prev_cluster_assignment is not None and \
              (prev_cluster_assignment==self.cluster_assignment).all():
                break
            # Print number of new assignments 
            if prev_cluster_assignment is not None:
                num_changed = np.sum(prev_cluster_assignment!=self.cluster_assignment)
                if verbose:
                    print('    {0:5d} elements changed their cluster assignment.'.format(num_changed))   
            # Record heterogeneity convergence metric
            if record_heterogeneity is not None:
                # YOUR CODE HERE
                score = compute_heterogeneity(self.data, self.k, centroids, cluster_assignment)
                record_heterogeneity.append(score)
            prev_cluster_assignment = cluster_assignment[:]
        self.centroids=centroids
        self.cluster_assignment=cluster_assignment
        return centroids, cluster_assignment
    
    def kmeans_multiple_runs(self, maxiter, num_runs, seed_list=None, verbose=False):
        
        heterogeneity = {}
        min_heterogeneity_achieved = float('inf')
        best_seed = None
        final_centroids = None
        final_cluster_assignment = None
    
        for i in range(num_runs):
        
            # Use UTC time if no seeds are provided 
            if seed_list is not None: 
                seed = seed_list[i]
                np.random.seed(seed)
            else: 
                seed = int(time.time())
                np.random.seed(seed)
        
            # Use k-means++ initialization
            
            self.initial_centroids = self.smart_initialize()
        
            # Run k-means
 
            centroids, cluster_assignment = self.kmeans(maxiter, record_heterogeneity=None, verbose=False)
        
            # To save time, compute heterogeneity only once in the end
      
            heterogeneity[seed] = self.compute_heterogeneity()
        
            if verbose:
                print('seed={0:06d}, heterogeneity={1:.5f}'.format(seed, heterogeneity[seed]))
                sys.stdout.flush()
        
            # if current measurement of heterogeneity is lower than previously seen,
            # update the minimum record of heterogeneity.
            if heterogeneity[seed] < min_heterogeneity_achieved:
                min_heterogeneity_achieved = heterogeneity[seed]
                best_seed = seed
                final_centroids = centroids
                final_cluster_assignment = cluster_assignment
        self.centroids=final_centroids
        self.cluster_assignment=final_cluster_assignment
        self.heterogeneities=heterogeneity
        return final_centroids, final_cluster_assignment
    
    def clusterEvaluation(self):
        clustMaxDist={}
        clustMinDist={}
        clustMeanDist={}
        for i in range(self.k):
            binMaxDist=[]
            binMinDist=[]
            binMeanDist=[]
            for j in np.concatenate(np.argwhere(self.cluster_assignment==i)):
                dist=pairwise_distances(self.data[np.concatenate(np.argwhere(self.cluster_assignment==i))], self.data[j], metric='euclidean').flatten()
                dist=dist**2
                binMaxDist.append(np.max(dist))
                binMinDist.append(np.min(dist))
                binMeanDist.append(np.mean(dist))
            clustMaxDist[i]=np.max(binMaxDist)
            clustMinDist[i]=np.min(binMinDist)
            clustMeanDist[i]=np.mean(binMeanDist)
        plt.figure(figsize=(7,4.5))
        plt.plot(clustMaxDist.keys(),clustMaxDist.values(), linewidth=2, label='Maximum distance among clusters')
        plt.plot(clustMaxDist.keys(),clustMinDist.values(), linewidth=2, label='Minimum distance among clusters')
        plt.plot(clustMaxDist.keys(),clustMeanDist.values(), linewidth=2, label='avarage distance among clusters')
        plt.xlabel('Cluster number')
        plt.ylabel('Eculidean distance')
        plt.legend(loc='best', prop={'size':15})
        plt.rcParams.update({'font.size':16})
        plt.tight_layout()
        plt.show()
        return np.sum(clustMeanDist)

    def compute_heterogeneity(self):
    
        heterogeneity = 0.0
        for i in range(self.k):
            # Select all data points that belong to cluster i. Fill in the blank (RHS only)
            member_data_points = self.data[self.cluster_assignment==i, :]
        
            if member_data_points.shape[0] > 0: # check if i-th cluster is non-empty
            # Compute distances from centroid to data points (RHS only)
                distances = pairwise_distances(member_data_points, [self.centroids[i]], metric='euclidean')
                squared_distances = distances**2
                heterogeneity += np.sum(squared_distances)
        self.heterogeneity=heterogeneity
        return heterogeneity
        
    def plot_k_vs_heterogeneity(self, k_values, heterogeneity_values):
        plt.figure(figsize=(7,4))
        plt.plot(k_values, heterogeneity_values, linewidth=4)
        plt.xlabel('K')
        plt.ylabel('Heterogeneity')
        plt.title('K vs. Heterogeneity')
        plt.rcParams.update({'font.size': 16})
        plt.tight_layout()
        plt.show()
        return None
    def get_cluster_data(self, cluster_number):
        return self.data[np.in1d(np.array(self.cluster_assignment), cluster_number),:], self.cellNames[np.in1d(np.array(self.cluster_assignment), cluster_number)]
    
    def select_K(self):
        cluster_centroids={}
        cluster_assignments={}
        hetroginity_score=float('inf')
        delta_k={}
        max_K_value=self.k
        hetro_Per_K={}
        deltaHetro=None
        for i in range(max_K_value):
            self.k=i+1
            print("going for k=", i+1)
            cluster_centroid, cluster_assignment=self.kmeans_multiple_runs(5,100)
            hetro=self.compute_heterogeneity()
            hetro_Per_K[i+1]=hetro
            if hetro<hetroginity_score:
                if hetroginity_score==float('inf'):
                    hetroginity_score=hetro
                    deltaHetro=0
                else:
                    deltaHetro=hetroginity_score-hetro
                    hetroginity_score=hetro
                    cluster_centroids[i+1]=cluster_centroid
                    cluster_assignments[i+1]=cluster_assignment
                    delta_k[i+1]=deltaHetro
        best_k=sum(delta_k.values()[1:]>sum(delta_k.values())/(2*len(delta_k.values())))
        print("best k value:", best_k, delta_k)
        self.centroids=cluster_centroids[best_k]
        self.cluster_assignment=cluster_assignments[best_k]
        self.k=best_k
        self.getVisualization(method="tsne")
        self.plot_k_vs_heterogeneity(hetro_Per_K.keys(), hetro_Per_K.values())
        return self.k 

