#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This script creates the Replay-Attack database in a single pass.
"""

import os

from .models import *


def add_clients(session, protodir, verbose):
  """Add clients to the replay attack database."""

  for client in open(os.path.join(protodir, 'clients.txt'), 'rt'):
    s = client.strip().split(' ', 2)
    if not s:
      continue  # empty line
    id = int(s[0])
    set = s[1]
    if verbose:
      print("Adding client %d on '%s' set..." % (id, set))
    session.add(Client(id, set))


def add_real_lists(session, protodir, verbose):
  """Adds all RCD filelists"""

  def add_real_list(session, filename):
    """Adds an RCD filelist and materializes RealAccess'es."""

    def parse_real_filename(f):
      """Parses the RCD filename and break it in the relevant chunks."""

      v = os.path.splitext(os.path.basename(f))[0].split('_')
      client_id = int(v[0].replace('client', ''))
      path = os.path.splitext(f)[0]  # keep only the filename stem
      propuse = v[2]
      device = v[3]
      light = v[4]
      return [client_id, path, light, device], [propuse, device]

    for fname in open(filename, 'rt'):
      s = fname.strip()
      if not s:
        continue  # emtpy line
      filefields, realfields = parse_real_filename(s)
      filefields[0] = session.query(Client).filter(Client.id == filefields[0]).one()
      file = File(*filefields)
      session.add(file)
      realfields.insert(0, file)
      session.add(RealAccess(*realfields))

  add_real_list(session, os.path.join(protodir, 'alldevices/real-alldevices-train.txt'))
  add_real_list(session, os.path.join(protodir, 'alldevices/real-alldevices-devel.txt'))
  add_real_list(session, os.path.join(protodir, 'alldevices/real-alldevices-test.txt'))

  add_real_list(session, os.path.join(protodir, 'alldevices/enroll-alldevices-train.txt'))
  add_real_list(session, os.path.join(protodir, 'alldevices/enroll-alldevices-devel.txt'))
  add_real_list(session, os.path.join(protodir, 'alldevices/enroll-alldevices-test.txt'))


def add_attack_lists(session, protodir, verbose):
  """Adds all RAD filelists"""

  def add_attack_list(session, filename):
    """Adds an RAD filelist and materializes Attacks."""

    def parse_attack_filename(f):
      """Parses the RAD filename and break it in the relevant chunks."""

      v = os.path.splitext(os.path.basename(f))[0].split('_')
      client_id = int(v[1].replace('client', ''))
      path = os.path.splitext(f)[0]  # keep only the filename stem
      light = v[7]
      # attack_support = f.split('/')[-2]

      attack_support = v[4]  # fixed, hand
      attack_device = v[3]  # print, mattescreen
      sample_type = v[6]  # photo or video
      sample_device = v[5]  # tablet or mobile

      return [client_id, path, light, sample_device], [attack_support, attack_device, sample_type, sample_device]

    for fname in open(filename, 'rt'):
      s = fname.strip()
      if not s:
        continue  # emtpy line
      filefields, attackfields = parse_attack_filename(s)
      filefields[0] = session.query(Client).filter(Client.id == filefields[0]).one()
      file = File(*filefields)
      session.add(file)
      attackfields.insert(0, file)
      session.add(Attack(*attackfields))

  add_attack_list(session, os.path.join(protodir, 'alldevices/attack-grandtest-allsupports-alldevices-train.txt'))
  add_attack_list(session, os.path.join(protodir, 'alldevices/attack-grandtest-allsupports-alldevices-devel.txt'))
  add_attack_list(session, os.path.join(protodir, 'alldevices/attack-grandtest-allsupports-alldevices-test.txt'))


