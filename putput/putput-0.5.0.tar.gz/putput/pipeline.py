import random
from copy import deepcopy
from functools import reduce
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict  # pylint: disable=unused-import
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union
from typing import overload

import yaml

from putput.combiner import combine
from putput.expander import expand
from putput.expander import expand_utterance_patterns_ranges_and_groups
from putput.expander import get_base_item_map
from putput.joiner import ComboOptions
from putput.logger import get_logger
from putput.presets.factory import get_preset
from putput.validator import validate_pattern_def

try:
    get_ipython() # type: ignore
    from tqdm import tqdm_notebook as tqdm # pragma: no cover
except NameError:
    from tqdm import tqdm

_E_H_MAP = Mapping[str, Sequence[Callable[[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]],
                                          Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]]]]
_C_H_MAP = Mapping[str, Sequence[Callable]]
_T_UP_KEY = TypeVar('_T_UP_KEY',
                    _C_H_MAP,
                    _E_H_MAP,
                    Mapping[str, ComboOptions])
T_PIPELINE = TypeVar('T_PIPELINE', bound='Pipeline')

class Pipeline:
    """Transforms a pattern definition into labeled data.

    To perform this transformation, initialize 'Pipeline' and
    call 'flow'.

    There are two ways to initialize 'Pipeline': by passing
    in desired arguments or through the use of a 'preset' in
    the method 'from_preset'. 'Presets' instantiate the 'Pipeline'
    with arguments that cover common use cases. As these arguments
    become attributes that the user can modify, using a 'preset' does
    not give up customizability.

    Once 'Pipeline' has been initialized, calling the method 'flow'
    will cause labeled data to flow through 'Pipeline' to the user.

    There are two stages in 'flow'. The first stage, 'expansion', expands
    the pattern definition file into an 'utterance_combo', 'tokens', and 'groups'
    for each utterance pattern. At the end of the first stage,
    if hooks in 'expansion_hooks_map' are specified for the
    current utterance pattern, they are applied in order where the output
    of a previous hook becomes the input to the next hook.

    The second stage, 'combination', yields a sequence of
    'utterance', 'handled_tokens', and 'handled_groups'. This stage
    applies handlers from 'token_handler_map' and 'group_handler_map' and
    is subject to constraints specified in 'combo_options_map'.
    At the end of the second stage, if hooks in 'combo_hooks_map' are
    specified for the current 'utterance_pattern', they are applied
    in order where the output of a previous hook becomes the input
    to the next hook.

    Examples:
        Default behavior

        >>> pattern_def_path = Path(__file__).parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
        >>> dynamic_token_patterns_map = {'ITEM': ('fries',)}
        >>> p = Pipeline(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
        >>> generator = p.flow(disable_progress_bar=True)
        >>> for utterance, tokens, groups in generator:
        ...     print(utterance)
        ...     print(tokens)
        ...     print(groups)
        can she get fries can she get fries and fries
        ('[ADD(can she get)]', '[ITEM(fries)]', '[ADD(can she get)]', '[ITEM(fries)]', '[CONJUNCTION(and)]',
        '[ITEM(fries)]')
        ('{ADD_ITEM([ADD(can she get)] [ITEM(fries)])}', '{ADD_ITEM([ADD(can she get)] [ITEM(fries)])}',
        '{None([CONJUNCTION(and)])}', '{None([ITEM(fries)])}')
        can she get fries may she get fries and fries
        ('[ADD(can she get)]', '[ITEM(fries)]', '[ADD(may she get)]', '[ITEM(fries)]', '[CONJUNCTION(and)]',
        '[ITEM(fries)]')
        ('{ADD_ITEM([ADD(can she get)] [ITEM(fries)])}', '{ADD_ITEM([ADD(may she get)] [ITEM(fries)])}',
        '{None([CONJUNCTION(and)])}', '{None([ITEM(fries)])}')
        may she get fries can she get fries and fries
        ('[ADD(may she get)]', '[ITEM(fries)]', '[ADD(can she get)]', '[ITEM(fries)]', '[CONJUNCTION(and)]',
        '[ITEM(fries)]')
        ('{ADD_ITEM([ADD(may she get)] [ITEM(fries)])}', '{ADD_ITEM([ADD(can she get)] [ITEM(fries)])}',
        '{None([CONJUNCTION(and)])}', '{None([ITEM(fries)])}')
        may she get fries may she get fries and fries
        ('[ADD(may she get)]', '[ITEM(fries)]', '[ADD(may she get)]', '[ITEM(fries)]', '[CONJUNCTION(and)]',
        '[ITEM(fries)]')
        ('{ADD_ITEM([ADD(may she get)] [ITEM(fries)])}', '{ADD_ITEM([ADD(may she get)] [ITEM(fries)])}',
        '{None([CONJUNCTION(and)])}', '{None([ITEM(fries)])}')

        With arguments

        >>> import json
        >>> import random
        >>> def _just_tokens(token: str, _: str) -> str:
        ...     return '[{token}]'.format(token=token)
        >>> def _just_groups(group_name: str, _: Sequence[str]) -> str:
        ...     return '[{group_name}]'.format(group_name=group_name)
        >>> def _add_random_words(utterance: str,
        ...                       handled_tokens: Sequence[str],
        ...                       handled_groups: Sequence[str]
        ...                       ) -> Tuple[str, Sequence[str], Sequence[str]]:
        ...     utterances = utterance.split()
        ...     random_words = ['hmmmm', 'uh', 'um', 'please']
        ...     insert_index = random.randint(0, len(utterances))
        ...     random_word = random.choice(random_words)
        ...     utterances.insert(insert_index, random_word)
        ...     utterance = ' '.join(utterances)
        ...     return utterance, handled_tokens, handled_groups
        >>> def _jsonify(utterance: str,
        ...              handled_tokens: Sequence[str],
        ...              handled_groups: Sequence[str]
        ...              ) -> str:
        ...     return json.dumps(dict(utterance=utterance,
        ...                            handled_tokens=handled_tokens,
        ...                            handled_groups=handled_groups),
        ...                       sort_keys=True)
        >>> def _sample_utterance_combo(utterance_combo: Sequence[Sequence[str]],
        ...                             tokens: Sequence[str],
        ...                             groups: Sequence[Tuple[str, int]]
        ...                             ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
        ...        TOKEN_INDEX = tokens.index('ADD')
        ...        utterance_combo_list = list(utterance_combo)
        ...        sampled_combos = tuple(random.sample(utterance_combo_list.pop(TOKEN_INDEX), 1))
        ...        utterance_combo_list.insert(TOKEN_INDEX, sampled_combos)
        ...        utterance_combo = tuple(utterance_combo_list)
        ...        return utterance_combo, tokens, groups
        >>> token_handler_map = {'ITEM': _just_tokens}
        >>> group_handler_map = {'ADD_ITEM': _just_groups}
        >>> expansion_hooks_map = {'ADD_ITEM, 2, CONJUNCTION, ITEM': (_sample_utterance_combo,)}
        >>> combo_hooks_map = {'ADD_ITEM, 2, CONJUNCTION, ITEM': (_add_random_words, _add_random_words, _jsonify),
        ...                    'DEFAULT': (_jsonify,)}
        >>> combo_options_map = {'DEFAULT': ComboOptions(max_sample_size=2, with_replacement=False)}
        >>> p = Pipeline(pattern_def_path,
        ...              dynamic_token_patterns_map=dynamic_token_patterns_map,
        ...              token_handler_map=token_handler_map,
        ...              group_handler_map=group_handler_map,
        ...              expansion_hooks_map=expansion_hooks_map,
        ...              combo_hooks_map=combo_hooks_map,
        ...              combo_options_map=combo_options_map,
        ...              seed=0)
        >>> for json_result in p.flow(disable_progress_bar=True):
        ...     print(json_result)
        {"handled_groups": ["[ADD_ITEM]", "[ADD_ITEM]", "{None([CONJUNCTION(and)])}", "{None([ITEM])}"],
         "handled_tokens": ["[ADD(may she get)]", "[ITEM]", "[ADD(can she get)]", "[ITEM]", "[CONJUNCTION(and)]",
                            "[ITEM]"],
         "utterance": "may she get fries please can she hmmmm get fries and fries"}
        {"handled_groups": ["[ADD_ITEM]", "[ADD_ITEM]", "{None([CONJUNCTION(and)])}", "{None([ITEM])}"],
         "handled_tokens": ["[ADD(may she get)]", "[ITEM]", "[ADD(may she get)]", "[ITEM]", "[CONJUNCTION(and)]",
                            "[ITEM]"],
         "utterance": "may she get fries may she um um get fries and fries"}

        With a preset

        >>> dynamic_token_patterns_map = {'ITEM': ('fries',)}
        >>> p = Pipeline.from_preset('IOB2',
        ...                          pattern_def_path,
        ...                          dynamic_token_patterns_map=dynamic_token_patterns_map)
        >>> generator = p.flow(disable_progress_bar=True)
        >>> for utterance, tokens, groups in generator:
        ...     print(utterance)
        ...     print(tokens)
        ...     print(groups)
        ...     break
        can she get fries can she get fries and fries
        ('B-ADD I-ADD I-ADD', 'B-ITEM', 'B-ADD I-ADD I-ADD', 'B-ITEM', 'B-CONJUNCTION', 'B-ITEM')
        ('B-ADD_ITEM I-ADD_ITEM I-ADD_ITEM I-ADD_ITEM', 'B-ADD_ITEM I-ADD_ITEM I-ADD_ITEM I-ADD_ITEM', 'B-None',
         'B-None')
    """
    # pylint: disable=attribute-defined-outside-init, too-many-instance-attributes
    def __init__(self,
                 pattern_def_path: Path,
                 *,
                 dynamic_token_patterns_map: Optional[Mapping[str, Sequence[str]]] = None,
                 token_handler_map: Optional[Mapping[str, Callable[[str, str], str]]] = None,
                 group_handler_map: Optional[Mapping[str, Callable[[str, Sequence[str]], str]]] = None,
                 expansion_hooks_map: Optional[_E_H_MAP] = None,
                 combo_hooks_map: Optional[_C_H_MAP] = None,
                 combo_options_map: Optional[Mapping[str, ComboOptions]] = None,
                 seed: Optional[int] = None
                 ) -> None:
        """Instantiates 'Pipeline'.

        Validates the pattern definition, expands utterance patterns used as keys in maps,
        and sets public attributes.

        Args:
            pattern_def_path: See property docstring.

            dynamic_token_patterns_map: See property docstring.

            token_handler_map: See property docstring.

            group_handler_map: See property docstring.

            expansion_hooks_map: See property docstring.

            combo_hooks_map: See property docstring.

            combo_options: See property docstring.

            seed: See property docstring.

        Raises:
            PatternDefinitionValidationError: If the pattern definition file fails
                validation rules in validator.
            yaml.YAMLError: If the pattern definition is invalid yaml.
        """
        self.seed = seed

        pattern_def = _load_pattern_def(pattern_def_path)
        validate_pattern_def(pattern_def)
        self._pattern_def_path = pattern_def_path
        self._pattern_def = pattern_def

        self.dynamic_token_patterns_map = dynamic_token_patterns_map
        self.token_handler_map = token_handler_map
        self.group_handler_map = group_handler_map
        self.expansion_hooks_map = expansion_hooks_map
        self.combo_hooks_map = combo_hooks_map
        self.combo_options_map = combo_options_map

    @property
    def pattern_def_path(self) -> Path:
        """Read-only path to the pattern definition."""
        return self._pattern_def_path

    @property
    def dynamic_token_patterns_map(self) -> Optional[Mapping[str, Sequence[str]]]:
        """The dynamic counterpart to the static section in the pattern definition.
        This mapping between token and token patterns is useful in
        scenarios where tokens and token patterns cannot be known before runtime.
        """
        return self._dynamic_token_patterns_map

    @dynamic_token_patterns_map.setter
    def dynamic_token_patterns_map(self,
                                   token_patterns_map: Optional[Mapping[str, Sequence[str]]]
                                   ) -> None:
        self._dynamic_token_patterns_map = token_patterns_map

    @property
    def token_handler_map(self) -> Optional[Mapping[str, Callable[[str, str], str]]]:
        """A mapping between a token and a function with args (token, phrase to tokenize) that returns a handled token.
        If 'DEFAULT' is specified as the token, the handler will apply to all tokens not otherwise
        specified in the mapping.
        """
        return self._token_handler_map

    @token_handler_map.setter
    def token_handler_map(self, handler_map: Optional[Mapping[str, Callable[[str, str], str]]]) -> None:
        self._token_handler_map = handler_map

    @property
    def group_handler_map(self) -> Optional[Mapping[str, Callable[[str, Sequence[str]], str]]]:
        """A mapping between a group name and a function with args (group name, handled tokens) that
        returns a handled group. If 'DEFAULT' is specified as the group name, the handler will apply to all groups
        not otherwise specified in the mapping.
        """
        return self._group_handler_map

    @group_handler_map.setter
    def group_handler_map(self, handler_map: Optional[Mapping[str, Callable[[str, Sequence[str]], str]]]):
        self._group_handler_map = handler_map

    @property
    def expansion_hooks_map(self) -> Optional[_E_H_MAP]:
        """A mapping between an utterance pattern and hooks to apply after
        the expansion phase. If 'DEFAULT' is specified as the utterance pattern, the hooks
        will apply to all utterance patterns not otherwise specified in the mapping. During,
        'flow', hooks are applied in order where the output of the previous hook becomes
        the input to the next hook.
        """
        return self._expansion_hooks_map

    @expansion_hooks_map.setter
    def expansion_hooks_map(self, hooks_map: Optional[_E_H_MAP]) -> None:
        if hooks_map:
            groups_map = get_base_item_map(self._pattern_def, 'groups')
            self._expansion_hooks_map = _expand_map_with_utterance_pattern_as_key(
                hooks_map, groups_map) # type: Optional[_E_H_MAP]
        else:
            self._expansion_hooks_map = hooks_map

    @property
    def combo_hooks_map(self) -> Optional[_C_H_MAP]:
        """A mapping between an utterance pattern and hooks to apply after
        the combination phase. If 'DEFAULT' is specified as the utterance pattern, the hooks
        will apply to all utterance patterns not otherwise specified in the mapping. During,
        'flow', hooks are applied in order where the output of the previous hook becomes
        the input to the next hook.
        """
        return self._combo_hooks_map

    @combo_hooks_map.setter
    def combo_hooks_map(self, hooks_map: Optional[_C_H_MAP]) -> None:
        if hooks_map:
            groups_map = get_base_item_map(self._pattern_def, 'groups')
            self._combo_hooks_map = _expand_map_with_utterance_pattern_as_key(
                hooks_map, groups_map) # type: Optional[_C_H_MAP]
        else:
            self._combo_hooks_map = hooks_map

    @property
    def combo_options_map(self) -> Optional[Mapping[str, ComboOptions]]:
        """A mapping between an utterance pattern and ComboOptions to apply during
        the combination phase. If 'DEFAULT' is specified as the utterance pattern, the options
        will apply to all utterance patterns not otherwise specified in the mapping.
        """
        return self._combo_options_map

    @combo_options_map.setter
    def combo_options_map(self, options_map: Optional[Mapping[str, ComboOptions]]) -> None:
        if options_map:
            groups_map = get_base_item_map(self._pattern_def, 'groups')
            self._combo_options_map = _expand_map_with_utterance_pattern_as_key(
                options_map, groups_map) # type: Optional[Mapping[str, ComboOptions]]
        else:
            self._combo_options_map = options_map

    @property
    def seed(self) -> Optional[int]:
        """Seed to control random behavior for Pipeline."""
        return self._seed

    @seed.setter
    def seed(self, seed_val: Optional[int]) -> None:
        if seed_val is not None:
            random.seed(seed_val)
            self._seed = seed_val

    @classmethod
    def from_preset(cls: Type[T_PIPELINE],
                    preset: Union[str, Callable, Sequence[Union[str, Callable]]],
                    *args: Any,
                    **kwargs: Any) -> T_PIPELINE:
        """Instantiates 'Pipeline' from a preset configuration.

        There are two ways to use 'from_preset'. The simplest way is to use the
        preset's name. However, presets may have optional arguments that allow
        for more control. In that case, use a call to the preset's method, 'preset',
        with the desired arguments.

        Args:
            preset: A str that is the preset's name, a Callable that is the
                result of calling the preset's 'preset' function, or a Sequence
                of the two. The Callable form allows more control over the
                preset's behavior. If a Sequence is specified, the result of
                calling the presets' 'preset' function may only overlap in
                'combo_hooks_map' and 'expansion_hooks_map'. If there is overlap,
                functions will be applied in the order of the Sequence.

            args: See __init__ docstring.

            kwargs: See __init__ docstring.

        Raises:
            ValueError: If presets or kwargs contain the same keys, and those
                keys are not 'combo_hooks_map' or 'expansion_hooks_map'.

        Returns:
            An instance of Pipeline.

        Examples:
            Preset str

            >>> from pathlib import Path
            >>> from putput.pipeline import Pipeline
            >>> pattern_def_path = Path(__file__).parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
            >>> dynamic_token_patterns_map = {'ITEM': ('fries',)}
            >>> p = Pipeline.from_preset('IOB2',
            ...                          pattern_def_path,
            ...                          dynamic_token_patterns_map=dynamic_token_patterns_map)
            >>> generator = p.flow(disable_progress_bar=True)
            >>> for utterance, tokens, groups in generator:
            ...     print(utterance)
            ...     print(tokens)
            ...     print(groups)
            ...     break
            can she get fries can she get fries and fries
            ('B-ADD I-ADD I-ADD', 'B-ITEM', 'B-ADD I-ADD I-ADD', 'B-ITEM', 'B-CONJUNCTION', 'B-ITEM')
            ('B-ADD_ITEM I-ADD_ITEM I-ADD_ITEM I-ADD_ITEM', 'B-ADD_ITEM I-ADD_ITEM I-ADD_ITEM I-ADD_ITEM',
            'B-None', 'B-None')

            Preset function with arguments

            >>> from putput.presets import iob2
            >>> p = Pipeline.from_preset(iob2.preset(tokens_to_include=('ITEM',), groups_to_include=('ADD_ITEM',)),
            ...                          pattern_def_path,
            ...                          dynamic_token_patterns_map=dynamic_token_patterns_map)
            >>> generator = p.flow(disable_progress_bar=True)
            >>> for utterance, tokens, groups in generator:
            ...     print(utterance)
            ...     print(tokens)
            ...     print(groups)
            ...     break
            can she get fries can she get fries and fries
            ('O O O', 'B-ITEM', 'O O O', 'B-ITEM', 'O', 'B-ITEM')
            ('B-ADD_ITEM I-ADD_ITEM I-ADD_ITEM I-ADD_ITEM', 'B-ADD_ITEM I-ADD_ITEM I-ADD_ITEM I-ADD_ITEM', 'O', 'O')
        """
        if isinstance(preset, str):
            init_kwargs = get_preset(preset)()
        elif isinstance(preset, Sequence):
            warning = ('Presets are not guaranteed to work together. Choose presets that logically fit together. '
                       'When in doubt, check the shapes of the return values of the hooks '
                       'as well the transformations done in the handlers.')
            logger = get_logger(__name__)
            logger.warning(warning)
            for pre in preset: # type: ignore
                if isinstance(pre, str):
                    init_kwargs = get_preset(pre)()
                else:
                    init_kwargs = pre()
                try:
                    accumulated_init_kwargs = _merge_kwargs(accumulated_init_kwargs, init_kwargs)
                except NameError:
                    accumulated_init_kwargs = _merge_kwargs({}, init_kwargs)
            init_kwargs = accumulated_init_kwargs
        else:
            init_kwargs = preset()
        init_kwargs = _merge_kwargs(init_kwargs, kwargs)
        return cls(*args, **init_kwargs)

    def flow(self, *, disable_progress_bar: bool = False) -> Iterable:
        """Generates labeled data one utterance at a time.

        Args:
            disable_progress_bar: Option to display progress of expansion
                and combination stages as the Iterable is consumed.

        Yields:
            Labeled data.

        Examples:
            >>> from pathlib import Path
            >>> from putput.pipeline import Pipeline
            >>> pattern_def_path = Path(__file__).parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
            >>> dynamic_token_patterns_map = {'ITEM': ('fries',)}
            >>> p = Pipeline(pattern_def_path, dynamic_token_patterns_map=dynamic_token_patterns_map)
            >>> generator = p.flow(disable_progress_bar=True)
            >>> for utterance, tokens, groups in generator:
            ...     print(utterance)
            ...     print(tokens)
            ...     print(groups)
            ...     break
            can she get fries can she get fries and fries
            ('[ADD(can she get)]', '[ITEM(fries)]', '[ADD(can she get)]', '[ITEM(fries)]',
            '[CONJUNCTION(and)]', '[ITEM(fries)]')
            ('{ADD_ITEM([ADD(can she get)] [ITEM(fries)])}', '{ADD_ITEM([ADD(can she get)] [ITEM(fries)])}',
            '{None([CONJUNCTION(and)])}', '{None([ITEM(fries)])}')
        """
        for utterance_combo, tokens, groups in self._expand(disable_progress_bar=disable_progress_bar):
            for result in self._combine(utterance_combo,
                                        tokens,
                                        groups,
                                        disable_progress_bar=disable_progress_bar):
                if result is not None:
                    yield result

    def _combine(self,
                 utterance_combo: Sequence[Sequence[str]],
                 tokens: Sequence[str],
                 groups: Sequence[Tuple[str, int]],
                 *,
                 disable_progress_bar: bool = False
                 ) -> Iterable[Tuple[str, Sequence[str], Sequence[str]]]:
        combo_options = _get_combo_options(tokens, self._combo_options_map) if self._combo_options_map else None

        sample_size, combo_gen = combine(utterance_combo,
                                         tokens,
                                         groups,
                                         token_handler_map=self._token_handler_map,
                                         group_handler_map=self._group_handler_map,
                                         combo_options=combo_options)
        with tqdm(combo_gen,
                  desc='Combination...',
                  total=sample_size,
                  disable=disable_progress_bar,
                  leave=False,
                  miniters=1) as pbar:
            for utterance, handled_tokens, handled_groups in pbar:
                if self._combo_hooks_map:
                    result = _execute_hooks(tokens,
                                            (utterance, handled_tokens, handled_groups),
                                            self._combo_hooks_map)
                else:
                    result = (utterance, handled_tokens, handled_groups)
                yield result

    def _expand(self,
                *,
                disable_progress_bar: bool = False
                ) -> Iterable[Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]]:
        ilen, exp_gen = expand(self._pattern_def, dynamic_token_patterns_map=self._dynamic_token_patterns_map)
        with tqdm(exp_gen, desc='Expansion...', total=ilen, disable=disable_progress_bar, miniters=1) as expansion_tqdm:
            for utterance_combo, tokens, groups in expansion_tqdm:
                if self._expansion_hooks_map:
                    utterance_combo, tokens, groups = _execute_hooks(tokens,
                                                                     (utterance_combo, tokens, groups),
                                                                     self._expansion_hooks_map)
                yield utterance_combo, tokens, groups

