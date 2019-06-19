import itertools
import re
from functools import reduce
from typing import Any
from typing import Mapping
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Union

RANGE_REGEX = r'^\d+(\-\d+)?$'
OPTIONAL_REGEX = r'^\(\|?\w+(\|\w+)*\)$'
_ALL_VALID_REGEX = r'(^[\w\|\(\)]+$|^\d+(\-\d+)?$)'
_TOKEN_REGEX = r'^[^\(\)\|]+$'
_RESERVED_TOKEN = 'none'

class PatternDefinitionValidationError(Exception):
    """Exception that describes an invalid pattern defintion."""

def _validate_instance(item: Any, instance: Any, err_msg: str) -> None:
    if not item or not isinstance(item, instance):
        raise PatternDefinitionValidationError(err_msg)

def _validate_pattern_with_range_or_optional(pattern: Sequence[str]) -> None:
    is_previous_word_range = False
    for index, word in enumerate(pattern):
        if not re.match(_ALL_VALID_REGEX, word):
            raise PatternDefinitionValidationError('Not valid syntax: {}'.format(word))
        if re.match(RANGE_REGEX, word):
            if is_previous_word_range:
                raise PatternDefinitionValidationError('Can\'t have two ranges in a row: {}'.format(pattern))
            is_previous_word_range = True
            if index == 0:
                raise PatternDefinitionValidationError('First token is a range: {}'.format(pattern))
            min_range, max_range = _parse_range_token(word)
            if min_range and min_range >= max_range:
                raise PatternDefinitionValidationError('Not valid range syntax, max must be > min: {}'.format(word))
        else:
            is_previous_word_range = False
        if '(' in word or '|' in word or ')' in word:
            if not re.match(OPTIONAL_REGEX, word):
                raise PatternDefinitionValidationError('Not valid optional syntax: {}'.format(word))

def _check_for_overlap(token_sets: Sequence[Set[str]]) -> None:
    for token_set_1, token_set_2 in itertools.combinations(token_sets, 2):
        overlap = token_set_1 & token_set_2
        if overlap:
            err_msg = ('{} cannot be defined as both static and dynamic tokens'.format(overlap))
            raise PatternDefinitionValidationError(err_msg)

def _check_for_reserved_null_token(token_sets: Sequence[Set[str]]) -> None:
    all_tokens = reduce(lambda x, y: x | y, token_sets)
    for token in all_tokens:
        if token.lower() == _RESERVED_TOKEN:
            raise PatternDefinitionValidationError('Using reserved token: {}'.format(_RESERVED_TOKEN))

def _check_for_undefined_tokens(token_set_to_check: Set[str],
                                defined_token_sets: Sequence[Set[str]],
                                ) -> None:
    defined_tokens = set.union(*defined_token_sets)
    undefined_tokens = token_set_to_check - defined_tokens
    undefined_tokens_and_not_range = {token for token in undefined_tokens
                                      if not re.match(RANGE_REGEX, token) and '|' not in token}
    if undefined_tokens_and_not_range:
        err_msg = 'Undefined tokens: {}'.format(undefined_tokens_and_not_range)
        raise PatternDefinitionValidationError(err_msg)

def _validate_base_pattern(pattern_def: Mapping, key: str) -> None:
    if key in pattern_def:
        _validate_instance(pattern_def[key], list, 'invalid {}'.format(key))
        for base_token_dict in pattern_def[key]:
            _validate_instance(base_token_dict, dict, 'invalid {}'.format(key))
            base_token_group_name = next(iter(base_token_dict.keys()))
            if not base_token_dict[base_token_group_name]:
                raise PatternDefinitionValidationError('{} is not defined'.format(base_token_group_name))
            for base_token in base_token_dict[base_token_group_name]:
                _validate_instance(base_token, str, 'token must be string or int')
                if key == 'base_tokens':
                    if not re.match(_TOKEN_REGEX, base_token):
                        error_msg = 'Invalid token: {}'.format(base_token)
                        raise PatternDefinitionValidationError(error_msg)
            if key == 'groups':
                _validate_pattern_with_range_or_optional(base_token_dict[base_token_group_name])

def _validate_utterance_patterns(pattern_def: Mapping) -> None:
    for utterance_pattern_tokens in pattern_def['utterance_patterns']:
        _validate_instance(utterance_pattern_tokens, list, 'utterance_patterns must contain a list')
        for token in utterance_pattern_tokens:
            _validate_instance(token, str, 'token must be string or int')
        _validate_pattern_with_range_or_optional(utterance_pattern_tokens)

