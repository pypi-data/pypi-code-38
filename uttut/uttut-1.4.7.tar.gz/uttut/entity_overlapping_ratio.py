from .elements import Datum, Entity
from .exceptions import DifferentUtterance
from . import ENTITY_LABEL

NOT_ENTITY = ENTITY_LABEL['NOT_ENTITY']


def check_utter_index_in_entity(
        utter_ind: int,
        entity: Entity,
        ent_list: list,
    ) -> bool:
    if utter_ind >= entity.start and utter_ind < entity.end:
        ent_list.append(entity.label)
    elif utter_ind >= entity.end:
        return False
    else:
        ent_list.append(NOT_ENTITY)
    return True


def expand_entity_to_list(
        datum: Datum,
    ) -> list:
    ent_list = []
    ent_ind = 0
    utter_len = len(datum.utterance)
    max_ent_ind = len(datum.entities)

    ind = -1
    while True:
        ind += 1
        if ind >= utter_len:
            break
        if ent_ind >= max_ent_ind:
            ent_list.append(NOT_ENTITY)
            continue
        cur_ent = datum.entities[ent_ind]
        if not check_utter_index_in_entity(ind, cur_ent, ent_list):
            ent_ind += 1
            ind -= 1
    return ent_list


def penalty_on_same_entity_or_not(
        ent1: int,
        ent2: int,
        wrong_penalty_rate: float,
    ) -> float:
    if ent1 == ent2:
        return 0
    else:
        if ent1 == NOT_ENTITY or ent2 == NOT_ENTITY:
            return 1
        else:
            return wrong_penalty_rate


def entity_overlapping_ratio(
        datum1: Datum,
        datum2: Datum,
        wrong_penalty_rate: float,
    ) -> float:
    if not datum1.has_same_utterance_as(datum2):
        raise DifferentUtterance("""Only two data with same utterance can be compared
got:
{}
{}
""".format(datum1.utterance, datum2.utterance))

    penalty = 0.
    ent1_list = expand_entity_to_list(datum1)
    ent2_list = expand_entity_to_list(datum2)
    for ent1, ent2 in zip(ent1_list, ent2_list):
        penalty += penalty_on_same_entity_or_not(
            ent1, ent2, wrong_penalty_rate)
    score = 1 - penalty / len(datum1.utterance)
    return score
