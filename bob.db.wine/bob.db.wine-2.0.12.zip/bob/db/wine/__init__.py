#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Sun 20 Jan 19:02:00 2013 CEST
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""Bob's database entry for the Wine database
"""

import os
import sys
import numpy
from . import driver

names = ['Alcohol', 'Malic Acid', 'Ash', 'Alcalinity of Ash',
         'Magnesium', 'Total Phenols', 'Flavanoids', 'Nonflavanoid Phenols',
         'Proanthocyanins', 'Color intensity', 'Hue',
         'OD280/OD315 of Diluted Wines', 'Proline']
"""Names of the features for each entry in the dataset."""

def data():
  """Loads from (text) file and returns Wine Dataset.

  This set is small and simple enough to require an SQL backend. We keep the
  single file it has in text and load it on-the-fly every time this method is
  called.

  We return a dictionary containing the 3 classes of wines catalogued in
  this dataset. Each dictionary entry contains a 2D :py:class:`numpy.ndarray`
  of 64-bit floats and they have respectively 59, 71 and 48 samples. Each
  sample is an Array with 13 features as described by "names".
  """
  from .driver import Interface
  import csv
  import pkg_resources

  data = pkg_resources.resource_filename(__name__, 'wine.data')

  # The CSV file reader API changed between Python2 and Python3
  open_dict = dict(mode='rb') #python2.x
  if sys.version_info[0] >= 3: #python3.x
    open_dict = dict(mode='rt', encoding='ascii', newline='')

  retval = {}
  with open(data, **open_dict) as csvfile:
    for row in csv.reader(csvfile):
      name = 'wine' + row[0][:].lower()
      retval.setdefault(name, []).append([float(k) for k in row[1:14]])

  # Convert to a float64 2D numpy.ndarray
  for key, value in retval.items():
    retval[key] = numpy.array(value, dtype='float64')

  return retval

def __dump__(args):
  """Dumps the database to stdout.

  Keyword arguments:

  args
    A argparse.Arguments object with options set. We use two of the options:
    ``cls`` for the class to be dumped (if None, then dump all data) and
    ``selftest``, which runs the internal test.
  """

  d = data()
  if args.cls: d = {args.cls: d[args.cls]}

  output = sys.stdout
  if args.selftest:
    from ..utils import null
    output = null()

  for k, v in d.items():
    for array in v:
      s = ','.join(['%.1f' % array[i] for i in range(array.shape[0])] + [k])
      output.write('%s\n' % (s,))

  return 0

def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__)

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
