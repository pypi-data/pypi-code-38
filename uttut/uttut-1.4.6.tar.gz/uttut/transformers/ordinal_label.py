import json
from typing import Mapping

from .. import NOT_ENTITY
from ..elements import Datum, Intent, Entity
from .base import BaseTransformer


class OrdinalLabel(BaseTransformer):
    """Transformer that turn raw label into integers"""

    def __init__(
            self,
            intent2index: Mapping[str, int],
            entity2index: Mapping[str, int],
            not_entity_index: int = 0,
        ):
        if OrdinalLabel.is_valid_mapping(intent2index):
            self._intent2index = intent2index
        else:
            raise ValueError('Intent mapping is not valid.')

        self._not_entity_index = not_entity_index
        if OrdinalLabel.is_valid_mapping({**entity2index, NOT_ENTITY: not_entity_index}):
            self._entity2index = entity2index
        else:
            raise ValueError('Entity mapping is not valid.')

    @staticmethod
    def is_valid_mapping(str2idx: Mapping[str, int]) -> bool:
        idxs = sorted(list(str2idx.values()))
        return idxs == list(range(len(idxs)))

    @property
    def not_entity_index(self):
        return self._not_entity_index

    def index2entity(self, idx):
        for entity, current_idx in self._entity2index.items():
            if idx == current_idx:
                return entity
        else:
            raise KeyError("Entity index {} not found".format(idx))

    def index2intent(self, idx):
        for intent, current_idx in self._intent2index.items():
            if idx == current_idx:
                return intent
        else:
            raise KeyError("Intent index {} not found".format(idx))

    def humanize(self, datum):
        raw_dict = {}
        raw_dict['utterance'] = datum.utterance
        raw_dict['intent'] = {
            'names': [self.index2intent(intent.label) for intent in datum.intents],
        }
        if datum.has_entities():
            entities = []

            for entity in datum.entities:
                raw_entity = {
                    'name': self.index2entity(entity.label),
                    'start': entity.start,
                    'end': entity.end,
                }
                if not entity.no_replacements():
                    raw_entity['replacements'] = list(entity.replacements)
                entities.append(raw_entity)
            raw_dict['entities'] = entities
        return raw_dict

    def machanize(self, raw_dict):
        utterance = raw_dict['utterance']
        intents = [Intent(self._intent2index[name]) for name in raw_dict['intent']['names']]
        entities = []
        if 'entities' in raw_dict:
            for raw_entity in raw_dict['entities']:
                label = self._entity2index[raw_entity['name']]
                start = raw_entity['start']
                end = raw_entity['end']
                value = utterance[start: end]
                replacements = raw_entity.get('replacements')
                entities.append(Entity(
                    label,
                    value,
                    start,
                    end,
                    replacements,
                ))
        datum = Datum(utterance, intents, entities)
        return datum

    def serialize(self) -> str:
        serializable = {
            'intent2index': self._intent2index,
            'entity2index': self._entity2index,
            'not_entity_index': self._not_entity_index,
        }
        return json.dumps(serializable)

    @classmethod
    def deserialize(cls, serialized):
        loaded = json.loads(serialized)
        intent2index = loaded['intent2index']
        entity2index = loaded['entity2index']
        not_entity_index = loaded['not_entity_index']
        return cls(intent2index, entity2index, not_entity_index)

    @classmethod
    def from_raw_dictionary(cls, raw_dict, not_entity_index=0):
        if not isinstance(not_entity_index, int):
            raise TypeError(f"not_entity_index must be integer, got {not_entity_index}"
                            f"with type{type(not_entity_index)}")
        intents = [i for d in raw_dict['data'] for i in d['intent']['names']]
        entities = [e['name'] for d in raw_dict['data'] for e in d.get('entities', [])]

        intent2index = {}
        idx = 0
        for intent in intents:
            if intent not in intent2index:
                intent2index[intent] = idx
                idx += 1
            continue

        entity2index = {}
        idx = 0
        for entity in entities:
            if entity not in entity2index:
                if idx == not_entity_index:
                    idx += 1
                entity2index[entity] = idx
                idx += 1
            continue

        return cls(intent2index, entity2index, not_entity_index=not_entity_index)
