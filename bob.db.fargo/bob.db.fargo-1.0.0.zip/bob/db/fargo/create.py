#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
from .models import *

from bob.db.base.driver import Interface as BaseInterface

import bob.core
logger = bob.core.log.setup('bob.db.fargo')


def add_clients(session, imagesdir):
  """Add clients

  This function adds clients to the database. 

  Parameters
  ----------
  session:
    The session to the SQLite database 
  imagesdir : :py:obj:str
    The directory where the images have been extracted
  verbose : bool
    Print some information

  """
  for d in os.listdir(imagesdir):
    client_id = int(d)
    if client_id <= 25:
      group = 'world'
    elif client_id <= 50:
      group = 'dev'
    else:
      group = 'eval'
    logger.info("Adding client {} in group {}".format(client_id, group))
    session.add(Client(client_id, group))

def add_files(session, imagesdir, extension='.png'):
  """ Add face images files.

  This function adds the face image files to the database.

  Parameters
  ----------
  session:
    The session to the SQLite database 
  imagesdir : :py:obj:str
    The directory where the images have been extracted
  extension: :py:obj:str
    The extension of the image file.

  """
  for root, dirs, files in os.walk(imagesdir, topdown=False):
    for name in files:
      image_filename = os.path.join(root, name)

      # just to make sure that nothing weird will be added
      if os.path.splitext(image_filename)[1] == extension:

        # get all the info, base on the file path
        image_info = image_filename.replace(imagesdir, '')
        infos = image_info.split('/')
        
        client_id = int(infos[0])
        light = infos[1]
        device = infos[2].replace('SR300-', '')
        recording = infos[3]
        stream = infos[4]
        if stream == 'color': modality = 'rgb'
        if stream == 'ir': modality = 'nir'
        if stream == 'depth': modality = 'depth'
        
        # default pose is frontal
        pose = 'frontal'
        if 'yaw' in image_filename:
          pose = 'yaw'
        if 'pitch' in image_filename:
          pose = 'pitch'
        
        stem = image_info[0:-len(extension)]

        logger.info("Adding file {}".format(stem))
        o = File(client_id=client_id, path=stem, light=light, device=device, pose=pose, modality=modality, recording=recording)
        session.add(o)


