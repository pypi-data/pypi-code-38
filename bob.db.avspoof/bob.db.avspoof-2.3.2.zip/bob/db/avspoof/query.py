#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Wed 19 Aug 13:43:50 2015

"""This module provides the Dataset interface allowing the user to query the
avspoof attack database in the most obvious ways.
"""

from bob.db.base import utils
from .models import *
from .driver import Interface

INFO = Interface()

SQLITE_FILE = INFO.files()[0]


class Database(object):
    """The dataset class opens and maintains a connection opened to the Database.

    It provides many different ways to probe for the characteristics of the data
    and for the data itself inside the database.
    """

    def __init__(self):
        # opens a session to the database - keep it open until the end
        self.connect()

    def __del__(self):
        """Releases the opened file descriptor"""
        if self.session:
            try:
                # Since the dispose function re-creates a pool
                # which might fail in some conditions, e.g., when this
                # destructor is called during the exit of the python interpreter
                self.session.close()
                self.session.bind.dispose()
            except TypeError:
                # ... I can just ignore the according exception...
                pass
            except AttributeError:
                pass

    def connect(self):
        """Tries connecting or re-connecting to the database"""
        if not os.path.exists(SQLITE_FILE):
            self.session = None

        else:
            self.session = utils.session_try_readonly(INFO.type(), SQLITE_FILE)

    def is_valid(self):
        """Returns if a valid session has been opened for reading the database"""

        return self.session is not None

    def assert_validity(self):
        """Raise a RuntimeError if the database backend is not available"""

        if not self.is_valid():
            raise RuntimeError("Database '%s' cannot be found at expected location '%s'. "
                               " Create it and then try re-connecting using Database.connect()" % (
                               INFO.name(), SQLITE_FILE))

    def objects(self, attack_type=File.attack_type_choices,
                protocol='grandtest', groups=Client.set_choices, cls=('real',),
                recording_devices=File.recording_device_choices, sessions=File.session_choices, gender=Client.gender_choices,
                attack_devices=File.attack_device_choices, clients=None):
        """Returns a list of unique :py:class:`.File` objects for the specific
        query by the user.

        Keyword parameters:

        attack_type
            One of the valid attack types as returned by models.Attack.attack_types() or all,
            as a tuple.  If you set this parameter to an empty string or the value
            None, we reset it to the default, which is to get all.

        protocol
            The protocol for the attack. One of the ones returned by protocols(). If
            you set this parameter to an empty string or the value None, we reset
            it to the default, "grandtest".

        groups
            One of the protocol subgroups of data as returned by groups() or a
            tuple with several of them.  If you set this parameter to an empty string
            or the value None, we reset it to the default which is to get all.

        cls
            Either "attack", "real", "enroll", "probe", or a combination of those (in a
            tuple). Defines the class of data to be retrieved.  If you set this
            parameter to an empty string or the value None, we reset it to the
            default, ("real").

        recording_devices
            One of the recording_devices used to record the data (laptop, phone1, and phone2)
            or a combination of them (in a tuple), which is also the default.

        clients
            If set, should be a single integer or a list of integers that define the
            client identifiers from which files should be retrieved. If omitted, set
            to None or an empty list, then data from all clients is retrieved.

        Returns: A list of :py:class:`.File` objects.
        """

        self.assert_validity()

        # check if groups set are valid
        VALID_GROUPS = self.groups()
        groups = self.check_parameters_for_validity(groups, "group", VALID_GROUPS, None)

        # check if groups set are valid
        VALID_GENDER = self.genders()
        gender = self.check_parameters_for_validity(gender, "gender", VALID_GENDER, None)

        # check if supports set are valid
        VALID_SUPPORTS = self.attack_types()
        attack_type = self.check_parameters_for_validity(attack_type, "attack_type", VALID_SUPPORTS, None)

        # check if supports set are valid
        VALID_ATTACKDEVICES = self.attack_devices()
        attack_devices = self.check_parameters_for_validity(attack_devices, "attack_device", VALID_ATTACKDEVICES, None)

        # by default, do NOT grab enrollment data from the database
        VALID_CLASSES = ('real', 'attack', 'enroll', 'probe')
        cls = self.check_parameters_for_validity(cls, "class", VALID_CLASSES, VALID_CLASSES)

        # check protocol validity
        VALID_PROTOCOLS = [k.name for k in self.protocols()]
        protocol = self.check_parameters_for_validity(protocol, "protocol", VALID_PROTOCOLS, ('grandtest',))

        # checks client identity validity
        VALID_CLIENTS = [k.id for k in self.clients()]
        clients = self.check_parameters_for_validity(clients, "client", VALID_CLIENTS, None)

        # checks if the device is valid
        VALID_DEVICES = self.devices()
        recording_devices = self.check_parameters_for_validity(recording_devices, "recording_device", VALID_DEVICES, None)

        # checks if the device is valid
        VALID_SESSIONS = self.sessions()
        sessions = self.check_parameters_for_validity(sessions, "session", VALID_SESSIONS, None)

        # now query the database
        retval = []

        # first, check the real data
        purpose = ('real',)
        if 'real' in cls:  # if we need enroll data (a small subset of real data)
            # init the query
            q = self.session.query(File).join(ProtocolFiles).join((Protocol, ProtocolFiles.protocol)).join(Client)
            if groups: q = q.filter(Client.set.in_(groups))
            if clients: q = q.filter(Client.id.in_(clients))
            if gender: q = q.filter(Client.gender.in_(gender))
            if recording_devices: q = q.filter(File.recording_device.in_(recording_devices))
            if sessions: q = q.filter(File.session.in_(sessions))
            q = q.filter(File.purpose.in_(purpose))
            q = q.filter(Protocol.name.in_(protocol))
            q = q.order_by(File.path)
            retval += list(q)

        if 'enroll' in cls:  # if we need enroll data (a small subset of real data)
            # init the query
            q = self.session.query(File).join(ProtocolFiles).join((Protocol, ProtocolFiles.protocol)).join(Client)
            from sqlalchemy import and_
            # only data from sess1 and laptop is in enrollment
            q = q.filter(and_(File.recording_device == 'laptop', File.session == 'sess1'))
            if groups: q = q.filter(Client.set.in_(groups))
            if clients: q = q.filter(Client.id.in_(clients))
            if gender: q = q.filter(Client.gender.in_(gender))
            if recording_devices: q = q.filter(File.recording_device.in_(recording_devices))
            if sessions: q = q.filter(File.session.in_(sessions))
            q = q.filter(File.purpose.in_(purpose))
            q = q.filter(Protocol.name.in_(protocol))
            q = q.order_by(File.path)
            retval += list(q)

        if 'probe' in cls:  # if we need probe data (a large subset of real data)
            # init the query
            q = self.session.query(File).join(ProtocolFiles).join((Protocol, ProtocolFiles.protocol)).join(Client)
            from sqlalchemy import or_
            # all data except the one from sess1 and laptop
            q = q.filter(or_(File.recording_device != 'laptop', File.session != 'sess1'))
            if groups: q = q.filter(Client.set.in_(groups))
            if clients: q = q.filter(Client.id.in_(clients))
            if gender: q = q.filter(Client.gender.in_(gender))
            if recording_devices: q = q.filter(File.recording_device.in_(recording_devices))
            if sessions: q = q.filter(File.session.in_(sessions))
            q = q.filter(File.purpose.in_(purpose))
            q = q.filter(Protocol.name.in_(protocol))
            q = q.order_by(File.path)
            retval += list(q)

        if 'attack' in cls:
            purpose = ('attack',)
            # init the query
            q = self.session.query(File).join(ProtocolFiles).join((Protocol, ProtocolFiles.protocol)).join(Client)
            # if both enroll and probe data is requested, then do not do anything
            if groups: q = q.filter(Client.set.in_(groups))
            if clients: q = q.filter(Client.id.in_(clients))
            if gender: q = q.filter(Client.gender.in_(gender))
            if attack_type: q = q.filter(File.attack_type.in_(attack_type))
            if attack_devices: q = q.filter(File.attack_device.in_(attack_devices))
            if recording_devices: q = q.filter(File.recording_device.in_(recording_devices))
            if sessions: q = q.filter(File.session.in_(sessions))
            q = q.filter(File.purpose.in_(purpose))
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
        for each file in the avspoof attack database. Conserve these numbers if you
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
            The groups to which the subjects attached to the models belong ('train', 'devel', 'eval')

        gender
            The gender to consider ('male', 'female')

        Returns: A list containing the ids of all models belonging to the given group.
        """
        if protocol == '.': protocol = None
        protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names(), None)
        groups = self.check_parameters_for_validity(groups, "group", self.groups(), self.groups())
        gender = self.check_parameters_for_validity(gender, "gender", self.genders(), None)

        retval = []
        if groups:
            q = self.session.query(Client).filter(Client.set.in_(groups))
            if gender:
                q = q.filter(Client.gender.in_(gender))
            q = q.order_by(Client.id)
            retval += list(q)

        return retval

    def has_client_id(self, id):
        """Returns True if we have a client with a certain integer identifier"""

        self.assert_validity()
        return self.session.query(Client).filter(Client.id == id).count() != 0

    def client(self, id):
        """Returns the Client object in the database given a certain id. Raises
        an error if that does not exist."""

        return self.session.query(Client).filter(Client.id == id).one()

    def protocols(self):
        """Returns all protocol objects.
        """

        self.assert_validity()
        return list(self.session.query(Protocol))

    def protocol_names(self):
        """Returns all registered protocol names"""

        l = self.protocols()
        retval = [str(k.name) for k in l]
        return retval

    def has_protocol(self, name):
        """Tells if a certain protocol is available"""

        self.assert_validity()
        return self.session.query(Protocol).filter(Protocol.name == name).count() != 0

    def protocol(self, name):
        """Returns the protocol object in the database given a certain name. Raises
        an error if that does not exist."""

        self.assert_validity()
        return self.session.query(Protocol).filter(Protocol.name == name).one()

    def groups(self):
        """Returns the names of all registered groups"""

        return Client.set_choices

    def genders(self):
        """Returns the list of genders"""

        return Client.gender_choices

    def devices(self):
        """Returns devices used in the database"""

        return File.recording_device_choices

    def sessions(self):
        """Returns sessions used in the database"""

        return File.session_choices

    def attack_types(self):
        """Returns attack supports available in the database"""

        return File.attack_type_choices

    def attack_devices(self):
        """Returns attack devices available in the database"""

        return File.attack_device_choices

    def file_speech(self):
        """Returns attack sample types available in the database"""

        return File.speech_choices

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

        fobj = self.session.query(File).filter(File.id.in_(ids))
        retval = []
        for p in ids:
            retval.extend([k.make_path(prefix, suffix) for k in fobj if k.id == p])
        return retval

    def reverse(self, paths):
        """Reverses the lookup: from certain stems, returning file ids

        Keyword Parameters:

        paths
            The filename stems I'll query for. This object should be a python
            iterable (such as a tuple or list)

        Returns a list (that may be empty).
        """

        self.assert_validity()

        fobj = self.session.query(File).filter(File.path.in_(paths))
        retval = []
        for p in paths:
            retval.extend([k.id for k in fobj if k.path == p])
        return retval

    def save_one(self, id, obj, directory, extension):
        """Saves a single object supporting the bob save() protocol.

        .. deprecated:: 1.1.0

            This function is *deprecated*, use :py:meth:`.File.save()` instead.

        This method will call save() on the the given object using the correct
        database filename stem for the given id.

        Keyword Parameters:

        id
            The id of the object in the database table "file".

        obj
            The object that needs to be saved, respecting the bob save() protocol.

        directory
            This is the base directory to which you want to save the data. The
            directory is tested for existence and created if it is not there with
            os.makedirs()

        extension
            The extension determines the way each of the arrays will be saved.
        """

        import warnings
        warnings.warn(
            "The method Database.save_one() is deprecated, use the File object directly as returned by Database.objects() for more powerful object manipulation.",
            DeprecationWarning)

        self.assert_validity()

        fobj = self.session.query(File).filter_by(id=id).one()

        fullpath = os.path.join(directory, str(fobj.path) + extension)
        fulldir = os.path.dirname(fullpath)
        utils.makedirs_safe(fulldir)

        from bob.io.base import save

        save(obj, fullpath)

    def save(self, data, directory, extension):
        """This method takes a dictionary of blitz arrays or bob.database.Array's
        and saves the data respecting the original arrangement as returned by
        files().

        .. deprecated:: 1.1.0

            This function is *deprecated*, use :py:meth:`.File.save()` instead.

        Keyword Parameters:

        data
            A dictionary with two keys 'real', 'attack', and 'enroll', each containing a
            dictionary mapping file ids from the original database to an object that
            supports the bob "save()" protocol.

        directory
            This is the base directory to which you want to save the data. The
            directory is tested for existence and created if it is not there with
            os.makedirs()

        extension
            The extension determines the way each of the arrays will be saved.
        """

        import warnings
        warnings.warn(
            "The method Database.save() is deprecated, use the File object directly as returned by Database.objects() for more powerful object manipulation.",
            DeprecationWarning)

        for key, value in data:
            self.save_one(key, value, directory, extension)

    def check_parameters_for_validity(self, parameters, parameter_description, valid_parameters,
                                      default_parameters=None):
        """Checks the given parameters for validity, i.e., if they are contained in the set of valid parameters.
        It also assures that the parameters form a tuple or a list.
        If parameters is 'None' or empty, the default_parameters will be returned (if default_parameters is omitted, all valid_parameters are returned).
        This function will return a tuple or list of parameters, or raise a ValueError.

        Keyword parameters:

        parameters : str, [str] or None
            The parameters to be checked.
            Might be a string, a list/tuple of strings, or None.

        parameter_description : str
            A short description of the parameter.
            This will be used to raise an exception in case the parameter is not valid.

        valid_parameters : [str]
            A list/tuple of valid values for the parameters.
            default_parameters : [str] or None

        default_parameters : [str] or None
            The list/tuple of default parameters that will be returned in case parameters is None or empty.
            If omitted, all valid_parameters are used.
        """
        if parameters is None or parameters == '':
            # parameters are not specified, i.e., 'None' or empty lists
            return default_parameters
            #if default_parameters is not None else valid_parameters

        if not isinstance(parameters, (list, tuple, set)):
            # parameter is just a single element, not a tuple or list -> transform it into a tuple
            parameters = (parameters,)

        # perform the checks
        for parameter in parameters:
            if parameter not in valid_parameters:
                raise ValueError("Invalid %s '%s'. Valid values are %s, or lists/tuples of those" % (
                parameter_description, parameter, valid_parameters))

        # check passed, now return the list/tuple of parameters
        return parameters

    def check_parameter_for_validity(self, parameter, parameter_description, valid_parameters, default_parameter=None):
        """
        Checks the given parameter for validity, i.e., if it is contained in the set of valid parameters.
        If the parameter is 'None' or empty, the default_parameter will be returned, in case it is specified, otherwise a ValueError will be raised.
        This function will return the parameter after the check tuple or list of parameters, or raise a ValueError.

        Keyword parameters:

        parameter : str
            The single parameter to be checked.
            Might be a string or None.

        parameter_description : str
            A short description of the parameter.
            This will be used to raise an exception in case the parameter is not valid.

        valid_parameters : [str]
            A list/tuple of valid values for the parameters.

        default_parameters : [str] or None
            The default parameter that will be returned in case parameter is None or empty.
            If omitted and parameter is empty, a ValueError is raised.
        """
        if parameter is None:
            # parameter not specified ...
            if default_parameter is not None:
                # ... -> use default parameter
                parameter = default_parameter
            else:
                # ... -> raise an exception
                raise ValueError(
                    "The %s has to be one of %s, it might not be 'None'." % (parameter_description, valid_parameters))

        if isinstance(parameter, (list, tuple, set)):
            # the parameter is in a list/tuple ...
            if len(parameter) > 1:
                raise ValueError("The %s has to be one of %s, it might not be more than one (%s was given)." % (
                parameter_description, valid_parameters, parameter))
            # ... -> we take the first one
            parameter = parameter[0]

        # perform the check
        if parameter not in valid_parameters:
            raise ValueError("The given %s '%s' is not allowed. Please choose one of %s." % (
            parameter_description, parameter, valid_parameters))

        # tests passed -> return the parameter
        return parameter
