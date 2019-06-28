from .openbis_object import OpenBisObject 
from .utils import VERBOSE
from .property import PropertyHolder, PropertyAssignments
from .attribute import AttrHolder
import json

class Material(OpenBisObject):
    """ Managing openBIS materials
    """

    def __init__(self, openbis_obj, type, data=None, props=None, **kwargs):
        self.__dict__['entity'] = 'Material'
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['type'] = type
        self.__dict__['p'] = PropertyHolder(openbis_obj, type)
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Material', type)

        if data is not None:
            self._set_data(data)

        if props is not None:
            for key in props:
                setattr(self.p, key, props[key])

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])


    def __dir__(self):
        return [
            'code','description',
            'set_tags()', 'add_tags()', 'del_tags()'
        ]


    def save(self):
        for prop_name, prop in self.props._property_names.items():
            if prop['mandatory']:
                if getattr(self.props, prop_name) is None or getattr(self.props, prop_name) == "":
                    raise ValueError("Property '{}' is mandatory and must not be None".format(prop_name))

        props = self.p._all_props()

        if self.is_new:
            request = self._new_attrs()
            request["params"][1][0]["properties"] = props
            resp = self.openbis._post_request(self.openbis.as_v3, request)

            if VERBOSE: print("Material successfully created.")
            new_material_data = self.openbis.get_tag(resp[0]['permId'], only_data=True)
            self._set_data(new_material_data)
            return self

        else:
            request = self._up_attrs()
            request["params"][1][0]["properties"] = props
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Material successfully updated.")
            new_material_data = self.openbis.get_tag(self.permId, only_data=True)
            self._set_data(new_material_data)


    def delete(self, reason='no reason'):
        self.openbis.delete_entity(entity=self.entity,id=self.permId, reason=reason)
        if VERBOSE: print("Material {} successfully deleted.".format(self.permId))

