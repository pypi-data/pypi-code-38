#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
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

"""This script creates the MOBIO database in a single pass.
"""

import os

from .models import *

def nodot(item):
  """Can be used to ignore hidden files, starting with the . character."""
  return item[0] != '.'

def add_files(session, datadir, extensions, verbose):
  """Add files to the MOBIO database."""

  def add_file(session, datadir, location, client_id_dir, session_device, basename, verbose):
    """Parse a single filename and add it to the list.
       Also add a client entry if not already in the database."""
    v = os.path.splitext(basename)[0].split('_')
    bname = os.path.splitext(basename)[0]
    full_bname = os.path.join(location, client_id_dir, session_device, bname)

    gender = ''
    if v[0][0] == 'm': gender = 'male'
    if v[0][0] == 'f': gender = 'female'
    institute = int(v[0][1])
    institute_dir = ''
    if institute == 0:
      institute = 'idiap'
      institute_dir = 'idiap'
    elif institute == 1:
      institute = 'manchester'
      institute_dir = 'uman'
    elif institute == 2:
      institute = 'surrey'
      institute_dir = 'unis'
    elif institute == 3:
      institute = 'oulu'
      institute_dir = 'uoulu'
    elif institute == 4:
      institute = 'brno'
      institute_dir = 'but'
    elif institute == 5:
      institute = 'avignon'
      institute_dir = 'lia'
    if institute_dir != location:
      error_msg = "File: %s -- Find location %s in directory of location %s!" % (full_bname, location, institute_dir)
      raise RuntimeError(error_msg)
    client_id = v[0][1:4]
    if v[0][0:4] != client_id_dir:
      error_msg = "File: %s -- Find identity %s in directory of identity %s!" % (full_bname, v[0][0:4], client_id)
      raise RuntimeError(error_msg)
    if not (client_id in client_dict):
      if (institute == 'surrey' or institute == 'avignon'):
        group = 'world'
      elif (institute == 'manchester' or institute == 'oulu'):
        group = 'dev'
      elif (institute == 'idiap' or institute == 'brno'):
        group = 'eval'
      if verbose>1: print("  Adding client %d..." % int(client_id))
      session.add(Client(int(client_id), group, gender, institute))
      client_dict[client_id] = True

    w = session_device.split('_')
    session_id_from_dir = int(w[0])
    device_from_dir = w[1]

    session_id = int(v[1])
    speech_type = v[2][0]
    shot_id = v[2][1:3]
    environment = v[3][0]
    device = v[3][1]
    if( device == '0'):
      device = 'mobile'
    elif( device == '1'):
      device = 'laptop'
    if device != device_from_dir:
      error_msg = "File: %s -- Find device %s in directory of device %s!" % (full_bname, device, device_from_dir)
      raise RuntimeError(error_msg)
    if session_id != session_id_from_dir:
      error_msg = "File: %s -- Find session_id %d in directory of session_id %d!" % (full_bname, session_id, session_id_from_dir)
      raise RuntimeError(error_msg)
    channel = int(v[4][0])

    if verbose>1: print("    Adding file '%s'..." % full_bname)
    session.add(File(int(client_id), full_bname, session_id, speech_type, shot_id, environment, device, channel))

  client_dict = {}
  if verbose: print("Adding clients and files ...")
  for location in filter(nodot, os.listdir(datadir)):
    location_dir = os.path.join(datadir, location)
    if os.path.isdir(location_dir):
      for client_id in filter(nodot, os.listdir(location_dir)):
        client_dir = os.path.join(location_dir, client_id)
        if os.path.isdir(client_dir):
          for session_device in filter(nodot, os.listdir(client_dir)):
            session_device_dir = os.path.join(client_dir, session_device)
            if os.path.isdir(session_device_dir):
              for filename in filter(nodot, os.listdir(session_device_dir)):
                for ext in extensions:
                  if filename.endswith(ext):
                    add_file(session, datadir, location, client_id, session_device, os.path.basename(filename), verbose)

