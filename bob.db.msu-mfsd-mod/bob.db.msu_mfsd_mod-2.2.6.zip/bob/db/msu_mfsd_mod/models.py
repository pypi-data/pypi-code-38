#!/usr/bin/env python
# Sushil Bhattacharjee <sushil.bhattacharjee@idiap.ch>
# Mon 16 Mar 12:49:23 CET 2015

# from replay::models.py
import os
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from bob.db.base.sqlalchemy_migration import Enum, relationship
import bob.db.base.utils
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
import numpy
import bob.io.video
from bob.db.base import File as BaseFile
import bob.core


Base = declarative_base()
logger = bob.core.log.setup('bob.db.msu_mfsd_mod')


class Client(Base):
  """Database clients, marked by an integer identifier and the set they belong
  to"""

  __tablename__ = 'client'

  #  NOTE: the following 2 '_choices' tuples are only for information; they are not directly used for adding fields to the client-Table.
  group_choices = ('train', 'devel', 'test')
  fold_choices = ('fold1', 'fold2', 'fold3', 'fold4', 'fold5')

  fold1_choices = group_choices  # ('train', 'devel', 'test')
  """Possible groups to which clients may belong to"""
  fold2_choices = group_choices  # ('train', 'devel', 'test')
  fold3_choices = group_choices  # ('train', 'devel', 'test')
  fold4_choices = group_choices  # ('train', 'devel', 'test')
  fold5_choices = group_choices  # ('train', 'devel', 'test')

  # group_choices = ('train', 'devel', 'test')

  id = Column(Integer, primary_key=True)
  """Key identifier for clients"""

  client_fold1 = Column(Enum(*fold1_choices))
  """ Client's group in this fold. """

  client_fold2 = Column(Enum(*fold2_choices))
  """ Client's group in this fold. """

  client_fold3 = Column(Enum(*fold3_choices))
  """ Client's group in this fold. """

  client_fold4 = Column(Enum(*fold4_choices))
  """ Client's group in this fold. """

  client_fold5 = Column(Enum(*fold5_choices))
  """ Client's group in this fold. """

  def __init__(self, client_num, client_fold1, client_fold2, client_fold3, client_fold4, client_fold5):
    self.id = client_num
    self.client_fold1 = client_fold1
    self.client_fold2 = client_fold2
    self.client_fold3 = client_fold3
    self.client_fold4 = client_fold4
    self.client_fold5 = client_fold5

  def __repr__(self):
    return "<Client('%s', '%s', '%s', '%s', '%s', '%s')>" % (self.id, self.client_fold1, self.client_fold2, self.client_fold3, self.client_fold4, self.client_fold5)
# return "<Client(Id:'%s', Fold1:'%s', Fold2:'%s', Fold3:'%s', Fold4:'%s', Fold5:'%s')>" % (self.id, self.client_fold1, self.client_fold2, self.client_fold3, self.client_fold4, self.client_fold5)


class File(Base, BaseFile):
  """Generic file container"""

  __tablename__ = 'file'
  # has fields: id, client_id, path, cls, rotate, quality, instrument

  quality_choices = ('laptop', 'mobile')
  """List of options for quality of device used for data-capture"""

  instrument_choices = ('video_hd', 'video_mobile', 'print', '')
  """List of options for attack-instruments ('video_hd'==ipad, 'video_mobile'==iphone_video, 'print'==printed_photo"""

  presentation_choices = ('real', 'attack')
  """List of possible presentations """

