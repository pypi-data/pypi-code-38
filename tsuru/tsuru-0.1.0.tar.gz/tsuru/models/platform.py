from tsuru.models.base import BaseModel


class Platform(BaseModel):
    _RESOURCE_NAME = 'platforms'
    _PK_FIELD = 'Name'

    @property
    def name(self):
        return self._get('Name')

    @property
    def is_enabled(self):
        return not self._get('Disabled')
