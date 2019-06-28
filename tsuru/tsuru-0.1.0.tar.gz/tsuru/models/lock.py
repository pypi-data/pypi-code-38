from tsuru.models.base import UnsupportedModelMixin, BaseModel


class Lock(UnsupportedModelMixin, BaseModel):
    _RESOURCE_NAME = 'locks'

    @property
    def locked(self):
        return self._get('Locked')

    @property
    def reason(self):
        return self._get('Reason')

    @property
    def owner(self):
        return self._get('Owner')

    @property
    def acquire_date(self):
        date_str = self._get('AcquireDate')
        return self._parse_date(date_str=date_str)