#  rotation_choices = (True, False)
#  """Does the original video need to be rotated or not"""

  id = Column(Integer, primary_key=True)
  """Key identifier for files"""

  client_id = Column(Integer, ForeignKey('client.id'))
  """The client identifier to which this file is bound to"""

  path = Column(String(200), unique=True)
  """The (unique) path to this file inside the database"""

  cls = Column(Enum(*presentation_choices))  # Presentation-type variable name 'cls' used for legacy reasons
  """presentation-class: real or attack"""

  rotate = Column(Boolean, unique=False, default=False)  # Column(Enum(*rotation_choices), unique=False)
  """ To rotate or not to rotate..."""

  quality = Column(Enum(*quality_choices), unique=False)
  """Quality of device used to acquire video"""

  instrument = Column(Enum(*instrument_choices), unique=False)
  """Attack-type"""

  # for Python
  client = relationship(Client, backref=backref('files', order_by=id))
  """A direct link to the client object that this file belongs to"""

  def __init__(self, fId, client, path, presentation, quality, atype, rotation=False):
    """Inputs other than 'self'
       fId: integer giving the file-id.
       client: integer giving the client-id
       path: string giving the file-stem
       presentation: string specifying 'real' or 'attack'
       quality: string specifying 'laptop' or 'mobile'
       atype: string specifying 'video_hd', 'video_mobile', or 'print'
       rotation: bool: True if the file should be rotated upon load, otherwise False.
    """
    BaseFile.__init__(self, path, fId)
    self.client_id = client  # clientId
    self.cls = presentation   # real or attack
    self.quality = quality  # laptop or mobile
    self.instrument = atype  # video_hd, video_mobile, or print
    self.rotate = rotation  # True or False

  def __repr__(self):
    return "<File('%s', '%s', '%s', '%s', '%s', '%s', '%s', )>" % (self.id, self.client_id, self.path, self.cls, self.quality, self.instrument, self.rotate)
# return "<File(FileId:'%s', ClientId:'%s', FilePath:'%s', Presentation:'%s', Quality:'%s', AttackInstrument:'%s', Rotate:'%s', )>" % (self.id, self.client_id, self.path, self.cls, self.quality, self.instrument, self.rotate)

  def make_path(self, directory=None, extension=None):
    """Wraps the current path so that a complete path is formed

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    extension
      An optional extension that will be suffixed to the returned filename. The
      extension normally includes the leading ``.`` character as in ``.jpg`` or
      ``.hdf5``.

    Returns a string containing the newly generated file path.
    """

    if not directory:
      directory = ''
    if not extension:
      extension = ''

    return str(os.path.join(directory, self.path + extension))

  def get_quality(self):
    """Returns quality of the video recording as a string. Possible return-value: 'laptop', or 'mobile'."""
    return self.quality

  def get_instrument(self):
    """Returns the attack-instrument (formerly, type) associated with the file-object.
    Return:
    String, one of: 'video_hd', 'video_mobile', 'print', or None
    Returns None only when the presentation is 'real'
    """
    return self.instrument

  def videofile(self, directory=None):
    """Returns the path to the database video file for this object
    Keyword parameters:
    directory: An optional directory name that will be prefixed to the returned result.

    Returns a string containing the video file path.
    """

    if self.get_quality() == 'laptop':
      return self.make_path(directory, '.mov')
    else:
      return self.make_path(directory, '.mp4')

  def get_file(self, pc):
    '''Returns the full file path given the path components pc'''
    from pkg_resources import resource_filename
    return resource_filename(__name__, os.path.join(pc))

  def facefile(self, directory=''):
    """Returns the path to the companion face bounding-box file

    Keyword parameters:
    directory: An optional directory name that will be prefixed to the returned result.

    Returns a string containing the face file path.
    """
    if not directory:
      directory = self.get_file('face-locations')  # 'face-locations'
    return self.make_path(directory, '.face')

  def bbx(self, directory=None):
    """Reads the file containing the face locations for the frames in the current video

    Keyword parameters:
    directory: A directory name that will be prepended to the final filepaths where the face bounding boxes are located, if not on the current directory.

    Returns:
      A :py:class:`numpy.ndarray` containing information about the located faces in the videos.
      Each row of the :py:class:`numpy.ndarray` corresponds for one frame.
      The five columns of the :py:class:`numpy.ndarray` are (all integers):
      * Frame number (float)
      * Bounding box top-left X coordinate (float)
      * Bounding box top-left Y coordinate (float)
      * Bounding box width (float)
      * Bounding box height (float)
      * Left eye X coordinate (float)
      * Left eye Y coordinate (float)
      * Right eye X coordinate (float)
      * Right eye Y coordinate (float)

      Note that **not** all the frames may contain detected faces.
    """

    coords = numpy.loadtxt(self.facefile(directory), delimiter=',')
    coords[:, 3] = coords[:, 3] - coords[:, 1]
    coords[:, 4] = coords[:, 4] - coords[:, 2]

    return coords

  def get_client_id(self):
    """The ID of the client. Value from 1 to 50. Clients in the train and devel set may have IDs from 1 to 20;
       clients in the test set have IDs from 21 to 50.
    """
    # real_clientID_cameraType_resolution_scenario
    # attack_clientID_cameraType_resolution_attackType_scenario
    stem_file = os.path.basename(self.path)  # the file stem of the filename
    stem_client = stem_file.split('_')[1]  # the client stem of the filename
    return stem_client[-2:]

  def is_real(self):
    """Returns True if this file belongs to a real access, False otherwise"""
    return bool(self.cls == 'real')