def define_protocols(session, protodir, verbose):
  """Defines all available protocols"""

  # figures out which protocols to use
  valid = {}
  # Three grandtest protocols
  # files_protocol = ['alldevices/attack-grandtest-allsupports-alldevices-train.txt', 'mobile/attack-mobilegrandtest-allsupports-mobile-train' ,'tablet/attack-tabletgrandtest-allsupports-tablet-train' ]

  files_protocol = ['alldevices/attack-grandtest-allsupports-alldevices-train.txt', 'alldevices/attack-print-allsupports-alldevices-train', 'alldevices/attack-mattescreen-fixed-alldevices-alltype-train']

  for fname in files_protocol:
    s = fname.split('-', 5)
    folder = fname.split('/', 1)[0]
    consider = True
    files = {}

    for grp in ('train', 'devel', 'test'):

      # check attack file
      if len(s) < 6:
        attack = os.path.join(protodir, '%s/attack-%s-%s-%s-%s.txt' % (folder, s[1], s[2], s[3], grp))
      else:
        attack = os.path.join(protodir, '%s/attack-%s-%s-%s-alltype-%s.txt' % (folder, s[1], s[2], s[3], grp))
      if not os.path.exists(attack):
        if verbose:
          print("Not considering protocol %s as attack list '%s' was not found" % (s[1], attack))
        consider = False

      # check real file
      real = os.path.join(protodir, '%s/real-%s-%s.txt' % (folder, s[3], grp))
      if not os.path.exists(real):
       alt_real = os.path.join(protodir, '%s/real-%s-%s.txt' % (folder, s[3], grp))
       if not os.path.exists(alt_real):
         if verbose:
           print("Not considering protocol %s as real list '%s' or '%s' were not found" % (s[1], real, alt_real))
         consider = False
       else:
         real = alt_real

      if consider:
        files[grp] = (attack, real)

    if consider:
      valid[s[1]] = files

  for protocol, groups in valid.items():
    if verbose:
      print("Creating protocol '%s'..." % protocol)

    # create protocol on the protocol table
    obj = Protocol(name=protocol)

    for grp, flist in groups.items():
      # print grp
      # print flist
      counter = 0
      for fname in open(flist[0], 'rt'):
        s = os.path.splitext(fname.strip())[0]
        q = session.query(Attack).join(File).filter(File.path == s).one()
        q.protocols.append(obj)
        counter += 1
      if verbose:
        print("  -> %5s/%-6s: %d files" % (grp, "attack", counter))

      counter = 0
      for fname in open(flist[1], 'rt'):
        s = os.path.splitext(fname.strip())[0]
        q = session.query(RealAccess).join(File).filter(File.path == s).one()
        q.protocols.append(obj)
        counter += 1
      if verbose:
        print("  -> %5s/%-6s: %d files" % (grp, "real", counter))

    session.add(obj)


def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))
  Client.metadata.create_all(engine)
  RealAccess.metadata.create_all(engine)
  Attack.metadata.create_all(engine)
  Protocol.metadata.create_all(engine)

# Driver API
# ==========


def create(args):
  """Creates or re-creates this database"""

  from bob.db.base.utils import session_try_nolock

  dbfile = args.files[0]

  if args.recreate:
    if args.verbose and os.path.exists(dbfile):
      print(('unlinking %s...' % dbfile))
    if os.path.exists(dbfile):
      os.unlink(dbfile)

  if not os.path.exists(os.path.dirname(dbfile)):
    os.makedirs(os.path.dirname(dbfile))

  # the real work...
  create_tables(args)
  s = session_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))
  add_clients(s, args.protodir, args.verbose)
  add_real_lists(s, args.protodir, args.verbose)
  add_attack_lists(s, args.protodir, args.verbose)
  define_protocols(s, args.protodir, args.verbose)
  s.commit()
  s.close()

  return 0


def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', default=False,
                      help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', default=0,
                      help="Do SQL operations in a verbose way")
  parser.add_argument('-D', '--protodir', action='store',
                      default='/idiap/group/biometric/databases/replay-mobile/database/protocols',
                      #       default='/idiap/user/sbhatta/work/replay-mobile/database/protocols',
                      metavar='DIR',
                      help="Change the relative path to the directory containing the protocol definitions for replay attacks (defaults to %(default)s)")

  parser.set_defaults(func=create)  # action