def add_subworlds(session, verbose):
  """Adds subworlds"""

  twothirds_subsampled_filelist = [
    "unis/f214/01_mobile/f214_01_p01_i0_0", "unis/f214/01_mobile/f214_01_f12_i0_0", "unis/f214/01_mobile/f214_01_l11_i0_0",
    "unis/f214/02_mobile/f214_02_p01_i0_0", "unis/f214/02_mobile/f214_02_f12_i0_0", "unis/f214/02_mobile/f214_02_l11_i0_0",
    "unis/f214/03_mobile/f214_03_p01_i0_0", "unis/f214/03_mobile/f214_03_f12_i0_0", "unis/f214/03_mobile/f214_03_l11_i0_0",
    "unis/f214/04_mobile/f214_04_p01_i0_0", "unis/f214/04_mobile/f214_04_f12_i0_0", "unis/f214/04_mobile/f214_04_l11_i0_0",
    "unis/f214/05_mobile/f214_05_p01_i0_0", "unis/f214/05_mobile/f214_05_f12_i0_0", "unis/f214/05_mobile/f214_05_l11_i0_0",
    "unis/f214/06_mobile/f214_06_p01_i0_0", "unis/f214/06_mobile/f214_06_f12_i0_0", "unis/f214/06_mobile/f214_06_l11_i0_0",
    "unis/f214/07_mobile/f214_07_p01_i0_0", "unis/f214/07_mobile/f214_07_f07_i0_0", "unis/f214/07_mobile/f214_07_l06_i0_0",
    "unis/f214/08_mobile/f214_08_p01_i0_0", "unis/f214/08_mobile/f214_08_f07_i0_0", "unis/f214/08_mobile/f214_08_l06_i0_0",
    "unis/f214/09_mobile/f214_09_p01_i0_0", "unis/f214/09_mobile/f214_09_f07_i0_0", "unis/f214/09_mobile/f214_09_l06_i0_0",
    "unis/f214/10_mobile/f214_10_p01_i0_0", "unis/f214/10_mobile/f214_10_f07_i0_0", "unis/f214/10_mobile/f214_10_l06_i0_0",
    "unis/f214/11_mobile/f214_11_p01_i0_0", "unis/f214/11_mobile/f214_11_f07_i0_0", "unis/f214/11_mobile/f214_11_l06_i0_0",
    "unis/f214/12_mobile/f214_12_p01_i0_0", "unis/f214/12_mobile/f214_12_f07_i0_0", "unis/f214/12_mobile/f214_12_l06_i0_0",
    "unis/f218/01_mobile/f218_01_p01_i0_0", "unis/f218/01_mobile/f218_01_f12_i0_0", "unis/f218/01_mobile/f218_01_l11_i0_0",
    "unis/f218/02_mobile/f218_02_p01_i0_0", "unis/f218/02_mobile/f218_02_f12_i0_0", "unis/f218/02_mobile/f218_02_l11_i0_0",
    "unis/f218/03_mobile/f218_03_p01_i0_0", "unis/f218/03_mobile/f218_03_f12_i0_0", "unis/f218/03_mobile/f218_03_l11_i0_0",
    "unis/f218/09_mobile/f218_09_p01_i0_0", "unis/f218/09_mobile/f218_09_f12_i0_0", "unis/f218/09_mobile/f218_09_l11_i0_0",
    "unis/f218/10_mobile/f218_10_p01_i0_0", "unis/f218/10_mobile/f218_10_f12_i0_0", "unis/f218/10_mobile/f218_10_l11_i0_0",
    "unis/f218/11_mobile/f218_11_p01_i0_0", "unis/f218/11_mobile/f218_11_f12_i0_0", "unis/f218/11_mobile/f218_11_l11_i0_0",
    "unis/f218/12_mobile/f218_12_p01_i0_0", "unis/f218/12_mobile/f218_12_f07_i0_0", "unis/f218/12_mobile/f218_12_l06_i0_0",
    "unis/f218/13_mobile/f218_13_p01_i0_0", "unis/f218/13_mobile/f218_13_f07_i0_0", "unis/f218/13_mobile/f218_13_l06_i0_0",
    "unis/f218/14_mobile/f218_14_p01_i0_0", "unis/f218/14_mobile/f218_14_f07_i0_0", "unis/f218/14_mobile/f218_14_l06_i0_0",
    "unis/f218/15_mobile/f218_15_p01_i0_0", "unis/f218/15_mobile/f218_15_f07_i0_0", "unis/f218/15_mobile/f218_15_l06_i0_0",
    "unis/f218/16_mobile/f218_16_p01_i0_0", "unis/f218/16_mobile/f218_16_f07_i0_0", "unis/f218/16_mobile/f218_16_l06_i0_0",
    "unis/f218/17_mobile/f218_17_p01_i0_0", "unis/f218/17_mobile/f218_17_f07_i0_0", "unis/f218/17_mobile/f218_17_l06_i0_0",
    "unis/f230/01_mobile/f230_01_p01_i0_0", "unis/f230/01_mobile/f230_01_f12_i0_0", "unis/f230/01_mobile/f230_01_l11_i0_0",
    "unis/f230/02_mobile/f230_02_p01_i0_0", "unis/f230/02_mobile/f230_02_f12_i0_0", "unis/f230/02_mobile/f230_02_l11_i0_0",
    "unis/f230/03_mobile/f230_03_p01_i0_0", "unis/f230/03_mobile/f230_03_f12_i0_0", "unis/f230/03_mobile/f230_03_l11_i0_0",
    "unis/f230/04_mobile/f230_04_p01_i0_0", "unis/f230/04_mobile/f230_04_f12_i0_0", "unis/f230/04_mobile/f230_04_l11_i0_0",
    "unis/f230/05_mobile/f230_05_p01_i0_0", "unis/f230/05_mobile/f230_05_f12_i0_0", "unis/f230/05_mobile/f230_05_l11_i0_0",
    "unis/f230/06_mobile/f230_06_p01_i0_0", "unis/f230/06_mobile/f230_06_f12_i0_0", "unis/f230/06_mobile/f230_06_l11_i0_0",
    "unis/f230/07_mobile/f230_07_p01_i0_0", "unis/f230/07_mobile/f230_07_f07_i0_0", "unis/f230/07_mobile/f230_07_l06_i0_0",
    "unis/f230/08_mobile/f230_08_p01_i0_0", "unis/f230/08_mobile/f230_08_f07_i0_0", "unis/f230/08_mobile/f230_08_l06_i0_0",
    "unis/f230/09_mobile/f230_09_p01_i0_0", "unis/f230/09_mobile/f230_09_f07_i0_0", "unis/f230/09_mobile/f230_09_l06_i0_0",
    "unis/f230/10_mobile/f230_10_p01_i0_0", "unis/f230/10_mobile/f230_10_f07_i0_0", "unis/f230/10_mobile/f230_10_l06_i0_0",
    "unis/f230/11_mobile/f230_11_p01_i0_0", "unis/f230/11_mobile/f230_11_f07_i0_0", "unis/f230/11_mobile/f230_11_l06_i0_0",
    "unis/f230/12_mobile/f230_12_p01_i0_0", "unis/f230/12_mobile/f230_12_f07_i0_0", "unis/f230/12_mobile/f230_12_l06_i0_0",
    "unis/f232/01_mobile/f232_01_p01_i0_0", "unis/f232/01_mobile/f232_01_f12_i0_0", "unis/f232/01_mobile/f232_01_l11_i0_0",
    "unis/f232/02_mobile/f232_02_p01_i0_0", "unis/f232/02_mobile/f232_02_f12_i0_0", "unis/f232/02_mobile/f232_02_l11_i0_0",
    "unis/f232/03_mobile/f232_03_p01_i0_0", "unis/f232/03_mobile/f232_03_f12_i0_0", "unis/f232/03_mobile/f232_03_l11_i0_0",
    "unis/f232/04_mobile/f232_04_p01_i0_0", "unis/f232/04_mobile/f232_04_f12_i0_0", "unis/f232/04_mobile/f232_04_l11_i0_0",
    "unis/f232/05_mobile/f232_05_p01_i0_0", "unis/f232/05_mobile/f232_05_f12_i0_0", "unis/f232/05_mobile/f232_05_l11_i0_0",
    "unis/f232/07_mobile/f232_07_p01_i0_0", "unis/f232/07_mobile/f232_07_f12_i0_0", "unis/f232/07_mobile/f232_07_l11_i0_0",
    "unis/f232/08_mobile/f232_08_p01_i0_0", "unis/f232/08_mobile/f232_08_f07_i0_0", "unis/f232/08_mobile/f232_08_l06_i0_0",
    "unis/f232/09_mobile/f232_09_p01_i0_0", "unis/f232/09_mobile/f232_09_f07_i0_0", "unis/f232/09_mobile/f232_09_l06_i0_0",
    "unis/f232/10_mobile/f232_10_p01_i0_0", "unis/f232/10_mobile/f232_10_f07_i0_0", "unis/f232/10_mobile/f232_10_l06_i0_0",
    "unis/f232/11_mobile/f232_11_p01_i0_0", "unis/f232/11_mobile/f232_11_f07_i0_0", "unis/f232/11_mobile/f232_11_l06_i0_0",
    "unis/f232/12_mobile/f232_12_p01_i0_0", "unis/f232/12_mobile/f232_12_f07_i0_0", "unis/f232/12_mobile/f232_12_l06_i0_0",
    "unis/f232/13_mobile/f232_13_p01_i0_0", "unis/f232/13_mobile/f232_13_f07_i0_0", "unis/f232/13_mobile/f232_13_l06_i0_0",
    "lia/f507/01_mobile/f507_01_p01_i0_0", "lia/f507/01_mobile/f507_01_f12_i0_0", "lia/f507/01_mobile/f507_01_l11_i0_0",
    "lia/f507/02_mobile/f507_02_p01_i0_0", "lia/f507/02_mobile/f507_02_f12_i0_0", "lia/f507/02_mobile/f507_02_l11_i0_0",
    "lia/f507/03_mobile/f507_03_p01_i0_0", "lia/f507/03_mobile/f507_03_f12_i0_0", "lia/f507/03_mobile/f507_03_l11_i0_0",
    "lia/f507/04_mobile/f507_04_p01_i0_0", "lia/f507/04_mobile/f507_04_f12_i0_0", "lia/f507/04_mobile/f507_04_l11_i0_0",
    "lia/f507/05_mobile/f507_05_p01_i0_0", "lia/f507/05_mobile/f507_05_f12_i0_0", "lia/f507/05_mobile/f507_05_l11_i0_0",
    "lia/f507/06_mobile/f507_06_p01_i0_0", "lia/f507/06_mobile/f507_06_f12_i0_0", "lia/f507/06_mobile/f507_06_l11_i0_0",
    "lia/f507/07_mobile/f507_07_p01_i0_0", "lia/f507/07_mobile/f507_07_f07_i0_0", "lia/f507/07_mobile/f507_07_l06_i0_0",
    "lia/f507/08_mobile/f507_08_p01_i0_0", "lia/f507/08_mobile/f507_08_f07_i0_0", "lia/f507/08_mobile/f507_08_l06_i0_0",
    "lia/f507/09_mobile/f507_09_p01_i0_0", "lia/f507/09_mobile/f507_09_f07_i0_0", "lia/f507/09_mobile/f507_09_l06_i0_0",
    "lia/f507/10_mobile/f507_10_p01_i0_0", "lia/f507/10_mobile/f507_10_f07_i0_0", "lia/f507/10_mobile/f507_10_l06_i0_0",
    "lia/f507/11_mobile/f507_11_p01_i0_0", "lia/f507/11_mobile/f507_11_f07_i0_0", "lia/f507/11_mobile/f507_11_l06_i0_0",
    "lia/f507/12_mobile/f507_12_p01_i0_0", "lia/f507/12_mobile/f507_12_f07_i0_0", "lia/f507/12_mobile/f507_12_l06_i0_0",
    "lia/f508/01_mobile/f508_01_p01_i0_0", "lia/f508/01_mobile/f508_01_f12_i0_0", "lia/f508/01_mobile/f508_01_l11_i0_0",
    "lia/f508/02_mobile/f508_02_p01_i0_0", "lia/f508/02_mobile/f508_02_f12_i0_0", "lia/f508/02_mobile/f508_02_l11_i0_0",
    "lia/f508/03_mobile/f508_03_p01_i0_0", "lia/f508/03_mobile/f508_03_f12_i0_0", "lia/f508/03_mobile/f508_03_l11_i0_0",
    "lia/f508/04_mobile/f508_04_p01_i0_0", "lia/f508/04_mobile/f508_04_f12_i0_0", "lia/f508/04_mobile/f508_04_l11_i0_0",
    "lia/f508/05_mobile/f508_05_p01_i0_0", "lia/f508/05_mobile/f508_05_f12_i0_0", "lia/f508/05_mobile/f508_05_l11_i0_0",
    "lia/f508/06_mobile/f508_06_p01_i0_0", "lia/f508/06_mobile/f508_06_f12_i0_0", "lia/f508/06_mobile/f508_06_l11_i0_0",
    "lia/f508/07_mobile/f508_07_p01_i0_0", "lia/f508/07_mobile/f508_07_f07_i0_0", "lia/f508/07_mobile/f508_07_l06_i0_0",
    "lia/f508/08_mobile/f508_08_p01_i0_0", "lia/f508/08_mobile/f508_08_f07_i0_0", "lia/f508/08_mobile/f508_08_l06_i0_0",
    "lia/f508/09_mobile/f508_09_p01_i0_0", "lia/f508/09_mobile/f508_09_f07_i0_0", "lia/f508/09_mobile/f508_09_l06_i0_0",
    "lia/f508/10_mobile/f508_10_p01_i0_0", "lia/f508/10_mobile/f508_10_f07_i0_0", "lia/f508/10_mobile/f508_10_l06_i0_0",
    "lia/f508/11_mobile/f508_11_p01_i0_0", "lia/f508/11_mobile/f508_11_f07_i0_0", "lia/f508/11_mobile/f508_11_l06_i0_0",
    "lia/f508/12_mobile/f508_12_p01_i0_0", "lia/f508/12_mobile/f508_12_f07_i0_0", "lia/f508/12_mobile/f508_12_l06_i0_0",
    "lia/f509/01_mobile/f509_01_p01_i0_0", "lia/f509/01_mobile/f509_01_f12_i0_0", "lia/f509/01_mobile/f509_01_l11_i0_0",
    "lia/f509/02_mobile/f509_02_p01_i0_0", "lia/f509/02_mobile/f509_02_f12_i0_0", "lia/f509/02_mobile/f509_02_l11_i0_0",
    "lia/f509/03_mobile/f509_03_p01_i0_0", "lia/f509/03_mobile/f509_03_f12_i0_0", "lia/f509/03_mobile/f509_03_l11_i0_0",
    "lia/f509/04_mobile/f509_04_p01_i0_0", "lia/f509/04_mobile/f509_04_f12_i0_0", "lia/f509/04_mobile/f509_04_l11_i0_0",
    "lia/f509/05_mobile/f509_05_p01_i0_0", "lia/f509/05_mobile/f509_05_f12_i0_0", "lia/f509/05_mobile/f509_05_l11_i0_0",
    "lia/f509/06_mobile/f509_06_p01_i0_0", "lia/f509/06_mobile/f509_06_f12_i0_0", "lia/f509/06_mobile/f509_06_l11_i0_0",
    "lia/f509/07_mobile/f509_07_p01_i0_0", "lia/f509/07_mobile/f509_07_f07_i0_0", "lia/f509/07_mobile/f509_07_l06_i0_0",
    "lia/f509/08_mobile/f509_08_p01_i0_0", "lia/f509/08_mobile/f509_08_f07_i0_0", "lia/f509/08_mobile/f509_08_l06_i0_0",
    "lia/f509/09_mobile/f509_09_p01_i0_0", "lia/f509/09_mobile/f509_09_f07_i0_0", "lia/f509/09_mobile/f509_09_l06_i0_0",
    "lia/f509/10_mobile/f509_10_p01_i0_0", "lia/f509/10_mobile/f509_10_f07_i0_0", "lia/f509/10_mobile/f509_10_l06_i0_0",
    "lia/f509/11_mobile/f509_11_p01_i0_0", "lia/f509/11_mobile/f509_11_f07_i0_0", "lia/f509/11_mobile/f509_11_l06_i0_0",
    "lia/f509/12_mobile/f509_12_p01_i0_0", "lia/f509/12_mobile/f509_12_f07_i0_0", "lia/f509/12_mobile/f509_12_l06_i0_0",
    "lia/f510/01_mobile/f510_01_p01_i0_0", "lia/f510/01_mobile/f510_01_f12_i0_0", "lia/f510/01_mobile/f510_01_l11_i0_0",
    "lia/f510/02_mobile/f510_02_p01_i0_0", "lia/f510/02_mobile/f510_02_f12_i0_0", "lia/f510/02_mobile/f510_02_l11_i0_0",
    "lia/f510/03_mobile/f510_03_p01_i0_0", "lia/f510/03_mobile/f510_03_f12_i0_0", "lia/f510/03_mobile/f510_03_l11_i0_0",
    "lia/f510/04_mobile/f510_04_p01_i0_0", "lia/f510/04_mobile/f510_04_f12_i0_0", "lia/f510/04_mobile/f510_04_l11_i0_0",
    "lia/f510/05_mobile/f510_05_p01_i0_0", "lia/f510/05_mobile/f510_05_f12_i0_0", "lia/f510/05_mobile/f510_05_l11_i0_0",
    "lia/f510/06_mobile/f510_06_p01_i0_0", "lia/f510/06_mobile/f510_06_f12_i0_0", "lia/f510/06_mobile/f510_06_l11_i0_0",
    "lia/f510/07_mobile/f510_07_p01_i0_0", "lia/f510/07_mobile/f510_07_f07_i0_0", "lia/f510/07_mobile/f510_07_l06_i0_0",
    "lia/f510/08_mobile/f510_08_p01_i0_0", "lia/f510/08_mobile/f510_08_f07_i0_0", "lia/f510/08_mobile/f510_08_l06_i0_0",
    "lia/f510/09_mobile/f510_09_p01_i0_0", "lia/f510/09_mobile/f510_09_f07_i0_0", "lia/f510/09_mobile/f510_09_l06_i0_0",
    "lia/f510/10_mobile/f510_10_p01_i0_0", "lia/f510/10_mobile/f510_10_f07_i0_0", "lia/f510/10_mobile/f510_10_l06_i0_0",
    "lia/f510/11_mobile/f510_11_p01_i0_0", "lia/f510/11_mobile/f510_11_f07_i0_0", "lia/f510/11_mobile/f510_11_l06_i0_0",
    "lia/f510/12_mobile/f510_12_p01_i0_0", "lia/f510/12_mobile/f510_12_f07_i0_0", "lia/f510/12_mobile/f510_12_l06_i0_0",
    "lia/f528/01_mobile/f528_01_p01_i0_0", "lia/f528/01_mobile/f528_01_f12_i0_0", "lia/f528/01_mobile/f528_01_l11_i0_0",
    "lia/f528/02_mobile/f528_02_p01_i0_0", "lia/f528/02_mobile/f528_02_f12_i0_0", "lia/f528/02_mobile/f528_02_l11_i0_0",
    "lia/f528/03_mobile/f528_03_p01_i0_0", "lia/f528/03_mobile/f528_03_f12_i0_0", "lia/f528/03_mobile/f528_03_l11_i0_0",
    "lia/f528/04_mobile/f528_04_p01_i0_0", "lia/f528/04_mobile/f528_04_f12_i0_0", "lia/f528/04_mobile/f528_04_l11_i0_0",
    "lia/f528/05_mobile/f528_05_p01_i0_0", "lia/f528/05_mobile/f528_05_f12_i0_0", "lia/f528/05_mobile/f528_05_l11_i0_0",
    "lia/f528/06_mobile/f528_06_p01_i0_0", "lia/f528/06_mobile/f528_06_f12_i0_0", "lia/f528/06_mobile/f528_06_l11_i0_0",
    "lia/f528/07_mobile/f528_07_p01_i0_0", "lia/f528/07_mobile/f528_07_f07_i0_0", "lia/f528/07_mobile/f528_07_l06_i0_0",
    "lia/f528/08_mobile/f528_08_p01_i0_0", "lia/f528/08_mobile/f528_08_f07_i0_0", "lia/f528/08_mobile/f528_08_l06_i0_0",
    "lia/f528/09_mobile/f528_09_p01_i0_0", "lia/f528/09_mobile/f528_09_f07_i0_0", "lia/f528/09_mobile/f528_09_l06_i0_0",
    "lia/f528/10_mobile/f528_10_p01_i0_0", "lia/f528/10_mobile/f528_10_f07_i0_0", "lia/f528/10_mobile/f528_10_l06_i0_0",
    "lia/f528/11_mobile/f528_11_p01_i0_0", "lia/f528/11_mobile/f528_11_f07_i0_0", "lia/f528/11_mobile/f528_11_l06_i0_0",
    "lia/f528/12_mobile/f528_12_p01_i0_0", "lia/f528/12_mobile/f528_12_f07_i0_0", "lia/f528/12_mobile/f528_12_l06_i0_0",
    "unis/m202/01_mobile/m202_01_p01_i0_0", "unis/m202/01_mobile/m202_01_f12_i0_0", "unis/m202/01_mobile/m202_01_l11_i0_0",
    "unis/m202/02_mobile/m202_02_p01_i0_0", "unis/m202/02_mobile/m202_02_f12_i0_0", "unis/m202/02_mobile/m202_02_l11_i0_0",
    "unis/m202/03_mobile/m202_03_p01_i0_0", "unis/m202/03_mobile/m202_03_f12_i0_0", "unis/m202/03_mobile/m202_03_l11_i0_0",
    "unis/m202/04_mobile/m202_04_p01_i0_0", "unis/m202/04_mobile/m202_04_f12_i0_0", "unis/m202/04_mobile/m202_04_l11_i0_0",
    "unis/m202/05_mobile/m202_05_p01_i0_0", "unis/m202/05_mobile/m202_05_f12_i0_0", "unis/m202/05_mobile/m202_05_l11_i0_0",
    "unis/m202/06_mobile/m202_06_p01_i0_0", "unis/m202/06_mobile/m202_06_f12_i0_0", "unis/m202/06_mobile/m202_06_l11_i0_0",
    "unis/m202/07_mobile/m202_07_p01_i0_0", "unis/m202/07_mobile/m202_07_f07_i0_0", "unis/m202/07_mobile/m202_07_l06_i0_0",
    "unis/m202/08_mobile/m202_08_p01_i0_0", "unis/m202/08_mobile/m202_08_f07_i0_0", "unis/m202/08_mobile/m202_08_l06_i0_0",
    "unis/m202/09_mobile/m202_09_p01_i0_0", "unis/m202/09_mobile/m202_09_f07_i0_0", "unis/m202/09_mobile/m202_09_l06_i0_0",
    "unis/m202/10_mobile/m202_10_p01_i0_0", "unis/m202/10_mobile/m202_10_f07_i0_0", "unis/m202/10_mobile/m202_10_l06_i0_0",
    "unis/m202/11_mobile/m202_11_p01_i0_0", "unis/m202/11_mobile/m202_11_f07_i0_0", "unis/m202/11_mobile/m202_11_l06_i0_0",
    "unis/m202/12_mobile/m202_12_p01_i0_0", "unis/m202/12_mobile/m202_12_f07_i0_0", "unis/m202/12_mobile/m202_12_l06_i0_0",
    "unis/m203/01_mobile/m203_01_p01_i0_0", "unis/m203/01_mobile/m203_01_f12_i0_0", "unis/m203/01_mobile/m203_01_l11_i0_0",
    "unis/m203/03_mobile/m203_03_p01_i0_0", "unis/m203/03_mobile/m203_03_f12_i0_0", "unis/m203/03_mobile/m203_03_l11_i0_0",
    "unis/m203/04_mobile/m203_04_p01_i0_0", "unis/m203/04_mobile/m203_04_f12_i0_0", "unis/m203/04_mobile/m203_04_l11_i0_0",
    "unis/m203/05_mobile/m203_05_p01_i0_0", "unis/m203/05_mobile/m203_05_f12_i0_0", "unis/m203/05_mobile/m203_05_l11_i0_0",
    "unis/m203/06_mobile/m203_06_p01_i0_0", "unis/m203/06_mobile/m203_06_f12_i0_0", "unis/m203/06_mobile/m203_06_l11_i0_0",
    "unis/m203/07_mobile/m203_07_p01_i0_0", "unis/m203/07_mobile/m203_07_f12_i0_0", "unis/m203/07_mobile/m203_07_l11_i0_0",
    "unis/m203/08_mobile/m203_08_p01_i0_0", "unis/m203/08_mobile/m203_08_f07_i0_0", "unis/m203/08_mobile/m203_08_l06_i0_0",
    "unis/m203/09_mobile/m203_09_p01_i0_0", "unis/m203/09_mobile/m203_09_f07_i0_0", "unis/m203/09_mobile/m203_09_l06_i0_0",
    "unis/m203/10_mobile/m203_10_p01_i0_0", "unis/m203/10_mobile/m203_10_f07_i0_0", "unis/m203/10_mobile/m203_10_l06_i0_0",
    "unis/m203/11_mobile/m203_11_p01_i0_0", "unis/m203/11_mobile/m203_11_f07_i0_0", "unis/m203/11_mobile/m203_11_l06_i0_0",
    "unis/m203/12_mobile/m203_12_p01_i0_0", "unis/m203/12_mobile/m203_12_f07_i0_0", "unis/m203/12_mobile/m203_12_l06_i0_0",
    "unis/m203/13_mobile/m203_13_p01_i0_0", "unis/m203/13_mobile/m203_13_f07_i0_0", "unis/m203/13_mobile/m203_13_l06_i0_0",
    "unis/m207/01_mobile/m207_01_p01_i0_0", "unis/m207/01_mobile/m207_01_f12_i0_0", "unis/m207/01_mobile/m207_01_l11_i0_0",
    "unis/m207/02_mobile/m207_02_p01_i0_0", "unis/m207/02_mobile/m207_02_f12_i0_0", "unis/m207/02_mobile/m207_02_l11_i0_0",
    "unis/m207/03_mobile/m207_03_p01_i0_0", "unis/m207/03_mobile/m207_03_f12_i0_0", "unis/m207/03_mobile/m207_03_l11_i0_0",
    "unis/m207/04_mobile/m207_04_p01_i0_0", "unis/m207/04_mobile/m207_04_f12_i0_0", "unis/m207/04_mobile/m207_04_l11_i0_0",
    "unis/m207/05_mobile/m207_05_p01_i0_0", "unis/m207/05_mobile/m207_05_f12_i0_0", "unis/m207/05_mobile/m207_05_l11_i0_0",
    "unis/m207/06_mobile/m207_06_p01_i0_0", "unis/m207/06_mobile/m207_06_f12_i0_0", "unis/m207/06_mobile/m207_06_l11_i0_0",
    "unis/m207/07_mobile/m207_07_p01_i0_0", "unis/m207/07_mobile/m207_07_f07_i0_0", "unis/m207/07_mobile/m207_07_l06_i0_0",
    "unis/m207/08_mobile/m207_08_p01_i0_0", "unis/m207/08_mobile/m207_08_f07_i0_0", "unis/m207/08_mobile/m207_08_l06_i0_0",
    "unis/m207/09_mobile/m207_09_p01_i0_0", "unis/m207/09_mobile/m207_09_f07_i0_0", "unis/m207/09_mobile/m207_09_l06_i0_0",
    "unis/m207/10_mobile/m207_10_p01_i0_0", "unis/m207/10_mobile/m207_10_f07_i0_0", "unis/m207/10_mobile/m207_10_l06_i0_0",
    "unis/m207/11_mobile/m207_11_p01_i0_0", "unis/m207/11_mobile/m207_11_f07_i0_0", "unis/m207/11_mobile/m207_11_l06_i0_0",
    "unis/m207/12_mobile/m207_12_p01_i0_0", "unis/m207/12_mobile/m207_12_f07_i0_0", "unis/m207/12_mobile/m207_12_l06_i0_0",
    "unis/m208/01_mobile/m208_01_p01_i0_0", "unis/m208/01_mobile/m208_01_f12_i0_0", "unis/m208/01_mobile/m208_01_l11_i0_0",
    "unis/m208/02_mobile/m208_02_p01_i0_0", "unis/m208/02_mobile/m208_02_f12_i0_0", "unis/m208/02_mobile/m208_02_l11_i0_0",
    "unis/m208/03_mobile/m208_03_p01_i0_0", "unis/m208/03_mobile/m208_03_f12_i0_0", "unis/m208/03_mobile/m208_03_l11_i0_0",
    "unis/m208/04_mobile/m208_04_p01_i0_0", "unis/m208/04_mobile/m208_04_f12_i0_0", "unis/m208/04_mobile/m208_04_l11_i0_0",
    "unis/m208/05_mobile/m208_05_p01_i0_0", "unis/m208/05_mobile/m208_05_f12_i0_0", "unis/m208/05_mobile/m208_05_l11_i0_0",
    "unis/m208/06_mobile/m208_06_p01_i0_0", "unis/m208/06_mobile/m208_06_f12_i0_0", "unis/m208/06_mobile/m208_06_l11_i0_0",
    "unis/m208/07_mobile/m208_07_p01_i0_0", "unis/m208/07_mobile/m208_07_f07_i0_0", "unis/m208/07_mobile/m208_07_l06_i0_0",
    "unis/m208/08_mobile/m208_08_p01_i0_0", "unis/m208/08_mobile/m208_08_f07_i0_0", "unis/m208/08_mobile/m208_08_l06_i0_0",
    "unis/m208/09_mobile/m208_09_p01_i0_0", "unis/m208/09_mobile/m208_09_f07_i0_0", "unis/m208/09_mobile/m208_09_l06_i0_0",
    "unis/m208/10_mobile/m208_10_p01_i0_0", "unis/m208/10_mobile/m208_10_f07_i0_0", "unis/m208/10_mobile/m208_10_l06_i0_0",
    "unis/m208/11_mobile/m208_11_p01_i0_0", "unis/m208/11_mobile/m208_11_f07_i0_0", "unis/m208/11_mobile/m208_11_l06_i0_0",
    "unis/m208/12_mobile/m208_12_p01_i0_0", "unis/m208/12_mobile/m208_12_f07_i0_0", "unis/m208/12_mobile/m208_12_l06_i0_0",
    "unis/m212/01_mobile/m212_01_p01_i0_0", "unis/m212/01_mobile/m212_01_f12_i0_0", "unis/m212/01_mobile/m212_01_l11_i0_0",
    "unis/m212/02_mobile/m212_02_p01_i0_0", "unis/m212/02_mobile/m212_02_f12_i0_0", "unis/m212/02_mobile/m212_02_l11_i0_0",
    "unis/m212/03_mobile/m212_03_p01_i0_0", "unis/m212/03_mobile/m212_03_f12_i0_0", "unis/m212/03_mobile/m212_03_l11_i0_0",
    "unis/m212/04_mobile/m212_04_p01_i0_0", "unis/m212/04_mobile/m212_04_f12_i0_0", "unis/m212/04_mobile/m212_04_l11_i0_0",
    "unis/m212/05_mobile/m212_05_p01_i0_0", "unis/m212/05_mobile/m212_05_f12_i0_0", "unis/m212/05_mobile/m212_05_l11_i0_0",
    "unis/m212/06_mobile/m212_06_p01_i0_0", "unis/m212/06_mobile/m212_06_f12_i0_0", "unis/m212/06_mobile/m212_06_l11_i0_0",
    "unis/m212/07_mobile/m212_07_p01_i0_0", "unis/m212/07_mobile/m212_07_f07_i0_0", "unis/m212/07_mobile/m212_07_l06_i0_0",
    "unis/m212/08_mobile/m212_08_p01_i0_0", "unis/m212/08_mobile/m212_08_f07_i0_0", "unis/m212/08_mobile/m212_08_l06_i0_0",
    "unis/m212/09_mobile/m212_09_p01_i0_0", "unis/m212/09_mobile/m212_09_f07_i0_0", "unis/m212/09_mobile/m212_09_l06_i0_0",
    "unis/m212/10_mobile/m212_10_p01_i0_0", "unis/m212/10_mobile/m212_10_f07_i0_0", "unis/m212/10_mobile/m212_10_l06_i0_0",
    "unis/m212/11_mobile/m212_11_p01_i0_0", "unis/m212/11_mobile/m212_11_f07_i0_0", "unis/m212/11_mobile/m212_11_l06_i0_0",
    "unis/m212/12_mobile/m212_12_p01_i0_0", "unis/m212/12_mobile/m212_12_f07_i0_0", "unis/m212/12_mobile/m212_12_l06_i0_0",
    "unis/m215/02_mobile/m215_02_p01_i0_0", "unis/m215/02_mobile/m215_02_f12_i0_0", "unis/m215/02_mobile/m215_02_l11_i0_0",
    "unis/m215/03_mobile/m215_03_p01_i0_0", "unis/m215/03_mobile/m215_03_f12_i0_0", "unis/m215/03_mobile/m215_03_l11_i0_0",
    "unis/m215/04_mobile/m215_04_p01_i0_0", "unis/m215/04_mobile/m215_04_f12_i0_0", "unis/m215/04_mobile/m215_04_l11_i0_0",
    "unis/m215/05_mobile/m215_05_p01_i0_0", "unis/m215/05_mobile/m215_05_f12_i0_0", "unis/m215/05_mobile/m215_05_l11_i0_0",
    "unis/m215/06_mobile/m215_06_p01_i0_0", "unis/m215/06_mobile/m215_06_f12_i0_0", "unis/m215/06_mobile/m215_06_l11_i0_0",
    "unis/m215/07_mobile/m215_07_p01_i0_0", "unis/m215/07_mobile/m215_07_f12_i0_0", "unis/m215/07_mobile/m215_07_l11_i0_0",
    "unis/m215/08_mobile/m215_08_p01_i0_0", "unis/m215/08_mobile/m215_08_f07_i0_0", "unis/m215/08_mobile/m215_08_l06_i0_0",
    "unis/m215/09_mobile/m215_09_p01_i0_0", "unis/m215/09_mobile/m215_09_f07_i0_0", "unis/m215/09_mobile/m215_09_l06_i0_0",
    "unis/m215/10_mobile/m215_10_p01_i0_0", "unis/m215/10_mobile/m215_10_f07_i0_0", "unis/m215/10_mobile/m215_10_l06_i0_0",
    "unis/m215/11_mobile/m215_11_p01_i0_0", "unis/m215/11_mobile/m215_11_f07_i0_0", "unis/m215/11_mobile/m215_11_l06_i0_0",
    "unis/m215/12_mobile/m215_12_p01_i0_0", "unis/m215/12_mobile/m215_12_f07_i0_0", "unis/m215/12_mobile/m215_12_l06_i0_0",
    "unis/m215/13_mobile/m215_13_p01_i0_0", "unis/m215/13_mobile/m215_13_f07_i0_0", "unis/m215/13_mobile/m215_13_l06_i0_0",
    "unis/m217/01_mobile/m217_01_p01_i0_0", "unis/m217/01_mobile/m217_01_f12_i0_0", "unis/m217/01_mobile/m217_01_l11_i0_0",
    "unis/m217/02_mobile/m217_02_p01_i0_0", "unis/m217/02_mobile/m217_02_f12_i0_0", "unis/m217/02_mobile/m217_02_l11_i0_0",
    "unis/m217/03_mobile/m217_03_p01_i0_0", "unis/m217/03_mobile/m217_03_f12_i0_0", "unis/m217/03_mobile/m217_03_l11_i0_0",
    "unis/m217/04_mobile/m217_04_p01_i0_0", "unis/m217/04_mobile/m217_04_f12_i0_0", "unis/m217/04_mobile/m217_04_l11_i0_0",
    "unis/m217/05_mobile/m217_05_p01_i0_0", "unis/m217/05_mobile/m217_05_f12_i0_0", "unis/m217/05_mobile/m217_05_l11_i0_0",
    "unis/m217/06_mobile/m217_06_p01_i0_0", "unis/m217/06_mobile/m217_06_f12_i0_0", "unis/m217/06_mobile/m217_06_l11_i0_0",
    "unis/m217/07_mobile/m217_07_p01_i0_0", "unis/m217/07_mobile/m217_07_f07_i0_0", "unis/m217/07_mobile/m217_07_l06_i0_0",
    "unis/m217/08_mobile/m217_08_p01_i0_0", "unis/m217/08_mobile/m217_08_f07_i0_0", "unis/m217/08_mobile/m217_08_l06_i0_0",
    "unis/m217/09_mobile/m217_09_p01_i0_0", "unis/m217/09_mobile/m217_09_f07_i0_0", "unis/m217/09_mobile/m217_09_l06_i0_0",
    "unis/m217/10_mobile/m217_10_p01_i0_0", "unis/m217/10_mobile/m217_10_f07_i0_0", "unis/m217/10_mobile/m217_10_l06_i0_0",
    "unis/m217/11_mobile/m217_11_p01_i0_0", "unis/m217/11_mobile/m217_11_f07_i0_0", "unis/m217/11_mobile/m217_11_l06_i0_0",
    "unis/m217/12_mobile/m217_12_p01_i0_0", "unis/m217/12_mobile/m217_12_f07_i0_0", "unis/m217/12_mobile/m217_12_l06_i0_0",
    "unis/m223/01_mobile/m223_01_p01_i0_0", "unis/m223/01_mobile/m223_01_f12_i0_0", "unis/m223/01_mobile/m223_01_l11_i0_0",
    "unis/m223/02_mobile/m223_02_p01_i0_0", "unis/m223/02_mobile/m223_02_f12_i0_0", "unis/m223/02_mobile/m223_02_l11_i0_0",
    "unis/m223/03_mobile/m223_03_p01_i0_0", "unis/m223/03_mobile/m223_03_f12_i0_0", "unis/m223/03_mobile/m223_03_l11_i0_0",
    "unis/m223/04_mobile/m223_04_p01_i0_0", "unis/m223/04_mobile/m223_04_f12_i0_0", "unis/m223/04_mobile/m223_04_l11_i0_0",
    "unis/m223/05_mobile/m223_05_p01_i0_0", "unis/m223/05_mobile/m223_05_f12_i0_0", "unis/m223/05_mobile/m223_05_l11_i0_0",
    "unis/m223/06_mobile/m223_06_p01_i0_0", "unis/m223/06_mobile/m223_06_f12_i0_0", "unis/m223/06_mobile/m223_06_l11_i0_0",
    "unis/m223/07_mobile/m223_07_p01_i0_0", "unis/m223/07_mobile/m223_07_f07_i0_0", "unis/m223/07_mobile/m223_07_l06_i0_0",
    "unis/m223/08_mobile/m223_08_p01_i0_0", "unis/m223/08_mobile/m223_08_f07_i0_0", "unis/m223/08_mobile/m223_08_l06_i0_0",
    "unis/m223/09_mobile/m223_09_p01_i0_0", "unis/m223/09_mobile/m223_09_f07_i0_0", "unis/m223/09_mobile/m223_09_l06_i0_0",
    "unis/m223/10_mobile/m223_10_p01_i0_0", "unis/m223/10_mobile/m223_10_f07_i0_0", "unis/m223/10_mobile/m223_10_l06_i0_0",
    "unis/m223/11_mobile/m223_11_p01_i0_0", "unis/m223/11_mobile/m223_11_f07_i0_0", "unis/m223/11_mobile/m223_11_l06_i0_0",
    "unis/m223/12_mobile/m223_12_p01_i0_0", "unis/m223/12_mobile/m223_12_f07_i0_0", "unis/m223/12_mobile/m223_12_l06_i0_0",
    "unis/m224/01_mobile/m224_01_p01_i0_0", "unis/m224/01_mobile/m224_01_f12_i0_0", "unis/m224/01_mobile/m224_01_l11_i0_0",
    "unis/m224/02_mobile/m224_02_p01_i0_0", "unis/m224/02_mobile/m224_02_f12_i0_0", "unis/m224/02_mobile/m224_02_l11_i0_0",
    "unis/m224/03_mobile/m224_03_p01_i0_0", "unis/m224/03_mobile/m224_03_f12_i0_0", "unis/m224/03_mobile/m224_03_l11_i0_0",
    "unis/m224/04_mobile/m224_04_p01_i0_0", "unis/m224/04_mobile/m224_04_f12_i0_0", "unis/m224/04_mobile/m224_04_l11_i0_0",
    "unis/m224/05_mobile/m224_05_p01_i0_0", "unis/m224/05_mobile/m224_05_f12_i0_0", "unis/m224/05_mobile/m224_05_l11_i0_0",
    "unis/m224/06_mobile/m224_06_p01_i0_0", "unis/m224/06_mobile/m224_06_f12_i0_0", "unis/m224/06_mobile/m224_06_l11_i0_0",
    "unis/m224/07_mobile/m224_07_p01_i0_0", "unis/m224/07_mobile/m224_07_f07_i0_0", "unis/m224/07_mobile/m224_07_l06_i0_0",
    "unis/m224/08_mobile/m224_08_p01_i0_0", "unis/m224/08_mobile/m224_08_f07_i0_0", "unis/m224/08_mobile/m224_08_l06_i0_0",
    "unis/m224/09_mobile/m224_09_p01_i0_0", "unis/m224/09_mobile/m224_09_f07_i0_0", "unis/m224/09_mobile/m224_09_l06_i0_0",
    "unis/m224/10_mobile/m224_10_p01_i0_0", "unis/m224/10_mobile/m224_10_f07_i0_0", "unis/m224/10_mobile/m224_10_l06_i0_0",
    "unis/m224/11_mobile/m224_11_p01_i0_0", "unis/m224/11_mobile/m224_11_f07_i0_0", "unis/m224/11_mobile/m224_11_l06_i0_0",
    "unis/m224/12_mobile/m224_12_p01_i0_0", "unis/m224/12_mobile/m224_12_f07_i0_0", "unis/m224/12_mobile/m224_12_l06_i0_0",
    "unis/m225/01_mobile/m225_01_p01_i0_0", "unis/m225/01_mobile/m225_01_f12_i0_0", "unis/m225/01_mobile/m225_01_l11_i0_0",
    "unis/m225/03_mobile/m225_03_p01_i0_0", "unis/m225/03_mobile/m225_03_f12_i0_0", "unis/m225/03_mobile/m225_03_l11_i0_0",
    "unis/m225/04_mobile/m225_04_p01_i0_0", "unis/m225/04_mobile/m225_04_f12_i0_0", "unis/m225/04_mobile/m225_04_l11_i0_0",
    "unis/m225/05_mobile/m225_05_p01_i0_0", "unis/m225/05_mobile/m225_05_f12_i0_0", "unis/m225/05_mobile/m225_05_l11_i0_0",
    "unis/m225/06_mobile/m225_06_p01_i0_0", "unis/m225/06_mobile/m225_06_f12_i0_0", "unis/m225/06_mobile/m225_06_l11_i0_0",
    "unis/m225/07_mobile/m225_07_p01_i0_0", "unis/m225/07_mobile/m225_07_f12_i0_0", "unis/m225/07_mobile/m225_07_l11_i0_0",
    "unis/m225/08_mobile/m225_08_p01_i0_0", "unis/m225/08_mobile/m225_08_f07_i0_0", "unis/m225/08_mobile/m225_08_l06_i0_0",
    "unis/m225/09_mobile/m225_09_p01_i0_0", "unis/m225/09_mobile/m225_09_f07_i0_0", "unis/m225/09_mobile/m225_09_l06_i0_0",
    "unis/m225/10_mobile/m225_10_p01_i0_0", "unis/m225/10_mobile/m225_10_f07_i0_0", "unis/m225/10_mobile/m225_10_l06_i0_0",
    "unis/m225/11_mobile/m225_11_p01_i0_0", "unis/m225/11_mobile/m225_11_f07_i0_0", "unis/m225/11_mobile/m225_11_l06_i0_0",
    "unis/m225/12_mobile/m225_12_p01_i0_0", "unis/m225/12_mobile/m225_12_f07_i0_0", "unis/m225/12_mobile/m225_12_l06_i0_0",
    "unis/m225/13_mobile/m225_13_p01_i0_0", "unis/m225/13_mobile/m225_13_f07_i0_0", "unis/m225/13_mobile/m225_13_l06_i0_0",
    "unis/m227/01_mobile/m227_01_p01_i0_0", "unis/m227/01_mobile/m227_01_f12_i0_0", "unis/m227/01_mobile/m227_01_l11_i0_0",
    "unis/m227/02_mobile/m227_02_p01_i0_0", "unis/m227/02_mobile/m227_02_f12_i0_0", "unis/m227/02_mobile/m227_02_l11_i0_0",
    "unis/m227/03_mobile/m227_03_p01_i0_0", "unis/m227/03_mobile/m227_03_f12_i0_0", "unis/m227/03_mobile/m227_03_l11_i0_0",
    "unis/m227/04_mobile/m227_04_p01_i0_0", "unis/m227/04_mobile/m227_04_f12_i0_0", "unis/m227/04_mobile/m227_04_l11_i0_0",
    "unis/m227/05_mobile/m227_05_p01_i0_0", "unis/m227/05_mobile/m227_05_f12_i0_0", "unis/m227/05_mobile/m227_05_l11_i0_0",
    "unis/m227/06_mobile/m227_06_p01_i0_0", "unis/m227/06_mobile/m227_06_f12_i0_0", "unis/m227/06_mobile/m227_06_l11_i0_0",
    "unis/m227/07_mobile/m227_07_p01_i0_0", "unis/m227/07_mobile/m227_07_f07_i0_0", "unis/m227/07_mobile/m227_07_l06_i0_0",
    "unis/m227/08_mobile/m227_08_p01_i0_0", "unis/m227/08_mobile/m227_08_f07_i0_0", "unis/m227/08_mobile/m227_08_l06_i0_0",
    "unis/m227/09_mobile/m227_09_p01_i0_0", "unis/m227/09_mobile/m227_09_f07_i0_0", "unis/m227/09_mobile/m227_09_l06_i0_0",
    "unis/m227/10_mobile/m227_10_p01_i0_0", "unis/m227/10_mobile/m227_10_f07_i0_0", "unis/m227/10_mobile/m227_10_l06_i0_0",
    "unis/m227/11_mobile/m227_11_p01_i0_0", "unis/m227/11_mobile/m227_11_f07_i0_0", "unis/m227/11_mobile/m227_11_l06_i0_0",
    "unis/m227/12_mobile/m227_12_p01_i0_0", "unis/m227/12_mobile/m227_12_f07_i0_0", "unis/m227/12_mobile/m227_12_l06_i0_0",
    "unis/m228/01_mobile/m228_01_p01_i0_0", "unis/m228/01_mobile/m228_01_f12_i0_0", "unis/m228/01_mobile/m228_01_l11_i0_0",
    "unis/m228/02_mobile/m228_02_p01_i0_0", "unis/m228/02_mobile/m228_02_f12_i0_0", "unis/m228/02_mobile/m228_02_l11_i0_0",
    "unis/m228/03_mobile/m228_03_p01_i0_0", "unis/m228/03_mobile/m228_03_f12_i0_0", "unis/m228/03_mobile/m228_03_l11_i0_0",
    "unis/m228/04_mobile/m228_04_p01_i0_0", "unis/m228/04_mobile/m228_04_f12_i0_0", "unis/m228/04_mobile/m228_04_l11_i0_0",
    "unis/m228/05_mobile/m228_05_p01_i0_0", "unis/m228/05_mobile/m228_05_f12_i0_0", "unis/m228/05_mobile/m228_05_l11_i0_0",
    "unis/m228/06_mobile/m228_06_p01_i0_0", "unis/m228/06_mobile/m228_06_f12_i0_0", "unis/m228/06_mobile/m228_06_l11_i0_0",
    "unis/m228/07_mobile/m228_07_p01_i0_0", "unis/m228/07_mobile/m228_07_f07_i0_0", "unis/m228/07_mobile/m228_07_l06_i0_0",
    "unis/m228/08_mobile/m228_08_p01_i0_0", "unis/m228/08_mobile/m228_08_f07_i0_0", "unis/m228/08_mobile/m228_08_l06_i0_0",
    "unis/m228/09_mobile/m228_09_p01_i0_0", "unis/m228/09_mobile/m228_09_f07_i0_0", "unis/m228/09_mobile/m228_09_l06_i0_0",
    "unis/m228/10_mobile/m228_10_p01_i0_0", "unis/m228/10_mobile/m228_10_f07_i0_0", "unis/m228/10_mobile/m228_10_l06_i0_0",
    "unis/m228/11_mobile/m228_11_p01_i0_0", "unis/m228/11_mobile/m228_11_f07_i0_0", "unis/m228/11_mobile/m228_11_l06_i0_0",
    "unis/m228/12_mobile/m228_12_p01_i0_0", "unis/m228/12_mobile/m228_12_f07_i0_0", "unis/m228/12_mobile/m228_12_l06_i0_0",
    "lia/m501/01_mobile/m501_01_p01_i0_0", "lia/m501/01_mobile/m501_01_f12_i0_0", "lia/m501/01_mobile/m501_01_l11_i0_0",
    "lia/m501/02_mobile/m501_02_p01_i0_0", "lia/m501/02_mobile/m501_02_f12_i0_0", "lia/m501/02_mobile/m501_02_l11_i0_0",
    "lia/m501/03_mobile/m501_03_p01_i0_0", "lia/m501/03_mobile/m501_03_f12_i0_0", "lia/m501/03_mobile/m501_03_l11_i0_0",
    "lia/m501/04_mobile/m501_04_p01_i0_0", "lia/m501/04_mobile/m501_04_f12_i0_0", "lia/m501/04_mobile/m501_04_l11_i0_0",
    "lia/m501/05_mobile/m501_05_p01_i0_0", "lia/m501/05_mobile/m501_05_f12_i0_0", "lia/m501/05_mobile/m501_05_l11_i0_0",
    "lia/m501/06_mobile/m501_06_p01_i0_0", "lia/m501/06_mobile/m501_06_f12_i0_0", "lia/m501/06_mobile/m501_06_l11_i0_0",
    "lia/m501/07_mobile/m501_07_p01_i0_0", "lia/m501/07_mobile/m501_07_f07_i0_0", "lia/m501/07_mobile/m501_07_l06_i0_0",
    "lia/m501/08_mobile/m501_08_p01_i0_0", "lia/m501/08_mobile/m501_08_f07_i0_0", "lia/m501/08_mobile/m501_08_l06_i0_0",
    "lia/m501/09_mobile/m501_09_p01_i0_0", "lia/m501/09_mobile/m501_09_f07_i0_0", "lia/m501/09_mobile/m501_09_l06_i0_0",
    "lia/m501/10_mobile/m501_10_p01_i0_0", "lia/m501/10_mobile/m501_10_f07_i0_0", "lia/m501/10_mobile/m501_10_l06_i0_0",
    "lia/m501/11_mobile/m501_11_p01_i0_0", "lia/m501/11_mobile/m501_11_f07_i0_0", "lia/m501/11_mobile/m501_11_l06_i0_0",
    "lia/m501/12_mobile/m501_12_p01_i0_0", "lia/m501/12_mobile/m501_12_f07_i0_0", "lia/m501/12_mobile/m501_12_l06_i0_0",
    "lia/m503/01_mobile/m503_01_p01_i0_0", "lia/m503/01_mobile/m503_01_f12_i0_0", "lia/m503/01_mobile/m503_01_l11_i0_0",
    "lia/m503/02_mobile/m503_02_p01_i0_0", "lia/m503/02_mobile/m503_02_f12_i0_0", "lia/m503/02_mobile/m503_02_l11_i0_0",
    "lia/m503/03_mobile/m503_03_p01_i0_0", "lia/m503/03_mobile/m503_03_f12_i0_0", "lia/m503/03_mobile/m503_03_l11_i0_0",
    "lia/m503/04_mobile/m503_04_p01_i0_0", "lia/m503/04_mobile/m503_04_f12_i0_0", "lia/m503/04_mobile/m503_04_l11_i0_0",
    "lia/m503/05_mobile/m503_05_p01_i0_0", "lia/m503/05_mobile/m503_05_f12_i0_0", "lia/m503/05_mobile/m503_05_l11_i0_0",
    "lia/m503/06_mobile/m503_06_p01_i0_0", "lia/m503/06_mobile/m503_06_f12_i0_0", "lia/m503/06_mobile/m503_06_l11_i0_0",
    "lia/m503/07_mobile/m503_07_p01_i0_0", "lia/m503/07_mobile/m503_07_f07_i0_0", "lia/m503/07_mobile/m503_07_l06_i0_0",
    "lia/m503/08_mobile/m503_08_p01_i0_0", "lia/m503/08_mobile/m503_08_f07_i0_0", "lia/m503/08_mobile/m503_08_l06_i0_0",
    "lia/m503/09_mobile/m503_09_p01_i0_0", "lia/m503/09_mobile/m503_09_f07_i0_0", "lia/m503/09_mobile/m503_09_l06_i0_0",
    "lia/m503/10_mobile/m503_10_p01_i0_0", "lia/m503/10_mobile/m503_10_f07_i0_0", "lia/m503/10_mobile/m503_10_l06_i0_0",
    "lia/m503/11_mobile/m503_11_p01_i0_0", "lia/m503/11_mobile/m503_11_f07_i0_0", "lia/m503/11_mobile/m503_11_l06_i0_0",
    "lia/m503/12_mobile/m503_12_p01_i0_0", "lia/m503/12_mobile/m503_12_f07_i0_0", "lia/m503/12_mobile/m503_12_l06_i0_0",
    "lia/m504/01_mobile/m504_01_p01_i0_0", "lia/m504/01_mobile/m504_01_f12_i0_0", "lia/m504/01_mobile/m504_01_l11_i0_0",
    "lia/m504/02_mobile/m504_02_p01_i0_0", "lia/m504/02_mobile/m504_02_f12_i0_0", "lia/m504/02_mobile/m504_02_l11_i0_0",
    "lia/m504/03_mobile/m504_03_p01_i0_0", "lia/m504/03_mobile/m504_03_f12_i0_0", "lia/m504/03_mobile/m504_03_l11_i0_0",
    "lia/m504/04_mobile/m504_04_p01_i0_0", "lia/m504/04_mobile/m504_04_f12_i0_0", "lia/m504/04_mobile/m504_04_l11_i0_0",
    "lia/m504/05_mobile/m504_05_p01_i0_0", "lia/m504/05_mobile/m504_05_f12_i0_0", "lia/m504/05_mobile/m504_05_l11_i0_0",
    "lia/m504/06_mobile/m504_06_p01_i0_0", "lia/m504/06_mobile/m504_06_f12_i0_0", "lia/m504/06_mobile/m504_06_l11_i0_0",
    "lia/m504/07_mobile/m504_07_p01_i0_0", "lia/m504/07_mobile/m504_07_f07_i0_0", "lia/m504/07_mobile/m504_07_l06_i0_0",
    "lia/m504/08_mobile/m504_08_p01_i0_0", "lia/m504/08_mobile/m504_08_f07_i0_0", "lia/m504/08_mobile/m504_08_l06_i0_0",
    "lia/m504/09_mobile/m504_09_p01_i0_0", "lia/m504/09_mobile/m504_09_f07_i0_0", "lia/m504/09_mobile/m504_09_l06_i0_0",
    "lia/m504/10_mobile/m504_10_p01_i0_0", "lia/m504/10_mobile/m504_10_f07_i0_0", "lia/m504/10_mobile/m504_10_l06_i0_0",
    "lia/m504/11_mobile/m504_11_p01_i0_0", "lia/m504/11_mobile/m504_11_f07_i0_0", "lia/m504/11_mobile/m504_11_l06_i0_0",
    "lia/m504/12_mobile/m504_12_p01_i0_0", "lia/m504/12_mobile/m504_12_f07_i0_0", "lia/m504/12_mobile/m504_12_l06_i0_0",
    "lia/m514/01_mobile/m514_01_p01_i0_0", "lia/m514/01_mobile/m514_01_f12_i0_0", "lia/m514/01_mobile/m514_01_l11_i0_0",
    "lia/m514/02_mobile/m514_02_p01_i0_0", "lia/m514/02_mobile/m514_02_f12_i0_0", "lia/m514/02_mobile/m514_02_l11_i0_0",
    "lia/m514/03_mobile/m514_03_p01_i0_0", "lia/m514/03_mobile/m514_03_f12_i0_0", "lia/m514/03_mobile/m514_03_l11_i0_0",
    "lia/m514/04_mobile/m514_04_p01_i0_0", "lia/m514/04_mobile/m514_04_f12_i0_0", "lia/m514/04_mobile/m514_04_l11_i0_0",
    "lia/m514/05_mobile/m514_05_p01_i0_0", "lia/m514/05_mobile/m514_05_f12_i0_0", "lia/m514/05_mobile/m514_05_l11_i0_0",
    "lia/m514/06_mobile/m514_06_p01_i0_0", "lia/m514/06_mobile/m514_06_f12_i0_0", "lia/m514/06_mobile/m514_06_l11_i0_0",
    "lia/m514/07_mobile/m514_07_p01_i0_0", "lia/m514/07_mobile/m514_07_f07_i0_0", "lia/m514/07_mobile/m514_07_l06_i0_0",
    "lia/m514/08_mobile/m514_08_p01_i0_0", "lia/m514/08_mobile/m514_08_f07_i0_0", "lia/m514/08_mobile/m514_08_l06_i0_0",
    "lia/m514/09_mobile/m514_09_p01_i0_0", "lia/m514/09_mobile/m514_09_f07_i0_0", "lia/m514/09_mobile/m514_09_l06_i0_0",
    "lia/m514/10_mobile/m514_10_p01_i0_0", "lia/m514/10_mobile/m514_10_f07_i0_0", "lia/m514/10_mobile/m514_10_l06_i0_0",
    "lia/m514/11_mobile/m514_11_p01_i0_0", "lia/m514/11_mobile/m514_11_f07_i0_0", "lia/m514/11_mobile/m514_11_l06_i0_0",
    "lia/m514/12_mobile/m514_12_p01_i0_0", "lia/m514/12_mobile/m514_12_f07_i0_0", "lia/m514/12_mobile/m514_12_l06_i0_0",
    "lia/m516/01_mobile/m516_01_p01_i0_0", "lia/m516/01_mobile/m516_01_f12_i0_0", "lia/m516/01_mobile/m516_01_l11_i0_0",
    "lia/m516/02_mobile/m516_02_p01_i0_0", "lia/m516/02_mobile/m516_02_f12_i0_0", "lia/m516/02_mobile/m516_02_l11_i0_0",
    "lia/m516/03_mobile/m516_03_p01_i0_0", "lia/m516/03_mobile/m516_03_f12_i0_0", "lia/m516/03_mobile/m516_03_l11_i0_0",
    "lia/m516/04_mobile/m516_04_p01_i0_0", "lia/m516/04_mobile/m516_04_f12_i0_0", "lia/m516/04_mobile/m516_04_l11_i0_0",
    "lia/m516/05_mobile/m516_05_p01_i0_0", "lia/m516/05_mobile/m516_05_f12_i0_0", "lia/m516/05_mobile/m516_05_l11_i0_0",
    "lia/m516/06_mobile/m516_06_p01_i0_0", "lia/m516/06_mobile/m516_06_f12_i0_0", "lia/m516/06_mobile/m516_06_l11_i0_0",
    "lia/m516/07_mobile/m516_07_p01_i0_0", "lia/m516/07_mobile/m516_07_f07_i0_0", "lia/m516/07_mobile/m516_07_l06_i0_0",
    "lia/m516/08_mobile/m516_08_p01_i0_0", "lia/m516/08_mobile/m516_08_f07_i0_0", "lia/m516/08_mobile/m516_08_l06_i0_0",
    "lia/m516/09_mobile/m516_09_p01_i0_0", "lia/m516/09_mobile/m516_09_f07_i0_0", "lia/m516/09_mobile/m516_09_l06_i0_0",
    "lia/m516/10_mobile/m516_10_p01_i0_0", "lia/m516/10_mobile/m516_10_f07_i0_0", "lia/m516/10_mobile/m516_10_l06_i0_0",
    "lia/m516/11_mobile/m516_11_p01_i0_0", "lia/m516/11_mobile/m516_11_f07_i0_0", "lia/m516/11_mobile/m516_11_l06_i0_0",
    "lia/m516/12_mobile/m516_12_p01_i0_0", "lia/m516/12_mobile/m516_12_f07_i0_0", "lia/m516/12_mobile/m516_12_l06_i0_0",
    "lia/m517/01_mobile/m517_01_p01_i0_0", "lia/m517/01_mobile/m517_01_f12_i0_0", "lia/m517/01_mobile/m517_01_l11_i0_0",
    "lia/m517/02_mobile/m517_02_p01_i0_0", "lia/m517/02_mobile/m517_02_f12_i0_0", "lia/m517/02_mobile/m517_02_l11_i0_0",
    "lia/m517/03_mobile/m517_03_p01_i0_0", "lia/m517/03_mobile/m517_03_f12_i0_0", "lia/m517/03_mobile/m517_03_l11_i0_0",
    "lia/m517/04_mobile/m517_04_p01_i0_0", "lia/m517/04_mobile/m517_04_f12_i0_0", "lia/m517/04_mobile/m517_04_l11_i0_0",
    "lia/m517/05_mobile/m517_05_p01_i0_0", "lia/m517/05_mobile/m517_05_f12_i0_0", "lia/m517/05_mobile/m517_05_l11_i0_0",
    "lia/m517/06_mobile/m517_06_p01_i0_0", "lia/m517/06_mobile/m517_06_f12_i0_0", "lia/m517/06_mobile/m517_06_l11_i0_0",
    "lia/m517/07_mobile/m517_07_p01_i0_0", "lia/m517/07_mobile/m517_07_f07_i0_0", "lia/m517/07_mobile/m517_07_l06_i0_0",
    "lia/m517/08_mobile/m517_08_p01_i0_0", "lia/m517/08_mobile/m517_08_f07_i0_0", "lia/m517/08_mobile/m517_08_l06_i0_0",
    "lia/m517/09_mobile/m517_09_p01_i0_0", "lia/m517/09_mobile/m517_09_f07_i0_0", "lia/m517/09_mobile/m517_09_l06_i0_0",
    "lia/m517/10_mobile/m517_10_p01_i0_0", "lia/m517/10_mobile/m517_10_f07_i0_0", "lia/m517/10_mobile/m517_10_l06_i0_0",
    "lia/m517/11_mobile/m517_11_p01_i0_0", "lia/m517/11_mobile/m517_11_f07_i0_0", "lia/m517/11_mobile/m517_11_l06_i0_0",
    "lia/m517/12_mobile/m517_12_p01_i0_0", "lia/m517/12_mobile/m517_12_f07_i0_0", "lia/m517/12_mobile/m517_12_l06_i0_0",
    "lia/m518/01_mobile/m518_01_p01_i0_0", "lia/m518/01_mobile/m518_01_f12_i0_0", "lia/m518/01_mobile/m518_01_l11_i0_0",
    "lia/m518/02_mobile/m518_02_p01_i0_0", "lia/m518/02_mobile/m518_02_f12_i0_0", "lia/m518/02_mobile/m518_02_l11_i0_0",
    "lia/m518/03_mobile/m518_03_p01_i0_0", "lia/m518/03_mobile/m518_03_f12_i0_0", "lia/m518/03_mobile/m518_03_l11_i0_0",
    "lia/m518/04_mobile/m518_04_p01_i0_0", "lia/m518/04_mobile/m518_04_f12_i0_0", "lia/m518/04_mobile/m518_04_l11_i0_0",
    "lia/m518/05_mobile/m518_05_p01_i0_0", "lia/m518/05_mobile/m518_05_f12_i0_0", "lia/m518/05_mobile/m518_05_l11_i0_0",
    "lia/m518/06_mobile/m518_06_p01_i0_0", "lia/m518/06_mobile/m518_06_f12_i0_0", "lia/m518/06_mobile/m518_06_l11_i0_0",
    "lia/m518/07_mobile/m518_07_p01_i0_0", "lia/m518/07_mobile/m518_07_f07_i0_0", "lia/m518/07_mobile/m518_07_l06_i0_0",
    "lia/m518/08_mobile/m518_08_p01_i0_0", "lia/m518/08_mobile/m518_08_f07_i0_0", "lia/m518/08_mobile/m518_08_l06_i0_0",
    "lia/m518/09_mobile/m518_09_p01_i0_0", "lia/m518/09_mobile/m518_09_f07_i0_0", "lia/m518/09_mobile/m518_09_l06_i0_0",
    "lia/m518/10_mobile/m518_10_p01_i0_0", "lia/m518/10_mobile/m518_10_f07_i0_0", "lia/m518/10_mobile/m518_10_l06_i0_0",
    "lia/m518/11_mobile/m518_11_p01_i0_0", "lia/m518/11_mobile/m518_11_f07_i0_0", "lia/m518/11_mobile/m518_11_l06_i0_0",
    "lia/m518/12_mobile/m518_12_p01_i0_0", "lia/m518/12_mobile/m518_12_f07_i0_0", "lia/m518/12_mobile/m518_12_l06_i0_0",
    "lia/m520/01_mobile/m520_01_p01_i0_0", "lia/m520/01_mobile/m520_01_f12_i0_0", "lia/m520/01_mobile/m520_01_l11_i0_0",
    "lia/m520/02_mobile/m520_02_p01_i0_0", "lia/m520/02_mobile/m520_02_f12_i0_0", "lia/m520/02_mobile/m520_02_l11_i0_0",
    "lia/m520/03_mobile/m520_03_p01_i0_0", "lia/m520/03_mobile/m520_03_f12_i0_0", "lia/m520/03_mobile/m520_03_l11_i0_0",
    "lia/m520/04_mobile/m520_04_p01_i0_0", "lia/m520/04_mobile/m520_04_f12_i0_0", "lia/m520/04_mobile/m520_04_l11_i0_0",
    "lia/m520/05_mobile/m520_05_p01_i0_0", "lia/m520/05_mobile/m520_05_f12_i0_0", "lia/m520/05_mobile/m520_05_l11_i0_0",
    "lia/m520/06_mobile/m520_06_p01_i0_0", "lia/m520/06_mobile/m520_06_f12_i0_0", "lia/m520/06_mobile/m520_06_l11_i0_0",
    "lia/m520/07_mobile/m520_07_p01_i0_0", "lia/m520/07_mobile/m520_07_f07_i0_0", "lia/m520/07_mobile/m520_07_l06_i0_0",
    "lia/m520/08_mobile/m520_08_p01_i0_0", "lia/m520/08_mobile/m520_08_f07_i0_0", "lia/m520/08_mobile/m520_08_l06_i0_0",
    "lia/m520/09_mobile/m520_09_p01_i0_0", "lia/m520/09_mobile/m520_09_f07_i0_0", "lia/m520/09_mobile/m520_09_l06_i0_0",
    "lia/m520/10_mobile/m520_10_p01_i0_0", "lia/m520/10_mobile/m520_10_f07_i0_0", "lia/m520/10_mobile/m520_10_l06_i0_0",
    "lia/m520/11_mobile/m520_11_p01_i0_0", "lia/m520/11_mobile/m520_11_f07_i0_0", "lia/m520/11_mobile/m520_11_l06_i0_0",
    "lia/m520/12_mobile/m520_12_p01_i0_0", "lia/m520/12_mobile/m520_12_f07_i0_0", "lia/m520/12_mobile/m520_12_l06_i0_0",
    "lia/m521/01_mobile/m521_01_p01_i0_0", "lia/m521/01_mobile/m521_01_f12_i0_0", "lia/m521/01_mobile/m521_01_l11_i0_0",
    "lia/m521/02_mobile/m521_02_p01_i0_0", "lia/m521/02_mobile/m521_02_f12_i0_0", "lia/m521/02_mobile/m521_02_l11_i0_0",
    "lia/m521/03_mobile/m521_03_p01_i0_0", "lia/m521/03_mobile/m521_03_f12_i0_0", "lia/m521/03_mobile/m521_03_l11_i0_0",
    "lia/m521/04_mobile/m521_04_p01_i0_0", "lia/m521/04_mobile/m521_04_f12_i0_0", "lia/m521/04_mobile/m521_04_l11_i0_0",
    "lia/m521/05_mobile/m521_05_p01_i0_0", "lia/m521/05_mobile/m521_05_f12_i0_0", "lia/m521/05_mobile/m521_05_l11_i0_0",
    "lia/m521/06_mobile/m521_06_p01_i0_0", "lia/m521/06_mobile/m521_06_f12_i0_0", "lia/m521/06_mobile/m521_06_l11_i0_0",
    "lia/m521/07_mobile/m521_07_p01_i0_0", "lia/m521/07_mobile/m521_07_f07_i0_0", "lia/m521/07_mobile/m521_07_l06_i0_0",
    "lia/m521/08_mobile/m521_08_p01_i0_0", "lia/m521/08_mobile/m521_08_f07_i0_0", "lia/m521/08_mobile/m521_08_l06_i0_0",
    "lia/m521/09_mobile/m521_09_p01_i0_0", "lia/m521/09_mobile/m521_09_f07_i0_0", "lia/m521/09_mobile/m521_09_l06_i0_0",
    "lia/m521/10_mobile/m521_10_p01_i0_0", "lia/m521/10_mobile/m521_10_f07_i0_0", "lia/m521/10_mobile/m521_10_l06_i0_0",
    "lia/m521/11_mobile/m521_11_p01_i0_0", "lia/m521/11_mobile/m521_11_f07_i0_0", "lia/m521/11_mobile/m521_11_l06_i0_0",
    "lia/m521/12_mobile/m521_12_p01_i0_0", "lia/m521/12_mobile/m521_12_f07_i0_0", "lia/m521/12_mobile/m521_12_l06_i0_0",
    "lia/m522/01_mobile/m522_01_p01_i0_0", "lia/m522/01_mobile/m522_01_f12_i0_0", "lia/m522/01_mobile/m522_01_l11_i0_0",
    "lia/m522/02_mobile/m522_02_p01_i0_0", "lia/m522/02_mobile/m522_02_f12_i0_0", "lia/m522/02_mobile/m522_02_l11_i0_0",
    "lia/m522/03_mobile/m522_03_p01_i0_0", "lia/m522/03_mobile/m522_03_f12_i0_0", "lia/m522/03_mobile/m522_03_l11_i0_0",
    "lia/m522/04_mobile/m522_04_p01_i0_0", "lia/m522/04_mobile/m522_04_f12_i0_0", "lia/m522/04_mobile/m522_04_l11_i0_0",
    "lia/m522/05_mobile/m522_05_p01_i0_0", "lia/m522/05_mobile/m522_05_f12_i0_0", "lia/m522/05_mobile/m522_05_l11_i0_0",
    "lia/m522/06_mobile/m522_06_p01_i0_0", "lia/m522/06_mobile/m522_06_f12_i0_0", "lia/m522/06_mobile/m522_06_l11_i0_0",
    "lia/m522/07_mobile/m522_07_p01_i0_0", "lia/m522/07_mobile/m522_07_f07_i0_0", "lia/m522/07_mobile/m522_07_l06_i0_0",
    "lia/m522/08_mobile/m522_08_p01_i0_0", "lia/m522/08_mobile/m522_08_f07_i0_0", "lia/m522/08_mobile/m522_08_l06_i0_0",
    "lia/m522/09_mobile/m522_09_p01_i0_0", "lia/m522/09_mobile/m522_09_f07_i0_0", "lia/m522/09_mobile/m522_09_l06_i0_0",
    "lia/m522/10_mobile/m522_10_p01_i0_0", "lia/m522/10_mobile/m522_10_f07_i0_0", "lia/m522/10_mobile/m522_10_l06_i0_0",
    "lia/m522/11_mobile/m522_11_p01_i0_0", "lia/m522/11_mobile/m522_11_f07_i0_0", "lia/m522/11_mobile/m522_11_l06_i0_0",
    "lia/m522/12_mobile/m522_12_p01_i0_0", "lia/m522/12_mobile/m522_12_f07_i0_0", "lia/m522/12_mobile/m522_12_l06_i0_0",
    "lia/m524/01_mobile/m524_01_p01_i0_0", "lia/m524/01_mobile/m524_01_f12_i0_0", "lia/m524/01_mobile/m524_01_l11_i0_0",
    "lia/m524/02_mobile/m524_02_p01_i0_0", "lia/m524/02_mobile/m524_02_f12_i0_0", "lia/m524/02_mobile/m524_02_l11_i0_0",
    "lia/m524/03_mobile/m524_03_p01_i0_0", "lia/m524/03_mobile/m524_03_f12_i0_0", "lia/m524/03_mobile/m524_03_l11_i0_0",
    "lia/m524/04_mobile/m524_04_p01_i0_0", "lia/m524/04_mobile/m524_04_f12_i0_0", "lia/m524/04_mobile/m524_04_l11_i0_0",
    "lia/m524/05_mobile/m524_05_p01_i0_0", "lia/m524/05_mobile/m524_05_f12_i0_0", "lia/m524/05_mobile/m524_05_l11_i0_0",
    "lia/m524/06_mobile/m524_06_p01_i0_0", "lia/m524/06_mobile/m524_06_f12_i0_0", "lia/m524/06_mobile/m524_06_l11_i0_0",
    "lia/m524/07_mobile/m524_07_p01_i0_0", "lia/m524/07_mobile/m524_07_f07_i0_0", "lia/m524/07_mobile/m524_07_l06_i0_0",
    "lia/m524/08_mobile/m524_08_p01_i0_0", "lia/m524/08_mobile/m524_08_f07_i0_0", "lia/m524/08_mobile/m524_08_l06_i0_0",
    "lia/m524/09_mobile/m524_09_p01_i0_0", "lia/m524/09_mobile/m524_09_f07_i0_0", "lia/m524/09_mobile/m524_09_l06_i0_0",
    "lia/m524/10_mobile/m524_10_p01_i0_0", "lia/m524/10_mobile/m524_10_f07_i0_0", "lia/m524/10_mobile/m524_10_l06_i0_0",
    "lia/m524/11_mobile/m524_11_p01_i0_0", "lia/m524/11_mobile/m524_11_f07_i0_0", "lia/m524/11_mobile/m524_11_l06_i0_0",
    "lia/m524/12_mobile/m524_12_p01_i0_0", "lia/m524/12_mobile/m524_12_f07_i0_0", "lia/m524/12_mobile/m524_12_l06_i0_0",
    "lia/m526/01_mobile/m526_01_p01_i0_0", "lia/m526/01_mobile/m526_01_f12_i0_0", "lia/m526/01_mobile/m526_01_l11_i0_0",
    "lia/m526/02_mobile/m526_02_p01_i0_0", "lia/m526/02_mobile/m526_02_f12_i0_0", "lia/m526/02_mobile/m526_02_l11_i0_0",
    "lia/m526/03_mobile/m526_03_p01_i0_0", "lia/m526/03_mobile/m526_03_f12_i0_0", "lia/m526/03_mobile/m526_03_l11_i0_0",
    "lia/m526/04_mobile/m526_04_p01_i0_0", "lia/m526/04_mobile/m526_04_f12_i0_0", "lia/m526/04_mobile/m526_04_l11_i0_0",
    "lia/m526/05_mobile/m526_05_p01_i0_0", "lia/m526/05_mobile/m526_05_f12_i0_0", "lia/m526/05_mobile/m526_05_l11_i0_0",
    "lia/m526/06_mobile/m526_06_p01_i0_0", "lia/m526/06_mobile/m526_06_f12_i0_0", "lia/m526/06_mobile/m526_06_l11_i0_0",
    "lia/m526/07_mobile/m526_07_p01_i0_0", "lia/m526/07_mobile/m526_07_f07_i0_0", "lia/m526/07_mobile/m526_07_l06_i0_0",
    "lia/m526/08_mobile/m526_08_p01_i0_0", "lia/m526/08_mobile/m526_08_f07_i0_0", "lia/m526/08_mobile/m526_08_l06_i0_0",
    "lia/m526/09_mobile/m526_09_p01_i0_0", "lia/m526/09_mobile/m526_09_f07_i0_0", "lia/m526/09_mobile/m526_09_l06_i0_0",
    "lia/m526/10_mobile/m526_10_p01_i0_0", "lia/m526/10_mobile/m526_10_f07_i0_0", "lia/m526/10_mobile/m526_10_l06_i0_0",
    "lia/m526/11_mobile/m526_11_p01_i0_0", "lia/m526/11_mobile/m526_11_f07_i0_0", "lia/m526/11_mobile/m526_11_l06_i0_0",
    "lia/m526/12_mobile/m526_12_p01_i0_0", "lia/m526/12_mobile/m526_12_f07_i0_0", "lia/m526/12_mobile/m526_12_l06_i0_0",
    "lia/m527/01_mobile/m527_01_p01_i0_0", "lia/m527/01_mobile/m527_01_f12_i0_0", "lia/m527/01_mobile/m527_01_l11_i0_0",
    "lia/m527/02_mobile/m527_02_p01_i0_0", "lia/m527/02_mobile/m527_02_f12_i0_0", "lia/m527/02_mobile/m527_02_l11_i0_0",
    "lia/m527/03_mobile/m527_03_p01_i0_0", "lia/m527/03_mobile/m527_03_f12_i0_0", "lia/m527/03_mobile/m527_03_l11_i0_0",
    "lia/m527/04_mobile/m527_04_p01_i0_0", "lia/m527/04_mobile/m527_04_f12_i0_0", "lia/m527/04_mobile/m527_04_l11_i0_0",
    "lia/m527/05_mobile/m527_05_p01_i0_0", "lia/m527/05_mobile/m527_05_f12_i0_0", "lia/m527/05_mobile/m527_05_l11_i0_0",
    "lia/m527/06_mobile/m527_06_p01_i0_0", "lia/m527/06_mobile/m527_06_f12_i0_0", "lia/m527/06_mobile/m527_06_l11_i0_0",
    "lia/m527/07_mobile/m527_07_p01_i0_0", "lia/m527/07_mobile/m527_07_f07_i0_0", "lia/m527/07_mobile/m527_07_l06_i0_0",
    "lia/m527/08_mobile/m527_08_p01_i0_0", "lia/m527/08_mobile/m527_08_f07_i0_0", "lia/m527/08_mobile/m527_08_l06_i0_0",
    "lia/m527/09_mobile/m527_09_p01_i0_0", "lia/m527/09_mobile/m527_09_f07_i0_0", "lia/m527/09_mobile/m527_09_l06_i0_0",
    "lia/m527/10_mobile/m527_10_p01_i0_0", "lia/m527/10_mobile/m527_10_f07_i0_0", "lia/m527/10_mobile/m527_10_l06_i0_0",
    "lia/m527/11_mobile/m527_11_p01_i0_0", "lia/m527/11_mobile/m527_11_f07_i0_0", "lia/m527/11_mobile/m527_11_l06_i0_0",
    "lia/m527/12_mobile/m527_12_p01_i0_0", "lia/m527/12_mobile/m527_12_f07_i0_0", "lia/m527/12_mobile/m527_12_l06_i0_0"]

  snames = ['onethird', 'twothirds', 'twothirds-subsampled']
  onethird_list = [229, 502, 515, 529, 204, 205, 211, 220, 222, 226,
                   233, 505, 511, 512, 519, 523]
  twothirds_list = [214, 218, 230, 232, 507, 508, 509, 510, 528, 202,
                    203, 207, 208, 212, 215, 217, 223, 224, 225, 227,
                    228, 501, 503, 504, 514, 516, 517, 518, 520, 521,
                    522, 524, 526, 527]
  slists = [onethird_list, twothirds_list, twothirds_list]
  for k in range(len(snames)):
    if verbose: print("Adding subworld '%s'..." %(snames[k], ))
    su = Subworld(snames[k])
    session.add(su)
    session.flush()
    session.refresh(su)
    l = slists[k]
    if k != 2: # Not twothirds-subsampled
      # Add clients
      for c_id in l:
        if verbose>1: print("  Adding client '%d' to subworld '%s'..." %(c_id, snames[k]))
        su.clients.append(session.query(Client).filter(Client.id == c_id).first())
        # Add all files from this client
        q = session.query(File).join(Client).filter(Client.id == c_id)
        for c_file in q:
          if verbose>1: print("    Adding file '%s' to subworld '%s'..." %(c_file.path, snames[k]))
          su.files.append(c_file)
    else: # twothirds-subsampled: Files were randomly selected from twothirds
      # Add clients
      for c_id in l:
        if verbose>1: print("  Adding client '%d' to subworld '%s'..." %(c_id, snames[k]))
        su.clients.append(session.query(Client).filter(Client.id == c_id).first())
      # Add subsampled files only
      for path in twothirds_subsampled_filelist:
        q = session.query(File).filter(File.path == path)
        for c_file in q:
          if verbose>1: print("  Adding file '%s' to subworld '%s'..." %(c_file.path, snames[k]))
          su.files.append(c_file)

