from tsuru.models.base import BaseModel


class Plan(BaseModel):
    _RESOURCE_NAME = 'plans'
    _PK_FIELD = 'name'

    @property
    def cpu_share(self):
        return self._get('cpushare')

    @property
    def memory(self):
        return self._get('memory')

    @property
    def name(self):
        return self._get('name')

    @property
    def router(self):
        return self._get('router')

    @property
    def swap(self):
        return self._get('swap')
