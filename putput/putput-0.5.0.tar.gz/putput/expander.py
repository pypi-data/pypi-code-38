import re
from functools import lru_cache
from itertools import chain
from itertools import product
from itertools import repeat
from typing import Dict  # pylint: disable=unused-import
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union
from typing import cast

from putput.joiner import join_combo
from putput.validator import OPTIONAL_REGEX
from putput.validator import RANGE_REGEX


def expand(pattern_def: Mapping,
           *,
           dynamic_token_patterns_map: Optional[Mapping[str, Sequence[str]]] = None
           ) -> Tuple[int, Iterable[Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]]]:
    """Expands the pattern_def to prepare for combination.

    Args:
        pattern_def: A dictionary representation of the pattern definition.

        dynamic_token_patterns_map: The 'dynamic' counterpart to the 'static' section in the
            pattern definition. This mapping between token and token patterns is useful in
            scenarios where tokens and token patterns cannot be known before runtime.

    Returns:
        The length of the Iterable, and the Iterable consisting of
        an utterance_combo, tokens (that have yet to be handled),
        and groups (that have yet to be handled).

    Examples:
        >>> from pathlib import Path
        >>> from putput.pipeline import _load_pattern_def
        >>> pattern_def_path = Path(__file__).parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
        >>> pattern_def = _load_pattern_def(pattern_def_path)
        >>> dynamic_token_patterns_map = {'ITEM': ('fries',)}
        >>> num_utterance_patterns, generator = expand(pattern_def,
        ...                                            dynamic_token_patterns_map=dynamic_token_patterns_map)
        >>> num_utterance_patterns
        1
        >>> for utterance_combo, unhandled_tokens, unhandled_groups in generator:
        ...     print(utterance_combo)
        ...     print(unhandled_tokens)
        ...     print(unhandled_groups)
        (('can she get', 'may she get'), ('fries',), ('can she get', 'may she get'), ('fries',), ('and',), ('fries',))
        ('ADD', 'ITEM', 'ADD', 'ITEM', 'CONJUNCTION', 'ITEM')
        (('ADD_ITEM', 2), ('ADD_ITEM', 2), ('None', 1), ('None', 1))
    """
    utterance_patterns_expanded_ranges_and_groups, groups = expand_utterance_patterns_ranges_and_groups(
        pattern_def['utterance_patterns'], get_base_item_map(pattern_def, 'groups'))

    def _expand() -> Iterable[Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]]:
        token_patterns_map = _get_token_patterns_map(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)
        for utterance_pattern, group in zip(utterance_patterns_expanded_ranges_and_groups, groups):
            utterance_combo = _compute_utterance_combo(utterance_pattern, token_patterns_map)
            yield utterance_combo, tuple(utterance_pattern), tuple(group)
    return len(utterance_patterns_expanded_ranges_and_groups), _expand()

def expand_utterance_patterns_ranges_and_groups(utterance_patterns: Sequence[Sequence[str]],
                                                group_map: Mapping[str, Sequence[str]]
                                                ) -> Tuple[Sequence[Sequence[str]],
                                                           Sequence[Sequence[Tuple[str, int]]]]:
    """Expands ranges and groups in utterance patterns, ensuring each utterance pattern is unique.

    Args:
        utterance_patterns: utterance_patterns section of pattern_def.

        group_map: A mapping between a group name and the tokens that make up the group.

    Returns:
        A tuple of utterance patterns with group names and ranges replaced by tokens, and
        groups which are tuples of (group_name, number of tokens the group spans).

    Examples:
        >>> utterance_patterns = [['WAKE', 'PLAY_ARTIST', '1-2']]
        >>> group_map = {'PLAY_ARTIST': ('PLAY', 'ARTIST')}
        >>> patterns, groups = expand_utterance_patterns_ranges_and_groups(utterance_patterns, group_map)
        >>> tuple(sorted(patterns, key=lambda item: len(item)))
        (('WAKE', 'PLAY', 'ARTIST'), ('WAKE', 'PLAY', 'ARTIST', 'PLAY', 'ARTIST'))
        >>> tuple(sorted(groups, key=lambda item: len(item)))
        ((('None', 1), ('PLAY_ARTIST', 2)), (('None', 1), ('PLAY_ARTIST', 2), ('PLAY_ARTIST', 2)))
    """
    expanded_ranges = _expand_utterance_patterns_ranges(utterance_patterns)
    expanded_ranges_groups, groups = _expand_utterance_patterns_groups(expanded_ranges, group_map)
    deduped_expanded_ranges_groups, groups = zip(*sorted(set(zip(expanded_ranges_groups, groups))))
    return deduped_expanded_ranges_groups, groups

def _expand_utterance_patterns_ranges(utterance_patterns: Sequence[Sequence[str]]) -> Sequence[Sequence[str]]:
    utterance_patterns_expanded_optional = tuple(chain.from_iterable(map(_expand_optional, utterance_patterns)))
    return tuple(chain.from_iterable(map(_expand_ranges, utterance_patterns_expanded_optional)))

