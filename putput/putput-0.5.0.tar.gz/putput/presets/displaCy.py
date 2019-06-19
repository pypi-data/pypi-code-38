import re
from typing import Callable
from typing import Mapping
from typing import Sequence
from typing import Tuple


def preset() -> Callable:
    """Configures the Pipeline for the 'DISPLACY' ENT format.

    The ENT format: https://spacy.io/usage/visualizers#manual-usage

    Returns:
        A Callable that when called returns parameters for instantiating a Pipeline.
        This Callable can be passed into putput.Pipeline as the 'preset' argument.

    Examples:
        >>> import json
        >>> from pathlib import Path
        >>> from putput.pipeline import Pipeline
        >>> pattern_def_path = Path(__file__).parent.parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
        >>> dynamic_token_patterns_map = {'ITEM': ('fries',)}
        >>> p = Pipeline.from_preset(preset(),
        ...                          pattern_def_path,
        ...                          dynamic_token_patterns_map=dynamic_token_patterns_map)
        >>> generator = p.flow(disable_progress_bar=True)
        >>> for token_visualizer, group_visualizer in generator:
        ...     print(json.dumps(token_visualizer, sort_keys=True))
        ...     print(json.dumps(group_visualizer, sort_keys=True))
        ...     break
        {"ents": [{"end": 11, "label": "ADD", "start": 0},
                {"end": 17, "label": "ITEM", "start": 12},
                {"end": 29, "label": "ADD", "start": 18},
                {"end": 35, "label": "ITEM", "start": 30},
                {"end": 39, "label": "CONJUNCTION", "start": 36},
                {"end": 45, "label": "ITEM", "start": 40}],
        "text": "can she get fries can she get fries and fries",
        "title": "Tokens"}
        {"ents": [{"end": 17, "label": "ADD_ITEM", "start": 0},
                {"end": 35, "label": "ADD_ITEM", "start": 18},
                {"end": 39, "label": "None", "start": 36},
                {"end": 45, "label": "None", "start": 40}],
                "text": "can she get fries can she get fries and fries",
                "title": "Groups"}
    """
    return _preset

def _preset() -> Mapping:
    combo_hooks_map = {}
    combo_hooks_map['DEFAULT'] = (_handled_tokens_to_ent, _handled_groups_to_ent, _convert_to_displaCy_visualizer)
    return {
        'combo_hooks_map': combo_hooks_map
    }

def _convert_to_ents(utterance: str,
                     handled_items: Sequence[str],
                     label_extractor: Callable[[str], str]
                     ) -> Sequence[Mapping]:
    ents = []
    offset = 0
    for handled_item in handled_items:
        label = label_extractor(handled_item)
        phrase = ' '.join(re.findall(r'\(([^()]+)\)', handled_item))
        start = offset + utterance[offset:].index(phrase)
        end = start + len(phrase)
        ent = {
            'start': start,
            'end': end,
            'label': label
        }
        ents.append(ent)
        offset = end
    return ents

def _handled_groups_to_ent(utterance: str,
                           handled_tokens: Sequence,
                           handled_groups: Sequence[str]
                           ) -> Tuple[str, Sequence, Sequence[Mapping]]:
    label_extractor = lambda s: s[s.index('{') + 1: s.index('(')]
    ents = _convert_to_ents(utterance, handled_groups, label_extractor)
    return utterance, handled_tokens, ents

def _handled_tokens_to_ent(utterance: str,
                           handled_tokens: Sequence[str],
                           handled_groups: Sequence
                           ) -> Tuple[str, Sequence[Mapping], Sequence]:
    label_extractor = lambda s: s[s.index('[') + 1: s.index('(')]
    ents = _convert_to_ents(utterance, handled_tokens, label_extractor)
    return utterance, ents, handled_groups

def _convert_to_displaCy_visualizer(utterance: str,
                                    handled_tokens: Sequence[Mapping],
                                    handled_groups: Sequence[Mapping]
                                    ) -> Tuple[Mapping, Mapping]:
    # https://spacy.io/usage/visualizers#manual-usage
    # ent usage
    token_visualizer = {
        'text': utterance,
        'ents': handled_tokens,
        'title': 'Tokens'
    }
    group_visualizer = {
        'text': utterance,
        'ents': handled_groups,
        'title': 'Groups'
    }
    return (token_visualizer, group_visualizer)
