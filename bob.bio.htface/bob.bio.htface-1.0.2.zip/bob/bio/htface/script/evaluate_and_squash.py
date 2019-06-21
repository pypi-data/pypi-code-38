#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import bob.measure
import numpy
import math
import os
import bob.bio.base
#from docopt import docopt
from bob.extension.scripts.click_helper import ResourceOption, verbosity_option
import click


# matplotlib stuff

import matplotlib; matplotlib.use('agg') #avoids TkInter threaded start
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages

# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('lines', linewidth = 4)

# increase the default font size
import bob.core
logger = bob.core.log.setup("bob.bio.base")


def _plot_cmc(cmcs, colors, labels, title, linestyle,  fontsize=12, position=None, xmin=0, xmax=100):

  if position is None: position = 4

  # open new page for current plot

  figure = pyplot.figure(dpi=600)
  offset = 0
  step   = int(len(cmcs)/len(labels))
  params = {'legend.fontsize': int(fontsize)}
  matplotlib.rcParams.update(params)
  matplotlib.rc('xtick', labelsize=10)
  matplotlib.rc('ytick', labelsize=10)
  matplotlib.rcParams.update({'font.size': 16})

  #For each group of labels
  max_x   =  0 #Maximum CMC size
  for i in range(len(labels)):
    #Computing the CMCs

    cmc_curves = []
    for j in range(offset,offset+step):
      cmc_curves.append(bob.measure.cmc(cmcs[j]))
      max_x = max(len(cmc_curves[j-offset]), max_x)

    #Adding the padding with '1's
    cmc_accumulator = numpy.zeros(shape=(step,max_x), dtype='float')
    for j in range(step):
      padding_diff =  max_x-len(cmc_curves[j])
      cmc_accumulator[j,:] = numpy.pad(cmc_curves[j],(0,padding_diff), 'constant',constant_values=(1))
      #cmc_average  += numpy.pad(cmc_curves[j],(0,padding_diff), 'constant',constant_values=(1))

    cmc_std     = numpy.std(cmc_accumulator, axis=0);# cmc_std[-1]
    cmc_average = numpy.mean(cmc_accumulator, axis=0)

    if(linestyle is not None):
      pyplot.semilogx(range(1, cmc_average.shape[0]+1), cmc_average * 100, lw=2, ms=10, mew=1.5, label=labels[i], ls=linestyle[i].replace('\\',''), color=colors[i])
    else:
      pyplot.semilogx(range(1, cmc_average.shape[0]+1), cmc_average * 100, lw=2, ms=10, mew=1.5, label=labels[i], color=colors[i])

    pyplot.errorbar(range(1, cmc_average.shape[0]+1), cmc_average*100, cmc_std*100, lw=0.5, ms=10,color=colors[i])
    offset += step    

  # change axes accordingly
  ticks = [int(t) for t in pyplot.xticks()[0]]
  pyplot.xlabel('Rank')
  pyplot.ylabel('Identification rate (\%)')
  pyplot.xticks(ticks, [str(t) for t in ticks])
  #pyplot.axis([0, max_x, xmin, 100])
  pyplot.axis([0, max_x, xmin, xmax])  
  pyplot.legend(loc=position, fontsize=8)
  pyplot.title("")
  pyplot.grid(True)

  return figure


def _plot_roc(scores, colors, labels, title, linestyle,  fontsize=12, position=None, xmin=0, xmax=100):

    def _semilogx(x, y, color, label, **kwargs):
        # remove points were x is 0
        x, y = numpy.asarray(x), numpy.asarray(y)
        zero_index = x == 0
        x = x[~zero_index]
        y = y[~zero_index]
        return pyplot.semilogx(x, y, label=label, color=color, lw=2, ms=10, mew=1.5,  **kwargs)

    if position is None: position = 4

    # open new page for current plot

    figure = pyplot.figure(dpi=600)
    offset = 0
    step   = int(len(scores)/len(labels))
    params = {'legend.fontsize': int(fontsize)}
    matplotlib.rcParams.update(params)
    matplotlib.rc('xtick', labelsize=10)
    matplotlib.rc('ytick', labelsize=10)
    matplotlib.rcParams.update({'font.size': 16})

    rocs     = []
    for s in scores:
        negatives, positives = bob.bio.base.score.load.split_four_column(s)
        rocs.append(bob.measure.roc(negatives, positives, n_points=100))
    rocs = numpy.array(rocs)
 
    for i in range(len(labels)):
        l = labels[i]

        mean_x   = numpy.mean(rocs[offset : offset+step,0,:], axis=0)
        mean_y   = 1-numpy.mean(rocs[offset : offset+step,1,:], axis=0)

        #std_x   = numpy.std(rocs[offset : offset+step,0,:], axis=0)
        std_y   = numpy.std(rocs[offset : offset+step,1,:], axis=0)

        offset += step
        _semilogx(mean_x, mean_y, colors[i], labels[i])
        pyplot.errorbar(mean_x, mean_y, std_y, lw=0.5, ms=10,color=colors[i])
       
        
        
    # change axes accordingly
    #ticks = [int(t) for t in pyplot.xticks()[0]]
    pyplot.xlabel('False Acceptance Rate @')
    pyplot.ylabel('Verification Rate (\%)')
    pyplot.legend(loc=position, fontsize=12)
    pyplot.title("")

    
    #pyplot.xticks(ticks, [str(t) for t in ticks])
    #pyplot.axis([0, max_x, xmin, 100])
    pyplot.axis([10e-3, 1., 0., 1.])
    pyplot.grid(True)

    return figure


