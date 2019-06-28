from .openbis_object import OpenBisObject 
from .utils import VERBOSE
from .attribute import AttrHolder
import json

class Tag(OpenBisObject):
    """ 
    """

    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['entity'] = 'Tag'
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['a'] = AttrHolder(openbis_obj, self.entity)

        if data is not None:
            self._set_data(data)

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __dir__(self):
        return [
            'code','description',
            'get_samples()',
            'get_experiments()',
            'get_materials()',
            'owner()',
        ]

    def delete(self, reason='no reason'):
        self.openbis.delete_entity(entity=self.entity,id=self.permId, reason=reason)
        if VERBOSE: print("Tag {} successfully deleted.".format(self.permId))

    def save(self):

        if self.is_new:
            request = self._new_attrs()
            resp = self.openbis._post_request(self.openbis.as_v3, request)

            if VERBOSE: print("Tag successfully created.")
            new_tag_data = self.openbis.get_tag(resp[0]['permId'], only_data=True)
            self._set_data(new_tag_data)
            return self

        else:
            request = self._up_attrs()
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Tag successfully updated.")
            new_tag_data = self.openbis.get_tag(self.permId, only_data=True)
            self._set_data(new_tag_data)

    def get_samples(self):
        return self.openbis.get_samples(tags=[self.code])
        #raise ValueError('not yet implemented')

    def get_experiments(self):
        return self.openbis.get_experiments(tags=[self.code])

    def get_materials(self):
        raise ValueError('not yet implemented')