def add_tmodels(session, protocol_id, mobile_only, speech_type, verbose):
  """Adds T-Norm models"""

  # T-Models: client followed by list of session_ids (one session is used for one model,
  # leading to several T-Norm models per identity
  tmodels_list = [(214, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (218, ['01', '02', '03', '09', '10', '11', '12', '13', '14', '15', '16', '17']),
                  (229, ['01', '02', '03', '06', '07', '08', '09', '10', '11', '12', '13', '14']),
                  (230, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (232, ['01', '02', '03', '04', '05', '07', '08', '09', '10', '11', '12', '13']),
                  (502, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (507, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (508, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (509, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (510, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (515, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (528, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (529, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (202, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (203, ['01', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']),
                  (204, ['01', '02', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']),
                  (205, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (207, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (208, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (211, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (212, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (215, ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']),
                  (217, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (220, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (222, ['01', '02', '03', '04', '06', '07', '08', '09', '10', '11', '12', '13']),
                  (223, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (224, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (225, ['01', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']),
                  (226, ['01', '02', '03', '04', '06', '07', '08', '09', '10', '11', '12', '13']),
                  (227, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (228, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (233, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (501, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (503, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (504, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (505, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (511, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (512, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (514, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (516, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (517, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (518, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (519, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (520, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (521, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (522, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (523, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (524, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (526, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']),
                  (527, ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])]

  if verbose: print("Adding T-Norm models...")
  strategies = {}
  # Strategies are defined as a list [use_all_sessions, conditions_list, per_session]
  per_session = True
  if mobile_only:
    device_types = ['mobile']
  else:
    device_types = ['mobile', 'laptop']
  for model_list in tmodels_list:
    cid = model_list[0]
    for device_type in device_types:
      # Several T-Model per client
      if 'laptop' == device_type:
        slist = [model_list[1][0]] # If laptop only, then first session only!
      else:
        slist = model_list[1]
      for sid in slist:
        tmodel_name = str(cid) + '_' + sid + '_' + device_type
        tmodel = TModel(tmodel_name, cid, protocol_id)
        if verbose>1: print("  Adding T-norm model ('%s')..." % tmodel_name)
        session.add(tmodel)
        session.flush()
        session.refresh(tmodel)
        q = session.query(File).join(Client).\
              filter(and_(Client.id == cid, File.session_id == int(sid), File.speech_type.in_(speech_type), File.device.in_(device_types))).\
              order_by(File.id)
        for k in q:
          if verbose>1: print("    Adding T-norm file '%s' to model '%s'..." % (k.path, tmodel_name))
          tmodel.files.append(k)


def add_protocols(session, verbose):
  """Adds protocols"""

  # 1. DEFINITIONS
  # Numbers in the lists correspond to session identifiers
  protocol_definitions = {}

  # Split male and female clients: list of (client_id, first_session_id) # few exceptions with 2 as first session
  clients_male = [(  1,1), (  2,1), (  4,1), (  8,1), ( 11,1), ( 12,1), ( 15,1), ( 16,1), ( 17,1), ( 19,2),
                  ( 21,1), ( 23,1), ( 24,1), ( 25,1), ( 26,1), ( 28,1), ( 29,1), ( 30,1), ( 31,1), ( 33,1),
                  ( 34,1), (103,1), (104,1), (106,1), (107,1), (108,1), (109,1), (111,1), (112,1), (114,1),
                  (115,1), (116,1), (117,1), (119,1), (120,1), (301,1), (304,1), (305,1), (308,1), (310,1),
                  (313,1), (314,1), (315,1), (317,1), (319,1), (416,1), (417,1), (418,1), (419,1), (420,1),
                  (421,1), (422,1), (423,1), (424,1), (425,1), (426,1), (427,1), (428,1), (429,1), (430,1),
                  (431,1), (432,1)]
  clients_female = [(  7,2), (  9,1), ( 10,1), ( 22,1), ( 32,1), (118,1), (122,1), (123,1), (125,1), (126,1),
                    (127,1), (128,1), (129,1), (130,1), (131,1), (133,1), (302,1), (303,1), (306,1), (307,1),
                    (309,1), (311,1), (320,1), (401,1), (402,1), (403,1), (404,1), (405,2), (406,1), (407,1),
                    (408,1), (409,1), (410,1), (411,1), (412,1), (413,1), (415,1), (433,1)]
  train_mobile = ['mobile']
  train_all = None
  enroll_laptop = [['laptop'],['p']]
  enroll_mobile = [['mobile'],['p']]
  enroll_laptop_mobile = [['laptop','mobile'], ['p']]
  probe = [['mobile'],['r', 'f']]
  gender_male = 'male'
  gender_female = 'female'
  protocol_definitions['mobile0-male']          = [clients_male, train_mobile, enroll_mobile, probe, gender_male]
  protocol_definitions['mobile0-female']        = [clients_female, train_mobile, enroll_mobile, probe, gender_female]
  protocol_definitions['mobile1-male']          = [clients_male, train_all, enroll_mobile, probe, gender_male]
  protocol_definitions['mobile1-female']        = [clients_female, train_all, enroll_mobile, probe, gender_female]
  protocol_definitions['laptop1-male']          = [clients_male, train_all, enroll_laptop, probe, gender_male]
  protocol_definitions['laptop1-female']        = [clients_female, train_all, enroll_laptop, probe, gender_female]
  protocol_definitions['laptop_mobile1-male']   = [clients_male, train_all, enroll_laptop_mobile, probe, gender_male]
  protocol_definitions['laptop_mobile1-female'] = [clients_female, train_all, enroll_laptop_mobile, probe, gender_female]

  # 2. ADDITIONS TO THE SQL DATABASE
  protocolPurpose_list = [('world', 'train'), ('dev', 'enroll'), ('dev', 'probe'), ('eval', 'enroll'), ('eval', 'probe')]
  for proto in protocol_definitions:
    p = Protocol(proto, protocol_definitions[proto][4])
    # Add protocol
    if verbose: print("Adding protocol '%s'..." % (proto))
    session.add(p)
    session.flush()
    session.refresh(p)

    # Add protocol purposes
    for key in range(len(protocolPurpose_list)):
      purpose = protocolPurpose_list[key]
      pu = ProtocolPurpose(p.id, purpose[0], purpose[1])
      if verbose>1: print("  Adding protocol purpose ('%s','%s')..." % (purpose[0], purpose[1]))
      session.add(pu)
      session.flush()
      session.refresh(pu)

       # Add files attached with this protocol purpose
      client_group = ""
      device_list = []
      speech_list = []
      if(key == 0): client_group = "world"
      elif(key == 1 or key == 2): client_group = "dev"
      elif(key == 3 or key == 4): client_group = "eval"
      if(key == 0):
        world_list = True
        session_list_in = False
        device_list = protocol_definitions[proto][1]
      if(key == 1 or key == 3):
        world_list = False
        session_list_in = True
        device_list = protocol_definitions[proto][2][0]
        speech_list = protocol_definitions[proto][2][1]
      elif(key == 2 or key == 4):
        world_list = False
        session_list_in = False
        device_list = protocol_definitions[proto][3][0]
        speech_list = protocol_definitions[proto][3][1]

      # Adds 'protocol' files
      # World set
      if world_list:
        q = session.query(File).join(Client).filter(Client.sgroup == 'world').order_by(File.id)
        if device_list:
          q = q.filter(File.device.in_(device_list))
        for k in q:
          if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
          pu.files.append(k)
      # Dev/eval set
      else:
        for client in protocol_definitions[proto][0]:
          cid = client[0] # client id
          sid = client[1] # session id
          q = session.query(File).join(Client).\
                filter(Client.sgroup == client_group).filter(Client.id == cid)
          if session_list_in: q = q.filter(File.session_id == sid)
          else: q = q.filter(File.session_id != sid)
          if device_list:
            q = q.filter(File.device.in_(device_list))
          if speech_list:
            q = q.filter(File.speech_type.in_(speech_list))
          q = q.order_by(File.id)
          for k in q:
            if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
            pu.files.append(k)

    # Add protocol
    speech_type = ['p','l','r','f']
    mobile_only = False
    if 'mobile0' in proto:
      mobile_only = True
    add_tmodels(session, p.id, mobile_only, speech_type, verbose)


def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  Base.metadata.create_all(engine)

# Driver API
# ==========

def create(args):
  """Creates or re-creates this database"""

  from bob.db.base.utils import session_try_nolock

  dbfile = args.files[0]

  if args.recreate:
    if args.verbose and os.path.exists(dbfile):
      print('unlinking %s...' % dbfile)
    if os.path.exists(dbfile): os.unlink(dbfile)

  if not os.path.exists(os.path.dirname(dbfile)):
    os.makedirs(os.path.dirname(dbfile))

  # the real work...
  create_tables(args)
  s = session_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  add_files(s, args.datadir, args.extensions, args.verbose)
  add_subworlds(s, args.verbose)
  add_protocols(s, args.verbose)
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', help="Do SQL operations in a verbose way?")
  parser.add_argument('-D', '--datadir', metavar='DIR', default='/idiap/resource/database/mobio/IMAGES_PNG/', help="Change the relative path to the directory containing the data of the MOBIO database.")
  parser.add_argument('-E', '--extensions', type=str, nargs='+', default=['.png'], help="Change the extension of the MOBIO files used to create the database.")
  parser.set_defaults(func=create) #action
