#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Tue 22 Dec 2015 08:02:02 CET 
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the ipyplotied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

"""
This script will print  VIS-VIS and the VIS-NIR overlapped score distributions


"""

import bob.io.base
import bob.io.image
import bob.measure

import argparse
import numpy, math
import os

# matplotlib stuff

import matplotlib; matplotlib.use('pdf') #avoids TkInter threaded start
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as mpl


import bob.core
logger = bob.core.log.setup("bob.bio.base")



def command_line_arguments(command_line_parameters):
  """Parse the program options"""

  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('score_file_A',  help = "The file with the scores of the modality A.")
  
  parser.add_argument('score_file_B',  help = "The file with the scores of the modality B.")
  
  parser.add_argument('-o', '--output-file', default="score_distribution.pdf", help = "The name of the output file.")
  
  parser.add_argument('-l', '--modality-labels', nargs="+", default=['VIS-NIR','VIS-VIS'], help = "")

  # add verbose option
  bob.core.log.add_command_line_option(parser)

  # parse arguments
  args = parser.parse_args(command_line_parameters)

  # set verbosity level
  bob.core.log.set_verbosity_level(logger, args.verbose)

  return args


def main(command_line_parameters=None):
  """Reads score files, computes error measures and plots curves."""

  args = command_line_arguments(command_line_parameters)

  scores_A = bob.measure.load.split_four_column(args.score_file_A)
  scores_B = bob.measure.load.split_four_column(args.score_file_B)

  #import ipdb; ipdb.set_trace();
  mi = min(numpy.min(scores_A[0]), numpy.min(scores_B[0]), numpy.min(scores_A[1]), numpy.min(scores_B[1]))
  ma = max(numpy.max(scores_A[0]), numpy.max(scores_B[0]), numpy.max(scores_A[1]), numpy.max(scores_B[1]))
  scoresRange = (mi, ma)

  bob.io.base.create_directories_safe(os.path.dirname(args.output_file))
  pp = PdfPages(args.output_file)
  
  fig = mpl.figure()

  params = {'font.size': 8}
  params = {'legend.fontsize': 6}
  mpl.rcParams.update(params)


  mpl.subplot(2,1,1)
  
  mpl.hist(scores_A[0], label = 'Impostors', normed=True, facecolor='red', alpha=0.75, bins=100)
  mpl.hist(scores_A[1], label = 'Genuine', normed=True, facecolor='green', alpha=0.5, bins=100)

  mpl.vlines(numpy.mean(scores_A[0]), 0, 20, color='black', label='$\mu$ impostor',linestyles='dashed')
  mpl.vlines(numpy.mean(scores_A[1]), 0, 20, color='black', label='$\mu$ genuine',linestyles='solid')  


  mpl.legend(loc=1)
  mpl.grid(True, alpha=0.5)
  mpl.xlim(scoresRange[0], scoresRange[1])
  
  mpl.title("{0} score distribution".format(args.modality_labels[0]))

  ####

  mpl.subplot(2,1,2)

  params = {'font.size': 8}
  params = {'legend.fontsize': 6}
  mpl.rcParams.update(params)
  
  mpl.hist(scores_B[0], label = 'Impostors', normed=True, facecolor='red', alpha=0.75, bins=100)
  mpl.hist(scores_B[1], label = 'Genuine', normed=True, facecolor='green', alpha=0.5, bins=100)
  
  mpl.vlines(numpy.mean(scores_B[0]), 0, 10, color='black', label='$\mu$ impostor',linestyles='dashed')
  mpl.vlines(numpy.mean(scores_B[1]), 0, 10, color='black', label='$\mu$ genuine',linestyles='solid')  

  mpl.legend(loc=1)
  mpl.grid(True, alpha=0.5)
  mpl.xlim(scoresRange[0], scoresRange[1])  
  
  mpl.title("{0} score distribution".format(args.modality_labels[1]))
    
  pp.savefig(fig)
  pp.close()

