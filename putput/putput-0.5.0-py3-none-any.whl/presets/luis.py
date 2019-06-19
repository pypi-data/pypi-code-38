import re
from functools import partial
from typing import Callable
from typing import Mapping
from typing import Optional
from typing import Sequence


def preset(*,
           intent_map: Mapping[str, str] = None,
           entities: Optional[Sequence[str]] = None
           ) -> Callable:
    """Configures the Pipeline for LUIS test format.

    Adheres to: https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-tutorial-batch-testing.

    This function should be used as the 'preset' argument of putput.Pipeline instead of
    the 'LUIS' str to specify intents and entities.

    Examples:
        >>> import json
        >>> from pathlib import Path
        >>> from putput.pipeline import Pipeline
        >>> from pprint import pprint
        >>> import random
        >>> random.seed(0)
        >>> pattern_def_path = Path(__file__).parent.parent.parent / 'tests' / 'doc' / 'example_pattern_definition.yml'
        >>> dynamic_token_patterns_map = {'ITEM': ('fries',)}
        >>> intent_map = {'ADD_ITEM, 2, CONJUNCTION, ITEM': 'ADD_INTENT'}
        >>> p = Pipeline.from_preset(preset(intent_map=intent_map, entities=('ITEM',)),
        ...                          pattern_def_path,
        ...                          dynamic_token_patterns_map=dynamic_token_patterns_map)
        >>> for luis_result in p.flow(disable_progress_bar=True):
        ...     print(json.dumps(luis_result, sort_keys=True))
        ...     break
        {"entities": [{"endPos": 17, "entity": "ITEM", "startPos": 12},
                      {"endPos": 35, "entity": "ITEM", "startPos": 30},
                      {"endPos": 45, "entity": "ITEM", "startPos": 40}],
         "intent": "ADD_INTENT",
         "text": "can she get fries can she get fries and fries"}

    Args:
        intent_map: A mapping from an utterance pattern string to a single intent.
            If not specified, the first group's name will be the intent. The value '__DISCARD'
            is reserved.

        entities: A sequence of tokens that are considered entities. If not specified,
            every token will be considered an entity.

    Returns:
        A Callable that when called returns parameters for instantiating a Pipeline.
        This Callable can be passed into putput.Pipeline as the 'preset' argument.
    """
    if intent_map:
        if '__DISCARD' in set(intent_map.values()):
            raise ValueError('__DISCARD is a reserved value.')
    return partial(_preset,
                   intent_map=intent_map,
                   entities=entities)

def _preset(intent_map: Optional[Mapping[str, str]], entities: Optional[Sequence[str]]) -> Mapping:
    combo_hooks_map = {}
    if intent_map is not None: # caller specified intent_map
        if intent_map:
            for pattern, intent in intent_map.items():
                combo_hooks_map[pattern] = (partial(_handle_intents_and_entities, intent=intent, entities=entities),)
        combo_hooks_map['DEFAULT'] = (partial(_handle_intents_and_entities, intent='__DISCARD', entities=entities),)
    else: # caller specified empty intent_map
        combo_hooks_map['DEFAULT'] = (partial(_handle_intents_and_entities, entities=entities),)
    return {
        'combo_hooks_map': combo_hooks_map
    }

def _convert_to_luis_entities(utterance: str,
                              entities: Sequence[str],
                              handled_items: Sequence[str]
                              ) -> Sequence[Mapping]:
    ents = []
    offset = 0
    for handled_item in handled_items:
        label = _token_extractor(handled_item)
        phrase = ' '.join(re.findall(r'\(([^()]+)\)', handled_item))
        start = offset + utterance[offset:].index(phrase)
        end = start + len(phrase)
        if label in entities:
            ent = {
                'entity': label,
                'startPos': start,
                'endPos': end
            }
            ents.append(ent)
        offset = end
    return ents

def _token_extractor(handled_item: str) -> str:
    return handled_item[handled_item.index('[') + 1: handled_item.index('(')]

def _group_name_extractor(handled_group: str) -> str:
    return handled_group[handled_group.index('{') + 1: handled_group.index('(')]

def _handle_intents_and_entities(utterance: str,
                                 handled_tokens: Sequence[str],
                                 handled_groups: Sequence[str],
                                 *,
                                 intent: Optional[str] = None,
                                 entities: Optional[Sequence[str]] = None
                                 ) -> Optional[Mapping]:
    if intent == '__DISCARD':
        return None
    if intent is None:
        intent = _group_name_extractor(handled_groups[0])
    if entities is None:
        entities = list(map(_token_extractor, handled_tokens))
    luis_entities = _convert_to_luis_entities(utterance, entities, handled_tokens)
    return {
        'text': utterance,
        'intent': intent,
        'entities': luis_entities
    }
