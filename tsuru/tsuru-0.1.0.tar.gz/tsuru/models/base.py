from datetime import datetime, timezone

from requests import HTTPError

from tsuru import client, exceptions


class BaseModel:
    _RESOURCE_NAME = None
    _PK_FIELD = 'ID'

    def __init__(self, data):
        if not isinstance(data, dict):
            raise exceptions.UnexpectedDataFormat()
        if self._PK_FIELD not in data:
            raise exceptions.UnexpectedDataFormat(f"Missing mandatory {self._PK_FIELD}")
        self._data = data
        self._detailed = False

    @property
    def pk(self):
        return self._get(self._PK_FIELD)

    def _get(self, value):
        try:
            return self._data[value]
        except (KeyError, TypeError):
            if not self._detailed:
                self.refresh()
                return self._get(value)
            raise exceptions.UnexpectedDataFormat()

    def refresh(self):
        if not self._detailed:
            self._data = self.get(pk=self.pk)._data
            self._detailed = True

    @classmethod
    def get(cls, pk):
        try:
            data = client.TsuruClient.get(resource=cls._RESOURCE_NAME, pk=pk)
        except HTTPError as e:
            if e.response.status_code == 404:
                raise exceptions.DoesNotExist()
            raise

        obj = cls(data=data)
        obj._detailed = True
        return obj

    @classmethod
    def list(cls):
        data = client.TsuruClient.get(resource=cls._RESOURCE_NAME)
        for item in data:
            yield cls(data=item)

    def _bound_list(self, resource_class, params=None):
        data = client.TsuruClient.get(
            resource=resource_class._RESOURCE_NAME,
            from_pk=self.pk,
            from_resource=self._RESOURCE_NAME,
            params=params,
        )
        for item in data:
            yield resource_class(data=item)

    def _bound_detail(self, resource_class, pk, params=None):
        data = client.TsuruClient.get(
            resource=resource_class._RESOURCE_NAME,
            from_pk=self.pk,
            from_resource=self._RESOURCE_NAME,
            pk=pk,
            params=params,
        )
        for item in data:
            yield resource_class(data=item)

    @classmethod
    def _parse_date(cls, date_str):
        if date_str and not date_str.startswith('0001-01-01'):
            fmt = '.%f' if '.' in date_str else ''
            return datetime.strptime(date_str, f'%Y-%m-%dT%H:%M:%S{fmt}Z').astimezone(timezone.utc)
        return None


class UnsupportedModelMixin:
    @classmethod
    def get(cls, pk):
        raise exceptions.UnsupportedModelException()

    @classmethod
    def list(cls):
        raise exceptions.UnsupportedModelException()

    def _detail(self, resource_class):
        raise exceptions.UnsupportedModelException()
