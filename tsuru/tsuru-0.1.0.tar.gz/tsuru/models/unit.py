from tsuru.models.base import BaseModel


class Unit(BaseModel):
    _RESOURCE_NAME = 'units'

    @property
    def name(self):
        return self._get('Name')

    @property
    def process_name(self):
        return self._get('ProcessName')

    @property
    def app_name(self):
        return self._get('AppName')

    @property
    def type(self):
        return self._get('Type')

    @property
    def ip(self):
        return self._get('IP')

    @property
    def status(self):
        return self._get('Status')

    @property
    def address(self):
        data = self._get('Address')
        scheme = data['Scheme']
        user = data['User']
        host = data['Host']
        path = data['Path']
        raw_query = data['RawQuery']

        auth = f'{user}@' if user else ''
        query = f'?{raw_query}' if raw_query else ''
        return f"{scheme}://{auth}{host}{path}{query}"

    @property
    def host_(self):
        address = self._get('HostAddr')
        port = self._get('HostPort')
        return f"{address}:{port}"

    def app(self):
        from tsuru import App

        return App(data={'name': self.app_name})
