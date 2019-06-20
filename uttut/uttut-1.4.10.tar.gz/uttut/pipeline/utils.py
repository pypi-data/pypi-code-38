from typing import List, Tuple

from uttut.elements import Datum, Intent, Entity
from uttut import ENTITY_LABEL


def unpack_datum(datum: Datum) -> Tuple[str, List[int], List[int]]:

    utterance = datum.utterance
    uttlen = len(utterance)

    # intent
    intent_labels = [intent.label for intent in datum.intents]

    # entity
    entity_labels = [ENTITY_LABEL['NOT_ENTITY']] * uttlen
    for entity in datum.entities:
        label = entity.label
        for ind in range(entity.start, entity.end):
            entity_labels[ind] = label

    return utterance, intent_labels, entity_labels


def pack_to_datum(utterance: str, intent_labels: List[int], entity_labels: List[int]) -> Datum:

    if len(utterance) != len(entity_labels):
        raise ValueError('utterance and entity_labels are not compatible')

    # intent
    intents = [Intent(intent_label) for intent_label in sorted(set(intent_labels))]

    # entity
    entities = []
    start_indices = _get_meaningful_start_indices(entity_labels)
    end_indices = _get_meaningful_start_indices(entity_labels[::-1])
    for start, end in zip(start_indices, end_indices[::-1]):
        real_end = len(utterance) - end
        entity = Entity(
            start=start,
            end=real_end,
            value=utterance[start: real_end],
            label=entity_labels[start],
        )
        entities.append(entity)

    # datum
    return Datum(utterance=utterance, intents=intents, entities=entities)


def _get_meaningful_start_indices(labels: List[int]) -> List[int]:
    indices = _get_start_indices(labels)
    j = 0
    for ind in indices:
        if labels[ind] != ENTITY_LABEL['NOT_ENTITY']:
            indices[j] = ind
            j += 1
    return indices[: j]


def _get_start_indices(labels: List[int]) -> List[int]:
    current_label = labels[0]
    indices = [0]
    for i, label in enumerate(labels):
        if label != current_label:
            indices.append(i)
            current_label = label
    print(indices)
    return indices