def _expand_ranges(utterance_pattern: Sequence[str]) -> Sequence[Sequence[str]]:
    ranges = tuple(map(_parse_ranges, utterance_pattern))
    aligned_ranges_and_tokens = zip(ranges[1:] + ((0, 0),), utterance_pattern)
    aligned_range_tokens = map(lambda r_and_t: r_and_t[0] + (r_and_t[1],), aligned_ranges_and_tokens)
    range_tokens = filter(lambda r_and_t: not re.match(RANGE_REGEX, r_and_t[2]), aligned_range_tokens)
    utterance_pattern_expanded_ranges = tuple(map(tuple, map(chain.from_iterable, product( # type: ignore
        *map(_expand_tokens, range_tokens)))))  # type: ignore
    return cast(Sequence[Sequence[str]], utterance_pattern_expanded_ranges)

def _parse_ranges(token: str) -> Tuple[int, int]:
    if re.match(RANGE_REGEX, token):
        if '-' not in token:
            return int(token), int(token) + 1
        min_range, max_range = token.split('-')
        return int(min_range), int(max_range) + 1
    return (0, 0)

def _parse_optional(token: str) -> Sequence[str]:
    if re.match(OPTIONAL_REGEX, token):
        token_without_parantheses = token[1:-1]
        return tuple(token_without_parantheses.split('|'))
    return tuple([token])

def _expand_tokens(range_token: Tuple[int, int, str]) -> Iterable[Sequence[str]]:
    min_range, max_range, token = range_token
    if min_range == 0 and max_range == 0:
        return ((token,),)
    return map(lambda i: (token,) * i, range(min_range, max_range))

def _get_token_patterns_map(pattern_def: Mapping,
                            *,
                            dynamic_token_patterns_map: Optional[Mapping[str, Sequence[str]]] = None
                            ) -> Mapping[str, Sequence[Sequence[Sequence[str]]]]:
    token_patterns_map = {} # type: Dict[str, Sequence[Sequence[Sequence[str]]]]
    static_token_patterns_map = _get_static_token_patterns_map(pattern_def)
    token_patterns_map.update(static_token_patterns_map)
    if dynamic_token_patterns_map:
        token_patterns_map.update(_expand_dynamic_token_patterns_map(dynamic_token_patterns_map))
    return token_patterns_map

def get_base_item_map(pattern_def: Mapping, base_key: str) -> Mapping[str, Sequence[str]]:
    """Returns base item map or an empty dictionary if one does not exist.

    Args:
        pattern_def: A dictionary representation of the pattern definition.

        base_key: Key in pattern_def corresponding to the base item map.

    Examples:
        >>> from pathlib import Path
        >>> from putput.pipeline import _load_pattern_def
        >>> pattern_def_path = Path(__file__).parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
        >>> pattern_def = _load_pattern_def(pattern_def_path)
        >>> get_base_item_map(pattern_def, 'groups')
        {'ADD_ITEM': ('ADD', 'ITEM')}
        >>> get_base_item_map(pattern_def, 'base_tokens')
        {'PRONOUNS': ('she',)}
        >>> get_base_item_map(pattern_def, 'not_a_key')
        {}
    """
    if base_key in pattern_def:
        return {next(iter(base_item_map.keys())): tuple(next(iter(base_item_map.values())))
                for base_item_map in pattern_def[base_key]}
    return {}

def _get_static_token_patterns_map(pattern_def: Mapping) -> Mapping[str, Sequence[Sequence[Sequence[str]]]]:
    return {
        token: _expand_static_token_patterns(pattern_def, token_patterns)
        for token_type_map in pattern_def['token_patterns']
        for token_type in token_type_map
        if token_type == 'static'
        for static_token_patterns_map in token_type_map['static']
        for token, token_patterns in static_token_patterns_map.items()
    }

def _expand_dynamic_token_patterns_map(dynamic_token_patterns: Mapping[str, Sequence[str]]
                                       ) -> Mapping[str, Sequence[Sequence[Sequence[str]]]]:
    return {token: ((tuple(patterns),),) for token, patterns in dynamic_token_patterns.items()}

def _expand_static_token_patterns(pattern_def: Mapping,
                                  token_patterns: Sequence[Sequence[Union[str, Sequence[str]]]]
                                  ) -> Sequence[Sequence[Sequence[str]]]:
    if 'base_tokens' in pattern_def:
        token_patterns = _expand_base_tokens(pattern_def, token_patterns)
    return _convert_token_patterns_to_tuples(token_patterns)

def _convert_token_patterns_to_tuples(token_patterns: Sequence[Sequence[Sequence[str]]]
                                      ) -> Tuple[Tuple[Tuple[str, ...], ...], ...]:
    return tuple(tuple(tuple(phrases) for phrases in token_pattern) for token_pattern in token_patterns)

