from .property import PropertyHolder
from .attribute import AttrHolder
from .openbis_object import OpenBisObject 
from .definitions import openbis_definitions
from .utils import VERBOSE

class Experiment(OpenBisObject):
    """ 
    """

    def __init__(self, openbis_obj, type, project=None, data=None, props=None, code=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['type'] = type
        ph = PropertyHolder(openbis_obj, type)
        self.__dict__['p'] = ph
        self.__dict__['props'] = ph
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Experiment', type)

        if data is not None:
            self._set_data(data)

        if project is not None:
            setattr(self, 'project', project)

        if props is not None:
            for key in props:
                setattr(self.p, key, props[key])

        if code is not None:
            self.code = code

        if kwargs is not None:
            defs = openbis_definitions('Experiment')
            for key in kwargs:
                if key in defs['attrs']:
                    setattr(self, key, kwargs[key])
                else:
                    raise ValueError("{attr} is not a known attribute for an Experiment".format(attr=key))


    def _set_data(self, data):
        # assign the attribute data to self.a by calling it
        # (invoking the AttrHolder.__call__ function)
        self.a(data)
        self.__dict__['data'] = data

        # put the properties in the self.p namespace (without checking them)
        for key, value in data['properties'].items():
            self.p.__dict__[key.lower()] = value

    def __str__(self):
        return self.data['code']

    def __dir__(self):
        # the list of possible methods/attributes displayed
        # when invoking TAB-completition
        return [
            'code', 'permId', 'identifier',
            'type', 'project',
            'props.', 
            'project', 'tags', 'attachments', 'data',
            'get_datasets()', 'get_samples()',
            'set_tags()', 'add_tags()', 'del_tags()',
            'add_attachment()', 'get_attachments()', 'download_attachments()',
            'save()'
        ]

    @property
    def type(self):
        return self.__dict__['type']

    @type.setter
    def type(self, type_name):
        experiment_type = self.openbis.get_experiment_type(type_name)
        self.p.__dict__['_type'] = experiment_type
        self.a.__dict__['_type'] = experiment_type

    def __getattr__(self, name):
        return getattr(self.__dict__['a'], name)

    def __setattr__(self, name, value):
        if name in ['set_properties', 'add_tags()', 'del_tags()', 'set_tags()']:
            raise ValueError("These are methods which should not be overwritten")

        setattr(self.__dict__['a'], name, value)

    def _repr_html_(self):
        html = self.a._repr_html_()
        return html

    def set_properties(self, properties):
        for prop in properties.keys():
            setattr(self.p, prop, properties[prop])

    set_props = set_properties

    def save(self):
        for prop_name, prop in self.props._property_names.items():
            if prop['mandatory']:
                if getattr(self.props, prop_name) is None or getattr(self.props, prop_name) == "":
                    raise ValueError("Property '{}' is mandatory and must not be None".format(prop_name))

        if self.is_new:
            request = self._new_attrs()
            props = self.p._all_props()
            request["params"][1][0]["properties"] = props
            resp = self.openbis._post_request(self.openbis.as_v3, request)

            if VERBOSE: print("Experiment successfully created.")
            new_exp_data = self.openbis.get_experiment(resp[0]['permId'], only_data=True)
            self._set_data(new_exp_data)
            return self
        else:
            request = self._up_attrs()
            props = self.p._all_props()
            request["params"][1][0]["properties"] = props
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Experiment successfully updated.")
            new_exp_data = self.openbis.get_experiment(self.permId, only_data=True)
            self._set_data(new_exp_data)

    def delete(self, reason):
        if self.permId is None:
            return None
        self.openbis.delete_entity(entity='Experiment', id=self.permId, reason=reason)
        if VERBOSE: print("Experiment {} successfully deleted.".format(self.permId))

    def get_datasets(self, **kwargs):
        if self.permId is None:
            return None
        return self.openbis.get_datasets(experiment=self.permId, **kwargs)

    def get_projects(self, **kwargs):
        if self.permId is None:
            return None
        return self.openbis.get_project(experiment=self.permId, **kwargs)

    def get_samples(self, **kwargs):
        if self.permId is None:
            return None
        return self.openbis.get_samples(experiment=self.permId, **kwargs)

    get_objects = get_samples # Alias

    def add_samples(self, *samples):

        for sample in samples:
            if isinstance(sample, str):
                obj = self.openbis.get_sample(sample)
            else:
                # we assume we got a sample object
                obj = sample

            # a sample can only belong to exactly one experiment
            if obj.experiment is not None:
                raise ValueError(
                    "sample {} already belongs to experiment {}".format(
                        obj.code, obj.experiment
                    )
                )
            else:
                if self.is_new:
                    raise ValueError("You need to save this experiment first before you can assign any samples to it")
                else:
                    # update the sample directly
                    obj.experiment = self.identifier
                    obj.save()
                    self.a.__dict__['_samples'].append(obj._identifier)

    add_objects = add_samples # Alias

    def del_samples(self, samples):
        if not isinstance(samples, list):
            samples = [samples]

        
        for sample in samples:
            if isinstance(sample, str):
                obj = self.openbis.get_sample(sample)
                objects.append(obj)
            else:
                # we assume we got an object
                objects.append(obj)
        
        self.samples = objects

    del_objects = del_samples # Alias

