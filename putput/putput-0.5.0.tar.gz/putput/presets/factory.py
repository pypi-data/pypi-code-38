from typing import Callable

from putput.presets import displaCy
from putput.presets import iob2
from putput.presets import luis
from putput.presets import stochastic


def get_preset(preset: str) -> Callable:
    """A factory that gets a 'preset' Callable.

    Args:
        preset: the preset's name.

    Returns:
        The return value of calling a preset's 'preset'
        function without arguments.

    Examples:
        >>> from pathlib import Path
        >>> from putput.pipeline import Pipeline
        >>> pattern_def_path = Path(__file__).parent.parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
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
    """
    supported_presets = ('IOB2', 'DISPLACY', 'LUIS', 'STOCHASTIC')
    if preset == 'IOB2':
        return iob2.preset()
    if preset == 'DISPLACY':
        return displaCy.preset()
    if preset == 'LUIS':
        return luis.preset()
    if preset == 'STOCHASTIC': # pragma: no cover
        return stochastic.preset()
    raise ValueError('Unrecoginzed preset. Please choose from the supported presets: {}'.format(supported_presets))
