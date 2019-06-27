"""List and filtered list model."""

# standard libraries
import collections
import copy
import functools
import typing

# third party libraries
# None

# local libraries
from nion.utils import Event
from nion.utils import Observable
from nion.utils import Model
from nion.utils import ListModel as ListModelModule


# TODO: logical types: datetime, timestamp, uuid, etc.
# TODO: object references (w/ content changed, delete, etc.)


MDescription = typing.Union[str, dict]  # when napolean works: typing.NewType("MDescription", typing.Dict)
MFields = typing.List  # when napolean works: typing.NewType("MFields", typing.List)


STRING = "string"
BOOLEAN = "boolean"
INT = "int"
FLOAT = "double"


def define_string() -> MDescription:
    return "string"


def define_boolean() -> MDescription:
    return "boolean"


def define_int() -> MDescription:
    return "int"


def define_float() -> MDescription:
    return "double"


def define_field(name: str=None, type: str=None, *, default=None) -> MDescription:
    d = {"name": name, "type": type}
    if default is not None:
        d["default"] = default
    return d


def define_record(name: str, fields: MFields) -> MDescription:
    return {"type": "record", "name": name, "fields": fields}


def define_array(items: MDescription) -> MDescription:
    return {"type": "array", "items": items}


def build_model(schema: MDescription, *, default_value=None, value=None):
    if schema in ("string", "boolean", "int", "float"):
        return FieldPropertyModel(default_value if default_value is not None else value)
    type = schema.get("type")
    if type in ("string", "boolean", "int", "float"):
        return FieldPropertyModel(default_value if default_value is not None else value)
    elif type == "record":
        record_values = copy.copy(default_value or dict())
        record_values.update(value or dict())
        return RecordModel(schema, values=record_values)
    elif type == "array":
        return ArrayModel(schema, value if value is not None else default_value)


def build_value(schema: MDescription, *, value=None):
    if schema in ("string", "boolean", "int", "float"):
        return value
    type = schema.get("type")
    if type in ("string", "boolean", "int", "float"):
        return value
    elif type == "record":
        return RecordModel(schema, values=value)
    elif type == "array":
        return ArrayModel(schema, value)


class FieldPropertyModel(Model.PropertyModel):

    def __init__(self, value):
        super().__init__(value=value)
        self.field_value_changed_event = Event.Event()
        self.array_item_inserted_event = Event.Event()
        self.array_item_removed_event = Event.Event()
        self.model_changed_event = Event.Event()

    def from_dict_value(self, value) -> None:
        self.value = value

    def to_dict_value(self) -> typing.Optional[typing.Any]:
        if self.value is not None:
            return self.value
        return None

    @property
    def field_value(self):
        return self.value

    def notify_property_changed(self, key: str) -> None:
        super().notify_property_changed(key)
        self.field_value_changed_event.fire(key)
        self.model_changed_event.fire()


class RecordModel(Observable.Observable):

    __initialized = False

    def __init__(self, schema: MDescription, *, values=None):
        super().__init__()
        self.field_value_changed_event = Event.Event()
        self.array_item_inserted_event = Event.Event()
        self.array_item_removed_event = Event.Event()
        self.model_changed_event = Event.Event()
        self.__field_models = dict()
        self.__field_model_property_changed_listeners = dict()
        self.__field_model_changed_listeners = dict()
        self.__array_item_inserted_listeners = dict()
        self.__array_item_removed_listeners = dict()
        self.schema = schema
        for field_schema in schema["fields"]:
            field_name = field_schema["name"]
            field_type = field_schema["type"]
            field_default = field_schema.get("default")
            field_model = build_model(field_type, default_value=field_default, value=(values or dict()).get(field_name))
            self.__field_models[field_name] = field_model

            def handle_property_changed(field_name, name):
                if name == "value":
                    self.property_changed_event.fire(field_name)

            def handle_array_item_inserted(field_name, key, value, before_index):
                if key == "items":
                    self.item_inserted_event.fire(field_name, value, before_index)

            def handle_array_item_removed(field_name, key, value, index):
                if key == "items":
                    self.item_removed_event.fire(field_name, value, index)

            self.__field_model_property_changed_listeners[field_name] = field_model.field_value_changed_event.listen(functools.partial(handle_property_changed, field_name))
            self.__field_model_changed_listeners[field_name] = field_model.model_changed_event.listen(self.model_changed_event.fire)
            self.__array_item_inserted_listeners[field_name] = field_model.array_item_inserted_event.listen(functools.partial(handle_array_item_inserted, field_name))
            self.__array_item_removed_listeners[field_name] = field_model.array_item_removed_event.listen(functools.partial(handle_array_item_removed, field_name))
        self.__initialized = True

    def close(self):
        for field_name in self.__field_models.keys():
            self.__field_model_property_changed_listeners[field_name].close()
            del self.__field_model_property_changed_listeners[field_name]
            self.__array_item_inserted_listeners[field_name].close()
            del self.__array_item_inserted_listeners[field_name]
            self.__array_item_removed_listeners[field_name].close()
            del self.__array_item_removed_listeners[field_name]
            self.__field_model_changed_listeners[field_name].close()
            del self.__field_model_changed_listeners[field_name]

    def __deepcopy__(self, memo):
        values = self.to_dict_value()
        return RecordModel(copy.deepcopy(self.schema), values=values)

    def copy_from(self, record: "RecordModel") -> None:
        self.from_dict_value(record.to_dict_value())

    def from_dict_value(self, values):
        for k, v in self.__field_models.items():
            if k in values:
                self.__field_models[k].from_dict_value(values[k])

    def to_dict_value(self) -> typing.Optional[typing.Any]:
        d = dict()
        for field_schema in self.schema["fields"]:
            field_name = field_schema["name"]
            field_value = self.__field_models[field_name].to_dict_value()
            if field_value is not None:
                d[field_name] = field_value
        return d

    def __getattr__(self, name):
        if name in self.__field_models:
            return self.__field_models[name].field_value
        if name.endswith("_model") and name[:-6] in self.__field_models:
            return self.__field_models[name[:-6]]
        raise AttributeError()

    def __setattr__(self, name, value):
        if self.__initialized and name in self.__field_models and isinstance(self.__field_models[name], FieldPropertyModel):
            self.__field_models[name].value = value
        else:
            super().__setattr__(name, value)

    @property
    def field_value(self):
        return self