@overload
def _execute_hooks(tokens: Sequence[str],
                   args: Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]],
                   hooks_map: _E_H_MAP,
                   ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
    # pylint: disable=unused-argument
    pass # pragma: no cover

@overload
def _execute_hooks(tokens: Sequence[str],
                   args: Tuple[str, Sequence[str], Sequence[str]],
                   hooks_map: _C_H_MAP,
                   ) -> Any:
    # pylint: disable=unused-argument
    pass # pragma: no cover

def _execute_hooks(tokens: Sequence[str],
                   args: Union[Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]],
                               Tuple[str, Sequence[str], Sequence[str]]],
                   hooks_map: Union[_E_H_MAP, _C_H_MAP]
                   ) -> Union[Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]], Any]:
    key = ', '.join(tokens)
    if key not in hooks_map:
        key = 'DEFAULT'
    if key in hooks_map:
        args = reduce(lambda args, hook: hook(*args), hooks_map[key], args)
    return args

def _get_combo_options(tokens: Sequence[str],
                       combo_options_map: Mapping[str, ComboOptions]
                       ) -> Optional[ComboOptions]:
    # pylint: disable=no-self-use
    options_map = {} # type: Dict[str, ComboOptions]
    options_map.update(combo_options_map)
    key = ', '.join(tokens)
    return options_map.get(key) or options_map.get('DEFAULT')

