from abc import ABC, abstractmethod
from typing import List


class EntityBase(ABC):
    @property
    @abstractmethod
    def entity_id(self):
        raise NotImplementedError

    @property
    def event_service(self):
        return self._event_service

    @event_service.setter
    def event_service(self, event_service):
        super().__setattr__("_event_service", event_service)

    @property
    def change_log(self):
        try:
            self._changes
        except AttributeError:
            self.clear_change_log()
        return self._changes

    def clear_change_log(self):
        super().__setattr__("_changes", [])

    @property
    def entity_data(self):
        try:
            self._entity_data
        except AttributeError:
            self.clear_entity_data()
        return self._entity_data

    def clear_entity_data(self):
        super().__setattr__("_entity_data", {})

    def __setattr__(self, attr, value):
        try:
            old_value = self.__getattribute__(attr)
            change = {
                "key": attr,
                "old_value": _reflect(old_value),
                "new_value": _reflect(value),
            }

            self.change_log.append(change)
        except AttributeError:
            pass
        super().__setattr__(attr, value)

    def capture_field_values(self, fields: List):
        for field in fields:
            value = self.__getattribute__(field)
            self.entity_data[field] = _reflect(value)


def _reflect(value):
    """Reflect on attribute type and return JSON parse-able type.

    :param attr: attribute
    :return: converted object to correct type
    :rtype: str, int or None
    """
    if value is None:
        return value
    elif isinstance(value, bool):
        return value
    elif isinstance(value, int):
        return int(value)
    elif isinstance(value, EntityBase):
        return {
            "type": value.__class__.__name__,
            "entity_id": str(value.entity_id),
        }
    elif isinstance(value, List):
        return [_reflect(i) for i in value]
    else:
        return str(value)