class ItemsSequence(collections.abc.MutableSequence):

    def __init__(self, list_model):
        super().__init__()
        self.__list_model = list_model

    def __len__(self):
        return len(self.__list_model.items)

    def __getitem__(self, key):
        return self.__list_model.items[key]

    def __setitem__(self, key, value):
        raise IndexError()

    def __delitem__(self, key):
        self.__list_model.remove_item(key)

    def __contains__(self, item):
        return self.__list_model.items.contains(item)

    def insert(self, index, value):
        self.__list_model.insert_item(index, value)


class ArrayModel(ListModelModule.ListModel):

    def __init__(self, schema: MDescription, values=None):
        if values is not None:
            items = list()
            item_schema = schema["items"]
            for value in values:
                items.append(build_value(item_schema, value=value))
        else:
            items = None
        super().__init__(items=items)
        self.schema = schema
        self.field_value_changed_event = Event.Event()
        self.array_item_inserted_event = Event.Event()
        self.array_item_removed_event = Event.Event()
        self.model_changed_event = Event.Event()
        self.__model_changed_listeners = list()
        for item in self.items:
            trampoline = None
            if isinstance(item, (RecordModel, ArrayModel)):
                trampoline = item.model_changed_event.listen(self.model_changed_event.fire)
            self.__model_changed_listeners.append(trampoline)

    def close(self):
        for index, item in enumerate(self.items()):
            trampoline = self.__model_changed_listeners[index]
            if trampoline:
                trampoline.close()
        self.__model_changed_listeners = list()

    def __deepcopy__(self, memo):
        values = self.to_dict_value()
        return ArrayModel(copy.deepcopy(self.schema), values=values)

    def copy_from(self, array: "ArrayModel") -> None:
        self.from_dict_value(array.to_dict_value())

    def from_dict_value(self, values):
        while len(values) > len(self.items):
            item_schema = self.schema["items"]
            self.items.append(build_value(item_schema))
        while len(values) < len(self.items):
            del self.items[-1]
        for value, item in zip(values, self.items):
            item.from_dict_value(value)

    def to_dict_value(self) -> typing.Optional[typing.Any]:
        l = list()
        for item in self.items:
            l.append(item.to_dict_value())
        return l

    @property
    def field_value(self):
        return ItemsSequence(self)

    def notify_insert_item(self, key, value, before_index):
        super().notify_insert_item(key, value, before_index)
        self.array_item_inserted_event.fire(key, value, before_index)
        trampoline = None
        if isinstance(value, (RecordModel, ArrayModel)):
            trampoline = value.model_changed_event.listen(self.model_changed_event.fire)
        self.__model_changed_listeners.append(trampoline)
        self.model_changed_event.fire()

    def notify_remove_item(self, key, value, index):
        super().notify_remove_item(key, value, index)
        trampoline = self.__model_changed_listeners.pop(index)
        if trampoline:
            trampoline.close()
        self.array_item_removed_event.fire(key, value, index)
        self.model_changed_event.fire()