def _expand_map_with_utterance_pattern_as_key(map_with_utterance_pattern_as_key: _T_UP_KEY,
                                              groups_map: Mapping[str, Sequence[str]]
                                              ) -> _T_UP_KEY:
    expanded_map = {}
    for key, hooks in map_with_utterance_pattern_as_key.items():
        if key == 'DEFAULT':
            expanded_map[key] = hooks
        else:
            utterance_pattern = key.split(', ')
            expanded_utterance_patterns, _ = expand_utterance_patterns_ranges_and_groups((utterance_pattern,),
                                                                                         groups_map)
            for expanded_utterance_pattern in expanded_utterance_patterns:
                expanded_map[', '.join(expanded_utterance_pattern)] = hooks
    return expanded_map

def _load_pattern_def(pattern_def_path: Path) -> Mapping:
    with pattern_def_path.open(encoding='utf-8') as pattern_def_file:
        pattern_def = yaml.load(pattern_def_file, Loader=yaml.BaseLoader)
    return pattern_def

def _merge_kwargs(accumulated_kwargs: Mapping, kwargs_to_add: Mapping) -> Mapping:
    accumulated_kwargs = dict(deepcopy(accumulated_kwargs))
    hooks_maps = ('expansion_hooks_map', 'combo_hooks_map')
    for key in kwargs_to_add:
        if key in accumulated_kwargs:
            if key in hooks_maps:
                acc_hooks_map = accumulated_kwargs[key]
                kwargs_hooks_map = kwargs_to_add[key]
                for utterance_pattern in kwargs_hooks_map:
                    if utterance_pattern in acc_hooks_map:
                        acc_hooks_map[utterance_pattern] = (acc_hooks_map[utterance_pattern] +
                                                            kwargs_hooks_map[utterance_pattern])
                    else:
                        acc_hooks_map[utterance_pattern] = kwargs_hooks_map[utterance_pattern]
            else:
                raise ValueError('Multiple presets return the key: {}. Only keys in {} may overlap.'.format(key,
                                                                                                            hooks_maps))
        else:
            accumulated_kwargs[key] = kwargs_to_add[key]
    return accumulated_kwargs