def _validate_component(component: Union[list, str], base_tokens: Set[str]) -> None:
    err_msg = 'Invalid token: {}'
    if isinstance(component, list):
        _validate_instance(component, list, err_msg.format(str(component)))
        for word in component:
            _validate_instance(word, str, err_msg.format(word))
            if not re.match(_TOKEN_REGEX, word):
                raise PatternDefinitionValidationError(err_msg.format(word))
    else:
        _validate_instance(component, str, err_msg.format(component))
        if not re.match(_TOKEN_REGEX, component):
            raise PatternDefinitionValidationError(err_msg.format(component))
        if component not in base_tokens:
            raise PatternDefinitionValidationError(err_msg)

def _validate_static_token_patterns(static_maps: list, base_tokens: Set[str]) -> None:
    err_msg = 'invalid static token_patterns'
    for token_patterns_dict in static_maps:
        _validate_instance(token_patterns_dict, dict, err_msg)
        for token_patterns in token_patterns_dict.values():
            _validate_instance(token_patterns, list, err_msg)
            for token_pattern in token_patterns:
                _validate_instance(token_pattern, list, err_msg)
                for component in token_pattern:
                    _validate_component(component, base_tokens)

def _validate_token_patterns(pattern_def: Mapping, base_tokens: Set[str]) -> None:
    _validate_instance(pattern_def['token_patterns'], list, 'invalid token_patterns')
    for token_type_dict in pattern_def['token_patterns']:
        _validate_instance(token_type_dict, dict, 'invalid token_patterns')
        if 'static' in token_type_dict:
            _validate_static_token_patterns(token_type_dict['static'], base_tokens)
        elif 'dynamic' in token_type_dict:
            for token in token_type_dict['dynamic']:
                _validate_instance(token, str, 'invalid dynamic token_patterns')
        else:
            raise PatternDefinitionValidationError('token type must be either dynamic or static')

def _get_base_keys(pattern_def: Mapping, key: str) -> Set[str]:
    if key not in pattern_def:
        return set()
    return {base for base_dict in pattern_def[key] for base in base_dict}

def _parse_range_token(range_token: str) -> Tuple[Union[int, None], int]:
    if '-' not in range_token:
        return None, int(range_token)
    min_range, max_range = range_token.split('-')
    return int(min_range), int(max_range) + 1

def validate_pattern_def(pattern_def: Mapping) -> None:
    """Ensures the pattern definition is defined properly.

    Args:
        pattern_def: A dictionary representation of the pattern definition.

    Raises:
        PatternDefinitionValidationError: If the pattern definition file is invalid.

    Examples:
        >>> from pathlib import Path
        >>> from putput.pipeline import _load_pattern_def
        >>> pattern_def_path = Path(__file__).parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
        >>> pattern_def = _load_pattern_def(pattern_def_path)
        >>> validate_pattern_def(pattern_def)
    """
    if not pattern_def:
        raise PatternDefinitionValidationError('Pattern definition cannot be empty.')
    if not ({'token_patterns', 'utterance_patterns'} <= set(pattern_def)):
        err_msg = 'At the top level, token_patterns and utterance_patterns must exist.'
        raise PatternDefinitionValidationError(err_msg)

    base_tokens = _get_base_keys(pattern_def, 'base_tokens')
    groups = _get_base_keys(pattern_def, 'groups')

    _validate_token_patterns(pattern_def, base_tokens)
    _validate_utterance_patterns(pattern_def)
    _validate_base_pattern(pattern_def, 'base_tokens')
    _validate_base_pattern(pattern_def, 'groups')

    static_tokens = {
        static_token
        for token_type_dict in pattern_def['token_patterns']
        for token_type in token_type_dict
        if token_type == 'static'
        for static_token_to_token_patterns in token_type_dict['static']
        for static_token in static_token_to_token_patterns.keys()
    }
    dynamic_tokens = {
        dynamic_token
        for token_type_dict in pattern_def['token_patterns']
        for token_type in token_type_dict
        if token_type == 'dynamic'
        for dynamic_token in token_type_dict['dynamic']
    }
    utterance_pattern_tokens = {
        utterance_pattern_token
        for utterance_pattern_tokens in pattern_def['utterance_patterns']
        for utterance_pattern_token in utterance_pattern_tokens
    }
    _check_for_overlap([static_tokens, dynamic_tokens, base_tokens, groups])
    _check_for_undefined_tokens(utterance_pattern_tokens, [static_tokens, dynamic_tokens, groups])
    _check_for_reserved_null_token([static_tokens, dynamic_tokens, base_tokens, groups])
    if 'groups' in pattern_def:
        for base_token_dict in pattern_def['groups']:
            group_values = set(list(base_token_dict.values())[0])
            _check_for_undefined_tokens(group_values, [static_tokens, dynamic_tokens, groups])
