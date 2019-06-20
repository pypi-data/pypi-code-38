#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Thu 12 May 08:19:50 2011

"""This script creates the MSU-MFSD database in a single pass.
"""

import os
import fnmatch

from .models import *

def get_presentation_attributes(filename):
    """ Parses the given video-filename and determines the type of presentation (real or attack), the quality (laptop or mobile), 
        and in case of attack, the instrument used (video_hd, video_mobile, or print)
    Returns:
        presentation: a string either 'real' or 'attack'
        quality: a string either 'laptop' or 'mobile'
        instrument: a string, one of '', 'video_hd', 'video_mobile', 'print'. The value should be ''(empty str) IFF presentation is 'real'.
    """
    
    #input str 'filename' is assumed to have the structure like: './attack/attack_client006_android_SD_ipad_video_scene01.mp4'

    folder, filebase = filename.split('/',3)[-2:] #get last element of list returned by split().
    filebase = filebase.split('.')[0]
    nameparts = filebase.split('_')

    file_stem = folder+'/'+filebase

    presentation = nameparts[0]
    if presentation != 'attack' and presentation != 'real':
        assert False, 'Wrong presentation type.'
    
    cId = int((nameparts[1])[-3:])  #client-id extracted from filename.
    quality = nameparts[2]
    if quality != 'laptop' and quality != 'android':
        assert False, 'Wrong quality type.'
    if quality == 'android':
        quality = 'mobile'
    
    instrument = ''	#stored in nameparts[4] in case of attack.
    if presentation == 'attack':
        #'video_hd'==ipad, 'video_mobile'==iphone_video, 'print'==printed_photo
        if nameparts[4]=='ipad':
            instrument= 'video_hd'
        elif nameparts[4]=='iphone':
            instrument= 'video_mobile'
        elif nameparts[4]=='printed':
            instrument= 'print'
        else:
            assert False, 'We should never reach this point. Unknown attack-instrument!'

    return cId, file_stem, presentation, quality, instrument


def construct_protocol(foldNum, foldFile, foldDir, verbose=False):
    """Groups files according to protocol (train, devel, test).
    Returns:
        protocol: dictionary showing which client belongs to which set ('train', 'devel', 'test')
#        trainSet: list of filenames belonging to the training-set
#        develSet: list of filenames belonging to the devel-set
#        testSet: list of filenames belonging to the test-set
#               in the order: trainSet, develSet, testSet
    """
    if foldNum < 1 or foldNum>5:
        foldNum=1

#    trainSet = []
#    develSet = []
#    testSet = []
    protocol = {} #empty dictionary that will be filled in the loop below.
    
    #1. open text-file containing protocol
#    rootdir = foldDir #'/idiap/home/sbhatta/work/git/refactoring/bob.db.msu_mfsd_mod/bob/db/msu_mfsd_mod/folds'
    foldFile = os.path.join(foldDir, foldFile) #e.g., foldFile is 'clients_fold1.txt'
    foldFile = os.path.join(os.getcwd(), foldFile)
    if verbose: print("Processing fold %s: %s" %(foldNum, foldFile))

    #1b. construct protocol-dictionary: which id belongs to which group.
    for client in open(foldFile, 'rt'):
        s = client.strip().split(' ', 2)
        if s:
            id = int(s[0])
            set = s[1]
            protocol[id] = set
        
#    #2. process text-file containing real-filenames
#    for filename in open(os.path.join(rootdir, 'msu_mfsd_mod_realvids.txt'), 'rt'):
#        #2b. group real-filenames according to group in protocol
#        filename = filename.strip()
#        pos = filename.find('client')
#        clientId = int(filename[pos+6:pos+9]) #assuming that the clientId is represented by 3 digits (001 - 055)
#        if protocol[clientId]=='train':
#            trainSet.append(filename)
#        elif protocol[clientId]=='devel':
#            develSet.append(filename)
#        elif protocol[clientId]=='test':
#            testSet.append(filename)
#        else:
#            assert False, 'Sth. went wrong. We should never reach this point.'
    
#    #3. process text-file containing attack-filenames
#    for filename in open(os.path.join(rootdir, 'msu_mfsd_mod_attackvids.txt'), 'rt'):
#        #3b. group attack-filenames according to group in protocol
#        filename = filename.strip()
#        pos = filename.find('client')
#        clientId = int(filename[pos+6:pos+9]) #assuming that the clientId is represented by 3 digits (001 - 055)
#        if protocol[clientId]=='train':
#            trainSet.append(filename)
#        elif protocol[clientId]=='devel':
#            develSet.append(filename)
#        elif protocol[clientId]=='test':
#            testSet.append(filename)
#        else:
#            assert False, 'Sth. went wrong. We should never reach this point either.'
#    
#    return trainSet, develSet, testSet, protocol
    return protocol

###############



