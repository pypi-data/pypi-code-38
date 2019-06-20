import numpy as np
import pandas as pa
from sklearn.metrics import pairwise_distances
from scipy.sparse import csr_matrix
from scipy.sparse import spdiags
from scipy import stats
from scipy.stats import multivariate_normal
from copy import deepcopy
from MICTI import Kmeans

class GM:
    def __init__(self, data,k,geneNames,cellNames,initial_kmean_Model=None):
        self.data=data
        self.k=k
        self.geneNames=geneNames
        self.cellNames=cellNames
        self.mean=None
        self.weight=None
        self.covs=None
        self.out=None
        self.initial_kmean_Model=initial_kmean_Model
        self.cluster_assignment=None
        self.setMeans()
        self.setWeights()
        self.creatCovMat()
        self.heterogeneity=None
        return 
    
    def diag(self,array):
        n = len(array)
        return spdiags(array, 0, n, n)

    def logpdf_diagonal_gaussian(self, x, mean, cov):
        '''
        Compute logpdf of a multivariate Gaussian distribution with diagonal covariance at a given point x.
        A multivariate Gaussian distribution with a diagonal covariance is equivalent
        to a collection of independent Gaussian random variables.

        x should be a sparse matrix. The logpdf will be computed for each row of x.
        mean and cov should be given as 1D numpy arrays
        mean[i] : mean of i-th variable
        cov[i] : variance of i-th variable'''

        n = x.shape[0]
        dim = x.shape[1]
        assert(dim == len(mean) and dim == len(cov))

        # multiply each i-th column of x by (1/(2*sigma_i)), where sigma_i is sqrt of variance of i-th variable.
        scaled_x = x.dot(self.diag(1./(2*np.sqrt(cov))) )
        # multiply each i-th entry of mean by (1/(2*sigma_i))
        scaled_mean = mean/(2*np.sqrt(cov))

        # sum of pairwise squared Eulidean distances gives SUM[(x_i - mean_i)^2/(2*sigma_i^2)]
        return -np.sum(np.log(np.sqrt(2*np.pi*cov))) - pairwise_distances(scaled_x, [scaled_mean], 'euclidean').flatten()**2
    def initial_cluster_assignment(self):
        initial_kmean_Model=Kmeans.Kmeans(self.data, self.k, self.geneNames, self.cellNames)
        return initial_kmean_Model

    def creatCovMat(self):
        num_clusters=len(self.means)
        covs = []
        for i in range(self.k):
            member_rows = self.data[self.cluster_assignment==i]
            cov = (member_rows.multiply(member_rows) - 2*member_rows.dot(self.diag(self.means[i]))).sum(axis=0).A1 / member_rows.shape[0] \
            + self.means[i]**2
            cov[cov < 1e-8] = 1e-8
            covs.append(cov)
        self.covs=covs
        return covs
    
    def setMeans(self):
        #np.random.seed(5)
        num_clusters = self.k

        # Use scikit-learn's k-means to simplify workflow
        #kmeans_model = KMeans(n_clusters=num_clusters, n_init=5, max_iter=400, random_state=1, n_jobs=-1) # uncomment to use parallelism -- may break on your installation
        if self.initial_kmean_Model == None:
            kmeans_model = self.initial_cluster_assignment()
            centroids, cluster_assignment = kmeans_model.kmeans(10)
        else:
            centroids=self.initial_kmean_Model.centroids
            cluster_assignment=self.initial_kmean_Model.cluster_assignment
            
        means = [centroid for centroid in centroids]
        self.means=means
        self.cluster_assignment=cluster_assignment
        return
    
    def setWeights(self):
        num_docs = self.data.shape[0]
        weights = []
        for i in range(self.k):
        # Compute the number of data points assigned to cluster i:
            num_assigned = self.data[self.cluster_assignment==i,:].shape[0] # YOUR CODE HERE
            w = float(num_assigned) / num_docs
            weights.append(w)
        self.weights=weights
        return 
    
    def log_sum_exp(self,x, axis):
        '''Compute the log of a sum of exponentials'''
        x_max = np.max(x, axis=axis)
        if axis == 1:
            return x_max + np.log( np.sum(np.exp(x-x_max[:,np.newaxis]), axis=1) )
        else:
            return x_max + np.log( np.sum(np.exp(x-x_max), axis=0) )
    
    def EM_for_high_dimension(self,cov_smoothing=1e-5, maxiter=int(1e3), thresh=1e-4, verbose=False):
        # cov_smoothing: specifies the default variance assigned to absent features in a cluster.
        #                If we were to assign zero variances to absent features, we would be overconfient,
        #                as we hastily conclude that those featurese would NEVER appear in the cluster.
        #                We'd like to leave a little bit of possibility for absent features to show up later.
        n = self.data.shape[0]
        dim = self.data.shape[1]
        data=deepcopy(self.data)
        mu = deepcopy(self.means)
        Sigma = deepcopy(self.covs)
        K = len(mu)
        weights = np.array(self.weights)

        ll = None
        ll_trace = []

        for i in range(maxiter):
            # E-step: compute responsibilities
            logresp = np.zeros((n,K))
            for k in range(K):
                logresp[:,k] = np.log(weights[k]) + self.logpdf_diagonal_gaussian(data, mu[k], Sigma[k])
            ll_new = np.sum(self.log_sum_exp(logresp, axis=1))
            if verbose:
                print(ll_new)
            logresp -= np.vstack(self.log_sum_exp(logresp, axis=1))
            resp = np.exp(logresp)
            counts = np.sum(resp, axis=0)

            # M-step: update weights, means, covariances
            weights = counts / np.sum(counts)
            for k in range(K):
                mu[k] = (self.diag(resp[:,k]).dot(data)).sum(axis=0)/counts[k]
                mu[k] = mu[k].A1

                Sigma[k] = self.diag(resp[:,k]).dot( data.multiply(data)-2*data.dot(self.diag(mu[k])) ).sum(axis=0) \
                       + (mu[k]**2)*counts[k]
                Sigma[k] = Sigma[k].A1 / counts[k] + cov_smoothing*np.ones(dim)

            # check for convergence in log-likelihood
            ll_trace.append(ll_new)
            if ll is not None and (ll_new-ll) < thresh and ll_new > -np.inf:
                ll = ll_new
                break
            else:
                ll = ll_new

        out = {'weights':weights,'means':mu,'covs':Sigma,'loglik':ll_trace,'resp':resp}
        self.out=out
        return out
    
    def getResult(self):
        return self.out

    def compute_heterogeneity(self):
        heterogeneity = 0.0
        for i in range(self.k):
            # Select all data points that belong to cluster i. Fill in the blank (RHS only)
            member_data_points = self.data[self.cluster_assignment==i, :]

            if member_data_points.shape[0] > 0: # check if i-th cluster is non-empty
            # Compute distances from centroid to data points (RHS only)
                distances = pairwise_distances(member_data_points, [self.getResult["means"][i]], metric='euclidean')
                squared_distances = distances**2
                heterogeneity += np.sum(squared_distances)
        self.heterogeneity=heterogeneity
        return heterogeneity

    
    def getVisualization(self,dim=2,method="PCA"):

        if method=="PCA":
            if dim>3:
                print("Please give at most three dimentions")
            else:
                svd = TruncatedSVD(n_components=dim)
                svd_fit = svd.fit(self.data)
                svdTransform=svd.fit_transform(self.data)
                if dim==3:
                    fig=p.figure()
                    ax = p3.Axes3D(fig)
                    ax.scatter(svdTransform[:,0], svdTransform[:,1], svdTransform[:,2], c=self.cluster_assignment)
                    ax.set_xlabel("PCA1")
                    ax.set_ylabel("PCA2")
                    ax.set_zlabel("PCA3")
                    fig.add_axes(ax)
                    plt.show()
                elif dim==2:
                    plt.scatter(svdTransform[:,0], svdTransform[:,1], c=self.cluster_assignment)
                    plt.xlabel("PCA1")
                    plt.ylabel("PCA2")
                    plt.suptitle("Gaussian mixture with k={0:d}".format(self.k), fontsize=8)
                    plt.show()
                else:
                    print("dimentionality error")
        elif method=="tsne":
                if dim>3:
                    print("Please give at most three dimentions")
                else:
                    svd = TruncatedSVD(n_components=50)
                    svd_fit = svd.fit(self.data)
                    svdTransformTsne=svd.fit_transform(self.data)
                    X_tsne=TSNE(n_components=dim, random_state=0)
                    x_tsne=X_tsne.fit_transform(svdTransformTsne)
                    if dim==3:
                        fig=p.figure()
                        ax = p3.Axes3D(fig)
                        ax.scatter(x_tsne[:,0], x_tsne[:,1], x_tsne[:,2], c=self.cluster_assignment)
                        ax.set_xlabel("tsne1")
                        ax.set_xlabel("tsne2")
                        ax.set_xlabel("tsne3")
                        fig.add_axes(ax)
                        p.show()
                    elif dim==2:
                        plt.scatter(x_tsne[:,0], x_tsne[:,1], c=self.cluster_assignment)
                        plt.xlabel("tsne1")
                        plt.ylabel("tsne2")
                        plt.suptitle("Gaussian mixture with k={0:d}".format(self.k), fontsize=8)
                        plt.savefig("GM_Plot.png", format="png")
                        plt.show()
                    else:
                        print("dimetionality error")
        else:
            print("Please give method==pca or method=tsne")
                
        return None
    
    def visualize_EM_clusters(self):
        print('')
        print('==========================================================')

        num_clusters = len(self.out["means"])
        for c in range(self.k):
            print('Cluster {0:d}: Largest mean & variance in cluster '.format(c) + "   ")
            print('\n{0: <12}{1: <12}{2: <12}'.format('Gene', 'Mean', 'Variance'))
        
            # The k'th element of sorted_word_ids should be the index of the word 
            # that has the k'th-largest value in the cluster mean. Hint: Use np.argsort().
            sorted_word_ids = np.argsort(-self.out["means"][c])  # YOUR CODE HERE
            print(np.sum(self.cluster_assignment==c))
            for i in sorted_word_ids[:5]:
                print('{0: <12}{1:<10.2e}{2:10.2e}'.format(self.geneNames[i], 
                                                       self.out["means"][c][i],
                                                       self.out["covs"][c][i]))
            print('\n==========================================================')
    
    
