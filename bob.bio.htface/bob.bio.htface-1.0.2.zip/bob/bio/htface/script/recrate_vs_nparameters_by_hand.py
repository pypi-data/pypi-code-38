#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""
This script plots the Average recognition rate as a function of the number of parameters for
the Inception Resnet v1 and Inception Resnet v2 (with and without bias adaptation)

SORRY, THIS IS DONE BY HAND.


Usage:
  bob_htface_recrate_vs_nparameters.py [--report-name=<arg>]
  bob_htface_recrate_vs_nparameters.py -h | --help


Options:
  --report-name=<arg>       Name of the report [default: report_name.pdf]


"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import bob.measure
import numpy
import math
import os
from docopt import docopt
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

# Adding values by hand sorry again
systems = dict()
systems["CUHK CUFS"]    = [64.158, 74.653, 87.327, 88.515, 97.723, 59.703]
systems["CASIA"]        = [73.80, 80.589, 91.573, 93.512, 96.267, 49.464]
systems["NIVL"]         = [88.139, 91.293, 94.239, 94.324, 94.464, 58.588]
systems["Pola Thermal"]      = [17.774, 31.464, 65.155, 73.238, 67.083, 33.321]
#systems["CUHK CUFSF"]   = [16.559, 34.089, 61.903, 77.2, 85.862, 24.17]

n_parameters = [0, 320/1000., 33264/1000., 171696/1000., 439488/1000., 1668768/1000.]
#n_parameters2 = [0, 32/1000., 208/1000., 400/1000., 928/1000., 3328/1000.]


def main(command_line_parameters=None):
    """Reads score files, computes error measures and plots curves."""

    args = docopt(__doc__, version='Run experiment')

    bob.core.log.set_verbosity_level(logger, 3)
    xticks = ["No Adaptation", "$\\theta_{t[1-1]}(\\beta + W)$", "$\\theta_{t[1-2]}(\\beta + W)$",
               "$\\theta_{t[1-4]}(\\beta + W)$", "$\\theta_{t[1-5]}(\\beta + W)$", "$\\theta_{t[1-6]}(\\beta + W)$"]
    colors     = ['darkred', 'royalblue', 'olive', 'darkcyan', 'orange']         
    
    logger.info("Plotting")
    
    pdf = PdfPages(args["--report-name"])
       
    fig, ax1 = pyplot.subplots()
    pyplot.xticks(range(6), [str(t) for t in xticks],  rotation = '15' )

    for database, color in zip(systems, colors):
        pyplot.plot(range(6), systems[database], color, marker=".", linestyle="-", linewidth=1.5, label=database)

    pyplot.ylim(0, 100)
    
    ax2 = ax1.twinx()
    ax2.plot(range(6), n_parameters, 'darkred', marker=".", linestyle="--", linewidth=1.5, label="\#Parameters")
    #ax2.plot(range(6), n_parameters2, 'darkred', marker=".", linestyle="--", linewidth=1.5, label="\#Parameters")

    ax1.tick_params('y', colors='royalblue')
    #ax1.set_ylim(50, 100)
    ax1.set_ylabel('Identification rate (\%)', color='royalblue', fontsize=16)
    ax1.set_xlabel('Adaptation model')
    #ax1.legend(loc=2)
    ax1.legend(loc=2, bbox_to_anchor=(-0.1, 1.17), ncol=3, fontsize=11)
        
    ax2.tick_params('y', colors='darkred')
    ax2.set_ylabel('\#Parameters ($*10^3$)', color='darkred', fontsize=16)
    #ax2.legend(loc=1)+
    ax2.legend(loc=2, bbox_to_anchor=(0.78, 1.17), ncol=3, fontsize=11)
    #ax2.set_ylim(0, 5000)
    #pyplot.xticks(range(6), [str(t) for t in xticks],  rotation = 'vertical', rotation_mode="anchor")
    
    #pyplot.title(args["--title"])
    pdf.savefig(fig)
    
    #except RuntimeError as e:
    #    raise RuntimeError("During plotting of CMC curves, the following exception occured:\n%s\nUsually this happens when the label contains characters that LaTeX cannot parse." % e)

    pdf.close()
    logger.info("Done !!!")


if __name__ == '__main__':
    main()

