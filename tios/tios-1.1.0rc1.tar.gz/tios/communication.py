from __future__ import print_function
from bson.binary import Binary
import pickle
import zlib
import sys
import pymongo

from tios import environments
'''
The Tios communication module.

This module provides the generalised API for communication between the
simulation and the database.
'''

python3 = sys.version_info[0] == 3
def select(protocol, id):
    """
    Select the connection protocol.

    Args:
        protocol (str): The protocol to use. Currently only the options
            "Dummy" and "Mongo" are recognised.
        id (str): The ID of the entry

    Returns:
        connection (class TiosConnection): an instance of a `TiosConnection` 
            with "get", "put" methods, etc.
    """
    if protocol == 'Dummy':
        return DummyConnection(id)
    elif protocol == 'Mongo':
        return MongoConnection(id)
    else:
        raise ValueError('Error: protocol {} is not supported'.format(protocol))

class TiosConnection(object):
    """
    Base class for the database connection layer in Tios.
    """

    def __init__(self, id):
        self.id = id
        self.access = 'rw'

    def put(self, updates):
        """
        Update entry with data from the dictionary `updates`.

        Args:
            updates (dict): Dictionary of keys and values to be updated

        """
        raise NotImplementedError

    def get(self, key):
        """
        Returns the item with the given `key`.

        Args:
            key (str): Key of the Tios entry item to retrieve

        Returns:
            value: The value of the `key`, in whatever type is appropriate

        """
        raise NotImplementedError

    def has_entry(self):
        """
        Tests if the database has entry.

        Returns:
            is_present (bool): ``True`` if the id is found, otherwise ``False``
        """
        raise NotImplementedError

    def add_entry(self):
        """
        Create a new database record 

        """
        raise NotImplementedError

    def delete_entry(self):
        """
        Remove record from the database

        """
        raise NotImplementedError


class DummyConnection(TiosConnection):
    """
    A dummy connection object for testing purposes.
    """
    def __init__(self, id):
        self.id = None
        self._id = id
        self.data = {}
        self.access = 'rw'

    def put(self, updates):
        for key in updates:
            self.data[key] = updates[key]

    def get(self, key):
        return self.data[key]

    def has_entry(self):
        return self.id != None

    def add_entry(self):
        self.id = self._id

    def delete_entry(self):
        self.id = None

class MongoConnection(TiosConnection):
    """
    A Mongo-based connection object.
    """
    def __init__(self, id):

        self.id = id
        self.access = 'r'
        self.env = environments.load_mongo_env()
        self.collection = self.env['COLLECTION']
        if self.has_entry():
            self.access = 'rw'
        else:
            coll_names = [c for c in self.collection.database.list_collection_names()]
            for c in coll_names:
                self.collection = self.collection.database[c]
                if self.has_entry():
                    self.access = 'r'
                    break
               
            if not self.has_entry():
                self.collection = self.env['COLLECTION']
                self.access = 'rw'

    def put(self, updates):
        if updates is None:
            return
        if not 'w' in self.access:
            raise IOError('Error: you do not have write access to this entry')
        success = False
        while not success:
            try:
                result = self.collection.update_one(
                    {"id" : self.id},
                    {
                        "$set" : updates,
                        "$currentDate" : {"last_update" : True}
                    }
                )
                success = True
            except pymongo.errors.AutoReconnect:
                pass
        if result.matched_count != 1:
            print('Warning: TiosConnection.put(): update failed')

    def get(self, key):
        success = False
        while not success:
            try:
                result = self.collection.find_one(
                    {"id" : self.id},
                    projection=[key]
                )
                success = True
            except pymongo.errors.AutoReconnect:
                pass
        return result.get(key)

    def has_entry(self):
        success = False
        while not success:
            try:
                result = self.collection.find_one({'id': self.id}, 
                                                projection=['id']) is not None
                success = True
            except pymongo.errors.AutoReconnect:
                pass
        return result

    def add_entry(self):
        if not 'w' in self.access:
            raise IOError('Error: you do not have write access to this entry')
        data = {"id" : self.id}
        success = False
        while not success:
            try:
                self.collection.insert_one(data)
                success = True
            except pymongo.errors.AutoReconnect:
                pass

    def delete_entry(self):
        if not 'w' in self.access:
            raise IOError('Error: yYou do not have write access to this entry')
        success = False
        while not success:
            try:
                result = self.collection.delete_one({"id" : self.id})
                success = True
            except pymongo.errors.AutoReconnect:
                pass

