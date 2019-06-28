from tsuru.models.base import UnsupportedModelMixin, BaseModel


class Log(UnsupportedModelMixin, BaseModel):
    _RESOURCE_NAME = 'log'

    @property
    def date(self):
        date_str = self._get('Date')
        return self._parse_date(date_str=date_str)

    @property
    def message(self):
        return self._get('Message')

    @property
    def source(self):
        return self._get('Source')

    @property
    def app_name(self):
        return self._get('AppName')

    @property
    def unit(self):
        return self._get('Unit')
