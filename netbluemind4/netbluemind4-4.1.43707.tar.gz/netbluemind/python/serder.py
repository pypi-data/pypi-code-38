import base64
from base64 import b64decode
from base64 import b64encode
from  datetime import datetime

class ByteArraySerDer:

    @classmethod
    def parse(cls, value):
        if value == None:
            return None
        else:
            return b64decode(value)

    @classmethod
    def encode(cls, value):
        if value == None:
            return None
        else:
            return b64encode(value)

class STRING:

    @classmethod
    def parse(cls, value):
        return value

    @classmethod
    def encode(cls, value):
        return value

class STREAM:

    @classmethod
    def parse(cls, value):
        return value

    @classmethod
    def encode(cls, value):
        return value

class LONG:

    @classmethod
    def parse(cls, value):
        return value

    @classmethod
    def encode(cls, value):
        return value


class DOUBLE:

    @classmethod
    def parse(cls, value):
        return value

    @classmethod
    def encode(cls, value):
        return value


class INT:

    @classmethod
    def parse(cls, value):
        return value

    @classmethod
    def encode(cls, value):
        return value

class DATE:

    @classmethod
    def parse(cls, value):
        if value == None:
            return None
        else:
            return datetime.fromtimestamp(value/1000)

    @classmethod
    def encode(cls, value):
        if value == None:
            return None
        else:
            return int((value - datetime(1970, 1, 1)).total_seconds() * 1000)

class BOOLEAN:

    @classmethod
    def parse(cls, value):
        return value

    @classmethod
    def encode(cls, value):
        return value

class VOID:

    @classmethod
    def parse(cls, value):
        return value

    @classmethod
    def encode(cls, value):
        return value

class MapSerDer:
    def __init__(self, serder):
        self.serder = serder

    def parse(self, value):
        if value == None:
            return None

        ret = dict()
        for v in value.keys():
            ret[v] = self.serder.parse( value[v] )
        return ret


    def encode(self, value):
        if value == None:
            return None

        ret = dict()
        for v in value.keys():
            ret[v] = self.serder.encode( value[v] )
        return ret


class CollectionSerDer:
    def __init__(self, serder):
        self.serder = serder


    def parse(self, value):
        if value == None:
            return None

        ret = []
        for v in value:
            ret.append( self.serder.parse( v) )
        return ret

    def encode(self, value):
        if value == None:
            return None

        ret = []
        for v in value:
            ret.append( self.serder.encode( v) )
        return ret

class ListSerDer:
    def __init__(self, serder):
        self.serder = serder

    def parse(self, value):
        if value == None:
            return None

        ret = []
        for v in value:
            ret.append( self.serder.parse( v) )
        return ret

    def encode(self, value):
        if value == None:
            return None

        ret = []
        for v in value:
            ret.append( self.serder.encode( v) )
        return ret

class ArraySerDer:
    def __init__(self, serder):
        self.serder = serder

    def parse(self, value):
        if value == None:
            return None

        ret = []
        for v in value:
            ret.append( self.serder.parse( v) )
        return ret

    def encode(self, value):
        if value == None:
            return None

        ret = []
        for v in value:
            ret.append( self.serder.encode( v) )
        return ret


class SetSerDer:
    def __init__(self, serder):
        self.serder = serder

    def parse(self, value):
        if value == None:
            return None

        ret = []
        for v in value:
            ret.append( self.serder.parse( v) )
        return ret

    def encode(self, value):
        if value == None:
            return None

        ret = []
        for v in value:
            ret.append( self.serder.encode( v) )
        return ret
