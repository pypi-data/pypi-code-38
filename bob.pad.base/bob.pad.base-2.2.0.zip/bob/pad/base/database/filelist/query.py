#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date:   Thu Nov 17 16:09:22 CET 2016
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


"""This module provides the Database interface allowing the user to query the
PAD database based on file lists provided in the corresponding directory.
"""

import os

from .models import Client, ListReader
from .. import PadFile
from .. import PadDatabase
from bob.bio.base.database import FileListBioDatabase

class FileListPadDatabase(PadDatabase, FileListBioDatabase):
    """This class provides a user-friendly interface to databases that are given as file lists.

    Keyword parameters:

    filelists_directory : str
      The directory that contains the filelists defining the protocol(s). If you use the protocol
      attribute when querying the database, it will be appended to the base directory, such that
      several protocols are supported by the same class instance of `bob.pad.base`.

    name : str
      The name of the database

    protocol : str
      The protocol of the database. This should be a folder inside ``filelists_directory``.

    pad_file_class : class
      The class that should be used for return the files.
      This can be `PadFile`, `PadVoiceFile`, or anything similar.

    original_directory : str or ``None``
      The directory, where the original data can be found

    original_extension : str or [str] or ``None``
      The filename extension of the original data, or multiple extensions

    annotation_directory : str or ``None``
      The directory, where additional annotation files can be found

    annotation_extension : str or ``None``
      The filename extension of the annotation files

    annotation_type : str
    The type of the annotation file to read, see `bob.db.base.read_annotation_file` for accepted formats.

    train_subdir : str or ``None``
      Specify a custom subdirectory for the filelists of the development set (default is 'train')

    dev_subdir : str or ``None``
      Specify a custom subdirectory for the filelists of the development set (default is 'dev')

    eval_subdir : str or ``None``
      Specify a custom subdirectory for the filelists of the development set (default is 'eval')

    keep_read_lists_in_memory : bool
      If set to true, the lists are read only once and stored in memory
    """

    def __init__(
            self,
            filelists_directory,
            name,
            protocol=None,
            pad_file_class=PadFile,

            original_directory=None,
            original_extension=None,

            # PAD annotations should be supported in the future
            annotation_directory=None,
            annotation_extension="",
            annotation_type=None,

            train_subdir=None,
            dev_subdir=None,
            eval_subdir=None,

            real_filename=None,  # File containing the real files
            attack_filename=None,  # File containing the real files

            # if set to True (the RECOMMENDED default) lists are read only once and stored in memory.
            keep_read_lists_in_memory=True,
            **kwargs
    ):
        super(FileListPadDatabase, self).__init__(
                             name=name,
                             protocol=protocol,
                             original_directory=original_directory,
                             original_extension=original_extension,
                             annotation_directory=annotation_directory,
                             annotation_extension=annotation_extension,
                             annotation_type=annotation_type,
                             filelists_directory=filelists_directory,
                             dev_sub_directory=dev_subdir,
                             eval_sub_directory=eval_subdir,
                             **kwargs)
        # extra args for pretty printing
        self._kwargs.update(dict(
            train_sub_directory=train_subdir,
            real_filename=real_filename,
            attack_filename=attack_filename,
        ))

        self.pad_file_class = pad_file_class
        self.list_readers = {}

        self.m_base_dir = os.path.abspath(filelists_directory)
        if not os.path.isdir(self.m_base_dir):
            raise RuntimeError('Invalid directory specified %s.' % self.m_base_dir)

        # sub-directories for train, dev, and eval sets:
        self.m_dev_subdir = dev_subdir if dev_subdir is not None else 'dev'
        self.m_eval_subdir = eval_subdir if eval_subdir is not None else 'eval'
        self.m_train_subdir = train_subdir if train_subdir is not None else 'train'

        # real list:        format:   filename client_id
        self.m_real_filename = real_filename if real_filename is not None else 'for_real.lst'
        # attack list:        format:   filename client_id attack_type
        self.m_attack_filename = attack_filename if attack_filename is not None else 'for_attack.lst'

        self.keep_read_lists_in_memory = keep_read_lists_in_memory

    def _list_reader(self, protocol):
        if protocol not in self.list_readers:
            if protocol is not None:
                protocol_dir = os.path.join(self.get_base_directory(), protocol)
                if not os.path.isdir(protocol_dir):
                    raise ValueError(
                        "The directory %s for the given protocol '%s' does not exist" % (protocol_dir, protocol))
            self.list_readers[protocol] = ListReader(self.keep_read_lists_in_memory)

        return self.list_readers[protocol]

    def _make_pad(self, files):
        return [self.pad_file_class(client_id=f.client_id, path=f.path, attack_type=f.attack_type, file_id=f.id)
                for f in files]

    def groups(self, protocol=None, add_world=False, add_subworld=False):
        """This function returns the list of groups for this database.

        protocol : str or ``None``
          The protocol for which the groups should be retrieved.

        Returns: a list of groups
        """
        groups = []
        if protocol is not None:
            if os.path.isdir(os.path.join(self.get_base_directory(), protocol, self.m_dev_subdir)):
                groups.append('dev')
            if os.path.isdir(os.path.join(self.get_base_directory(), protocol, self.m_eval_subdir)):
                groups.append('eval')
            if os.path.isdir(os.path.join(self.get_base_directory(), protocol, self.m_train_subdir)):
                groups.append('train')
        else:
            if os.path.isdir(os.path.join(self.get_base_directory(), self.m_dev_subdir)):
                groups.append('dev')
            if os.path.isdir(os.path.join(self.get_base_directory(), self.m_eval_subdir)):
                groups.append('eval')
            if os.path.isdir(os.path.join(self.get_base_directory(), self.m_train_subdir)):
                groups.append('train')
        return groups

    def _get_list_file(self, group, type=None, protocol=None):
        if protocol:
            base_directory = os.path.join(self.get_base_directory(), protocol)
        else:
            base_directory = self.get_base_directory()

        group_dir = self.m_dev_subdir if group == 'dev' else self.m_eval_subdir if group == 'eval' else self.m_train_subdir
        list_name = {'for_real': self.m_real_filename,
                     'for_attack': self.m_attack_filename,
                     }[type]
        return os.path.join(base_directory, group_dir, list_name)


    def client_ids(self, protocol=None, groups=None):
        """Returns a list of client ids for the specific query by the user.

        Keyword Parameters:

        protocol : str or ``None``
          The protocol to consider

        groups : str or [str] or ``None``
          The groups to which the clients belong ("dev", "eval", "train").

        Returns: A list containing all the client ids which have the given properties.
        """

        groups = self.check_parameters_for_validity(groups, "group",
                                                    self.groups(protocol),
                                                    default_parameters=self.groups(protocol))

        return sorted(self.__client_id_list__(groups, 'for_real', protocol))

    def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, **kwargs):
        """Returns a set of :py:class:`PadFile` objects for the specific query by the user.

        Keyword Parameters:

        groups : str or [str] or ``None``
          One of the groups ("dev", "eval", "train") or a tuple with several of them.
          If 'None' is given (this is the default), it is considered the same as a
          tuple with all possible values.

        protocol : str or ``None``
          The protocol to consider

        purposes : str or [str] or ``None``
          The purposes required to be retrieved ("real", "attack") or a tuple
          with several of them. If 'None' is given (this is the default), it is
          considered the same as a tuple with all possible values.

        model_ids : [various type]
          This parameter is not supported in PAD databases yet

        Returns: A list of :py:class:`PadFile` objects considering all the filtering criteria.
        """

        purposes = self.check_parameters_for_validity(purposes, "purpose", ('real', 'attack'))
        groups = self.check_parameters_for_validity(groups, "group",
                                                    self.groups(protocol),
                                                    default_parameters=self.groups(protocol))

        # first, collect all the lists that we want to process
        lists = []
        for group in ('train', 'dev', 'eval'):
            if group in groups:
                if 'real' in purposes:
                    lists.append(
                        self._list_reader(protocol).read_list(self._get_list_file(group, 'for_real', protocol=protocol),
                                                     group, 'for_real'))
                if 'attack' in purposes:
                    lists.append(
                        self._list_reader(protocol).read_list(self._get_list_file(group, 'for_attack',
                                                                                  protocol=protocol),
                                                     group, 'for_attack'))

        # now, go through the lists and add add corresponding files
        retval = []

        # non-probe files; just filter by model id
        for flist in lists:
            for fileobj in flist:
                retval.append(fileobj)

        return self._make_pad(retval)

    def annotations(self, file):
        return FileListBioDatabase.annotations(self, file)

    def tobjects(self, groups=None, protocol=None, model_ids=None, **kwargs):
        pass

    def zobjects(self, groups=None, protocol=None, **kwargs):
        pass
