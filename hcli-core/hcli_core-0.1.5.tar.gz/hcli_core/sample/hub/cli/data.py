import json
import os

try:
        from types import SimpleNamespace as Namespace
except ImportError:
        # Python 2.x fallback
        from argparse import Namespace

class DAO:
    path = os.path.dirname(__file__)
    
    """ Adds an object's attributes verbatim to a resource """
    def __init__(self, model=None):
        if model is not None:
            for key, value in vars(model).items():
                setattr(self, key, value)

    """ Serializes an inherently well structured haliot resource to application/hal+json """
    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
                          sort_keys=True,
                          indent=4)

    def exists(self):
        if not os.path.exists(self.path + "/hub.json"):
            return False
        else:
            return True

    def save(self):
        with open(self.path + "/hub.json", "w") as f:
            f.write(self.serialize())
            f.close()

    def load(self, obj):
        with open(self.path + "/hub.json", "r") as f:
            j = f.read()
            f.close()
            obj.__dict__ = json.loads(j)
