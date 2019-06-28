from datetime import timedelta

from tsuru.models.base import BaseModel


class Deploy(BaseModel):
    _RESOURCE_NAME = 'deploys'
    _PK_FIELD = 'ID'

    @property
    def id(self):
        return self._get('ID')

    @property
    def app(self):
        from tsuru import App

        return App.get(pk=self._get('App'))

    @property
    def duration(self):
        nanoseconds = self._get('Duration')
        return timedelta(seconds=nanoseconds / 1000 / 1000 / 1000)

    @property
    def commit(self):
        return self._get('Commit')

    @property
    def error(self):
        return self._get('Error') or None

    @property
    def image(self):
        return self._get('Image')

    @property
    def log(self):
        # 'Log' field exists but it is empty when listing
        # When detailing, it is not empty anymore, so we force the detail
        self.refresh()
        return self._get('Log')

    @property
    def user(self):
        return self._get('User')

    @property
    def origin(self):
        return self._get('Origin')

    @property
    def can_rollback(self):
        return self._get('CanRollback')

    @property
    def removed_at(self):
        date_str = self._get('RemoveDate')
        return self._parse_date(date_str=date_str)

    @property
    def diff(self):
        return self._get('Diff')

    @property
    def timestamp(self):
        date_str = self._get('Timestamp')
        return self._parse_date(date_str=date_str)
