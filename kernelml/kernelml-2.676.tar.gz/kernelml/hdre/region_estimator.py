import time
import numpy as np
import numpy
import kernelml
import sys
from .hdr_helpers_bycython import *

class ArgumentError(Exception):
    pass

class VersionError(Exception):
    pass

### HDRE
class HighDensityRegions():

    def __init__(self,number_of_clusters, bins_per_dimension=21, number_of_random_simulations=500, number_of_realizations=10, smoothing_parameter=2.0):

        self.num_clusters = number_of_clusters
        self.simulations = number_of_random_simulations
        self.realizations = number_of_realizations
        self.smoothing_parameter = smoothing_parameter
        self.bins_per_dim = bins_per_dimension
        self.kmldata = None
        self.norm = 1
    
        if (self.bins_per_dim/2 == self.bins_per_dim//2+1):
            raise ArgumentError("The number of bins per dimensions must be an odd integer")

    def optimize(self,X,y=None,cost=None,agg_func='count',dview=None):

        def loss_func(X,y,w,args):
            np=numpy
            return hdre_loss(X,y,w,args)
        
        self.num_dim = X.shape[1]
        
        maxs = np.max(X,axis=0)
        mins = np.min(X,axis=0)
        widths = (maxs-mins)/(self.bins_per_dim)
        max_lim = maxs.copy()
        min_lim = mins.copy()
        maxs+=int(np.sqrt(self.bins_per_dim))*widths
        mins-=int(np.sqrt(self.bins_per_dim))*widths
        widths = (maxs-mins)/(self.bins_per_dim)
        
        dim_bins = [np.linspace(m0,m1,self.bins_per_dim) for m0,m1 in zip(mins,maxs)]
        dim_combos = [(i,j) for i in range(X.shape[1]) for j in range(X.shape[1]) if j>i]
        self.dim_combos = dim_combos
        
        half = (self.bins_per_dim)//2
        mesh = np.meshgrid(*[np.arange(-(half),half+1,1) for _ in range(2)])
        mesh = [d**2 for d in mesh]
        sigma = self.smoothing_parameter
        kernel = np.exp(-sum(mesh)/(2*sigma**2))/np.sqrt(2*np.pi*sigma**2)
        kernel = kernel/np.sum(kernel)
        fftkernel = np.fft.fftn(kernel)

        combo_len = len(dim_combos)
        pdf_combos = np.zeros((combo_len,self.bins_per_dim,self.bins_per_dim))
        bin_combos = np.zeros((combo_len,self.bins_per_dim,2))
        count=0
        for i,j in dim_combos:
            _X_ = X[:,[i,j]]
            bins3 = [dim_bins[i],dim_bins[j]]
#             bins3 = [np.concatenate([[-np.inf],_bins_,[np.inf]]) for _bins_ in bins3]
            bin_combos[count] = np.column_stack(bins3)
            data,_ = hdre_histogram(_X_,y,agg_func=agg_func,cost=cost,bins=bins3)
            data=data/np.sum(data)
            pdf_combos[count] = np.fft.fftshift(np.real(np.fft.ifftn(np.fft.fftn(data)*fftkernel)))
            count+=1

        self.kde_target = pdf_combos
        
        cycles = 100

        #The number of total simulations per realization = number of cycles * numer of simulations

        zcore = 2.0
        volume = 10 + self.num_dim
        volatility = 1
        zscore = 1


        param_to_dim = np.arange(0,self.num_dim*self.num_clusters)%self.num_dim

        args = [dim_combos,pdf_combos,bin_combos,fftkernel,min_lim,max_lim,param_to_dim,self.num_dim,widths]

        if self.kmldata is None:
            self.kml = kernelml.KernelML(
                 prior_sampler_fcn=hdre_prior_sampler,
                 posterior_sampler_fcn=None,
                 intermediate_sampler_fcn=None,
                 mini_batch_sampler_fcn=None,
                 parameter_transform_fcn=hdre_parameter_transform,
                 batch_size=None)

            if dview is not None:
                if not sys.version_info[:2] == (3, 5):
                    raise VersionError("Python 3.5 is required for parallel computing")
                self.kml.use_ipyparallel(dview)

        self.kml.optimize(X[:1],np.array([[]]),loss_function=loss_func,
                                        convergence_z_score=3.0,
                                        min_loss_per_change=0.0,
                                        number_of_parameters=self.num_clusters*self.num_dim+self.num_dim,
                                        args=args,
                                        number_of_realizations=self.realizations,
                                        number_of_random_simulations=self.simulations,
                                        update_volume=volume,
                                        update_volatility=volatility,
                                        number_of_cycles=cycles,
                                        print_feedback=True)

        self.kmldata = self.kml.kmldata
        self.kml.load_kmldata(self.kmldata)
        
        self.kde_estimate = np.zeros((combo_len,self.bins_per_dim,self.bins_per_dim))
        var = self.variance_
        mean = self.centroids_

        count=0
        for i,j in self.dim_combos:
            bins = bin_combos[count,:,0].shape[0]
            bins3 = [bin_combos[count,:,0],bin_combos[count,:,1]]
            
            data1 = np.random.uniform(0,1e-3,size=(bins,bins))
            for k in range(self.num_clusters):

                pdf = uniform_kernel(bins3[0],mean[k,[i]],var[i]).dot(uniform_kernel(bins3[1],mean[k,[j]],var[j]).T)
                data1 += pdf

            data1=data1/np.sum(data1)
            pdf = np.fft.fftshift(np.real(np.fft.ifftn(np.fft.fftn(data1)*fftkernel)))
            self.kde_estimate[count] = np.flipud(pdf)
            self.kde_target[count] = np.flipud(self.kde_target[count])
            count+=1
    
    @property
    def variance_(self):
        w = self.kmldata.best_weight_vector
        return np.abs(w[:self.num_dim]).reshape(-1,1)

    @property
    def centroids_(self):
        w = self.kmldata.best_weight_vector.flatten()
        w = w[self.num_dim:]
        return w.reshape((w.size//self.num_dim,self.num_dim))

    def get_polygons(self,i,j,k,pad=1):
        var = self.variance_
        mean = self.centroids_

        S = np.array([[var[i],0],[0,var[j]]])

        T = (S*pad)

        points = np.array([[-1.,1.],[1.,1.],[1.,-1.],[-1.,-1.],[-1.,1.]])
        points = points.dot(T)
        points[:,0] = points[:,0]+mean[k,i]
        points[:,1] = points[:,1]+mean[k,j]


        return points
   
    def get_assignments(self,X,pad=1):
        var = self.variance_
        mean = self.centroids_
        mask = np.zeros((X.shape[0],self.num_clusters),dtype=np.bool)
        count=0
        for i,j in self.dim_combos:
            for k in range(self.num_clusters):
                S = np.array([[var[i],0],[0,var[j]]])
                
                T = (S*pad)

                points = np.array([[-1.,1.],[1.,1.],[1.,-1.],[-1.,-1.],[-1.,1.]])
                points = points.dot(T)
                points[:,0] = points[:,0]+mean[k,i]
                points[:,1] = points[:,1]+mean[k,j]

                P = points.copy()

                pangles = np.zeros((X.shape[0]))
                nangles = np.zeros((X.shape[0]))
                for b in range(4):
                    a = X[:,[i,j]]-P[b]
                    v = X[:,[i,j]]-P[b+1]
                    d = v[:,0]*a[:,1]-v[:,1]*a[:,0]
                    pangles+=(d>0)
                    nangles+=(d<0)

                mask[:,k] = mask[:,k]|((nangles!=4)&(pangles!=4))


            count+=1
        return ~mask
    

    def get_distances(self,X,pad=1,distance='chebyshev'):
        var = self.variance_
        w = self.centroids_

        loss_matrix=np.zeros((X.shape[0],self.num_clusters))
        for i in range(w.shape[0]):
            if distance=='chebyshev':
                loss_matrix[:,i]=np.max(np.abs(X[:]-w[i]),axis=1)
            elif distance=='euclidean':
                loss_matrix[:,i]=np.sum(np.abs(X[:]-w[i])**2,axis=1)
            elif distance=='mae':
                loss_matrix[:,i]=np.mean(np.abs(X[:]-w[i]),axis=1)
            else:
                raise ArgumentError("Invalid distance metric")
        return loss_matrix

