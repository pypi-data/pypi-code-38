from .property import PropertyHolder
from .attribute import AttrHolder
from .openbis_object import OpenBisObject 
from .definitions import openbis_definitions
from .utils import VERBOSE

sample_definitions = openbis_definitions('Sample')

class Sample(OpenBisObject):
    """ A Sample is one of the most commonly used objects in openBIS.
    """

    def __init__(self, openbis_obj, type, project=None, data=None, props=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['type'] = type
        ph = PropertyHolder(openbis_obj, type)
        self.__dict__['p'] = ph
        self.__dict__['props'] = ph
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Sample', type)

        if data is not None:
            self._set_data(data)

        if project is not None:
            setattr(self, 'project', project)

        if props is not None:
            for key in props:
                setattr(self.p, key, props[key])

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

        if getattr(self, 'parents') is None:
            self.a.__dict__['_parents'] = []
        else:
            if not self.is_new:
                self.a.__dict__['_parents_orig'] = self.a.__dict__['_parents']

        if getattr(self, 'children') is None:
            self.a.__dict__['_children'] = []
        else:
            if not self.is_new:
                self.a.__dict__['_children_orig'] = self.a.__dict__['_children']

        if getattr(self, 'components') is None:
            self.a.__dict__['_components'] = []
        else:
            if not self.is_new:
                self.a.__dict__['_components_orig'] = self.a.__dict__['_components']


    def _set_data(self, data):
        # assign the attribute data to self.a by calling it
        # (invoking the AttrHolder.__call__ function)
        self.a(data)
        self.__dict__['data'] = data

        # put the properties in the self.p namespace (without checking them)
        for key, value in data['properties'].items():
            self.p.__dict__[key.lower()] = value


    def __dir__(self):
        return [
            'p', 'props', 
            'type',
            'get_parents()', 'get_children()', 'get_components()',
            'add_parents()', 'add_children()', 'add_components()', 
            'del_parents()', 'del_children()', 'del_components()',
            'set_parents()', 'set_children()', 'set_components()',
            'get_datasets()', 
            'space', 'project', 'experiment', 'container', 'tags',
            'set_tags()', 'add_tags()', 'del_tags()',
            'add_attachment()', 'get_attachments()', 'download_attachments()',
            'save()', 'delete()'
        ]


    def _container(self, value=None):
        if value is not None:
            if value == '':
                if self.is_new:
                    pass
                else:
                    self.a.__dict__['_container'] = {}
            else:
                obj = None
                if isinstance(value, str):
                    # fetch object in openBIS, make sure it actually exists
                    obj = getattr(self._openbis, "get_sample")(value)
                elif value is None:
                    self.a.__dict__['_container'] = {}
                else:
                    obj = value

                self.a.__dict__['_container'] = obj.data['identifier']

                # mark attribute as modified, if it's an existing entity
                if self.is_new:
                    pass
                else:
                    self.a.__dict__['_container']['isModified'] = True
        else:
            try:
                return self.openbis.get_sample(self.a._container['identifier'])
            except Exception:
                pass

    @property
    def type(self):
        return self.__dict__['type']

    @type.setter
    def type(self, type_name):
        sample_type = self.openbis.get_sample_type(type_name)
        self.p.__dict__['_type'] = sample_type
        self.a.__dict__['_type'] = sample_type

    def __getattr__(self, name):
        if name in ['container']:
            return getattr(self, "_"+name)()

        return getattr(self.__dict__['a'], name)

    def __setattr__(self, name, value):
        if name in ['set_properties', 'set_tags', 'add_tags']:
            raise ValueError("These are methods which should not be overwritten")

        if name in ['container']:
            return getattr(self, "_"+name)(value)

        # must be an attribute in the AttributeHolder class
        setattr(self.__dict__['a'], name, value)

    def _repr_html_(self):
        return self.a._repr_html_()

    def __repr__(self):
        return self.a.__repr__()

    def set_properties(self, properties):
        for prop in properties.keys():
            setattr(self.p, prop, properties[prop])

    set_props = set_properties

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

            if VERBOSE: print("Sample successfully created.")
            new_sample_data = self.openbis.get_sample(resp[0]['permId'], only_data=True)
            self._set_data(new_sample_data)
            return self

        else:
            request = self._up_attrs()
            request["params"][1][0]["properties"] = props
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Sample successfully updated.")
            new_sample_data = self.openbis.get_sample(self.permId, only_data=True)
            self._set_data(new_sample_data)

    def delete(self, reason):
        self.openbis.delete_entity(entity='Sample',id=self.permId, reason=reason)
        if VERBOSE: print("Sample {} successfully deleted.".format(self.permId))

    def get_datasets(self, **kwargs):
        return self.openbis.get_datasets(sample=self.permId, **kwargs)

    def get_projects(self, **kwargs):
        return self.openbis.get_project(withSamples=[self.permId], **kwargs)

    @property
    def experiment(self):
        try:
            return self.openbis.get_experiment(self._experiment['identifier'])
        except Exception:
            pass