#  def get_realaccess(self):
#    """Returns the real-access object equivalent to this file or raise"""
#    if not bool(self.cls == 'real'):
#      raise RuntimeError("%s is not a real-access" % self)
#    return self.realaccess[0]

#  def get_attack(self):
#    """Returns the attack object equivalent to this file or raise"""
#    if bool(self.cls == 'real'):
#      raise RuntimeError("%s is not an attack" % self)
#    return self.attack[0]

  def is_rotated(self):
    """True if the video file is originally recorded rotated by 180 degrees, False otherwise """

#    infilename = self.get_file(os.path.join('rotated_videos', 'rotated_videos.txt'))
#    f = open(infilename)
#    rotated_videos = f.readlines();
#    rotated_videos = [x[:-1] for x in rotated_videos] # removing the newline chars from the read lines
#    return bool(self.make_path() in rotated_videos)

    return self.rotate  # True or False stored in this field

  def load(self, directory=None, extension=None):
    """Loads the data at the specified location and using the given extension.

    Keyword parameters:
    data: The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory: [optional] If not empty or None, this directory is prefixed to the final file destination

    extension: [optional] The extension of the filename - this will control the type of output and the codec for saving the input blob.
    """

    if extension is None:
        if self.get_quality() == 'laptop':
            extension = '.mov'
        else:
            extension = '.mp4'

    if extension == '.mov' or extension == '.mp4':
        vfilename = self.make_path(directory, extension)
        video = bob.io.video.reader(vfilename)
        vin = video.load()
    else:
        vin = bob.io.base.load(self.make_path(directory, extension))

    logger.debug('{} is_rotated: {}'.format(self, self.is_rotated()))
    if self.is_rotated():
        vin = vin[:, :, ::-1, ::-1]

    return vin

  def save(self, data, directory=None, extension='.hdf5'):
    """Saves the input data at the specified location and using the given extension.

    Keyword parameters:
    data: The data blob to be saved (normally a :py:class:`numpy.ndarray`).
    directory: If specified (not empty and not None), this directory is prefixed to the final file destination
    extension: The filename-extension - this determines the type of output and the codec for saving the input blob.
    """

    path = self.make_path(directory, extension)
    bob.io.base.create_directories_safe(os.path.dirname(path))
    bob.io.base.save(data, path)


# # Intermediate mapping from RealAccess's to Protocol's
# realaccesses_protocols = Table('realaccesses_protocols', Base.metadata,
#                                Column('realaccess_id', Integer, ForeignKey('realaccess.id')),
#                                Column('protocol_id', Integer, ForeignKey('protocol.id')),
#                                )

# # Intermediate mapping from Attack's to Protocol's
# attacks_protocols = Table('attacks_protocols', Base.metadata,
#                           Column('attack_id', Integer, ForeignKey('attack.id')),
#                           Column('protocol_id', Integer, ForeignKey('protocol.id')),
#                           )


# class Protocol(Base):
#   """MSU_MFSD protocol"""
#
#   __tablename__ = 'protocol'
#
#   id = Column(Integer, primary_key=True)
#   """Unique identifier for the protocol (integer)"""
#
#   name = Column(String(20), unique=True)
#   """Protocol name"""

#   def __init__(self, name):
#     self.name = name
#
#   def __repr__(self):
#     return "Protocol('%s')" % (self.name,)
