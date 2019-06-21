#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""
This click command plots the ISV intuition
"""


import os
from bob.extension.scripts.click_helper import verbosity_option, ResourceOption
import click
from bob.extension import rc
import bob.io.base

import numpy
numpy.random.seed(2) # FIXING A SEED
import bob.learn.linear
import bob.learn.em

import matplotlib; matplotlib.use('pdf') #avoids TkInter threaded start
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

# This import is needed to modify the way figure behaves
from mpl_toolkits.mplot3d import Axes3D

import logging
logger = logging.getLogger("bob.bio.htface")


def MAP_features(features, ubm):
    trainer = bob.learn.em.MAP_GMMTrainer (ubm, relevance_factor=4, update_means=True, update_variances=False, update_weights=False)  
    gmm = bob.learn.em.GMMMachine(ubm.shape[0], ubm.shape[1])
    bob.learn.em.train(trainer, gmm, numpy.array([features[0,:]]))
  
    map_features = gmm.mean_supervector
    for i in range(1,features.shape[0]):
        gmm = bob.learn.em.GMMMachine(ubm.shape[0], ubm.shape[1])
        bob.learn.em.train(trainer, gmm, numpy.array([features[i,:]]))
        map_features = numpy.vstack((map_features, gmm.mean_supervector))

    return map_features


def train_ubm(features, n_gaussians):
    input_size = features.shape[1]

    kmeans_machine = bob.learn.em.KMeansMachine(int(n_gaussians), input_size)
    ubm            = bob.learn.em.GMMMachine(int(n_gaussians), input_size)

    # The K-means clustering is firstly used to used to estimate the initial means, the final variances and the final weights for each gaussian component
    kmeans_trainer = bob.learn.em.KMeansTrainer('RANDOM_NO_DUPLICATE')
    bob.learn.em.train(kmeans_trainer, kmeans_machine, features)

    #Getting the means, weights and the variances for each cluster. This is a very good estimator for the ML
    (variances, weights) = kmeans_machine.get_variances_and_weights_for_each_cluster(features)
    means = kmeans_machine.means

    # initialize the UBM with the output of kmeans
    ubm.means     = means
    ubm.variances = variances
    ubm.weights   = weights

    # Creating the ML Trainer. We will adapt only the means
    trainer = bob.learn.em.ML_GMMTrainer(update_means=True, update_variances=False, update_weights=False)
    bob.learn.em.train(trainer, ubm, features)

    return ubm


def isv_train(features, ubm):
    """
    Features com lista de listas [  [data_point_1_user_1,data_point_2_user_1], [data_point_1_user_2,data_point_2_user_2]  ] 
    """

    stats = []
    for user in features:
        user_stats = []
        for f in user:
            s = bob.learn.em.GMMStats(ubm.shape[0], ubm.shape[1])
            ubm.acc_statistics(f, s)
            user_stats.append(s)
        stats.append(user_stats)
     
    relevance_factor        = 4
    isv_training_iterations = 10
    subspace_dimension_of_u = 1

    isvbase = bob.learn.em.ISVBase(ubm, subspace_dimension_of_u)
    trainer = bob.learn.em.ISVTrainer(relevance_factor)
    #trainer.rng = bob.core.random.mt19937(int(self.init_seed))
    bob.learn.em.train(trainer, isvbase, stats, max_iterations=50)
  
    return isvbase


def isv_enroll(features, isvbase):

    user_stats = bob.learn.em.GMMStats(isvbase.ubm.shape[0], isvbase.ubm.shape[1])
    for f in features:
        isvbase.ubm.acc_statistics(f, user_stats)

    #Enroll
    relevance_factor = 4
    trainer          = bob.learn.em.ISVTrainer(relevance_factor)
    isvmachine = bob.learn.em.ISVMachine(isvbase)
    trainer.enroll(isvmachine, [user_stats], 1)

    #Estimating the Ux for testing
    ux = numpy.zeros((isvbase.ubm.mean_supervector.shape[0],), numpy.float64)
    isvmachine.estimate_ux(user_stats, ux)

    return isvmachine, ux


def plot_prior(X_a1, X_b1, X_a2, X_b2, ubm, u0, u1, print_prior_text=False):
    ### PLOTTING PRIOR ####
    ax = plt.axes()

    plt.scatter(X_a1[0:50, 0], X_a1[0:50, 1], c='r', marker=".", linewidths=0.00, s=100)
    plt.scatter(X_b2[0:50, 0], X_b1[0:50, 1], c='r', marker="^", linewidths=0.00, s=100)

    plt.scatter(X_a2[0:50, 0], X_a2[0:50, 1], c='b', marker=".", linewidths=0.00, s=100)
    plt.scatter(X_b1[0:50, 0], X_b2[0:50, 1], c='b', marker="^", linewidths=0.00, s=100)

    plt.plot(ubm.means[:,0],ubm.means[:,1], 'ko')


    ax.arrow(ubm.means[0,0], ubm.means[0,1], u0[0], u0[1], fc="k", ec="k", head_width=0.05, head_length=0.1 )
    ax.arrow(ubm.means[1,0], ubm.means[1,1], u1[0], u1[1], fc="k", ec="k", head_width=0.05, head_length=0.1 )
    plt.text(ubm.means[0,0]+u0[0], ubm.means[0,1]+u0[1]-0.3, r'$\mathbf{U}_1$', fontsize=15)
    plt.text(ubm.means[1,0]+u1[0], ubm.means[1,1]+u1[1]-0.3, r'$\mathbf{U}_2$', fontsize=15)    

    #plt.grid(True)
    plt.xlabel('$e_1$')
    plt.ylabel('$e_2$')

    plt.xlim([-5.5,10])

    if(print_prior_text):
        plt.text(-1, -6, r'$\{$', fontsize=100, rotation=90)    
        ax.annotate('$X_A = X_{A}^{1} \cup  X_{A}^{2} \cup ... \cup X_{A}^{N}$', xy=(0, -4.5), xytext=(-1, -4.5),
                #arrowprops=dict(facecolor='black', shrink=0.05),
                )

        plt.text(-1, 5, r'$\}$', fontsize=100, rotation=90)
        ax.annotate('$X_B = X_{B}^{1} \cup  X_{B}^{2}\cup ... \cup X_{B}^{N}$', xy=(0, 9.1), xytext=(-1, 9.1),
                #arrowprops=dict(facecolor='black', shrink=0.05),
                )


@click.command(context_settings={'ignore_unknown_options': True,
                                 'allow_extra_args': True})
@click.argument('output_file', required=True)
def isv_intuition(output_file, **kwargs):
    """
    This click command plots the ISV intuition plots
    
    \b
    Example:
        $ bob bio htface isv_intuition <OUTPUT-FILE>
 
    """

    ### GENERATING DATA
    cov = numpy.eye(2)*1

    X_a1 = numpy.random.multivariate_normal(mean=[0,0], cov=cov, size=(100))
    X_b1 = numpy.random.multivariate_normal(mean=[0,5], cov=cov, size=(100))

    X_a2 = numpy.random.multivariate_normal(mean=[5,0], cov=cov, size=(100))
    X_b2 = numpy.random.multivariate_normal(mean=[5,5], cov=cov, size=(100))

    X1   = numpy.vstack((X_a1,X_b1))
    X2   = numpy.vstack((X_a2,X_b2))

    features = numpy.vstack((X1, X2))

    #TRAINING THE PRIOR
    ubm      = train_ubm(features, 2)
    features = [[X_a1,X_b1],[X_a2,X_b2]]
    isvbase  = isv_train(features,ubm)

    #Variability direction
    u0 = isvbase.u[0:2,0] / numpy.linalg.norm(isvbase.u[0:2,0])
    u1 = isvbase.u[2:4,0] / numpy.linalg.norm(isvbase.u[2:4,0])

    #NEW_SAMPLE_ENROLL  = numpy.array([[-9,0.]])
    #NEW_SAMPLE_SCORING = numpy.array([[-7,8.]])

    NEW_SAMPLE_ENROLL  = numpy.array([[-5,0.]])
    NEW_SAMPLE_SCORING = numpy.array([[-4,8.]])


    logger.info("Plotting!!!")


    #----------------------------------------------------------------------
    # Plot result

    pp = PdfPages(output_file)

    #################################################################
    ###################### Page 1 - Prior model #####################
    #################################################################

    fig = plt.figure()

    params = {'legend.fontsize': 10}
    matplotlib.rcParams.update(params)


    plot_prior(X_a1, X_b1, X_a2, X_b2, ubm, u0,u1, print_prior_text=False)
    plt.legend(['UBM mean ($m$)'], loc=1,numpoints=1)  


    plt.title('')

    pp.savefig(fig)


    #################################################################
    ###################### Page 2 - ENROLL SAMPLE ###################
    #################################################################

    fig = plt.figure()
    ax = plt.axes()

    #### PLOTTING NEW SAMPLE for enroll ####
    #Enroll

    isvmachine, ux_enroll  = isv_enroll(NEW_SAMPLE_ENROLL, isvbase)

    shift   = isvbase.ubm.mean_supervector + isvbase.d * isvmachine.z

    data = numpy.array([  [shift[0], shift[1]],[shift[2], shift[3]]])
    plt.scatter(data[:,0],data[:,1],c='c',marker='D', linewidths=0.10, s=200)

    plt.scatter(NEW_SAMPLE_ENROLL[:, 0], NEW_SAMPLE_ENROLL[:, 1], c='g', marker=".", linewidths=0.00, s=200)
    plot_prior(X_a1, X_b1, X_a2, X_b2, ubm, u0,u1)

    plt.legend(['UBM means ($m_c$)','$\\Theta_{enroll}=m_c + D_{c}z$','Enrollment sample',], loc=1, scatterpoints=1, numpoints=1, bbox_to_anchor=(1.1, 1.1))  

    plt.title('')

    pp.savefig(fig)

    #################################################################
    ###################### Page 3 - TEST SAMPLE #####################
    #################################################################


    fig = plt.figure()
    ax = plt.axes()

    #### PLOTTING NEW SAMPLE for enroll ####
    #Enroll
    plt.scatter(NEW_SAMPLE_ENROLL[:, 0], NEW_SAMPLE_ENROLL[:, 1], c='g', marker=".", linewidths=0.00, s=200)

    isvmachine, ux_enroll  = isv_enroll(NEW_SAMPLE_ENROLL, isvbase)

    shift   = isvbase.ubm.mean_supervector + isvbase.d * isvmachine.z  
    data = numpy.array([  [shift[0], shift[1]],[shift[2], shift[3]]])
    plt.scatter(data[:,0],data[:,1],c='c',marker='D', linewidths=0.10, s=200)

    #scoring
    _, ux_scoring = isv_enroll(NEW_SAMPLE_SCORING, isvbase)

    plt.scatter(NEW_SAMPLE_SCORING[:, 0], NEW_SAMPLE_SCORING[:, 1], c='g', marker="^", linewidths=0.00, s=200)

    shift   = isvbase.ubm.mean_supervector + isvbase.d * isvmachine.z + ux_scoring
    data = numpy.array([  [shift[0], shift[1]],[shift[2], shift[3]]])
    plt.scatter(data[:,0],data[:,1],c='m',marker='D', linewidths=0.10, s=200)


    plot_prior(X_a1, X_b1, X_a2, X_b2, ubm, u0,u1)
    plt.legend(['UBM means ($m_c$)','Enrollment sample','$\\Theta_{enroll}=m_c + D_{c}z$','Scoring sample',"$\\Theta_{enroll} + U_{\mathcal{D}^s\mathcal{D}^t}w$"], loc=1, scatterpoints=1, numpoints=1, bbox_to_anchor=(1.13, 1.13))  
    plt.title('')

    pp.savefig(fig)


    #################################################################
    ###################### Page 4 - MAP SAMPLE #####################
    #################################################################

    fig = plt.figure()
    ax = plt.axes()

    #### PLOTTING NEW SAMPLE for enroll ####
    #Enroll
    plt.scatter(NEW_SAMPLE_ENROLL[:, 0], NEW_SAMPLE_ENROLL[:, 1], c='g', marker=".", linewidths=0.00, s=200)

    isvmachine, ux_enroll  = isv_enroll(NEW_SAMPLE_ENROLL, isvbase)

    shift   = isvbase.ubm.mean_supervector + isvbase.d * isvmachine.z 
    data = numpy.array([  [shift[0], shift[1]],[shift[2], shift[3]]])
    plt.scatter(data[:,0],data[:,1],c='c',marker='D', linewidths=0.10, s=200)

    #scoring
    _         , ux_scoring = isv_enroll(NEW_SAMPLE_SCORING, isvbase)

    plt.scatter(NEW_SAMPLE_SCORING[:, 0], NEW_SAMPLE_SCORING[:, 1], c='g', marker="^", linewidths=0.00, s=200)
    #plt.text(NEW_SAMPLE_SCORING[0, 0]+0.1, NEW_SAMPLE_SCORING[0, 1]+0.1, '$X_{B}^{i}$', fontsize=15)

    shift   = isvbase.ubm.mean_supervector + isvbase.d * isvmachine.z + ux_scoring
    data = numpy.array([  [shift[0], shift[1]],[shift[2], shift[3]]])
    plt.scatter(data[:,0],data[:,1],c='m',marker='D', linewidths=0.10, s=200)


    #scoring  ONLY MAP
    isvmachine        , ux_scoring = isv_enroll(NEW_SAMPLE_SCORING, isvbase)

    shift   = isvbase.ubm.mean_supervector + isvbase.d * isvmachine.z
    data = numpy.array([  [shift[0], shift[1]],[shift[2], shift[3]]])
    plt.scatter(data[:,0],data[:,1],c='darkorange',marker='D', linewidths=0.10, s=200)

    plot_prior(X_a1, X_b1, X_a2, X_b2, ubm, u0,u1)

    plt.legend(['UBM means ($m_c$)','Enrollment sample','$\\Theta_{enroll}=m_c + D_{c}z$','Scoring sample',"$\\Theta_{enroll} + U_{\mathcal{D}^s\mathcal{D}^t}w$",'MAP adaptation'], loc=1,   scatterpoints=1, numpoints=1, bbox_to_anchor=(1.13, 1.13))  

    plt.title('')
    pp.savefig(fig)


    pp.close()

    logger.info("Done!!!")           

