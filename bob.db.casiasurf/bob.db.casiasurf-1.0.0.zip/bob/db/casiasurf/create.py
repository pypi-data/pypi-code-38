#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
from .models import *
import glob

from bob.db.base.driver import Interface as BaseInterface

import bob.core
logger = bob.core.log.setup('bob.db.casiasurf')


def get_validation_labels(validation_label_filename):
  """ Get the label of the validation set
      
  The labels are read from a text file, and a dictionary
  is built. The key is the file stem and the value is 
  the lable (either 0 for an attack or 1 for banafide access).

  Parameters
  ----------
  validation_label_filename: str
    The path to the file containing the labels

  Returns
  -------
  dict:
    the dictionary with file as key and label as value
  
  """
  dict_validation = {}
  with open(validation_label_filename) as vl:
    for line in vl:
      temp = line.split(' ')[0]
      label = line.split(' ')[-1].rstrip()
      stem = temp.split('-')[0]
      dict_validation[stem] = label

  return dict_validation

def add_samples(session, imagesdir, validation_label_filename, extension='.jpg'):
  """ Add samples

  A sample is an instance of an example of the CASIA-SURF database.
  This is a "single" image with different modalities.

  Note that samples informations are inferred from the image filename. As
  a consequence, since a sample corresponds to several files, a check
  is made if the sample corresponding to a specific image file has 
  already been added.
  
  Parameters
  ----------
  session:
    The session to the SQLite database 
  imagesdir : :py:obj:str
    The directory where to find the images 
  extension: :py:obj:str
    The extension of the image file.
  
  """

  n_training_real_samples = 0
  n_training_attack_samples = 0
  n_validation_real_samples = 0
  n_validation_attack_samples = 0
  n_testing_samples = 0
  
  # get dictionary for validation labels
  valid_dict = get_validation_labels(validation_label_filename)

  for root, dirs, files in os.walk(imagesdir, topdown=False):
    for name in files:
      image_filename = os.path.join(root, name)

      # just to make sure that nothing weird will be added - considering only file ending with .jpg
      if os.path.splitext(image_filename)[1] == extension:

        # get all the info, base on the file path
        image_info = image_filename.replace(imagesdir, '')
        infos = image_info.split('/')
      
        # default attack_type is real (i.e. not an attack)
        attack_type = 0 
      
        ####################
        ### TRAINING SET ###
        ####################
        if infos[0] == 'Training': 
          
          group = 'train'
          
          # if this is an attack, get the type of the attack
          if infos[1] == 'fake_part': 
            attack_type = int(infos[3].split('_')[0])
            n_training_attack_samples += 1
          else:
            attack_type = 0 
            n_training_real_samples += 1
          
          sample_id = infos[2] + '-type-' + str(attack_type) + '-image-' + infos[5].split('.')[0]
        
        ##################
        ### VALIDATION ###
        ##################
        elif infos[0] == 'Val':

          group = 'validation'
          
          stem = "/".join(infos).split('-')[0]
          
          label = valid_dict[stem]
          if label == '0':
            attack_type = 1
            n_validation_attack_samples += 1
          elif label == '1':
            attack_type = 0
            n_validation_real_samples += 1

          temp = infos[2].split('-')
          stream = temp[1].split('.')[0]
          if stream == 'color': modality = 'color'
          if stream == 'ir': modality = 'infrared'
          if stream == 'depth': modality = 'depth'
          
          sample_id = temp[0] + '-type-' + str(attack_type)

        ###############
        ### TESTING ###
        ###############
        else:
          # this should be testing data
          assert infos[0] == 'Testing'

          group = 'test'
          
          temp = infos[2].split('-')
          stream = temp[1].split('.')[0]
          if stream == 'color': modality = 'color'
          if stream == 'ir': modality = 'infrared'
          if stream == 'depth': modality = 'depth'
          sample_id = temp[0] + '-type-unknown'
          attack_type = None # we actually don't know
          n_testing_samples += 1
          sample_id = infos[2].split('-')[0] + '-type-unknown'

        o = Sample(sample_id, group, attack_type)
        q = session.query(Sample.id).filter(Sample.id==sample_id)

        # test if the sample corresponding to this file is already in the table
        exists = session.query(q.exists()).scalar()
        if not exists:
          session.add(o)
          session.flush()
          session.refresh(o)
          # add image files for that sample
          q_im = session.query(ImageFile).join(Sample).filter(Sample.id == sample_id).order_by(ImageFile.id)
          logger.debug("Adding sample {}".format(sample_id))
          for k in q_im:
            o.files.append(k)
            logger.debug("with file {}".format(k))
        else:
          # decrease counter if sample exists !
          if group == 'train' and attack_type > 0:
            n_training_attack_samples -= 1
          if group == 'train' and attack_type == 0:
            n_training_real_samples -= 1
          if group == 'validation' and attack_type > 0:
            n_validation_attack_samples -= 1
          if group == 'validation' and attack_type == 0:
            n_validation_real_samples -= 1
          if group == 'test':
            n_testing_samples -= 1
          logger.debug("sample {} already exists".format(sample_id))
  
  logger.info("Added {} real training samples".format(n_training_real_samples))
  logger.info("Added {} attack training samples".format(n_training_attack_samples))
  logger.info("Added {} real validation samples".format(n_validation_real_samples))
  logger.info("Added {} attack validation samples".format(n_validation_attack_samples))
  logger.info("Added {} test samples".format(n_testing_samples))


