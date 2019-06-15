import datetime
from typing import Optional

from gumo.core.injector import injector
from gumo.datastore.infrastructure.entity_key_mapper import EntityKeyMapper

from google.cloud import datastore


class DatastoreMapperMixin:
    _entity_key_mapper = None
    DatastoreEntity = datastore.Entity

    @property
    def entity_key_mapper(self) -> EntityKeyMapper:
        if self._entity_key_mapper is None:
            self._entity_key_mapper = injector.get(EntityKeyMapper)  # type: EntityKeyMapper

        return self._entity_key_mapper

    def convert_datetime(self, t: datetime.datetime) -> Optional[datetime.datetime]:
        if t is None:
            return

        return datetime.datetime(
            year=t.year,
            month=t.month,
            day=t.day,
            hour=t.hour,
            minute=t.minute,
            second=t.second,
            microsecond=t.microsecond,
        )
