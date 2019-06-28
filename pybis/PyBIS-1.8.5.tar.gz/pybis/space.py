from .attribute import AttrHolder
from .openbis_object import OpenBisObject 
from .utils import parse_jackson, check_datatype, split_identifier, format_timestamp, is_identifier, is_permid, nvl, VERBOSE


class Space(OpenBisObject):
    """ managing openBIS spaces
    """

    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Space' )

        if data is not None:
            self.a(data)
            self.__dict__['data'] = data

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __dir__(self):
        """all the available methods and attributes that should be displayed
        when using the autocompletion feature (TAB) in Jupyter
        """
        return [
            'code', 'permId', 'description', 'registrator', 'registrationDate', 'modificationDate', 
            'get_projects()', 
            "new_project(code='', description='', attachments)", 
            'get_samples()', 
            'delete()'
        ]

    def __str__(self):
        return self.data.get('code', None)

    def get_samples(self, **kwargs):
        return self.openbis.get_samples(space=self.code, **kwargs)

    get_objects = get_samples  # Alias

    def get_sample(self, sample_code, project_code=None):
        if is_identifier(sample_code) or is_permid(sample_code):
            return self.openbis.get_sample(sample_code)
        else:
            if project_code is None:
                return self.openbis.get_sample('/{}/{}'.format(self.code,sample_code) )
            else:
                return self.openbis.get_sample('/{}/{}/{}'.format(self.code, project_code, sample_code) )
    get_object = get_sample  # Alias


    def get_projects(self, **kwargs):
        return self.openbis.get_projects(space=self.code, **kwargs)

    def new_project(self, code, description=None, **kwargs):
        return self.openbis.new_project(self.code, code, description, **kwargs)

    def new_sample(self, **kwargs):
        return self.openbis.new_sample(space=self, **kwargs)

    def delete(self, reason):
        self.openbis.delete_entity(entity='Space', id=self.permId, reason=reason)
        if VERBOSE: print("Space {} has been sucsessfully deleted.".format(self.permId))

    def save(self):
        if self.is_new:
            request = self._new_attrs()
            resp = self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Space successfully created.")
            new_space_data = self.openbis.get_space(resp[0]['permId'], only_data=True)
            self._set_data(new_space_data)
            return self

        else:
            request = self._up_attrs()
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Space successfully updated.")
            new_space_data = self.openbis.get_space(self.permId, only_data=True)
            self._set_data(new_space_data)