def add_clients(session, protocol_list, verbose=False):
  """adds clients to Client table, and construct the protocols for the 5 folds
  Inputs:
  session: the db session
  protocol_list: list of protocol-dictionaries. The list has 5 dictionaries, in order from fold1 to fold5
  """
  assert len(protocol_list)==5, "add_clients():: input protocol_list should have exactly 5 items"
  #1. construct list of client_nums from dictionary
  clientList = list(protocol_list[0].keys())
  
  #for each client, make one entry in the Client table.
  for cId in clientList:
    fold1Group = protocol_list[0][cId]
    fold2Group = protocol_list[1][cId]
    fold3Group = protocol_list[2][cId]
    fold4Group = protocol_list[3][cId]
    fold5Group = protocol_list[4][cId]
#    print("%s %s %s %s %s" %(fold1Group,fold2Group,fold3Group,fold4Group,fold5Group))

#    clientNumStr = str(cId).zfill(3)
    session.add(Client(cId, fold1Group, fold2Group, fold3Group, fold4Group, fold5Group))


    	
def add_files(session, real_fileList, attack_fileList, verbose=False):
  """Reads the 2 input files (real_fileList, attackFileList), and for each line in each file, adds a row in the File table
     Inputs:
     session: the db session
     real_fileList: text-file containing names of all video-files of real-presentations (1 filename per line)
     attack_fileList: text-file containing names of all video-files of attack-presentations (1 filename per line)
  """
  #load list of files that should be rotated
  rotFile = 'bob/db/msu_mfsd_mod/rotated_videos/rotated_videos.txt'  
  rotFile = os.path.join(os.getcwd(), rotFile)
  if verbose: print("Rotation file: %s" %(rotFile))


  rotate_list= []  #read the rotFile and append filenames of files to be rotated to this list
  for fn in open(rotFile, 'rt'):
    rotate_list.append(fn.strip())

  if verbose: print('Files to be rotated (%s): %s' % (len(rotate_list), rotate_list))

  # process real-presentation files
  inpFile = os.path.join(os.getcwd(), real_fileList)
  idCounter = 0
  for fname in open(inpFile, 'rt'):
    idCounter += 1
    rotate = False
    pa = get_presentation_attributes(fname) #extracts presentation attributes by parsing fname: cId, file_stem, presentation, quality, instrument
#    print(pa)
    if pa[1] in rotate_list: 
        rotate = True #pa[1] is the file_stem to be stored in the database
    if rotate:
        print(pa[1])
    session.add(File(idCounter, pa[0], pa[1], pa[2], pa[3], pa[4], rotate)) #(fId, client, path, presentation, quality, atype, rotation=False)

  #process attack-presentation files
  inpFile = os.path.join(os.getcwd(), attack_fileList)
  rotate = False
  for fname in open(inpFile, 'rt'):
    pa = get_presentation_attributes(fname) #extracts presentation attributes by parsing fname: cId, file_stem, presentation, quality, instrument
#    if pa[1] in rotate_list: rotate = True # test not necessary; the files needing rotation are all in the real-pres. set.
    idCounter += 1
    session.add(File(idCounter, pa[0], pa[1], pa[2], pa[3], pa[4], rotate)) #(self, fId, client, path, presentation, quality, atype, rotation=False)
  if verbose: print("%d files added to db" %(idCounter))

