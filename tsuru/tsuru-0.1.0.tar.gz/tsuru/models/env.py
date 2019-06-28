from tsuru.models.base import UnsupportedModelMixin, BaseModel


class Env(UnsupportedModelMixin, BaseModel):
    _RESOURCE_NAME = 'env'

    @property
    def name(self):
        return self._get('name')

    @property
    def value(self):
        return self._get('value')

    @property
    def public(self):
        return self._get('public')
