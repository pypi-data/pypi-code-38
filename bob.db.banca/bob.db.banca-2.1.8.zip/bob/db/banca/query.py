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

"""This module provides the Dataset interface allowing the user to query the
BANCA database in the most obvious ways.
"""

import os
import six
from bob.db.base import utils
from .models import *
from .driver import Interface
import bob.db.base

SQLITE_FILE = Interface().files()[0]


class Database(bob.db.base.SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension=None):
    # call base class constructors
        # copy original file name and extension

    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory, original_extension)

  def __group_replace_alias__(self, l):
    """Replace 'dev' by 'g1' and 'eval' by 'g2' in a list of groups, and
       returns the new list"""
    if not l:
      return l
    elif isinstance(l, six.string_types):
      return self.__group_replace_alias__((l,))
    l2 = []
    for val in l:
      if(val == 'dev'):
        l2.append('g1')
      elif(val == 'eval'):
        l2.append('g2')
      else:
        l2.append(val)
    return tuple(l2)

  def groups(self, protocol=None):
    """Returns the names of all registered groups"""

    return ProtocolPurpose.group_choices

  def client_groups(self):
    """Returns the names of the BANCA groups. This is specific to this database which
    does not have separate training, development and evaluation sets."""

    return Client.group_choices

  def genders(self):
    """Returns the list of genders: 'm' for male and 'f' for female"""

    return Client.gender_choices

  def languages(self):
    """Returns the list of languages"""

    return Client.language_choices

  def subworld_names(self):
    """Returns all registered subworld names"""

    l = self.subworlds()
    retval = [str(k.name) for k in l]
    return retval

  def subworlds(self):
    """Returns the list of subworlds"""

    return list(self.query(Subworld))

  def has_subworld(self, name):
    """Tells if a certain subworld is available"""

    return self.query(Subworld).filter(Subworld.name == name).count() != 0

  def clients(self, protocol=None, groups=None, genders=None, languages=None, subworld=None):
    """Returns a set of clients for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored since the clients are identical for all protocols.

    groups
      The groups to which the clients belong ('g1', 'g2', 'world').
      Note that 'dev' is an alias to 'g1' and 'eval' an alias to 'g2'

    genders
      The gender to which the clients belong ('f', 'm')

    languages
      TODO: only English is currently supported
      The languages spoken by the clients ('en',)

    subworld
      Specify a split of the world data ('onethird', 'twothirds')
      In order to be considered, 'world' should be in groups and only one
      split should be specified.

    Returns: A list containing all the clients which have the given properties.
    """

    groups = self.__group_replace_alias__(groups)
    groups = self.check_parameters_for_validity(
        groups, "group", self.client_groups())
    genders = self.check_parameters_for_validity(
        genders, "gender", self.genders())
    languages = self.check_parameters_for_validity(
        languages, "language", self.languages())
    subworld = self.check_parameters_for_validity(
        subworld, "subworld", self.subworld_names())

    retval = []
    # List of the clients
    if "world" in groups:
      if len(subworld) == 1:
        q = self.query(Client).join((Subworld, Client.subworld)
                                    ).filter(Subworld.name.in_(subworld))
      else:
        q = self.query(Client).filter(Client.sgroup == 'world')
      q = q.filter(Client.gender.in_(genders)).\
          filter(Client.language.in_(languages)).\
          order_by(Client.id)
      retval += list(q)

    if 'g1' in groups or 'g2' in groups:
      q = self.query(Client).filter(Client.sgroup != 'world').\
          filter(Client.sgroup.in_(groups)).\
          filter(Client.gender.in_(genders)).\
          filter(Client.language.in_(languages)).\
          order_by(Client.id)
      retval += list(q)

    return retval

  def tclients(self, protocol=None, groups=None):
    """Returns a set of T-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored since the clients are identical for all protocols.

    groups
      The groups to which the clients belong ('g1', 'g2').
      Note that 'dev' is an alias to 'g1' and 'eval' an alias to 'g2'

    Returns: A list containing all the T-norm clients which have the given properties.
    """

    groups = self.__group_replace_alias__(groups)
    groups = self.check_parameters_for_validity(groups, "group", ('g1', 'g2'))
    # g2 clients are used for normalizing g1 ones, etc.
    tgroups = []
    if 'g1' in groups:
      tgroups.append('g2')
    if 'g2' in groups:
      tgroups.append('g1')
    return self.clients(protocol, tgroups)

  def zclients(self, protocol=None, groups=None):
    """Returns a set of Z-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored since the clients are identical for all protocols.

    groups
      The groups to which the clients belong ('g1', 'g2').
      Note that 'dev' is an alias to 'g1' and 'eval' an alias to 'g2'

    Returns: A list containing all the Z-norm clients which have the given properties.
    """

    groups = self.__group_replace_alias__(groups)
    groups = self.check_parameters_for_validity(groups, "group", ('g1', 'g2'))
    # g2 clients are used for normalizing g1 ones, etc.
    zgroups = []
    if 'g1' in groups:
      zgroups.append('g2')
    if 'g2' in groups:
      zgroups.append('g1')
    return self.clients(protocol, zgroups)

  def models(self, protocol=None, groups=None):
    """Returns a set of models for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored since the models are identical for all protocols.

    groups
      The groups to which the subjects attached to the models belong ('g1', 'g2', 'world')
      Note that 'dev' is an alias to 'g1' and 'eval' an alias to 'g2'

    Returns: A list containing all the models which have the given properties.
    """

    return self.clients(protocol, groups)

  def model_ids(self, protocol=None, groups=None):
    """Returns a set of models ids for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored since the models are identical for all protocols.

    groups
      The groups to which the subjects attached to the models belong ('g1', 'g2', 'world')
      Note that 'dev' is an alias to 'g1' and 'eval' an alias to 'g2'

    Returns: A list containing all the models ids which have the given properties.
    """
    return [model.id for model in self.models(protocol, groups)]

  def tmodels(self, protocol=None, groups=None):
    """Returns a set of T-Norm models for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored since the models are identical for all protocols.

    groups
      The groups to which the clients belong ('g1', 'g2').
      Note that 'dev' is an alias to 'g1' and 'eval' an alias to 'g2'

    Returns: A list containing all the T-norm models which have the given properties.
    """

    return self.tclients(protocol, groups)

  def tmodel_ids(self, protocol=None, groups=None):
    """Returns a set of T-Norm model ids for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored since the models are identical for all protocols.

    groups
      The groups to which the clients belong ('g1', 'g2').
      Note that 'dev' is an alias to 'g1' and 'eval' an alias to 'g2'

    Returns: A list containing all the T-norm models which have the given properties.
    """
    return [model.id for model in self.tmodels(protocol, groups)]

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    return self.query(Client).filter(Client.id == id).count() != 0

  def client(self, id):
    """Returns the client object in the database given a certain id. Raises
    an error if that does not exist."""

    return self.query(Client).filter(Client.id == id).one()

  def get_client_id_from_model_id(self, model_id, **kwargs):
    """Returns the client_id attached to the given model_id

    Keyword Parameters:

    model_id
      The model_id to consider

    Returns: The client_id attached to the given model_id
    """
    return model_id

  def get_client_id_from_tmodel_id(self, tmodel_id, **kwargs):
    """Returns the client_id attached to the given T-Norm model_id

    Keyword Parameters:

    tmodel_id
      The tmodel_id to consider

    Returns: The client_id attached to the given T-Norm model_id
    """
    return tmodel_id

  def objects(self, protocol=None, purposes=None, model_ids=None, groups=None,
              classes=None, languages=None, subworld=None):
    """Returns a set of Files for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the BANCA protocols ('P', 'G', 'Mc', 'Md', 'Ma', 'Ud', 'Ua').

    purposes
      The purposes required to be retrieved ('enroll', 'probe', 'train') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the "world" group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      One of the groups ('dev', 'eval', 'world') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    classes
      The classes (types of accesses) to be retrieved ('client', 'impostor')
      or a tuple with several of them. If 'None' is given (this is the
      default), it is considered the same as a tuple with all possible values.

    languages
      The language spoken by the clients ('en')
      TODO: only English is currently supported
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    subworld
      Specify a split of the world data ('onethird', 'twothirds')
      In order to be considered, 'world' should be in groups and only one
      split should be specified.

    Returns: A list of files which have the given properties.
    """

    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(
        purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    languages = self.check_parameters_for_validity(
        languages, "language", self.languages())
    classes = self.check_parameters_for_validity(
        classes, "class", ('client', 'impostor'))
    subworld = self.check_parameters_for_validity(
        subworld, "subworld", self.subworld_names())

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids, collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    if 'world' in groups:
      q = self.query(File).join(Client).join(
          (ProtocolPurpose, File.protocolPurposes)).join(Protocol)
      if len(subworld) == 1:
        q = q.join((Subworld, Client.subworld)).filter(
            Subworld.name.in_(subworld))
      q = q.filter(Client.sgroup == 'world').\
          filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup == 'world')).\
          filter(Client.language.in_(languages))
      if model_ids:
        q = q.filter(Client.id.in_(model_ids))
      q = q.order_by(File.client_id, File.session_id,
                     File.claimed_id, File.shot_id)
      retval += list(q)

    if ('dev' in groups or 'eval' in groups):
      if('enroll' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
            filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                groups), ProtocolPurpose.purpose == 'enroll'))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id, File.session_id,
                       File.claimed_id, File.shot_id)
        retval += list(q)

      if('probe' in purposes):
        if('client' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(File.client_id == File.claimed_id).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe'))
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          q = q.order_by(File.client_id, File.session_id,
                         File.claimed_id, File.shot_id)
          retval += list(q)

        if('impostor' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(File.client_id != File.claimed_id).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe'))
          if model_ids:
            q = q.filter(File.claimed_id.in_(model_ids))
          q = q.order_by(File.client_id, File.session_id,
                         File.claimed_id, File.shot_id)
          retval += list(q)

    return list(set(retval))  # To remove duplicates

  def tobjects(self, protocol=None, model_ids=None, groups=None, languages=None):
    """Returns a set of Files for enrolling T-norm models for score
       normalization.

    Keyword Parameters:

    protocol
      One of the BANCA protocols ('P', 'G', 'Mc', 'Md', 'Ma', 'Ud', 'Ua').

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      The groups to which the clients belong ('dev', 'eval').

    languages
      The language spoken by the clients ('en')
      TODO: only English is currently supported
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    Returns: A list of Files which have the given properties.
    """

    groups = self.check_parameters_for_validity(
        groups, "group", ('dev', 'eval'))
    # g2 clients are used for normalizing g1 ones, etc.
    tgroups = []
    if 'dev' in groups:
      tgroups.append('eval')
    if 'eval' in groups:
      tgroups.append('dev')
    return self.objects(protocol, 'enroll', model_ids, tgroups, 'client', languages)

  def zobjects(self, protocol=None, model_ids=None, groups=None, languages=None):
    """Returns a set of Files to perform Z-norm score normalization.

    Keyword Parameters:

    protocol
      One of the BANCA protocols ('P', 'G', 'Mc', 'Md', 'Ma', 'Ud', 'Ua').

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      The groups to which the clients belong ('dev', 'eval').

    languages
      The language spoken by the clients ('en')
      TODO: only English is currently supported
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    Returns: A list of Files which have the given properties.
    """

    groups = self.check_parameters_for_validity(
        groups, "group", ('dev', 'eval'))
    # g2 clients are used for normalizing g1 ones, etc.
    zgroups = []
    if 'dev' in groups:
      zgroups.append('eval')
    if 'eval' in groups:
      zgroups.append('dev')
    return self.objects(protocol, 'probe', model_ids, zgroups, None, languages)

  def annotations(self, file):
    """Returns the annotations for the image with the given file id.

    Keyword Parameters:

    file
      The ``File`` object to retrieve the annotations for.

    Returns: the eye annotations as a dictionary {'reye':(y,x), 'leye':(y,x)}.
    """

    self.assert_validity()
    # return the annotations as returned by the call function of the
    # Annotation object
    return file.annotation()

  def protocol_names(self):
    """Returns all registered protocol names"""

    l = self.protocols()
    retval = [str(k.name) for k in l]
    return retval

  def protocols(self):
    """Returns all registered protocols"""

    return list(self.query(Protocol))

  def has_protocol(self, name):
    """Tells if a certain protocol is available"""

    return self.query(Protocol).filter(Protocol.name == name).count() != 0

  def protocol(self, name):
    """Returns the protocol object in the database given a certain name. Raises
    an error if that does not exist."""

    return self.query(Protocol).filter(Protocol.name == name).one()

  def protocol_purposes(self):
    """Returns all registered protocol purposes"""

    return list(self.query(ProtocolPurpose))

  def purposes(self):
    """Returns the list of allowed purposes"""

    return ProtocolPurpose.purpose_choices

  def t_model_ids(self, protocol, groups='dev', **kwargs):
    """Returns the list of model ids used for T-Norm of the given protocol for the given group that satisfy your query.
    For possible keyword arguments, please check the :py:meth:`tmodel_ids` function."""
    return self.uniquify(self.tmodel_ids(protocol=protocol, groups=groups, **kwargs))

  def t_enroll_files(self, protocol, model_id, groups='dev', **kwargs):
    """Returns the list of T-Norm model enrollment File objects from the given model id of the given protocol for the given group that satisfy your query.
    For possible keyword arguments, please check the :py:meth:`tobjects` function."""
    return self.uniquify(self.tobjects(protocol=protocol, groups=groups, model_ids=(model_id,), **kwargs))

  def z_probe_files(self, protocol, groups='dev', **kwargs):
    """Returns the list of Z-Norm probe File objects to probe the model with the given model id of the given protocol for the given group that satisfy your query.
    For possible keyword arguments, please check the :py:meth:`zobjects` function."""
    return self.uniquify(self.zobjects(protocol=protocol, groups=groups, **kwargs))
