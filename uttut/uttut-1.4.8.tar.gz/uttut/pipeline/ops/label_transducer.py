from typing import List

from collections import Counter

from uttut import ENTITY_LABEL


def get_most_common(labels: List[int], output_size: int) -> List[int]:
    counter = Counter(labels)
    common_label = counter.most_common()[0][0]
    return [common_label] * output_size


def get_most_common_except_not_entity(labels: List[int], output_size: int) -> List[int]:
    meaningful_labels = [label for label in labels if label != ENTITY_LABEL['NOT_ENTITY']]
    if len(meaningful_labels) == 0:
        return get_not_entity(labels, output_size)
    return get_most_common(meaningful_labels, output_size)


def get_not_entity(labels: List[int], output_size: int) -> List[int]:
    return [ENTITY_LABEL['NOT_ENTITY']] * output_size