class TiosAgent(object):
    """
    Class that provides a local interface to the tios data model.
    """
    def __init__(self, id, protocol='Mongo', new=False):
        """
        Create a local interface to an entry in the remote Tios datastore.

        Args:
            id (str): Tios entry id/code
            protocol (str, optional): The communication protocol. 
                Default is "Mongo".
            new (bool, optional): If True a new entry is created.

        Returns:
            agent (class TiosAgent): an object with properties to set and get 
                each key in the associated database entry.

        Raises:
            ValueError: If `new` is False and `id` does not already exist, or
                if `new` is True and `id` already exists.

        """
        self.data_connection = select(protocol, id)
        if new:
            if self.data_connection.has_entry():
                raise ValueError('Error: this entry already exists')
            else:
                self.data_connection.add_entry()
        else:
            if not self.data_connection.has_entry():
                raise ValueError('Error: this entry does not exist')
        self.id = id
        self.updates = {}
        self._title = None
        self._timepoint = None
        self._last_update = None
        self._status = None
        self._message = None
        self._md_code = None
        self._md_version = None
        self._host = None
        self._username = None
        self._trate = None
        self._frame_rate = None
        self._filepack = None
        self._checkpoint = None
        self._checkpoint_time = None
        self._splitpoint = None
        self._pdb = None
        self._box = None
        self._xyzsel = None
        self._xyzunsel = None
        self._monitors = None

    def inspect(self):
        """
        For debugging: report on what;s due to be synchronised.
        """
        for key in self.updates:
            value = self.updates[key]
            print('key={}, type={}, size={}'.format(key, type(value), sys.getsizeof(value)))

    def sync(self):
        """
        Synchronise updates to the local data object with the remote database
        """
        if len(self.updates.keys()) > 0:
            self.data_connection.put(self.updates)
        self.updates = {}

    @property
    def title(self):
        """
        String giving the user-supplied title for this Tios simulation.
        """
        self._title = self.data_connection.get('title')
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.updates['title'] = value

    @property
    def timepoint(self):
        """
        Float giving the age of the simulation (in picoseconds).
        """
        self._timepoint = self.data_connection.get('timepoint')
        return self._timepoint

    @timepoint.setter
    def timepoint(self, value):
        self._timepoint = value
        self.updates['timepoint'] = value

    @property
    def checkpoint_time(self):
        """
        Float giving the age of the checkpoint (in picoseconds).
        """
        self._checkpoint_time = self.data_connection.get('checkpoint_time')
        return self._checkpoint_time

    @checkpoint_time.setter
    def checkpoint_time(self, value):
        self._checkpoint_time = value
        self.updates['checkpoint_time'] = value

    @property
    def last_update(self):
        """
        Time-stamp of the last update to the remote database.
        """
        self._last_update = self.data_connection.get('last_update')
        return self._last_update

    @last_update.setter
    def last_update(self, value):
        self._last_update = value
        self.updates['last_update'] = value

    @property
    def status(self):
        """
        String giving the current status of the Tios simulation.
        """
        self._status = self.data_connection.get('status')
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        self.updates['status'] = value

    @property
    def message(self):
        """
        Dictionary to send messages to and from a running simulation.
        """
        self._message = self.data_connection.get('message')
        return self._message

    @message.setter
    def message(self, value):
        self._message = value
        self.updates['message'] = value

    @property
    def md_code(self):
        """
        String defining the MD code: "GROMACS", "NAMD", etc.
        """
        self._md_code = self.data_connection.get('md_code')
        return self._md_code

    @md_code.setter
    def md_code(self, value):
        self._md_code = value
        self.updates['md_code'] = value

    @property
    def md_version(self):
        """
        String defining the version of the MD code in current/last use.
        """
        self._md_version = self.data_connection.get('md_version')
        return self._md_version

    @md_version.setter
    def md_version(self, value):
        self._md_version = value
        self.updates['md_version'] = value

    @property
    def host(self):
        """
        String giving the current or most recent hostname for the simulation.
        """
        self._host = self.data_connection.get('host')
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        self.updates['host'] = value

    @property
    def username(self):
        """
        String with the current/most recent username running the simulation.
        """
        self._username = self.data_connection.get('username')
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
        self.updates['username'] = value

    @property
    def trate(self):
        """
        Float giving the interval between IMD samples (in picoseconds).
        """
        self._trate = self.data_connection.get('trate')
        return self._trate

    @trate.setter
    def trate(self, value):
        self._trate = value
        self.updates['trate'] = value

    @property
    def frame_rate(self):
        """
        Float giving the current/most recent number of IMD frames per minute.
        """
        self._frame_rate = self.data_connection.get('frame_rate')
        return self._frame_rate

    @frame_rate.setter
    def frame_rate(self, value):
        self._frame_rate = value
        self.updates['frame_rate'] = value

    @property
    def filepack(self):
        """
        A dictionary of ``{filename : filecontents}`` pairs of input files.
        """
        if python3:
            self._filepack = pickle.loads(self.data_connection.get('filepack'), encoding='latin1')
        else:
            self._filepack = pickle.loads(self.data_connection.get('filepack'))
        return self._filepack

    @filepack.setter
    def filepack(self, value):
        self._filepack = value
        self.updates['filepack'] = Binary(pickle.dumps(value))

    @property
    def checkpoint(self):
        """
        A MD-code specific checkpoint object.
        """
        self._checkpoint = self.data_connection.get('checkpoint')
        if self._checkpoint is not None:
            if python3:
                self._checkpoint = pickle.loads(self._checkpoint, encoding='latin1')
            else:
                self._checkpoint = pickle.loads(self._checkpoint)
        return self._checkpoint

    @checkpoint.setter
    def checkpoint(self, value):
        self._checkpoint = value
        if value is None:
            self.updates['checkpoint'] = value
        else:
            self.updates['checkpoint'] = Binary(pickle.dumps(value))

    @property
    def splitpoint(self):
        """
        The number of atoms in the first subset of coordinates, typically
        the most interesting, solute, ones..
        """
        self._splitpoint = self.data_connection.get('splitpoint')
        return self._splitpoint

    @splitpoint.setter
    def splitpoint(self, value):
        self._splitpoint = value
        self.updates['splitpoint'] = value

    @property
    def box(self):
        """
        A numpy array of floats with the periodic box information.
        """
        result = self.data_connection.get('box')
        if result is None:
            self._box = None
        else:
            if python3:
                self._box = pickle.loads(result, encoding='latin1')
            else:
                self._box = pickle.loads(result)
        return self._box

    @box.setter
    def box(self, value):
        self._box = value
        if value is None:
            self.updates['box'] = value
        else:
            self.updates['box'] = Binary(pickle.dumps(value))

    @property
    def pdb(self):
        """
        A string representation of a pdb file for the system
        """ 
        if python3:
            self._pdb = pickle.loads(zlib.decompress(self.data_connection.get('pdb')), encoding='latin1')
        else:
            self._pdb = pickle.loads(zlib.decompress(self.data_connection.get('pdb')))
        return self._pdb

    @pdb.setter
    def pdb(self, value):
        self._pdb = value
        self.updates['pdb'] = Binary(zlib.compress(pickle.dumps(value)))

    @property
    def xyzsel(self):
        """
        A numpy array of floats with the coordinates of the selected subset
        """ 
        if python3:
            self._xyzsel = pickle.loads(zlib.decompress(self.data_connection.get('xyzsel')), encoding='latin1')
        else:
            self._xyzsel = pickle.loads(zlib.decompress(self.data_connection.get('xyzsel')))
        return self._xyzsel

    @xyzsel.setter
    def xyzsel(self, value):
        self._xyzsel = value
        self.updates['xyzsel'] = Binary(zlib.compress(pickle.dumps(value)))

    @property
    def xyzunsel(self):
        """
        A numpy array of floats with the coordinates of non-selected atoms.
        """
        if python3:
            self._xyzunsel = pickle.loads(zlib.decompress(self.data_connection.get('xyzunsel')), encoding='latin1')
        else:
            self._xyzunsel = pickle.loads(zlib.decompress(self.data_connection.get('xyzunsel')))
        return self._xyzunsel

    @xyzunsel.setter
    def xyzunsel(self, value):
        self._xyzunsel = value
        self.updates['xyzunsel'] = Binary(zlib.compress(pickle.dumps(value)))

    @property
    def monitors(self):
        """
        A dictionary of simulation metrics
        """
        if python3:
            self._monitors = pickle.loads(self.data_connection.get('monitors'), encoding='latin1')
        else:
            self._monitors = pickle.loads(self.data_connection.get('monitors'))
        return self._monitors

    @monitors.setter
    def monitors(self, value):
        self._monitors = value
        self.updates['monitors'] = Binary(pickle.dumps(value))

