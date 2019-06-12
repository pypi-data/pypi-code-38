import importlib
import json
from datetime import date, datetime
from typing import List, AnyStr, Any, Type, GenericMeta, Dict


class SwaggerValidator(object):
    """
    Validate all attributes of a single Swagger model instance. Will raise an
    exception if an invalid type is detected, e.g. an address should be a
    string or None, but False is definitely a wrong type.
    """

    KEY_OPENAPI_TYPES = "openapi_types"
    VALID_NULL = None
    MAPPING_STR_TO_REAL_TYPES: Dict[str, Type] = {
        # Primitive types.
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,

        # Others
        "list": List,
        "dict": Dict,  # TODO need check
        "date": date,  # TODO need check
        "datetime": datetime,  # TODO need check
    }

    # e.g. we have server and client for the same swagger file.
    LOADED_SWAGGER_MODULES = set()

    def __init__(self, obj: Any, _type: Type[object]):
        self.obj: Any = obj
        self._type = _type
        self.errs: List[AnyStr] = []

    @classmethod
    def validate(cls, obj: Any, _type: Type[object]):
        cls._load_str_types_mapping(_type)

        validator = SwaggerValidator(obj, _type)
        validator._validate_obj()
        if validator.errs:
            msg = json_dumps_unicode(validator.errs)
            raise InvalidSwaggerDataType(msg)
        return validator

    def _validate_obj(self):
        # The root object should be a Swagger model instance.
        if not self._is_swagger_model_instance(self._type):
            return self.errs.append(
                "type:%s is not a valid Swagger model due to lacking"
                " attribute:%s" % (self._type, self.KEY_OPENAPI_TYPES))

        # Validate the whole object.
        self._validate_recursively(self.obj, self._type)

    def _validate_recursively(self, obj: Any,
                              _type: Type[object],
                              attr_path: str = None):
        # 1. [root] None is valid.
        if obj is self.VALID_NULL:
            return
        attr_path = attr_path or _type.__name__
        if self._is_same_class_name(obj, _type):
            return self._msg_of_wrong_type(attr_path, obj, _type)

        # 2. [children]
        # instance always can access the attributes of its class.
        field_types_container = obj
        types = getattr(field_types_container, self.KEY_OPENAPI_TYPES, None)
        if types is None:
            return  # 2.0. return earlier if it's general.
        for field_name, field_type in types.items():
            sub_attr_path = attr_path + "." + field_name

            if isinstance(field_type, str):
                # 'eval' is running on the client side, so there's no harm
                # for the server side.
                field_type = eval(field_type, self.MAPPING_STR_TO_REAL_TYPES)

            field_value = getattr(obj, field_name)
            # 2.1. An attribute is valid even it's None.
            if field_value is self.VALID_NULL:
                continue
            # 2.2. Or should be the type as it declared.
            if isinstance(field_type, GenericMeta):
                extra_type = getattr(field_type, "__extra__")
                field_type_args = getattr(field_type, "__args__")
                if extra_type == list:
                    for idx, _item in enumerate(field_value):
                        self._validate_recursively(
                            _item,
                            field_type_args[0],
                            sub_attr_path + "[%s]" % idx
                        )
                if extra_type == dict:  # TODO need check
                    for k, _item in field_value.items():
                        self._validate_recursively(
                            _item,
                            field_type_args[1],
                            sub_attr_path + "." + k
                        )
                continue

            if self._is_same_class_name(field_value, field_type):
                self._msg_of_wrong_type(sub_attr_path, field_value, field_type)
                continue
            # 2.3. Continue to validate if current attribute is still a
            #      composite.
            if self._is_swagger_model_instance(field_value):
                self._validate_recursively(
                    field_value, field_type, sub_attr_path)

    def _msg_of_wrong_type(self, attr_path, obj: Any, _type: Type[object]):
        return self.errs.append(
            "%s=%s does not belong to expected type:%s, but get type:%s" % (
                attr_path, repr(obj), _type, type(obj)))

    def _is_swagger_model_instance(self, obj: Any):
        return hasattr(obj, self.KEY_OPENAPI_TYPES)

    def _is_same_class_name(self, obj: Any, _type: Type[Any]) -> bool:
        """ allow same class names in different packages. """
        return type(obj).__name__ != _type.__name__

    @classmethod
    def _load_str_types_mapping(cls, any_swagger_model) -> Dict[str, Type]:
        # Extracted models module, e.g. from 'swagger_client.models.address'
        models_module_path = ".".join(
            any_swagger_model.__module__.split(".")[:2])
        if models_module_path in cls.LOADED_SWAGGER_MODULES:
            return cls.MAPPING_STR_TO_REAL_TYPES  # already loaded
        models_module = importlib.import_module(models_module_path)

        # 1. Find all Swagger models.
        for field in dir(models_module):
            potential_class = getattr(models_module, field)
            if hasattr(potential_class, cls.KEY_OPENAPI_TYPES):
                cls.MAPPING_STR_TO_REAL_TYPES[field] = \
                    potential_class

        cls.LOADED_SWAGGER_MODULES.add(models_module_path)
        return cls.MAPPING_STR_TO_REAL_TYPES


def json_dumps_unicode(obj):
    """
    Change Python default json.dumps acting like JavaScript, including allow
    Chinese characters and no space between any keys or values.
    """
    return json.dumps(obj,
                      ensure_ascii=False,
                      separators=(',', ':')
                      )


class InvalidSwaggerDataType(Exception):
    pass