def _expand_base_tokens(pattern_def: Mapping,
                        token_patterns: Sequence[Sequence[Union[str, Sequence[str]]]]
                        ) -> Sequence[Sequence[Sequence[str]]]:
    base_token_map = get_base_item_map(pattern_def, 'base_tokens')
    return tuple(tuple(base_token_map[component] if isinstance(component, str) else component
                       for component in token_pattern) for token_pattern in token_patterns)

def _expand_utterance_patterns_groups(utterance_patterns: Sequence[Sequence[str]],
                                      group_map: Mapping[str, Sequence[str]]
                                      ) -> Tuple[Sequence[Sequence[str]], Sequence[Sequence[Tuple[str, int]]]]:
    expanded_group_map = _expand_group_map(group_map)
    utterance_pattern_expanded_groups = tuple(chain.from_iterable(map(_expand_groups,
                                                                      utterance_patterns, repeat(expanded_group_map))))
    expanded_groups = tuple(chain.from_iterable(map(_create_groups,
                                                    utterance_patterns, repeat(expanded_group_map))))
    return utterance_pattern_expanded_groups, expanded_groups

def _expand_group_map(group_map: Mapping[str, Sequence[str]]) -> Mapping[str, Sequence[Sequence[str]]]:
    group_map_expanded_optional = {name: _expand_optional(pattern) for name, pattern in group_map.items()}
    group_map_expanded_optional_and_range = {name: tuple(chain(*map(_expand_ranges, patterns)))
                                             for name, patterns in group_map_expanded_optional.items()}
    expanded_group_map = {name : _expand_group_map_groups(patterns, group_map_expanded_optional_and_range)
                          for name, patterns in group_map_expanded_optional_and_range.items()}
    return expanded_group_map

def _expand_optional(utterance_pattern: Sequence[str]) -> Sequence[Sequence[str]]:
    optional_parsed = map(_parse_optional, utterance_pattern)
    return cast(Sequence[Sequence[str]], tuple(map(lambda x: tuple(filter(None, x)), product(*optional_parsed))))

def _expand_group_map_groups(patterns: Sequence[Sequence[str]],
                             expanded_group_map: Mapping[str, Sequence[Sequence[str]]]) -> Sequence[Sequence[str]]:
    if not any(token in expanded_group_map for pattern in patterns for token in pattern):
        return patterns
    expanded_patterns = tuple(chain.from_iterable(map(_expand_groups, patterns, repeat(expanded_group_map))))
    return _expand_group_map_groups(expanded_patterns, expanded_group_map)

def _create_groups(utterance_pattern: Sequence[str],
                   expanded_group_map: Mapping[str, Sequence[Sequence[str]]]
                   ) -> Iterable[Sequence[Tuple[str, int]]]:
    groups = map(_get_groups, utterance_pattern, repeat(expanded_group_map))
    return product(*groups)

def _expand_groups(utterance_pattern: Sequence[str],
                   expanded_group_map: Mapping[str, Sequence[Sequence[str]]]
                   ) -> Iterable[Sequence[str]]:
    utterance_pattern_replaced_groups = map(lambda token, group_map: group_map.get(token, ((token,),)),
                                            utterance_pattern, repeat(expanded_group_map))
    expanded_groups = map(tuple, map(chain.from_iterable, product(*utterance_pattern_replaced_groups))) # type: ignore
    return cast(Iterable[Sequence[str]], expanded_groups)

def _get_groups(token: str, expanded_group_map: Mapping[str, Sequence[Sequence[str]]]) -> Iterable[Tuple[str, int]]:
    if token not in expanded_group_map:
        return (('None', 1),)
    return map(lambda token, group: (token, len(group)), repeat(token), expanded_group_map[token])

def _compute_utterance_combo(utterance_pattern: Sequence[str],
                             token_patterns_map: Mapping[str, Sequence[Sequence[Sequence[str]]]]
                             ) -> Sequence[Sequence[str]]:
    expanded_utterance_pattern = tuple(token_patterns_map[token] for token in utterance_pattern)
    utterance_combo = tuple(map(_expand_utterance_components, expanded_utterance_pattern))
    return utterance_combo

def _expand_utterance_components(token_patterns: Sequence[Sequence[Sequence[str]]]) -> Sequence[str]:
    hashable_token_patterns = _convert_token_patterns_to_tuples(token_patterns)
    expanded_token_patterns = tuple(_expand_token_pattern(token_pattern)
                                    for token_pattern in hashable_token_patterns)
    utterance_components = tuple(chain.from_iterable(expanded_token_patterns))
    return utterance_components

@lru_cache(maxsize=None)
def _expand_token_pattern(token_pattern: Tuple[Tuple[str, ...], ...]) -> Sequence[str]:
    return tuple(' '.join(phrase) for phrase in join_combo(token_pattern))
