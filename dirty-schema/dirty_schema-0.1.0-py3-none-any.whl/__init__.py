from json import dumps, loads
from typing import Type

from dirty_models import BaseModel, JSONEncoder
from dirty_validators.complex import ModelValidateMixin

__version__ = '0.1.0'


def create_schema_from_validator(validator: Type[ModelValidateMixin], *,
                                 def_read_only: bool = True, to_update: bool = False):
    from .builder import Builder
    builder = Builder(def_read_only=def_read_only, to_update=to_update)

    return loads(dumps(builder.generate_from_model_validator(validator=validator), cls=JSONEncoder))


def create_schema_from_model(model: Type[BaseModel], *,
                             def_read_only: bool = True):
    from .builder import Builder
    builder = Builder(def_read_only=def_read_only)

    return loads(dumps(builder.generate_from_model(model_class=model), cls=JSONEncoder))
