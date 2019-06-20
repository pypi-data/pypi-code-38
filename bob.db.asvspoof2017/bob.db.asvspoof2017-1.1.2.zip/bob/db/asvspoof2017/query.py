#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Fri 3 Feb 13:43:22 2017

"""This module provides the Dataset interface allowing the user to query the
asvspoof2017 attack database in the most obvious ways.
"""

from .models import *
from .driver import Interface

import bob.db.base

INFO = Interface()

SQLITE_FILE = INFO.files()[0]


class Database(bob.db.base.SQLiteDatabase):
    """The dataset class opens and maintains a connection opened to the Database.

    It provides many different ways to probe for the characteristics of the data
    and for the data itself inside the database.
    """

    def __init__(self, original_directory=None, original_extension=None):
        # opens a session to the database - keep it open until the end
        super(Database, self).__init__(SQLITE_FILE, File,
                                       original_directory, original_extension)

    def objects(self, attacks=File.attack_choices,
                protocol='competition', groups=Client.group_choices, purposes='genuine',
                gender=Client.gender_choices, clients=None):
        """Returns a list of unique :py:class:`.File` objects for the specific
        query by the user.

        Keyword parameters:

        attacks
            One of the valid attack types (can be also "undefined") as returned by attack_supports() or all,
            as a tuple.  If you set this parameter to an empty string or the value
            None, we reset it to the default, which is to get all.

        protocol
            The protocol for the attack. One of the ones returned by protocols(). If
            you set this parameter to an empty string or the value None, we use reset
            it to the default, "CM".

        groups
            One of the protocol subgroups of data as returned by groups() or a
            tuple with several of them.  If you set this parameter to an empty string
            or the value None, we use reset it to the default which is to get all.

        purposes
            Either "attack", "real", "enroll", "impostor" or a combination of those (in a
            tuple). Defines the purpose of data to be retrieved.  If you set this
            parameter to an empty string or the value None, we use reset it to the
            default "real".

        gender
            A gender of the clients (in a tuple). It can be "undefined". By default return all genders.

        clients
            If set, should be a single integer or a list of integers that define the
            client identifiers from which files should be retrieved. If ommited, set
            to None or an empty list, then data from all clients is retrieved.

        Returns: A list of :py:class:`.File` objects.
        """

        self.assert_validity()

        # check if groups set are valid
        VALID_GROUPS = self.groups()
        groups = self.check_parameters_for_validity(
            groups, "group", VALID_GROUPS, None)

        # check if groups set are valid
        VALID_GENDER = self.genders()
        gender = self.check_parameters_for_validity(
            gender, "gender", VALID_GENDER, None)

        # check if supports set are valid
        VALID_ATTACKS = self.attack_supports()
        attacks = self.check_parameters_for_validity(
            attacks, "attacks", VALID_ATTACKS, None)

        # check if supports set are valid
        VALID_PURPOSE = self.purposes()
        purposes = self.check_parameters_for_validity(
            purposes, "purpose", VALID_PURPOSE, None)

        # check protocol validity
        VALID_PROTOCOLS = [k.name for k in self.protocols()]
        protocol = self.check_parameters_for_validity(
            protocol, "protocol", VALID_PROTOCOLS, ('competition',))

        # checks client identity validity
        VALID_CLIENTS = [k.id for k in self.clients()]
        clients = self.check_parameters_for_validity(
            clients, "client", VALID_CLIENTS, None)

        # now query the database
        retval = []

        q = self.m_session.query(File).join(ProtocolFiles).join(
            (Protocol, ProtocolFiles.protocol)).join(Client)
        if groups:
            q = q.filter(Client.group.in_(groups))
        if clients:
            q = q.filter(Client.id.in_(clients))
        if gender:
            q = q.filter(Client.gender.in_(gender))
        if attacks:
            q = q.filter(File.attacktype.in_(attacks))
        if purposes:
            q = q.filter(File.purpose.in_(purposes))
        q = q.filter(Protocol.name.in_(protocol))
        q = q.order_by(File.path)
        retval += list(q)

        return retval

    def files(self, directory=None, extension=None, **object_query):
        """Returns a set of filenames for the specific query by the user.

        .. deprecated:: 1.1.0

            This function is *deprecated*, use :py:meth:`.Database.objects` instead.

        Keyword Parameters:

        directory
            A directory name that will be prepended to the final filepath returned

        extension
            A filename extension that will be appended to the final filepath returned

        object_query
            All remaining arguments are passed to :py:meth:`.Database.objects`
            untouched. Please check the documentation for such method for more
            details.

        Returns: A dictionary containing the resolved filenames considering all
        the filtering criteria. The keys of the dictionary are unique identities
        for each file in the asvspoof2017 attack database. Conserve these numbers if you
        wish to save processing results later on.
        """

        import warnings
        warnings.warn(
            "The method Database.files() is deprecated, use Database.objects() for more powerful object retrieval",
            DeprecationWarning)

        return dict([(k.id, k.make_path(directory, extension)) for k in self.objects(**object_query)])

    def clients(self, groups=None, protocol=None, gender=None):
        """Returns a list of Clients for the specific query by the user.
        If no parameters are specified - return all clients.

        Keyword Parameters:

        protocol
            An AVspoof protocol.

        groups
            The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

        gender
            The gender to consider ('male', 'female')

        Returns: A list containing the ids of all models belonging to the given group.
        """
        if protocol == '.':
            protocol = None
        protocol = self.check_parameters_for_validity(
            protocol, "protocol", self.protocol_names(), None)
        groups = self.check_parameters_for_validity(
            groups, "group", self.groups(), self.groups())
        gender = self.check_parameters_for_validity(
            gender, "gender", self.genders(), None)

        retval = []
        if groups:
            q = self.m_session.query(Client).filter(Client.group.in_(groups))
            if gender:
                q = q.filter(Client.gender.in_(gender))
            q = q.order_by(Client.id)
            retval += list(q)

        return retval

    def has_client_id(self, id):
        """Returns True if we have a client with a certain integer identifier"""

        self.assert_validity()
        return self.m_session.query(Client).filter(Client.id == id).count() != 0

    def client(self, id):
        """Returns the Client object in the database given a certain id. Raises
        an error if that does not exist."""

        return self.m_session.query(Client).filter(Client.id == id).one()

    def protocols(self):
        """Returns all protocol objects.
        """

        self.assert_validity()
        return list(self.m_session.query(Protocol))

    def protocol_names(self):
        """Returns all registered protocol names"""

        l = self.protocols()
        retval = [str(k.name) for k in l]
        return retval

    def has_protocol(self, name):
        """Tells if a certain protocol is available"""

        self.assert_validity()
        return self.m_session.query(Protocol).filter(Protocol.name == name).count() != 0

    def protocol(self, name):
        """Returns the protocol object in the database given a certain name. Raises
        an error if that does not exist."""

        self.assert_validity()
        return self.m_session.query(Protocol).filter(Protocol.name == name).one()

    def groups(self):
        """Returns the names of all registered groups"""

        return Client.group_choices

    def genders(self):
        """Returns the list of genders"""

        return Client.gender_choices

    def purposes(self):
        """Returns devices used in the database"""

        return File.purpose_choices

    def attack_supports(self):
        """Returns attack supports available in the database"""

        return File.attack_choices

    def paths(self, ids, prefix='', suffix=''):
        """Returns a full file paths considering particular file ids, a given
        directory and an extension

        Keyword Parameters:

        id
            The ids of the object in the database table "file". This object should be
            a python iterable (such as a tuple or list).

        prefix
            The bit of path to be prepended to the filename stem

        suffix
            The extension determines the suffix that will be appended to the filename
            stem.

        Returns a list (that may be empty) of the fully constructed paths given the
        file ids.
        """

        self.assert_validity()

        fobj = self.m_session.query(File).filter(File.id.in_(ids))
        retval = []
        for p in ids:
            retval.extend([k.make_path(prefix, suffix)
                           for k in fobj if k.id == p])
        return retval
