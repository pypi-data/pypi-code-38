try:
    Text = basestring
except NameError:
    Text = (str, bytes)

NULL_FIELD = object()


class BatchHandler(object):
    """Simple enclosure for the batch operations ContextManager."""
    def __init__(self, parent_jobhandler):
        self._h = parent_jobhandler

    def __enter__(self):
        self._h._defer_write = True
        return self._h

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Only do something if the handler and its DataStorage object
        # are ready (i.e. not closed)
        if self._h._closed:
            raise ConnectionError("The handler has already been closed")
        else:
            self._h._defer_write = False
            self._h.write_all()


class JobHandler(object):
    """The elemental job handler, typically reused by a single job."""
    def __init__(self, datastorage, jobid):
        self._id = jobid
        self._data = datastorage
        self._inmemory_objects = dict()
        self.batch = BatchHandler(self)
        self._defer_write = False
        self._closed = False

    def __delitem__(self, key):
        if not isinstance(key, Text):
            raise ValueError("Field names must be strings")
        self._inmemory_objects[key] = None
        if not self._defer_write:
            self._data.set_value(self._id, key, None, raw_parameter=True)

    def __getitem__(self, item):
        if not isinstance(item, Text):
            raise ValueError("Field names must be strings")

        try:
            data = self._inmemory_objects[item]
        except KeyError:
            data = self._data.get_value(self._id, item)
            self._inmemory_objects[item] = data

        if data is NULL_FIELD:
            raise KeyError("Field %s is NULL" % item)
        else:
            return data

    def __setitem__(self, key, value):
        if not isinstance(key, Text):
            raise ValueError("Field names must be strings")

        self._data.set_value(self._id, key, value)
        self._inmemory_objects[key] = value

    def __contains__(self, item):
        if not isinstance(item, Text):
            raise ValueError("Field names must be strings")

        try:
            value = self._inmemory_objects[item]
            return value is not NULL_FIELD
        except KeyError:
            # No need to transform, just check if it is set
            return self._data.get_value(self._id, item, raw_return=True) is not NULL_FIELD

    def get(self, item, default=None):
        try:
            return self.__getitem__(item)
        except KeyError:
            return default

    def setdefault(self, item, default=None):
        # does a get, and stores it **if it is not null**
        # Note the difference between being None (a valid Python value)
        # or being NULL (equivalent to a KeyError)
        try:
            return self.__getitem__(item)
        except KeyError:
            self._inmemory_objects[item] = default
            if not self._defer_write:
                self._data.set_value(self._id, item, default)
            return default

    def write_all(self):
        if self._closed:
            raise ConnectionError("This handler has already been closed")
        self._data.set_values(self._id,
                              self._inmemory_objects.keys(),
                              self._inmemory_objects.values())

    def close(self):
        if not self._closed:
            self._defer_write = True
            self.write_all()
            self._closed = True

    def __del__(self):
        if not self._closed:
            self.close()
