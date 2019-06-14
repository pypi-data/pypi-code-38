from typing import List

from uttut.elements import Datum


def get_unique_entities(
        data: List[Datum],
    ) -> List:
    unique_entities = []
    for datum in data:
        if datum.entities is not None:
            for entity in datum.entities:
                unique_entities.append(entity.label)
    unique_entities = list(set(unique_entities))
    return unique_entities
