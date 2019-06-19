import json

class Serializer():
    '''
    Serializes all return values, can be replace with own Serializer
    '''
    def serialize(self, object):
        return json.dumps(object)
