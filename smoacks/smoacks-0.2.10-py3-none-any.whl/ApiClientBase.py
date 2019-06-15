# ApiClientBase.py - Base object for API clients
from abc import ABC, abstractmethod
from smoacks.api_util import call_api

class ApiClientBase(ABC):
    _api_path = None
    _id_fields = None
    _ro_fields = set()

    @abstractmethod
    def get_ids(self):
        pass
    
    # This method will primarily be used to update new objects after
    # they are saved; the POST response to an object create includes
    # the server-generated UUIDs in the returned JSON
    def set_ids(self, **kwargs):
        if not isinstance(self._id_fields, list):
            if self._id_fields in kwargs:
                setattr(self, self._id_fields, kwargs[self._id_fields])
        else:
            for field in self._id_fields:
                if field in kwargs:
                    setattr(self, field, kwargs[field])
        pass

    # This method creates a JSON object from a potentially nested
    # object. For child objects, parent_id is generally set to the
    # field name of the parent ID, so that it can be omitted from
    # the child JSON, as parent ID is in the parent JSON object
    def toJSON(self, deep=False, parent_id=None):
        result = {}
        for key, value in vars(self).items():
            if key.startswith('_'): continue
            if key == parent_id: continue
            if key in self._ro_fields: continue
            if not value: continue
            result[key] = value
        return result

    def save_new(self, session):
        resp = call_api(session, 'POST',
                        '/{}'.format(self._api_path),
                        self.toJSON(True))
        if resp.status_code == 201:
            # If id_fields is not list, we get a new ID back from create
            # otherwise, we don't need a value from the response
            if not isinstance(self._id_fields, set):
                self.set_ids(**resp.json())
            return True, None
        return False, resp

    def save_update(self, session):
        resp = call_api(session, 'PUT',
                        '/{}/{}'.format(self._api_path, '/'.join(self.get_ids())),
                        self.toJSON(False))
        if resp.status_code == 200:
            return True, None
        return False, resp

    def save_delete(self, session):
        resp = call_api(session, 'DELETE',
                        '/{}/{}'.format(self._api_path, '/'.join(self.get_ids())))
        if resp.status_code == 204:
            return True, None
        return False, resp

    @classmethod
    def get(cls, session, ids):
        # Second argument can be a string if child class has only one ID field,
        # should be a list otherwise. We'll convert to a list so that we can join
        # it around the API path separator character regardless
        ids_arg = [ids] if type(ids) == str else ids
        resp = call_api(session, 'GET',
                        '/{}/{}'.format(cls._api_path, '/'.join(ids_arg)))
        if resp.status_code == 200:
            return True, cls(**resp.json())
        return False, resp

    @classmethod
    def search(cls, session, text):
        resp = call_api(session, 'GET',
                        '/{}?search_text={}'.format(cls._api_path, text))
        if resp.status_code == 200:
            result = []
            resp_list = resp.json()
            for item in resp_list:
                result.append(cls(**item))
            return True, result
        return False, resp
