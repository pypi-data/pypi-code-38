from .attribute import AttrHolder
from .openbis_object import OpenBisObject 
from .utils import VERBOSE


class Project(OpenBisObject):
    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj
        self.__dict__['a'] = AttrHolder(openbis_obj, 'Project')

        if data is not None:
            self.a(data)
            self.__dict__['data'] = data

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def _modifiable_attrs(self):
        return

    def __dir__(self):
        """all the available methods and attributes that should be displayed
        when using the autocompletion feature (TAB) in Jupyter
        """
        return ['code', 'permId', 'identifier', 'description', 'space', 'registrator',
                'registrationDate', 'modifier', 'modificationDate', 'add_attachment()',
                'get_attachments()', 'download_attachments()',
                'get_experiments()', 'get_samples()', 'get_datasets()',
                'save()', 'delete()'
                ]

    def get_samples(self, **kwargs):
        return self.openbis.get_samples(project=self.permId, **kwargs)
    get_objects = get_samples # Alias

    def get_sample(self, sample_code):
        if is_identifier(sample_code) or is_permid(sample_code):
            return self.openbis.get_sample(sample_code)
        else:
            # we assume we just got the code
            return self.openbis.get_sample(project=self, code=sample_code)
    get_object = get_sample # Alias


    def get_experiments(self):
        return self.openbis.get_experiments(project=self.permId)
    get_collections = get_experiments  # Alias

    def get_datasets(self):
        return self.openbis.get_datasets(project=self.permId)

    def delete(self, reason):
        self.openbis.delete_entity(entity='Project', id=self.permId, reason=reason)
        if VERBOSE: print("Project {} successfully deleted.".format(self.permId))

    def save(self):
        if self.is_new:
            request = self._new_attrs()
            resp = self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Project successfully created.")
            new_project_data = self.openbis.get_project(resp[0]['permId'], only_data=True)
            self._set_data(new_project_data)
            return self
        else:
            request = self._up_attrs()
            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("Project successfully updated.")