def add_files(session, imagesdir, validation_label_filename, extension='.jpg'):
  """ Add face images files.

  This function adds the face image files to the database.

  Parameters
  ----------
  session:
    The session to the SQLite database 
  imagesdir : :py:obj:str
    The directory where to find the images 
  extension: :py:obj:str
    The extension of the image file.

  """

  n_training_real_images = 0
  n_training_attack_images = 0
  n_validation_real_images = 0
  n_validation_attack_images = 0
  n_test_images = 0
 
  # get dictionary for validation labels
  valid_dict = get_validation_labels(validation_label_filename)

  for root, dirs, files in os.walk(imagesdir, topdown=False):
    for name in files:
      image_filename = os.path.join(root, name)

      # just to make sure that nothing weird will be added
      if os.path.splitext(image_filename)[1] == extension:

        # get all the info, base on the file path
        image_info = image_filename.replace(imagesdir, '')
        infos = image_info.split('/')
        
      
        ####################
        ### TRAINING SET ###
        ####################
        if infos[0] == 'Training': 
          
          stream = infos[4]
          if stream == 'color': modality = 'color'
          if stream == 'ir': modality = 'infrared'
          if stream == 'depth': modality = 'depth'
          
          if infos[1] == 'fake_part': 
            attack_type = int(infos[3].split('_')[0])
            n_training_attack_images += 1
          else:
            attack_type = 0 
            n_training_real_images += 1
          
          sample_id = infos[2] + '-type-' + str(attack_type) + '-image-' + infos[5].split('.')[0]
      
        ##################
        ### VALIDATION ###
        ##################
        elif infos[0] == 'Val':

          stem = "/".join(infos).split('-')[0]
          
          label = valid_dict[stem]
          if label == '0':
            attack_type = 1
            n_validation_attack_images += 1
          elif label == '1':
            attack_type = 0
            n_validation_real_images += 1

          temp = infos[2].split('-')
          stream = temp[1].split('.')[0]
          if stream == 'color': modality = 'color'
          if stream == 'ir': modality = 'infrared'
          if stream == 'depth': modality = 'depth'
          
          sample_id = temp[0] + '-type-' + str(attack_type)

        ###############
        ### TESTING ###
        ###############
        else:
          assert infos[0] == 'Testing'
          
          temp = infos[2].split('-')
          stream = temp[1].split('.')[0]
          if stream == 'color': modality = 'color'
          if stream == 'ir': modality = 'infrared'
          if stream == 'depth': modality = 'depth'
          n_test_images +=1 
          sample_id = temp[0] + '-type-unknown'

        stem = image_info[0:-len(extension)]
        logger.debug("Adding file {}".format(stem))
        o = ImageFile(path=stem, sample_id=sample_id, modality=modality)
        session.add(o)

  logger.info("Added {} real training images".format(n_training_real_images))
  logger.info("Added {} attack training images".format(n_training_attack_images))
  logger.info("Added {} real validation images".format(n_validation_real_images))
  logger.info("Added {} attack validation images".format(n_validation_attack_images))
  logger.info("Added {} test images".format(n_test_images))


def add_protocols(session):
  """

  Protocols for the CASIA-SURF database.
  Basically, the protocols are used to know which modalities to use

  Parameters
  ----------
  session:
    The session to the SQLite database 
  """

  from sqlalchemy import and_

  modalities = ['all', 'color', 'infrared', 'depth']
  
  group_purpose_list = [('train', 'real'), ('train', 'attack'), ('validation', 'real'), ('validation', 'attack'), ('test', 'unknown')]


  for protocol_name in modalities:
    
    p = Protocol(protocol_name)
    logger.info("Adding protocol {}...".format(protocol_name))
    session.add(p)
    session.flush()
    session.refresh(p)

    for group_purpose in group_purpose_list: 

      group = group_purpose[0]
      purpose = group_purpose[1]
      pu = ProtocolPurpose(p.id, group, purpose)
    
      logger.info("  Adding protocol purpose ({}, {})...".format(group, purpose))
      session.add(pu)
      session.flush()
      session.refresh(pu)

      # first retrieve all files for the group and the purpose 
      if purpose == 'real':
        #q = session.query(ImageFile).join(Sample).filter(and_(Sample.group == group, Sample.attack_type == 0)).order_by(ImageFile.id)
        q = session.query(Sample).filter(and_(Sample.group == group, Sample.attack_type == 0)).order_by(Sample.id)
      if purpose == 'attack':
        #q = session.query(ImageFile).join(Sample).filter(and_(Sample.group == group, Sample.attack_type > 0)).order_by(ImageFile.id)
        q = session.query(Sample).filter(and_(Sample.group == group, Sample.attack_type > 0)).order_by(Sample.id)
      if purpose == 'unknown':
        #q = session.query(ImageFile).join(Sample).filter(Sample.group == group).order_by(ImageFile.id)
        q = session.query(Sample).filter(Sample.group == group).order_by(Sample.id)

      # now add the samples
      for k in q:
        pu.samples.append(k)
      logger.info("added {} samples".format(len(list(q))))


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
  
  add_files(s, args.imagesdir, args.validlabel)
  add_samples(s, args.imagesdir, args.validlabel)
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
                      help="The path to the extracted images of the database")
  parser.add_argument('validlabel', action='store', metavar='FILE',
                      help="The file containing validation set labels")

  parser.set_defaults(func=create)  # action
