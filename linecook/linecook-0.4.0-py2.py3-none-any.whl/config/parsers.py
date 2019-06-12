# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools

from toolz import dicttoolz

from ..transforms.core import color_text


TRANSFORM_PARSERS = {}

TRANSFORM_PARSER_START_ORDER = []

TRANSFORM_PARSER_FINISH_ORDER = ['transforms']


def register_transform_parser(config_type):
    """Add parser to registry of known linecook config parsers.

    Args:
        config_type (str): The config type that is parsed by this decorated
            function The resulting output will be stored in the parsed config
            under this name.

    A config parser takes a sequence representing updated the an object
    containing the parsed data.

    You can register the a parser with the same name multiple times, which will
    simply override older instances.
    """
    def decorator(func):
        TRANSFORM_PARSERS[config_type] = func
        return func
    return decorator


@register_transform_parser('colorizers')
def parse_colorizers(colorizers_dict_seq):
    """Return dictionary of transforms based on `colorizers` in config_dict.

    This converts `colorizers` field in a configuration dict into color
    transforms. For example, take the following configuration::

        'colorizers': {
            'warn_color': {
                'match_pattern': ' WARN ',
                'on_color': 'on_yellow',
            },
        },

    That configuration is parsed to return the transform::

        from linecook.transforms.core import color_text

        color_text(' WARN ', on_color='on_yellow')

    """
    colorizers_dict = dicttoolz.merge(colorizers_dict_seq)
    return {key: color_text(color_kwargs)
            for key, color_kwargs in colorizers_dict.items()}


@register_transform_parser('transforms')
def parse_transforms(transforms_dict_seq):
    """Return dictionary of transforms based on `transforms` in config_dict.

    All this really does is merge the transforms defined in multiple
    configuration dictionaries.
    """
    return dicttoolz.merge(transforms_dict_seq)


def _iter_parsers():
    """Yield parsers in required order.

    Parsers in `TRANSFORM_PARSER_START_ORDER` are yielded first, those in
    `TRANSFORM_PARSER_FINISH_ORDER` are yielded last, and all other parsers in
    `TRANSFORM_PARSERS` are yielded in between in no guaranteed order.
    """
    unordered_parsers = (
        set(TRANSFORM_PARSERS)
        .difference(TRANSFORM_PARSER_START_ORDER)
        .difference(TRANSFORM_PARSER_FINISH_ORDER)
    )

    config_type_order = itertools.chain(
        TRANSFORM_PARSER_START_ORDER,
        unordered_parsers,
        TRANSFORM_PARSER_FINISH_ORDER
    )
    for config_type in config_type_order:
        parse = TRANSFORM_PARSERS.get(config_type)
        if parse:
            yield config_type, parse


def collect_tranforms(config_dicts):
    """Return transform dictionary from a list of configuration dictionaries.

    Args:
        config_dicts (list(dict)): Unparsed configuration dictionaries. For
            each dictionary, this applies parsers registered with
            `register_transform_parser` that convert configuration data into
            named transform functions.
    """
    transforms = {}
    for config_type, parse in _iter_parsers():
        config_type_data = get_value_from_each(config_type, config_dicts)
        transforms.update(parse(config_type_data))
    return transforms


def resolve_recipe(recipe, transforms_registry):
    for transform in recipe:
        transform = transforms_registry.get(transform, transform)
        if not callable(transform):
            msg = "Expected transform to be a callable, but found: {!r}"
            raise RuntimeError(msg.format(transform))
        yield transform


def collect_recipes(config_dicts, transforms_registry):
    """Return recipe dictionary from a list of configuration dictionaries.

    Args:
        config_dicts (list(dict)): Unparsed configuration dictionaries. For
            each dictionary, only use the 'recipes' value, which itself is a
            dictionary, where the keys are recipe names and values are lists
            of transform functions or transform names.
        transforms_registry (dict): Dictionary containing named transform
            functions. See also `collect_tranforms`, which build this registry.
    """
    recipe_dict = dicttoolz.merge(get_value_from_each('recipes', config_dicts))
    return {name: list(resolve_recipe(r, transforms_registry))
            for name, r in recipe_dict.items()}


def get_value_from_each(key, dict_list):
    """Return list of values for `key` in a list of dictionaries."""
    return (d[key] for d in dict_list if key in d)