def _compute_rr(cmcs, labels):
    """
    Compute Average Recognition Rate
    """
    offset = 0
    step   = int(len(cmcs)/len(labels))

    #Computing the recognition rate for each score file
    rr     = []   
    for i in range(len(cmcs)):
        rr.append(bob.measure.recognition_rate(cmcs[i]))
      
    means   = []
    for i in range(len(labels)):
        l = labels[i]
        average   = round(numpy.mean(rr[offset : offset+step])*100,3)
        std_value = round(numpy.std(rr[offset : offset+step])*100,3)
        print("The AVERAGE Recognition Rate of the development set of '{0}' along '{1}' splits is {2}({3})".format(l, int(step), average, std_value))
        offset += step
        means.append(average)

    return means


def _compute_tpir_at_far(scores, labels, far=0.1):
    """
    Compute average TPIR@FAR=0.1
    """
    offset = 0
    step   = int(len(scores)/len(labels))

    #Computing the recognition rate for each score file
    tpir     = []
    for s in scores:
        negatives, positives = bob.bio.base.score.load.split_four_column(s)
        thres = bob.measure.far_threshold(negatives, positives, far_value=far)
        far, frr = bob.measure.farfrr(negatives, positives, thres)
        tpir.append(1.-frr)
      
    means   = []
    for i in range(len(labels)):
        l = labels[i]
        average   = round(numpy.mean(tpir[offset : offset+step])*100,3)
        std_value = round(numpy.std(tpir[offset : offset+step])*100,3)
        print("The AVERAGE TPIR@FAR=0.1 of '{0}' along '{1}' splits is {2}({3})".format(l, int(step), average, std_value))
        offset += step
        means.append(average)

    return means


def discover_scores(base_path, score_name="scores-dev", skip=["extracted", "preprocessed", "gridtk_logs"]):
    """
    Given a base path, get all the score files.
    """
    
    files = os.listdir(base_path)
    score_files = []
    for f in files:

        if f in skip:
            continue

        filename = os.path.join(base_path, f)
        if os.path.isdir(filename):
            score_files += discover_scores(filename, score_name)
        
        #if f==score_name:
        if f in ["scores-dev", "scores-eval"]:
            score_files += [filename]
        
    return score_files


@click.command(context_settings={'ignore_unknown_options': True,
                                 'allow_extra_args': True})
@click.argument('experiment', required=True, nargs=-1)
@click.option('--legends', help='Name of each experiment', required=True, multiple=True)
@click.option('--colors', help='Color of each plot', multiple=True)
@click.option('--report-name', help='Name of the report', default="report_name.pdf")
@click.option('--title', help='Title of the plot')
@click.option('--score-base-name', help='Name of the score files', default="scores-dev")
@click.option('--x-min', help='Axis x-min', default=0)
@click.option('--special-linestyle', help='Use the special set of linestily. Such set will do the first plot dashed and the rest as solid lines', default=False, is_flag=True)
@verbosity_option(cls=ResourceOption)
def evaluate_and_squash(experiment, legends, colors, report_name, title, score_base_name, x_min, special_linestyle, **kwargs):
    """
    This script runs CMC, DET plots and Recognition prints of groups of experiments.
    It's useful when an evaluation protocol is based of k-fold cross validation.


    Let's say you have executed 2 different experiments in a dataset whose protocol has five folds.
    The command bellow will search for the scores of every fold and average them accordingly

    Examples:

       `bob_htface_evaluate_and_squash.py <experiment_1> [<experiment_2>] --legends experiment1 --legends experiment2`
    
    """

    special_line_style = ["--", "-", "-", "-", "-", "-", "-","-","-","-","-","-","-","-","-","-","-","-"]
    #special_line_style = ["--", "--", "--", "--", "-", "-", "-","-","-","-","-","-","-","-","-","-","-","-"]

    # check that the legends have the same length as the dev-files
    if (len(experiment) % len(legends)) != 0:
        logger.error("The number of experiments (%d) is not multiple of --legends (%d) ", len(args["<experiment>"]), len(args["--legends"]))

    
    bob.core.log.set_verbosity_level(logger, 3)
    dev_files = []
    for e in experiment:
        df = discover_scores(e, score_name=score_base_name)
        dev_files += df
        logger.info("{0} scores discovered in {1}".format(len(df), e))


    # TPIR@FAR=0.1
    logger.info("Computing TPIR@FAR=0.1")
    _compute_tpir_at_far(dev_files, legends)

    # RR
    logger.info("Computing recognition rate")
    cmcs_dev = [bob.bio.base.score.load.cmc_four_column(f) for f in dev_files]
    _compute_rr(cmcs_dev, legends)
    
    # CMC
    logger.info("Plotting CMC")
    if len(colors) ==0:
        colors     = ['red','darkviolet','darkorange', 'dimgrey','darkcyan', 'royalblue', 'saddlebrown', 'darkmagenta', 'indigo', 'dodgerblue', 'coral', 'lime']
    else:
        if (len(experiment) % len(colors)) != 0:
            logger.error("The number of experiments (%d) is not multiple of --colors (%d) ", len(experiment), len(colors))
    
    pdf = PdfPages(report_name)
    try:
        # CMC
        if special_linestyle:
            fig = _plot_cmc(cmcs_dev, colors, legends, title, linestyle=special_line_style, xmin=int(x_min))
        else:
            fig = _plot_cmc(cmcs_dev, colors, legends, title, linestyle=None, xmin=int(x_min))
            
        pdf.savefig(fig)

        # ROC
        fig = _plot_roc(dev_files, colors, legends, title, linestyle=special_line_style,  fontsize=12, position=None, xmin=0, xmax=100)
        pdf.savefig(fig)
  
    except RuntimeError as e:
        raise RuntimeError("During plotting of CMC curves, the following exception occured:\n%s\nUsually this happens when the label contains characters that LaTeX cannot parse." % e)

    pdf.close()
    logger.info("Done !!!")

