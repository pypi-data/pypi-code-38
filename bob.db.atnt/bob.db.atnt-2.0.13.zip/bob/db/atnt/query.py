#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from .models import Client, File, DEFAULT_DATADIR

import bob.db.base

class Database(bob.db.base.Database):
    """Wrapper class for the AT&T (aka ORL) database of faces (http://www.cl.cam.ac.uk/research/dtg/attarchive/facedatabase.html).
    This class defines a simple protocol for training, enrollment and probe by splitting the few images of the database in a reasonable manner.
    Due to the small size of the database, there is only a 'dev' group, and I did not define an 'eval' group."""

    def __init__(self, original_directory=DEFAULT_DATADIR, original_extension='.pgm'):
        """**Constructor Documentation**

        Generates a database.

        Keyword parameters

        original_directory : str, optional
          The directory, where you extracted the original images to. If not
          provided, then use a directory internal to the package (``data``)

        original_extension : str
          The filename extension of the original images. Rarely changed.
        """
        self.original_directory = original_directory
        self.original_extension = original_extension
        # initialize members
        self.m_groups = ('world', 'dev')
        self.m_purposes = ('enroll', 'probe')
        self.m_training_clients = set([1, 2, 5, 6, 10, 11, 12, 14, 16, 17, 20, 21, 24, 26, 27, 29, 33, 34, 36, 39])
        self.m_enroll_files = set([2, 4, 5, 7, 9])

    def groups(self, protocol=None):
        """Returns the names of all registered groups

        Keyword parameters:

        protocol
          ignored.
        """
        return self.m_groups

    def clients(self, groups=None, protocol=None):
        """Returns the vector of clients used in a given group

        Keyword Parameters:

        groups : str or [str]
          One of the groups 'world', 'dev' or a tuple with both of them (which is the default).

        protocol
          Ignored.
        """
        groups = self.check_parameters_for_validity(groups, "group", self.m_groups)

        ids = set()
        if 'world' in groups:
            ids |= self.m_training_clients
        if 'dev' in groups:
            ids |= Client.m_valid_client_ids - self.m_training_clients

        return [Client(id) for id in ids]

    def client_ids(self, groups=None, protocol=None):
        """Returns the vector of ids of the clients used in a given group

        Keyword Parameters:

        groups : str or [str]
          One of the groups 'world', 'dev' or a tuple with both of them (which is the default).

        protocol
          Ignored.
        """

        groups = self.check_parameters_for_validity(groups, "group", self.m_groups)

        ids = set()
        if 'world' in groups:
            ids |= self.m_training_clients
        if 'dev' in groups:
            ids |= Client.m_valid_client_ids - self.m_training_clients

        return sorted(list(ids))

    def models(self, groups=None, protocol=None):
        """Returns the vector of models ( == clients ) used in a given group

        Keyword Parameters:

        groups : str or [str]
          One of the groups 'world', 'dev' or a tuple with both of them (which is the default).

        protocol
          Ignored.
        """

        return self.clients(groups, protocol)

    def model_ids(self, groups=None, protocol=None):
        """Returns the vector of ids of the models (i.e., the client ids) used in a given group

        Keyword Parameters:

        groups : str or [str]
          One of the groups 'world', 'dev' or a tuple with both of them (which is the default).

        protocol
          Ignored.
        """

        return self.client_ids(groups, protocol)

    def get_client_id_from_file_id(self, file_id, groups=None, protocol=None):
        """Returns the client id from the given image id.

        Keyword Parameters:

        file_id : int
          The ID of the :py:class:`File` object to get the client id for

        groups
          ignored.

        protocol
          ignored.
        """
        return File._from_file_id(file_id, self.original_directory,
            self.original_extension).client_id

    def get_client_id_from_model_id(self, model_id, groups=None, protocol=None):
        """Returns the client id from the given model id.
        Since client and model ids are identical, the model id is returned.

        Keyword Parameters:

        model_id : int
          The id of the model.

        groups
          ignored.

        protocol
          ignored.
        """
        return model_id

    def objects(self, model_ids=None, groups=None, purposes=None, protocol=None):
        """Returns a set of :py:class:`File` objects for the specific query by the user.

        Keyword Parameters:

        model_ids : int or [int]
          Limits the returned files relevant to this model id.
          This is expected to be used with groups='dev' only.
          When groups='world', this does not have any effect.
          Should be a list of integral numbers from [1,40]

        groups : str or [str]
          One of the groups 'world' or 'dev' or a list with both of them (which is the default).

        purposes : str or [str]
          One of the purposes 'enroll' or 'probe' or a list with both of them (which is the default).
          This field is ignored when the group 'world' is selected.

        protocol
          Ignored.

        Returns: A list of :py:class:`File` objects considering all the filtering criteria.
        """

        # check if groups set are valid
        groups = self.check_parameters_for_validity(groups, "group", self.m_groups)

        # collect the ids to retrieve
        ids = set(self.client_ids(groups))

        # check the desired client ids for sanity
        if isinstance(model_ids, int):
            model_ids = (model_ids,)
        model_ids = self.check_parameters_for_validity(model_ids, "model", list(Client.m_valid_client_ids))

        # calculate the intersection between the ids and the desired client ids
        ids = ids & set(model_ids)

        # check that the purposes are valid
        if 'dev' in groups:
            purposes = self.check_parameters_for_validity(purposes, "purpose", self.m_purposes)
        else:
            purposes = self.m_purposes

        # go through the dataset and collect all desired files
        retval = []
        if 'enroll' in purposes:
            for client_id in ids:
                for file_id in self.m_enroll_files:
                    retval.append(File(client_id, file_id,
                      self.original_directory, self.original_extension))

        if 'probe' in purposes:
            file_ids = File.m_valid_file_ids - self.m_enroll_files
            # for probe, we use all clients of the given groups
            for client_id in self.client_ids(groups):
                for file_id in file_ids:
                    retval.append(File(client_id, file_id,
                      self.original_directory, self.original_extension))

        return retval


    def paths(self, file_ids, prefix=None, suffix=None, preserve_order=True):
        """Returns a full file paths considering particular file ids, a given
        directory and an extension

        Keyword Parameters:

        file_ids : int or [int]
          The list of ids of the File objects in the database.

        prefix : str
          The bit of path to be prepended to the filename stem

        suffix : str
          The extension determines the suffix that will be appended to the filename
          stem.

        preserve_order : bool
          Ignored since the order is always preserved.

        Returns a list (that may be empty) of the fully constructed paths given the
        file ids.
        """

        files = [File._from_file_id(id, self.original_directory, self.original_extension) for id in file_ids]
        return [f.make_path(prefix, suffix) for f in files]


    def reverse(self, paths, preserve_order=True):
        """Reverses the lookup: from certain paths, return a list of
        File objects

        Keyword Parameters:

        paths : [str]
          The filename stems to query for. This object should be a python
          iterable (such as a tuple or list)

        preserve_order : bool
          Ignored since the order is always preserved.

        Returns a list (that may be empty).
        """

        return [File._from_path(p, self.original_directory, self.original_extension) for p in paths]
