import json
import pickle as pickle
import zlib


class CPickleSerializer(object):
    """ CPickleSerializer
    """

    @staticmethod
    def dumps(v):
        """ dumps value
        """
        return pickle.dumps(v)

    @staticmethod
    def loads(v):
        """ loads value
        """
        return pickle.loads(v)


class CompressedPickleSerializer(object):
    """ CompressedPickleSerializer
    """

    @staticmethod
    def dumps(v):
        """ dumps value
        """
        return zlib.compress(pickle.dumps(v))

    @staticmethod
    def loads(v):
        """ loads value
        """
        return pickle.loads(zlib.decompress(v))


class CompressedJsonSerializer(object):
    """ CompressedJsonSerializer
    """

    @staticmethod
    def dumps(v):
        """ dumps value
        """
        return zlib.compress(bytes(json.dumps(v), "utf-8"))

    @staticmethod
    def loads(v):
        """ loads value
        """
        return json.loads(zlib.decompress(v))


class CompressedStrSerializer(object):
    """ CompressedStrSerializer
    """

    @staticmethod
    def dumps(v):
        """ dumps value
        """
        if v is None:
            return None
        return zlib.compress(bytes(v, "utf-8"))

    @staticmethod
    def loads(v):
        """ loads value
        """
        if v is None:
            return None
        return zlib.decompress(v).decode("utf-8")
