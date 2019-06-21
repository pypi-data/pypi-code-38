#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""
This script plots the Average recognition rate as a function of the number of parameters for
the Inception Resnet v1 and Inception Resnet v2 (with and without bias adaptation)


Examples:

  `bob_htface_rec-rate_vs_n-parameters.py /home/experiments/ --base-system siamese-bias-resnetv1
  

Usage:
  bob_htface_rec-rate_vs_n-parameters.py <base-path> --base-system=<arg>... --legends=<arg>... [--score-base-name=<arg>] [--report-name=<arg>] [--title=<arg>]
  bob_htface_rec-rate_vs_n-parameters.py -h | --help

Options:
  --base-system=<arg>       The options are 'siamese-bias-resnetv1', 'siamese-bias-resnetv2', 'siamese-nobias-resnetv1', 'siamese-nobias-resnetv2', 'triplet-bias-resnetv1', 'triplet-bias-resnetv2', 'triplet-nobias-resnetv1', 'triplet-nobias-resnetv2'
  --score-base-name=<arg>   Name of the score files [default: scores-dev]
  --report-name=<arg>       Name of the report [default: report_name.pdf]
  --legends=<arg>           Legends of the plot
  --title=<arg>             Title of the plot
  -h --help                 Show this screen.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import bob.measure
import numpy
import math
import os
from docopt import docopt
from .evaluate_and_squash import _compute_rr, discover_scores

# matplotlib stuff
import tensorflow as tf
import matplotlib; matplotlib.use('agg') #avoids TkInter threaded start
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages

from bob.bio.htface.architectures.inception_v1_batch_norm import inception_resnet_v1_adapt_first_head,\
                                                                 inception_resnet_v1_adapt_layers_1_2_head,\
                                                                 inception_resnet_v1_adapt_layers_1_4_head,\
                                                                 inception_resnet_v1_adapt_layers_1_5_head,\
                                                                 inception_resnet_v1_adapt_layers_1_6_head

from bob.bio.htface.architectures.inception_v2_batch_norm import inception_resnet_v2_adapt_first_head,\
                                                                 inception_resnet_v2_adapt_layers_1_2_head,\
                                                                 inception_resnet_v2_adapt_layers_1_4_head,\
                                                                 inception_resnet_v2_adapt_layers_1_5_head,\
                                                                 inception_resnet_v2_adapt_layers_1_6_head

# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('lines', linewidth = 4)

# increase the default font size
import bob.core
logger = bob.core.log.setup("bob.bio.base")


sub_directories = dict()
sub_directories['siamese-bias-resnetv1'] = ["idiap_casia_inception_v1_gray",
                                            "siamese_inceptionv1_first_layer_betas_nonshared_batch_norm",
                                            "siamese_inceptionv1_adapt_1_2_betas_nonshared_batch_norm",
                                            "siamese_inceptionv1_adapt_1_4_betas_nonshared_batch_norm",
                                            "siamese_inceptionv1_adapt_1_5_betas_nonshared_batch_norm",
                                            "siamese_inceptionv1_adapt_1_6_betas_nonshared_batch_norm"]
                                            
sub_directories['siamese-nobias-resnetv1'] = ["idiap_casia_inception_v1_gray",
                                            "siamese_inceptionv1_first_layer_nonshared_batch_norm",
                                            "siamese_inceptionv1_adapt_1_2_nonshared_batch_norm",
                                            "siamese_inceptionv1_adapt_1_4_nonshared_batch_norm",
                                            "siamese_inceptionv1_adapt_1_5_nonshared_batch_norm",
                                            "siamese_inceptionv1_adapt_1_6_nonshared_batch_norm"]                                            

sub_directories['siamese-bias-resnetv2'] = ["idiap_casia_inception_v2_gray",
                                            "siamese_inceptionv2_first_layer_betas_nonshared_batch_norm",
                                            "siamese_inceptionv2_adapt_1_2_betas_nonshared_batch_norm",
                                            "siamese_inceptionv2_adapt_1_4_betas_nonshared_batch_norm",
                                            "siamese_inceptionv2_adapt_1_5_betas_nonshared_batch_norm",
                                            "siamese_inceptionv2_adapt_1_6_betas_nonshared_batch_norm"]

sub_directories['siamese-nobias-resnetv2'] = ["idiap_casia_inception_v2_gray",
                                            "idiap_casia_inception_v2_gray_adapt_first_layer_nonshared_batch_norm",
                                            "inception_resnet_v2_adapt_layers_1_2_nonshared_batch_norm",
                                            "inception_resnet_v2_adapt_layers_1_4_nonshared_batch_norm",
                                            "inception_resnet_v2_adapt_layers_1_5_nonshared_batch_norm",
                                            "inception_resnet_v2_adapt_layers_1_6_nonshared_batch_norm"]



def compute_trainable_variables(base_architecture):


    if "v1" in base_architecture:

        architectures = [inception_resnet_v1_adapt_first_head, inception_resnet_v1_adapt_layers_1_2_head,
                         inception_resnet_v1_adapt_layers_1_4_head, inception_resnet_v1_adapt_layers_1_5_head,
                         inception_resnet_v1_adapt_layers_1_6_head]

    elif "v2" in base_architecture:

        architectures = [inception_resnet_v2_adapt_first_head, inception_resnet_v2_adapt_layers_1_2_head,
                         inception_resnet_v2_adapt_layers_1_4_head, inception_resnet_v2_adapt_layers_1_5_head,
                         inception_resnet_v2_adapt_layers_1_6_head]
      
    n_parameters = []  
    for function in architectures:
    
        update_bias = "-bias-" in base_architecture
    
        input_left  = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))
        input_right = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))        

        input_left,_ = function(input_left,
                          dropout_keep_prob=0.8,
                          bottleneck_layer_size=128,
                          reuse=None,
                          scope='InceptionResnetV2',
                          mode=tf.estimator.ModeKeys.TRAIN,
                          trainable_variables=None,
                          is_siamese=True,
                          is_left = True,
                          force_weights_shutdown=update_bias)
        
        input_right,_ = function(input_right,
                           dropout_keep_prob=0.8,
                           bottleneck_layer_size=128,
                           reuse=True,
                           scope='InceptionResnetV2',
                           mode=tf.estimator.ModeKeys.TRAIN,
                           trainable_variables=None,
                           is_siamese=True,
                           is_left = False,
                           force_weights_shutdown=update_bias)
        n_parameters.append(sum([numpy.prod(v.get_shape().as_list()) for v in tf.trainable_variables()]))
        tf.reset_default_graph()
    return n_parameters


def main(command_line_parameters=None):
    """Reads score files, computes error measures and plots curves."""

    args = docopt(__doc__, version='Run experiment')

    bob.core.log.set_verbosity_level(logger, 3)
    xticks = ["No Adaptation", "$\\theta_{t[1-1]}$", "$\\theta_{t[1-2]}$",
               "$\\theta_{t[1-4]}$", "$\\theta_{t[1-5]}$", "$\\theta_{t[1-6]}$"]
    #colors     = ['darkred', 'royalblue']
    linestyles   = ["-", "--"]
    
    means = dict()
    n_parameters = dict()
    base_path = args["<base-path>"]
    for baseline in  args["--base-system"]:
        dev_files = []    
        for e in sub_directories[baseline]:
            path = os.path.join(base_path, e)    
            df = discover_scores(path, score_name=args["--score-base-name"])
            dev_files += df
            logger.info("{0} scores discovered in {1}".format(len(df), e))
            
        # RR
        logger.info("Computing recognition rate")
        cmcs_dev               = [bob.measure.load.cmc_four_column(f) for f in dev_files]
        means[baseline]        = _compute_rr(cmcs_dev, xticks)
        logger.info("Computing n_parameters")
        n_parameters[baseline] = compute_trainable_variables(baseline)        
    
    logger.info("Plotting")
    
    pdf = PdfPages(args["--report-name"])
       
    fig, ax1 = pyplot.subplots()    

    for baseline, linestyle, legend in zip(args["--base-system"], linestyles, args["--legends"]):
        pyplot.plot(range(6), means[baseline], 'royalblue', marker=".", linestyle=linestyle, linewidth=1.5, label=legend)
    pyplot.ylim(40, 100)
    
    ax2 = ax1.twinx()
    for baseline, linestyle in zip(args["--base-system"], linestyles):
        n_parameters[baseline].insert(0,0)
        ax2.plot(range(6), n_parameters[baseline], 'darkred', marker=".", linestyle="--", linewidth=1.5, label="\#Parameters")
        print("#Parameters per model: {0}".format(n_parameters[baseline]))
    

    ax1.tick_params('y', colors='royalblue')
    #ax1.set_ylim(50, 100)
    ax1.set_ylabel('Identification rate (\%)', color='royalblue')
    ax1.set_xlabel('Adaptation model')
    ax1.legend(loc=2)
        
    ax2.tick_params('y', colors='darkred')
    ax2.set_ylabel('\#Parameters', color='darkred')
    ax2.legend(loc=1)
    #ax2.set_ylim(0, 5000)
    pyplot.xticks(range(6), [str(t) for t in xticks])
    pyplot.title(args["--title"])
    pdf.savefig(fig)
    
    #except RuntimeError as e:
    #    raise RuntimeError("During plotting of CMC curves, the following exception occured:\n%s\nUsually this happens when the label contains characters that LaTeX cannot parse." % e)

    pdf.close()
    logger.info("Done !!!")


if __name__ == '__main__':
    main()

