#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
#
# Copyright (C) 2012-2014 Idiap Research Institute, Martigny, Switzerland
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

"""This script creates the NIST SRE 2012 database in a single pass.
"""

import os

from .models import *

def read_eval_key(protocolDir, protocol, group):
  """Returns a dictionary of tuples with (test segment and target value) for each client. 

  Keyword Parameters:

    protocol
      The protocol to consider ('eval')

    groups
      The groups to which the subjects attached to the models belong ('core-all','core-c1','core-c2','core-c3','core-c4','core-c5')

  """
  from pkg_resources import resource_filename

  key = {}
  fn = os.path.join(protocolDir,group,protocol,'key.lst')
  with open(fn) as fp:
    for l in fp:
      l = l.strip()
      s = l.split()
      tgt = s[0]
      tst = s[1]
      target = s[2]
      if tgt not in key:
        key[tgt] = []
      key[tgt].append((tst, target))
  return key

def add_files(session, all_files, verbose):
  """Add files to the NIST SRE 2012 database."""

  def add_model(session, id, gender, spkid, verbose):
    """Add a model to the database"""
    if verbose>1: print("  Adding model '%s'..." %(id,))

    model = Model(id, gender, spkid)
    session.add(model)
    session.flush()
    session.refresh(model)
    return model

  def add_file(session, c_id, path, side, verbose):
    """Parse a single filename and add it to the list.
       Also add a client entry if not already in the database."""
    if verbose>1: print("  Adding file '%s %s'..." %(path,side))
    file_ = File(c_id, path, side)
    session.add(file_)
    session.flush()
    session.refresh(file_)
    return file_

  if verbose: print("Adding files ...")
  model_dict = {}
  file_dict = {}
  f = open(all_files)
  for line in f:
    s = line.split()
    if len(s)==4:
      path, side, m_id, gender = s
      if (not m_id in model_dict) and m_id != 'M_ID_X':
        model_dict[m_id] = add_model(session, m_id, 'C_ID_X', gender, verbose)
      if not (path,side) in file_dict:
        file_dict[(path,side)] = add_file(session, 'C_ID_X', path, side, verbose)
    elif len(s)==5:
      path, side, m_id, spkid, gender = s
      if (not m_id in model_dict) and m_id != 'M_ID_X':
        model_dict[m_id] = add_model(session, m_id, spkid, gender, verbose)
      if not (path,side) in file_dict:
        file_dict[(path,side)] = add_file(session, spkid, path, side, verbose)
    else:
      raise RuntimeError("Line could not be parsed: '%s'" % line)

  return (file_dict, model_dict)


def add_protocols(session, protocol_dir, file_dict, model_dict, verbose):
  """Adds protocols"""

  groups = os.listdir(protocol_dir)
  protocolPurpose_list = [
    ('core-all', 'enroll', 'for_models.lst'), ('core-all', 'probe', 'for_probes.lst'),
    ('core-c1', 'enroll', 'for_models.lst'), ('core-c1', 'probe', 'for_probes.lst'),
    ('core-c2', 'enroll', 'for_models.lst'), ('core-c2', 'probe', 'for_probes.lst'),
    ('core-c3', 'enroll', 'for_models.lst'), ('core-c3', 'probe', 'for_probes.lst'),
    ('core-c4', 'enroll', 'for_models.lst'), ('core-c4', 'probe', 'for_probes.lst'),
    ('core-c5', 'enroll', 'for_models.lst'), ('core-c5', 'probe', 'for_probes.lst'),
] 

  for group in groups:
    protocols = os.listdir(os.path.join(protocol_dir,group))
    for proto in protocols:
      p = Protocol(proto)
      # Add protocol
      if verbose: print("Adding protocol %s..." % (proto))
      session.add(p)
      session.flush()
      session.refresh(p)


      # Add protocol purposes
      for purpose in protocolPurpose_list:
        if purpose[0] != proto:
          continue
        pu = ProtocolPurpose(p.id, group, purpose[1])
        if verbose>1: print("  Adding protocol purpose ('%s','%s')..." % (purpose[0], purpose[1]))
        session.add(pu)
        session.flush()
        session.refresh(pu)

        pu_model_dict = {}
        # Add files attached with this protocol purpose
        f = open(os.path.join(protocol_dir, group, proto, purpose[2]))
        for line in f:
          l = line.split()
          path = l[0]
          side = l[1]
          m_id = l[2]

          # add files and models into purpose entry (either enroll or probe)
          if (path,side) in file_dict:
            if verbose>1: print("    Adding protocol file to purpose %s '%s %s'..." % (purpose[1], path, side, ))
            # add file into files field of purpose record
            pu.files.append(file_dict[(path,side)])
            if purpose[1] == 'enroll':
              me = ModelEnrollLink (m_id, build_fileid(path, side), p.id)
              session.add(me)
              session.flush()
              session.refresh(me)
 
            # If model does not exist, add it to the enroll purpose
            if (not m_id in pu_model_dict) and m_id != 'M_ID_X':
              if verbose>1: print("    Adding protocol model to purpose %s '%s'..." % (purpose[1], m_id, ))
              if m_id in model_dict:
                pu.models.append(model_dict[m_id])
                pu_model_dict[m_id] = model_dict[m_id]
              else:
                raise RuntimeError("Model '%s' is in the protocol list but not in the database" % m_id)
          else:
            raise RuntimeError("File '%s' is in the protocol list but not in the database" % (path, side))

      # Add trial entries
      key = read_eval_key (protocol_dir, proto , group)
      n = 0
      nextn = 10000
      ntotal = sum(len(v) for v in key.itervalues())
      if verbose>1:
        print("  Adding trials to protocol %s") % p.name
      for model_id in key.keys():
        for k in key[model_id]:
          probe_id = k[0]
          trial = ModelProbeLink (model_id, probe_id, p.id)
          session.add(trial)
          session.flush()
          session.refresh(trial)
          n += 1
          if n>=nextn and verbose>1:
            print ("  Added %d/%d trials to protocol %s..." % (n, ntotal, p.name))
            nextn += 10000

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
  file_dict, model_dict = add_files(s, os.path.join(args.datadir, 'all_files.lst'), args.verbose)
  add_protocols(s, os.path.join(args.datadir, 'protocols'), file_dict, model_dict, args.verbose)
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', help="Do SQL operations in a verbose way")
  from pkg_resources import resource_filename
  sre12_basedir = 'sre12'
  sre12_path = resource_filename(__name__, sre12_basedir)
  parser.add_argument('-D', '--datadir', metavar='DIR', default=sre12_path, help="Change the path to the containing information about the NIST SRE 2012 database.")

  parser.set_defaults(func=create) #action