def add_protocols(session):
  """ Adds the different protocols of the FARGO database

  This function creates and adds protocols and protocol purposes for this database

  There are various protocols availables, addressing several tasks:
  
   - Frontal Face Verification using different modalities (RGB, NIR and depth)
     * MC (matched controlled): training, enrollment and probes are acquired in controlled conditions.
     * UD (unmatched degraded): training, enrollment are acquired in controlled conditions, probes with very low-light illumination
     * UO (unmatched outdoor): training, enrollment are acquired in controlled conditions, probes are acquired outdoor.
     These protocols are named in the following way: {mc, ud, uo}-{rgb,nir,depth}


   - Pose-varying Face Verification:
     * 'pos-yaw': training, enrollment are acquired in (frontal) controlled conditions, probes with varying yaw
     * 'pos-pitch': training, enrollment are acquired in (frontal) controlled conditions, probes with varying pitch
      
     
   - Heterogeneous Face Verification:
     The same 3 protocols (MC, UD, UO) have been investigated in mismatched modalities too. Basically, starting
     from a model trained using RGB, it is then adapted with the training set of the target modality. Enrollment
     image are RGB, and probes are coming from the target modality (i.e. either NIR or depth).
     These protocols are named in the following way: {mc, ud, uo}-rgb2{nir, depth}

  Parameters
  ----------
  session:
    The session to the SQLite database 
  """
  from sqlalchemy import and_

  # enrollment images are also the same for all protocols
  recordings_enroll = ['0']
 
  # now probes may change depending on the protocol
  protocol_probes = {}
  
  # this is constant across protocols
  device_probe = ['laptop', 'mobile']

  ##########
  ### MC ###
  ##########
  # matched controlled -> probes are controlled
  session_probe = 'controlled'
  recordings_probe = ['1']

  # add the modalities
  protocol_probes['mc-rgb'] = ['rgb', session_probe, device_probe, recordings_probe]
  protocol_probes['mc-nir'] = ['nir', session_probe, device_probe, recordings_probe]
  protocol_probes['mc-depth'] = ['depth', session_probe, device_probe, recordings_probe]
  # heterogeneous
  protocol_probes['mc-rgb2nir'] = [None , session_probe, device_probe, recordings_probe]
  protocol_probes['mc-rgb2depth'] = [None, session_probe, device_probe, recordings_probe]

  ##########
  ### UD ###
  ##########
  # unmatched degraded -> probes are dark
  session_probe = 'dark'
  recordings_probe = ['0', '1']

  # add the modalities
  protocol_probes['ud-rgb'] = ['rgb', session_probe, device_probe, recordings_probe]
  protocol_probes['ud-nir'] = ['nir', session_probe, device_probe, recordings_probe]
  protocol_probes['ud-depth'] = ['depth', session_probe, device_probe, recordings_probe]
  # heterogeneous
  protocol_probes['ud-rgb2nir'] = [None , session_probe, device_probe, recordings_probe]
  protocol_probes['ud-rgb2depth'] = [None, session_probe, device_probe, recordings_probe]

  ##########
  ### UO ###
  ##########
  # unmatched outdoor -> probes are outdoor
  session_probe = 'outdoor'
  recordings_probe = ['0', '1']

  # add the modalities
  protocol_probes['uo-rgb'] = ['rgb', session_probe, device_probe, recordings_probe]
  protocol_probes['uo-nir'] = ['nir', session_probe, device_probe, recordings_probe]
  protocol_probes['uo-depth'] = ['depth', session_probe, device_probe, recordings_probe]
  # heterogeneous
  protocol_probes['uo-rgb2nir'] = [None , session_probe, device_probe, recordings_probe]
  protocol_probes['uo-rgb2depth'] = [None, session_probe, device_probe, recordings_probe]

  ###############
  ### POS-YAW ###
  ###############
  # unmatched pose -> probes are with varying yaw
  session_probe = 'controlled'
  recordings_probe = ['0', '1']
  protocol_probes['pos-yaw'] = ['rgb', session_probe, device_probe, recordings_probe]
  
  #################
  ### POS-PITCH ###
  #################
  # unmatched pose -> probes are with varying pitch
  session_probe = 'controlled'
  recordings_probe = ['0', '1']
  protocol_probes['pos-pitch'] = ['rgb', session_probe, device_probe, recordings_probe]
 
  # the purpose list 
  group_purpose_list = [('world', 'train'), ('dev', 'enroll'), ('dev', 'probe'), ('eval', 'enroll'), ('eval', 'probe')]
  
  # add each protocol
  for protocol_name in protocol_probes:
  
    p = Protocol(protocol_name)
    logger.info("Adding protocol {}...".format(protocol_name))
    session.add(p)
    session.flush()
    session.refresh(p)

    modality = protocol_probes[protocol_name][0]
    
    # heterogeneous case
    if modality is None:
      if 'rgb2nir' in protocol_name:
        target_modality = 'nir'
      if 'rgb2depth' in protocol_name:
        target_modality = 'depth'
    
    # add protocol purposes
    for group_purpose in group_purpose_list:
     
      group = group_purpose[0]
      purpose = group_purpose[1]
      pu = ProtocolPurpose(p.id, group, purpose)
      
      logger.info("  Adding protocol purpose ({}, {})...".format(group, purpose))
      session.add(pu)
      session.flush()
      session.refresh(pu)

      # first retrieve all files for the group 
      q = session.query(File).join(Client).filter(Client.group == group).order_by(File.id)

      # if purpose is train, we have controlled frontal images in any cases
      if purpose == 'train':
        q = q.filter(and_(File.light == 'controlled', File.pose == 'frontal'))
        # now get the right modality

        # if HETEROGENEOUS get 2 modalities for the WORLD set
        if "rgb2nir" in p.name or "rgb2depth" in p.name:
          if modality is not None:
            q = q.filter(File.modality.in_([modality,"rgb"]))
          else:
            q = q.filter(File.modality.in_(["rgb", target_modality]))
        else:
          if modality is not None:
            q = q.filter(File.modality.in_([modality]))
          else:
            q = q.filter(File.modality.in_([target_modality]))
 
      # for enroll, we have controlled frontal images, for the first recording for each device
      if purpose == 'enroll':
        q = q.filter(and_(File.light == 'controlled', File.pose == 'frontal', File.recording.in_(recordings_enroll)))
        # now filter modality:
        if modality is not None:
          q = q.filter(File.modality == modality)
        else:
          q = q.filter(File.modality == 'rgb') # always rgb in heterogeneous case

      # now the probes 
      if purpose == 'probe':
        # for probes, the number of recording depends on the protocol
        q = q.filter(File.recording.in_(protocol_probes[protocol_name][3]))
        # the light condition as well
        q = q.filter(File.light == protocol_probes[protocol_name][1])
        # the pose
        if 'yaw' in protocol_name:
          q = q.filter(File.pose == 'yaw')
        elif 'pitch' in protocol_name:
          q = q.filter(File.pose == 'pitch')
        else:
          q = q.filter(File.pose == 'frontal')
        # the modality
        if modality is not None:
          q = q.filter(File.modality == modality)
        else:
          q = q.filter(File.modality == target_modality) # target modality in heterogeneous case

      # now add the files
      for k in q:
        pu.files.append(k)
      logger.info("added {} files".format(len(list(q))))


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

  print(args)
  dbfile = args.files[0]

  if args.recreate:
    if args.verbose and os.path.exists(dbfile):
      print(('unlinking %s...' % dbfile))
    if os.path.exists(dbfile):
      os.unlink(dbfile)

  if not os.path.exists(os.path.dirname(dbfile)):
    os.makedirs(os.path.dirname(dbfile))

  bob.core.log.set_verbosity_level(logger, args.verbose)

  # the real work...
  create_tables(args)
  s = session_try_nolock(args.type, args.files[0], echo=False)
  add_clients(s, args.imagesdir)
  add_files(s, args.imagesdir)
  add_protocols(s)
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
  parser.add_argument('imagesdir', action='store', metavar='DIR',
                      help="The path to the extracted images of the FARGO database")

  parser.set_defaults(func=create)  # action