#def add_real_lists(session, protodir, verbose):
#  """Adds all RCD filelists"""
#
#  def add_real_list(session, filename):
#    """Adds an RCD filelist and materializes RealAccess'es."""
#
#    def parse_real_filename(f):
#      """Parses the RCD filename and break it in the relevant chunks."""
#
#      v = os.path.splitext(os.path.basename(f))[0].split('_')
#      client_id = int(v[0].replace('client', ''))
#      path = os.path.splitext(f)[0]  # keep only the filename stem
#      purpose = v[3]
#      light = v[4]
#      if len(v) == 6:
#        take = int(v[5])  # authentication session
#      else:
#        take = 1  # enrollment session
#      return [client_id, path, light], [purpose, take]
#
#    for fname in open(filename, 'rt'):
#      s = fname.strip()
#      if not s:
#        continue  # emtpy line
#      filefields, realfields = parse_real_filename(s)
#      filefields[0] = session.query(Client).filter(Client.id == filefields[0]).one()
#      file = File(*filefields)
#      session.add(file)
#      realfields.insert(0, file)
#      session.add(RealAccess(*realfields))
#
#  add_real_list(session, os.path.join(protodir, 'real-train.txt'))
#  add_real_list(session, os.path.join(protodir, 'real-devel.txt'))
#  add_real_list(session, os.path.join(protodir, 'real-test.txt'))
#  add_real_list(session, os.path.join(protodir, 'recognition-train.txt'))
#  add_real_list(session, os.path.join(protodir, 'recognition-devel.txt'))
#  add_real_list(session, os.path.join(protodir, 'recognition-test.txt'))
#
#
#def add_attack_lists(session, protodir, verbose):
#  """Adds all RAD filelists"""
#
#  def add_attack_list(session, filename):
#    """Adds an RAD filelist and materializes Attacks."""
#
#    def parse_attack_filename(f):
#      """Parses the RAD filename and break it in the relevant chunks."""
#
#      v = os.path.splitext(os.path.basename(f))[0].split('_')
#      attack_device = v[1]  # print, mobile or highdef
#      client_id = int(v[2].replace('client', ''))
#      path = os.path.splitext(f)[0]  # keep only the filename stem
#      sample_device = v[4]  # highdef or mobile
#      sample_type = v[5]  # photo or video
#      light = v[6]
#      attack_support = f.split('/')[-2]
#      return [client_id, path, light], [attack_support, attack_device, sample_type, sample_device]
#
#    for fname in open(filename, 'rt'):
#      s = fname.strip()
#      if not s:
#        continue  # emtpy line
#      filefields, attackfields = parse_attack_filename(s)
#      filefields[0] = session.query(Client).filter(Client.id == filefields[0]).one()
#      file = File(*filefields)
#      session.add(file)
#      attackfields.insert(0, file)
#      session.add(Attack(*attackfields))
#
#  add_attack_list(session, os.path.join(protodir, 'attack-grandtest-allsupports-train.txt'))
#  add_attack_list(session, os.path.join(protodir, 'attack-grandtest-allsupports-devel.txt'))
#  add_attack_list(session, os.path.join(protodir, 'attack-grandtest-allsupports-test.txt'))
#
#
#def define_protocols(session, protodir, verbose):
#  """Defines all available protocols"""
#
#  # figures out which protocols to use
#  valid = {}
#
#  for fname in fnmatch.filter(os.listdir(protodir), 'attack-*-allsupports-train.txt'):
#    s = fname.split('-', 4)
#
#    consider = True
#    files = {}
#
#    for grp in ('train', 'devel', 'test'):
#
#      # check attack file
#      attack = os.path.join(protodir, 'attack-%s-allsupports-%s.txt' % (s[1], grp))
#      if not os.path.exists(attack):
#        if verbose:
#          print("Not considering protocol %s as attack list '%s' was not found" % (s[1], attack))
#        consider = False
#
#      # check real file
#      real = os.path.join(protodir, 'real-%s-allsupports-%s.txt' % (s[1], grp))
#      if not os.path.exists(real):
#        alt_real = os.path.join(protodir, 'real-%s.txt' % (grp,))
#        if not os.path.exists(alt_real):
#          if verbose:
#            print("Not considering protocol %s as real list '%s' or '%s' were not found" % (s[1], real, alt_real))
#          consider = False
#        else:
#          real = alt_real
#
#      if consider:
#        files[grp] = (attack, real)
#
#    if consider:
#      valid[s[1]] = files
#
#  for protocol, groups in valid.items():
#    if verbose:
#      print("Creating protocol '%s'..." % protocol)
#
#    # create protocol on the protocol table
#    obj = Protocol(name=protocol)
#
#    for grp, flist in groups.items():
#
#      counter = 0
#      for fname in open(flist[0], 'rt'):
#        s = os.path.splitext(fname.strip())[0]
#        q = session.query(Attack).join(File).filter(File.path == s).one()
#        q.protocols.append(obj)
#        counter += 1
#      if verbose:
#        print("  -> %5s/%-6s: %d files" % (grp, "attack", counter))
#
#      counter = 0
#      for fname in open(flist[1], 'rt'):
#        s = os.path.splitext(fname.strip())[0]
#        q = session.query(RealAccess).join(File).filter(File.path == s).one()
#        q.protocols.append(obj)
#        counter += 1
#      if verbose:
#        print("  -> %5s/%-6s: %d files" % (grp, "real", counter))
#
#    session.add(obj)


def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))
  Client.metadata.create_all(engine)
  File.metadata.create_all(engine)
#  RealAccess.metadata.create_all(engine)
#  Attack.metadata.create_all(engine)
#  Protocol.metadata.create_all(engine)

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
  
  #first, get list of protocol-dictionaries via construct_protocol() 
  protocol_list = []
  protocol_files = ['clients_fold1.txt', 'clients_fold2.txt', 'clients_fold3.txt', 'clients_fold4.txt', 'clients_fold5.txt']
  foldDir = 'bob/db/msu_mfsd_mod/folds' #args.protodir

  for fn, foldFilename in enumerate(protocol_files):
    protocol = construct_protocol(fn+1, foldFilename, foldDir, args.verbose)
    protocol_list.append(protocol)
  #fill in the Client table
  add_clients(s, protocol_list)

  #fill in the File table
  real_list = 'bob/db/msu_mfsd_mod/folds/msu_mfsd_mod_realvids.txt'
  attack_list = 'bob/db/msu_mfsd_mod/folds/msu_mfsd_mod_attackvids.txt'
  add_files(s, real_list, attack_list, args.verbose)
  
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
#  parser.add_argument('-D', '--protodir', action='store',
#                      default='folds', #bob.db.msu_mfsd_mod/bob/db/msu_mfsd_mod/folds
#                      metavar='DIR',
#                      help="Change the relative path to the directory containing the protocol definitions for replay attacks (defaults to %(default)s)")

  parser.set_defaults(func=create)  # action
