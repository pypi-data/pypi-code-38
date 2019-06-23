from typing import Any

from django.db.models.base import ModelBase
from neomodel import NodeMeta

from .relationship import CrossDBRelationship


class CrossDBModelMeta(ModelBase,
                       NodeMeta):

    def __new__(mcls, name, bases, attrs):
        mcls.cross_db = True

        all_rels = mcls.defined_cross_relationships(attrs)
        # mcls.__all_cross_relationships__ = all_rels
        attrs['__all_cross_relationships__'] = all_rels

        return super(CrossDBModelMeta, mcls).__new__(mcls,
                                                     name,
                                                     bases,
                                                     attrs)

    @classmethod
    def defined_cross_relationships(cls, attrs, rels=False):
        props = {}
        for name, property in attrs.items():
            if isinstance(property, CrossDBRelationship):
                props[name] = property
        return dict(props)


class CrossDBModel(metaclass=CrossDBModelMeta):
    GENERATED_ID_FIELDS: dict
    _data = dict()

    def __new__(cls, *args, **kwargs) -> Any:
        cls = super(CrossDBModel, cls).__new__(cls)

        for key, val in cls.__all_cross_relationships__.items():
            cls.__dict__[key] = val.build_cross_manager(cls, key)
        return cls

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
