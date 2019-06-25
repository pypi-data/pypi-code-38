import copy
import abc


class Config(object):
    __metaclass__ = abc.ABCMeta

    type = abc.abstractproperty()
    fields = abc.abstractproperty()

    def to_dict(self):
        d = copy.deepcopy(self.__dict__)
        d["type"] = self.type
        return {k: v for k, v in d.items() if v is not None}

    @classmethod
    def make_config_from_dict(cls, conf):
        d = copy.deepcopy(conf)
        del d["type"]
        return cls(**d)

    @classmethod
    def is_valid_dict(cls, conf):
        error = None
        if conf is None:
            error = "empty config"
            return (False, error)
        if not isinstance(conf, dict):
            error = "config must be a dictionary"
            return (False, error)
        if "type" not in conf or conf["type"] != cls.type:
            error = "field 'type' must exist and be equal to '{}''".format(cls.type)
            return (False, error)
        for key in cls.fields:
            if key not in conf:
                error = "field '{}' not present".format(key)
                return (False, error)
        return (True, error)


class GlobalConfig(Config):

    fields = ["user_name", "email", "token"]
    type = "global"

    def __init__(self, user_name="", email="", token="", owner=None, **kwargs):
        self.user_name = user_name
        self.email = email
        self.token = token
        self.owner = owner
