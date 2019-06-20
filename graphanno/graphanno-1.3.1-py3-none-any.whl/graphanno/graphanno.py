"""Main module."""
import inspect
import typing
from datetime import date, datetime, time

import graphene

BASIC_TYPE_MAPPINGS = {
    str: graphene.String,
    int: graphene.Int,
    bool: graphene.Boolean,
    float: graphene.Float,
    date: graphene.Date,
    datetime: graphene.DateTime,
    time: graphene.Time,
}

UNSUPORTED_TYPES = (list, dict, tuple, set)


class UnsupportedAnnotationError(Exception):
    """Raised on unsupported annotation resolve attempt."""


class NoAnnotationsError(Exception):
    """Raised when no annotations have been found (or all are excluded)."""


class SchemaClashError(Exception):
    """Raised when there are two different schema classes with the same name."""


class ObjectType(graphene.ObjectType):
    """
    Base class for type annotated graphene schemas.
    The subclass still has to be decorated, the purpose of this class is to provide hints
    for special graphanno attributes and those inherited from ObjectType.
    """

    __model__: typing.Any = None
    __excluded_fields__: typing.Iterable = tuple()
    __ignore_unsupported__: bool = False


def graph_annotations(  # pylint: disable=dangerous-default-value
    cls, cached_objects={}
):
    """Prepare GraphQL schema based on the type annotations."""
    attributes = {}
    target_class = cls.__model__ if hasattr(cls, "__model__") else cls

    ignore_unsupported = getattr(cls, "__ignore_unsupported__", False)
    excluded_keys = getattr(cls, "__excluded_fields__", tuple())

    cached = None
    if hasattr(cls, "__name__"):
        cached = _get_cached(
            cached_objects.get(cls.__name__, (None, None, None)),
            target_class,
            excluded_keys,
        )
    if cached:
        return cached

    annotations = _get_annotations_data(cls, excluded_keys, target_class)

    for name, annotation in annotations.items():
        if annotation in UNSUPORTED_TYPES:
            if ignore_unsupported:
                continue
            raise UnsupportedAnnotationError(
                f"The type annotation: {annotation} is not supported."
            )
        type_, args = _get_type_from_annotation(annotation)
        attributes[name] = type_(*args)

    superclasses = (
        (cls,) if issubclass(cls, graphene.ObjectType) else (cls, graphene.ObjectType)
    )
    result = type(cls.__name__, superclasses, attributes)
    cached_objects[result.__name__] = (
        result,
        target_class,
        hasattr(cls, "__model__") or set(annotations.keys()),
    )

    return result


def _get_annotations_data(cls, excluded_keys, target_class):
    annotations = dict(**getattr(target_class, "__annotations__", {}))
    annotations.update(getattr(cls, "__annotations__", {}))
    annotations.update(_get_property_annotations(target_class))
    private_keys = tuple(key for key in annotations.keys() if key.startswith("_"))
    for key in excluded_keys + private_keys:
        annotations.pop(key)
    if not annotations:
        raise NoAnnotationsError(
            f'No included annotations for class {cls.__name__ if hasattr(cls, "__name__") else cls}.'
        )
    return annotations


def _get_cached(cache_data, target, excluded_keys):
    cached, original, annotated = cache_data
    if cached:
        if (target.__module__, target) != (original.__module__, original):
            raise SchemaClashError(
                f'The schema with name "{target.__name__}" already exists, '
                f"and bases on another class:\n"
                f"\t- Current: {target.__module__}.{target.__name__}\n"
                f"\t- Existing: {original.__module__}.{original.__name__}"
            )
        if annotated is True:
            return cached
        for key in excluded_keys:
            delattr(cached, key)
            annotated.remove(key)
        if not annotated:
            raise NoAnnotationsError(
                f"No included annotations for class {target.__name__}."
            )
    return cached


def _get_type_from_annotation(annotation, type_only=False):
    basic_type = BASIC_TYPE_MAPPINGS.get(annotation)
    if basic_type:
        return basic_type if type_only else (basic_type, tuple())

    if str(annotation).startswith("typing.List"):
        return graphene.List, (_get_type_from_annotation(annotation.__args__[0], True),)

    if hasattr(annotation, "__origin__"):
        if annotation.__origin__ is typing.Union:
            if len(annotation.__args__) == 2 and any(
                isinstance(None, arg) for arg in annotation.__args__
            ):
                type_ = next(
                    arg for arg in annotation.__args__ if not isinstance(None, arg)
                )
                return _get_type_from_annotation(type_, type_only)

    type_ = graph_annotations(annotation)
    return type_ if type_only else (graphene.Field, (type_,))


def _get_property_annotations(cls):
    property_annotations = {}
    properties = inspect.getmembers(cls, lambda o: isinstance(o, property))
    for name, property_ in properties:
        members = {
            key: value
            for key, value in inspect.getmembers(
                property_.fget, lambda o: isinstance(o, dict)
            )
        }
        annotation = members.get("__annotations__", {}).get("return")
        if annotation:
            property_annotations[name] = annotation
    return property_annotations
