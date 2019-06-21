#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This module provides the Dataset interface allowing the user to query the
YouTube database.
"""

import six
from bob.db.base import utils
from .models import *
from sqlalchemy.orm import aliased
from .driver import Interface
import glob

import bob.db.base

SQLITE_FILE = Interface().files()[0]


class Database(bob.db.base.SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension='/*.jpg', annotation_extension='.labeled_faces.txt'):
    """**Keyword parameters**

    original_directory : str
      The directory where the original images (and annotations) can be found

    original_extension : str
      The filename filter to find the orignal images in the database; rarely changed

    annotation_extension : str
      The filename extension of the annotation files; rarely changed
    """
    # call base class constructor
    super(Database, self).__init__(SQLITE_FILE, Directory,
                                   original_directory, original_extension)

    self.m_valid_protocols = ('fold1', 'fold2', 'fold3', 'fold4',
                              'fold5', 'fold6', 'fold7', 'fold8', 'fold9', 'fold10')
    self.m_valid_groups = ('world', 'dev', 'eval')
    self.m_valid_purposes = ('enroll', 'probe')
    self.m_valid_classes = ('client', 'impostor')  # 'matched' and 'unmatched'
    self.m_subworld_counts = {'onefolds': 1, 'twofolds': 2, 'threefolds': 3,
                              'fourfolds': 4, 'fivefolds': 5, 'sixfolds': 6, 'sevenfolds': 7}
    self.m_valid_types = ('restricted', 'unrestricted')

    self.annotation_extension = annotation_extension

  def __eval__(self, fold):
    return int(fold[4:])

  def __dev__(self, eval):
    # take the two parts of the training set (the ones before the eval set)
    # for dev
    return ((eval + 7) % 10 + 1, (eval + 8) % 10 + 1)

  def __dev_for__(self, fold):
    return ["fold%d" % f for f in self.__dev__(self.__eval__(fold))]

  def __zt_fold_for__(self, fold):
    if fold is None:
      return None
    return 'fold%d' % ((int(fold[4:]) + 7) % 10 + 1)

  def __world_for__(self, fold, subworld):
    # the training sets for each fold are composed of all folds
    # except the given one and the previous
    eval = self.__eval__(fold)
    dev = self.__dev__(eval)
    world_count = self.m_subworld_counts[subworld]
    world = []
    for i in range(world_count):
      world.append((eval + i) % 10 + 1)
    return ["fold%d" % f for f in world]

  def protocol_names(self):
    """Returns the names of the valid protocols."""
    return self.m_valid_protocols

  def groups(self):
    """Returns the groups, which are available in the database."""
    return self.m_valid_groups

  def subworld_names(self, protocol=None):
    """Returns all valid sub-worlds for the fold.. protocols."""
    return self.m_subworld_counts.keys()

  def world_types(self):
    """Returns the valid types of worlds: ('restricted', 'unrestricted')."""
    return self.m_valid_types

  def clients(self, protocol=None, groups=None, subworld='sevenfolds', world_type='unrestricted'):
    """Returns a list of Client objects for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider; one of: ('fold1', ..., 'fold10'), or None

    groups
      The groups to which the clients belong; one or several of: ('world', 'dev', 'eval')

    subworld
      The subset of the training data. Has to be specified if groups includes 'world'
      and protocol is one of 'fold1', ..., 'fold10'.
      It might be exactly one of ('onefolds', 'twofolds', ..., 'sevenfolds').
      Ignored for group 'dev' and 'eval'.

    world_type
      One of ('restricted', 'unrestricted'). Ignored.

    Returns: A list containing all Client objects which have the desired properties.
    """
    protocols = self.check_parameters_for_validity(
        protocol, 'protocol', self.m_valid_protocols)
    groups = self.check_parameters_for_validity(
        groups, 'group', self.m_valid_groups)
    if subworld != None:
      subworld = self.check_parameter_for_validity(
          subworld, 'sub-world', list(self.m_subworld_counts.keys()))
    world_type = self.check_parameter_for_validity(
        world_type, 'training type', self.m_valid_types)

    queries = []

    # List of the clients
    for protocol in protocols:
      if 'world' in groups:
        # select training set for the given fold
        trainset = self.__world_for__(protocol, subworld)
        queries.append(
            self.query(Client).join(Directory).join((Pair, or_(Directory.id == Pair.enroll_directory_id, Directory.id == Pair.probe_directory_id))).
            filter(Pair.protocol.in_(trainset)).
            order_by(Client.id))
      if 'dev' in groups:
        # select development set for the given fold
        devset = self.__dev_for__(protocol)
        queries.append(
            self.query(Client).join(Directory).join((Pair, or_(Directory.id == Pair.enroll_directory_id, Directory.id == Pair.probe_directory_id))).
            filter(Pair.protocol.in_(devset)).
            order_by(Client.id))
      if 'eval' in groups:
        queries.append(
            self.query(Client).join(Directory).join((Pair, or_(Directory.id == Pair.enroll_directory_id, Directory.id == Pair.probe_directory_id))).
            filter(Pair.protocol == protocol).
            order_by(Client.id))

    # all queries are made; now collect the clients
    retval = []
    for query in queries:
      for client in query:
        retval.append(client)

    return self.uniquify(retval)

  def models(self, protocol=None, groups=None):
    """Returns a list of Directory objects (there are multiple models per client) for the specific query by the user.
    For the 'dev' and 'eval' groups, the first element of each pair is extracted.

    Keyword Parameters:

    protocol
      The protocol to consider; one of: ('fold1', ..., 'fold10'), or None

    groups
      The groups to which the clients belong; one or several of: ('dev', 'eval')

    Returns: A list containing all Directory objects which have the desired properties.
    """

    protocols = self.check_parameters_for_validity(
        protocol, 'protocol', self.m_valid_protocols)
    groups = self.check_parameters_for_validity(
        groups, 'group', ('dev', 'eval'))

    # the restricted case...
    queries = []

    # List of the models
    for protocol in protocols:
      if 'dev' in groups:
        # select development set for the given fold
        devset = self.__dev_for__(protocol)
        queries.append(
            self.query(Directory).join((Pair, Directory.id == Pair.enroll_directory_id)).
            filter(Pair.protocol.in_(devset)))
      if 'eval' in groups:
        queries.append(
            self.query(Directory).join((Pair, Directory.id == Pair.enroll_directory_id)).
            filter(Pair.protocol == protocol))

    # all queries are made; now collect the files
    retval = []
    for query in queries:
      retval.extend([file for file in query])

    return self.uniquify(retval)

  def model_ids(self, protocol=None, groups=None):
    """Returns a list of model ids for the specific query by the user.
    For the 'dev' and 'eval' groups, the first element of each pair is extracted.

    Keyword Parameters:

    protocol
      The protocol to consider; one of: ('fold1', ..., 'fold10'), or None

    groups
      The groups to which the clients belong; one or several of: ('dev', 'eval')
      The 'eval' group does not exist for protocol 'view1'.

    Returns: A list containing all model ids which have the desired properties.
    """
    return [file.id for file in self.models(protocol, groups)]

  def tmodels(self, protocol=None, groups=None):
    """Returns a list of T-Norm models that can be used for ZT norm.
    In fact, it uses the model ids from two other splits of the data,
    specifically, the last two of the training splits.
    Hence, to get training data independent from ZT-Norm data,
    use maximum subworld='fivefolds' in the world query.

    Keyword Parameters:

    protocol
      The protocol to consider; one of: ('fold1', ..., 'fold10'), or None

    groups
      Ignored.

    Returns: A list containing all Directory objects which have the desired properties.
    """
    return self.models(self.__zt_fold_for__(protocol), groups='dev')

  def tmodel_ids(self, protocol, groups=None):
    """Returns a list of T-Norm model ids that can be used for ZT norm.
    In fact, it uses the model ids from two other splits of the data,
    specifically, the last two of the training splits.
    Hence, to get training data independent from ZT-Norm data,
    use maximum subworld='fivefolds' in the world query.

    Keyword Parameters:

    protocol
      The protocol to consider; one of: ('fold1', ..., 'fold10'), or None

    groups
      Ignored.

    Returns: A list containing all Directory objects which have the desired properties.
    """
    return [file.id for file in self.tmodels(protocol, groups)]

  def get_client_id_from_file_id(self, file_id, **kwargs):
    """Returns the client_id (real client id) attached to the given file_id

    Keyword Parameters:

    file_id
      The file_id to consider

    Returns: The client_id attached to the given file_id
    """
    self.assert_validity()

    q = self.query(Directory).\
        filter(Directory.id == file_id)

    assert q.count() == 1
    return q.first().client_id

  def get_client_id_from_model_id(self, model_id, **kwargs):
    """Returns the client_id (real client id) attached to the given model id

    Keyword Parameters:

    model_id
      The model to consider

    Returns: The client_id attached to the given model
    """

    # since there is one model per file, we can re-use the function above.
    return self.get_client_id_from_file_id(model_id)

  def objects(self, protocol=None, model_ids=None, groups=None, purposes=None, subworld='sevenfolds', world_type='unrestricted'):
    """Returns a list of Directory objects for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('fold1', ..., 'fold10'), or None

    groups
      The groups to which the objects belong ('world', 'dev', 'eval')

    purposes
      The purposes of the objects ('enroll', 'probe')

    subworld
      The subset of the training data. Has to be specified if groups includes 'world'
      and protocol is one of 'fold1', ..., 'fold10'.
      It might be exactly one of ('onefolds', 'twofolds', ..., 'sevenfolds').

    world_type
      One of ('restricted', 'unrestricted'). If 'restricted', only the files that
      are used in one of the training pairs are used. For 'unrestricted', all
      files of the training people are returned.

    model_ids
      Only retrieves the objects for the provided list of model ids.
      If 'None' is given (this is the default), no filter over the model_ids is performed.
      Note that the combination of 'world' group and 'model_ids' should be avoided.

    Returns: A list of Directory objects considering all the filtering criteria.
    """

    protocols = self.check_parameters_for_validity(
        protocol, "protocol", self.m_valid_protocols)
    groups = self.check_parameters_for_validity(
        groups, "group", self.m_valid_groups)
    purposes = self.check_parameters_for_validity(
        purposes, "purpose", self.m_valid_purposes)
    world_type = self.check_parameter_for_validity(
        world_type, 'training type', self.m_valid_types)

    if subworld != None:
      subworld = self.check_parameter_for_validity(
          subworld, 'sub-world', list(self.m_subworld_counts.keys()))

    if(isinstance(model_ids, six.string_types)):
      model_ids = (model_ids,)

    queries = []
    probe_queries = []
    directory_alias = aliased(Directory)

    for protocol in protocols:
      if 'world' in groups:
        # world set of current fold of view 2
        trainset = self.__world_for__(protocol, subworld)
        if world_type == 'restricted':
          queries.append(
              self.query(Directory).join((Pair, or_(Directory.id == Pair.enroll_directory_id, Directory.id == Pair.probe_directory_id))).
              filter(Pair.protocol.in_(trainset)))
        else:
          queries.append(
              self.query(Directory).join(Client).join((Pair, or_(Client.id == Pair.enroll_client_id, Client.id == Pair.probe_client_id))).
              filter(Pair.protocol.in_(trainset)))

      if 'dev' in groups:
        # development set of current fold of view 2
        devset = self.__dev_for__(protocol)
        if 'enroll' in purposes:
          queries.append(
              self.query(Directory).join((Pair, Directory.id == Pair.enroll_directory_id)).
              filter(Pair.protocol.in_(devset)))
        if 'probe' in purposes:
          probe_queries.append(
              self.query(Directory).
              join((Pair, Directory.id == Pair.probe_directory_id)).
              join((directory_alias, directory_alias.id == Pair.enroll_directory_id)).
              filter(Pair.protocol.in_(devset)))

      if 'eval' in groups:
        # evaluation set of current fold of view 2; this is the REAL fold
        if 'enroll' in purposes:
          queries.append(
              self.query(Directory).join((Pair, Directory.id == Pair.enroll_directory_id)).
              filter(Pair.protocol == protocol))
        if 'probe' in purposes:
          probe_queries.append(
              self.query(Directory).
              join((Pair, Directory.id == Pair.probe_directory_id)).
              join((directory_alias, directory_alias.id == Pair.enroll_directory_id)).
              filter(Pair.protocol == protocol))

    retval = []
    for query in queries:
      if model_ids and len(model_ids):
        query = query.filter(Directory.id.in_(model_ids))

      retval.extend([file for file in query])

    for query in probe_queries:
      if model_ids and len(model_ids):
        query = query.filter(directory_alias.id.in_(model_ids))

      for probe in query:
        retval.append(probe)

    return self.uniquify(retval)

  def tobjects(self, protocol, model_ids=None, groups=None):
    """Returns a set of filenames for enrolling T-norm models for score
       normalization.

    Keyword Parameters:

    protocol
      The protocol to consider ('fold1', ..., 'fold10'), or None

    model_ids
      Only retrieves the files for the provided list of model ids.
      If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      Ignored.

    Returns: A set of Directory objects with the given properties.
    """
    return self.objects(self.__zt_fold_for__(protocol), groups='dev', model_ids=model_ids, purposes='enroll')

  def zobjects(self, protocol, model_ids=None, groups=None):
    """Returns a set of filenames for Z-norm probing for score
       normalization.

    Keyword Parameters:

    protocol
      The protocol to consider ('fold1', ..., 'fold10'), or None

    model_ids
      Only retrieves the files for the provided list of model ids.
      If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      Ignored.

    Returns: A set of Directory objects with the given properties.
    """
    return self.objects(self.__zt_fold_for__(protocol), groups='dev', model_ids=model_ids, purposes='probe')

  def pairs(self, protocol=None, groups=None, classes=None, subworld='sevenfolds'):
    """Queries a list of Pair's of files.

    Keyword Parameters:

    protocol
      The protocol to consider ('fold1', ..., 'fold10')

    groups
      The groups to which the objects belong ('world', 'dev', 'eval')

    classes
      The classes to which the pairs belong ('matched', 'unmatched')

    subworld
      The subset of the training data. Has to be specified if groups includes 'world'
      and protocol is one of 'fold1', ..., 'fold10'.
      It might be exactly one of ('onefolds', 'twofolds', ..., 'sevenfolds').

    Returns: A list of Pair's considering all the filtering criteria.
    """

    def default_query():
      return self.query(Pair).\
          join((Directory1, Directory1.id == Pair.enroll_directory_id)).\
          join((Directory2, Directory2.id == Pair.probe_directory_id))

    protocol = self.check_parameter_for_validity(
        protocol, "protocol", self.m_valid_protocols)
    groups = self.check_parameters_for_validity(
        groups, "group", self.m_valid_groups)
    classes = self.check_parameters_for_validity(
        classes, "class", self.m_valid_classes)
    if subworld != None:
      subworld = self.check_parameter_for_validity(
          subworld, 'sub-world', list(self.m_subworld_counts.keys()))

    queries = []
    Directory1 = aliased(Directory)
    Directory2 = aliased(Directory)

    if 'world' in groups:
      trainset = self.__world_for__(protocol, subworld)
      queries.append(default_query().filter(Pair.protocol.in_(trainset)))
    if 'dev' in groups:
      devset = self.__dev_for__(protocol)
      queries.append(default_query().filter(Pair.protocol.in_(devset)))
    if 'eval' in groups:
      queries.append(default_query().filter(Pair.protocol == protocol))

    retval = []
    for query in queries:
      if not 'client' in classes:
        query = query.filter(Pair.is_match == False)
      if not 'impostor' in classes:
        query = query.filter(Pair.is_match == True)

      for pair in query:
        retval.append(pair)

    return retval

  def annotations(self, directory, image_names=None):
    """Returns the annotations for the given file id as a dictionary of dictionaries, e.g. {'1.56.jpg' : {'topleft':(y,x), 'bottomright':(y,x)}, '1.57.jpg' : {'topleft':(y,x), 'bottomright':(y,x)}, ...}.
    Here, the key of the dictionary is the full image file name of the original image.

    Keyword parameters:

    directory
      The :py:class:`Directory` object for which you want to retrieve the annotations

    image_names
      If given, only the annotations for the given image names (without path, but including filaname extension) are extracted and returned
    """
    self.assert_validity()
    if self.original_directory is None:
      raise ValueError(
          "Please specify the 'original_directory' in the constructor of this class to get the annotations.")

    annotation_file = os.path.join(
        self.original_directory, directory.client.name + self.annotation_extension)

    annots = {}

    with open(annotation_file) as f:
      for line in f:
        splits = line.rstrip().split(',')
        shot_id = int(splits[0].split('\\')[1])
        index = splits[0].split('\\')[2]
        if shot_id == directory.shot_id:
          if image_names is None or index in image_names:
            # coordinates are: center x, center y, width, height
            (center_y, center_x, d_y, d_x) = (float(splits[3]), float(
                splits[2]), float(splits[5]) / 2., float(splits[4]) / 2.)
            # extract the bounding box information
            annots[index] = {
                'topleft': (center_y - d_y, center_x - d_x),
                'bottomright': (center_y + d_y, center_x + d_x)
            }

    # return the annotations as returned by the call function of the
    # Annotation object
    return annots

  def original_file_name(self, directory, check_existence=None):
    """Returns the list of original image names for the given ``directory``, sorted by frame number.
    In opposition to other bob databases, here a **list** of file names is returned.

    Keyword arguments:

    directory : :py:class:`bob.db.youtube.Directory`
      The Directory object to retrieve the list of file names for

    check_existence : bool
      Shall the existence of the files be checked?
    """

    # get original filename expression for the directory
    #file_name_filter = bob.db.base.Database.original_file_name(self, directory, check_existence = False)
    # check if directory is set
    if not self.original_directory or not self.original_extension:
      raise ValueError(
          "The original_directory and/or the original_extension were not specified in the constructor.")
    # extract file name
    file_name_list = directory.make_path(
        self.original_directory, self.original_extension)
    if not check_existence or os.path.exists(file_name):
      return file_name_list

    # list the data
    import glob
    file_name_list = glob.glob(file_name_filter)
    if check_existence and not file_name_list:
      raise ValueError("No image was found in directory '%s'. Please check the original directory '%s'." % (
          file_name_filter, self.original_directory))
    # get the file names sorted by id
    return sorted(file_name_list, key=lambda x: int(x.split('.')[-2]))
