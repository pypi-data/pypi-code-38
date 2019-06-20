#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Elie Khoury <Elie.Khoury@idiap.ch>
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

import sys, os
import argparse
from .query import Database


def sort_by_ids(files):
    """Returns a sorted version of the given list of File's (or other structures that define an 'id' data member).
    The files will be sorted according to their id, and duplicate entries will be removed."""
    sorted_files = sorted(files, cmp=lambda x,y: cmp(x.id, y.id))
    return [f for i,f in enumerate(sorted_files) if not i or sorted_files[i-1].id != f.id]


def sort_by_pathes(files):
    """Returns a sorted version of the given list of File's (or other structures that define an 'id' data member).
    The files will be sorted according to their id, and duplicate entries will be removed."""
    sorted_files = sorted(files, cmp=lambda x,y: cmp(x.path, y.path))
    return [f for i,f in enumerate(sorted_files) if not i or sorted_files[i-1].path != f.path]

def ensure_dir(dirname):
  """ Creates the directory dirname if it does not already exist,
      taking into account concurrent 'creation' on the grid.
      An exception is thrown if a file (rather than a directory) already
      exists. """
  try:
    # Tries to create the directory
    os.makedirs(dirname)
  except OSError:
    # Check that the directory exists
    if os.path.isdir(dirname): pass
    else: raise

def main():
  """Executes the main function"""

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-o', '--output-dir', metavar='DIR', type=str, dest='output_dir', default='./protocols/', help='Output directory (defaults to "%(default)s")')

  parser.add_argument('-p', '--protocol-name', type=str, dest='protocol_name', default='mobile0-male', help=' Protocol name (defaults to "%(default)s")')

  parser.add_argument('-g', '--gender-dependent', action='store_true', dest='gender_dependent', default=False, help='Use gender dependent Training data (defaults to "%(default)s")')

  parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help="Increase some verbosity")

  args = parser.parse_args()


  ########################
  # Loading Hiperparameters
  #########################
  m_output_dir = args.output_dir
  m_protocol_name = args.protocol_name
  m_gender_dependent = args.gender_dependent

  # verify that the protocol name exists
  db = Database()
  if m_protocol_name not in db.protocol_names():
    raise ValueError("The given protocol name '%s' does not exist."%m_protocol_name)

  gender_value = 'female'
  if m_protocol_name.find(gender_value) == -1:
    gender_value = 'male'
  print('gender: %s' % gender_value)



  ### List for world group
  if (m_gender_dependent):
    world_dir = m_output_dir +'/' + m_protocol_name + '_GD/' + 'norm'
    #world_dir = m_output_dir +'/' + m_protocol_name + '_GD/' + 'world'
    dev_dir = m_output_dir +'/' + m_protocol_name + '_GD/' + 'dev'
    eval_dir = m_output_dir +'/' + m_protocol_name + '_GD/' + 'eval'
  else:
    world_dir = m_output_dir +'/' + m_protocol_name + '/' + 'norm'
    #world_dir = m_output_dir +'/' + m_protocol_name + '/' + 'world'
    dev_dir = m_output_dir +'/' + m_protocol_name + '/' + 'dev'
    eval_dir = m_output_dir +'/' + m_protocol_name + '/' + 'eval'

  # ensure directories
  ensure_dir(world_dir)
  ensure_dir(dev_dir)
  ensure_dir(eval_dir)

  ### List for world group (norm/train_world.lst)
  if (m_gender_dependent):
    files = sort_by_ids(db.objects(protocol=m_protocol_name, groups="world", gender = gender_value))
  else:
    files = sort_by_ids(db.objects(protocol=m_protocol_name, groups="world"))

  files =  sort_by_pathes(files)
  known = set()
  file_list = open(world_dir+'/train_world.lst', 'w')

  for file in files:
    if file.path not in known and not known.add(file.path):
      file_list.write(file.path + ' ' + (str(file.client_id)).zfill(3) + '\n')
  file_list.close()


  ### List of DEV.clients (dev/for_models.lst) group
  if (m_gender_dependent):
    files = sort_by_ids(db.objects(protocol=m_protocol_name, groups="dev", purposes='enroll', gender = gender_value))
  else:
    files = sort_by_ids(db.objects(protocol=m_protocol_name, groups="dev", purposes='enroll'))

  files = sort_by_pathes(files)
  known = set()
  file_list = open(dev_dir+'/for_models.lst', 'w')

  for file in files:
    if file.path not in known and not known.add(file.path):

      file_list.write(file.path + ' ' + (str(file.client_id)).zfill(3) + ' ' + (str(file.client_id)).zfill(3) + '\n')
  file_list.close()

  ### List of DEV.trials (dev/for_scores.lst) group
  if (m_gender_dependent):
    files = sort_by_ids(db.objects(protocol=m_protocol_name, groups="dev", purposes='probe', gender = gender_value))
  else:
    files = sort_by_ids(db.objects(protocol=m_protocol_name, groups="dev", purposes='probe'))

  files = sort_by_pathes(files)

  clients =sort_by_ids(db.clients(protocol=m_protocol_name, groups="dev"))

  known = set()
  file_list = open(dev_dir+'/for_scores.lst', 'w')
  #file_list = open(dev_dir+'/trials.lst', 'w')

  for file in files:
    if file.path not in known and not known.add(file.path):
      for c in clients:
        file_list.write(file.path + ' ' + (str(c.id)).zfill(3) + ' ' + (str(c.id)).zfill(3) + ' ' + (str(file.client_id)).zfill(3) +'\n')
  file_list.close()


  ### List of EVAL.clients (eval/for_models.lst) group
  if (m_gender_dependent):
    files = sort_by_ids(db.objects(protocol=m_protocol_name, groups="eval", purposes='enroll', gender = gender_value))
  else:
    files = sort_by_ids(db.objects(protocol=m_protocol_name, groups="eval", purposes='enroll'))

  files = sort_by_pathes(files)
  known = set()
  file_list = open(eval_dir+'/for_models.lst', 'w')

  for file in files:
    if file.path not in known and not known.add(file.path):

      file_list.write(file.path + ' ' + (str(file.client_id)).zfill(3) + ' ' + (str(file.client_id)).zfill(3) + '\n')
  file_list.close()

  ### List of EVAL.trials (eval/for_scores.lst) group
  if (m_gender_dependent):
    files = sort_by_ids(db.objects(protocol=m_protocol_name, groups="eval", purposes='probe', gender = gender_value))
  else:
    files = sort_by_ids(db.objects(protocol=m_protocol_name, groups="eval", purposes='probe'))

  files = sort_by_pathes(files)
  clients =sort_by_ids(db.clients(protocol=m_protocol_name, groups="eval"))
  known = set()
  file_list = open(eval_dir+'/for_scores.lst', 'w')
  #file_list = open(eval_dir+'/trials.lst', 'w')

  for file in files:
    if file.path not in known and not known.add(file.path):
      for c in clients:
        file_list.write(file.path + ' ' + (str(c.id)).zfill(3) + ' ' + (str(c.id)).zfill(3) + ' ' + (str(file.client_id)).zfill(3) +'\n')
  file_list.close()



if __name__ == "__main__":
  main()

