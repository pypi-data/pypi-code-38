def entity_position_correct(utterance: str, entity) -> bool:
    start = entity.start
    end = entity.end
    if entity.value == utterance[start: end]:
        return True
    return False


def overlap(entity, next_entity) -> bool:
    return bool(entity.end > next_entity.start)


def msg_entity_wrong_position(utterance: str, entity) -> str:
    start = entity.start
    end = entity.end
    return """
        Utterance position {start} - {end} expected to be {expected},
        but got {result}.
    """.format(
        start=start,
        end=end,
        expected=entity.value,
        result=utterance[start: end],
    )


def msg_entity_overlapping(utterance: str, entity, next_entity) -> str:
    return """
        For utterance {utt}, entity {sv} ends at {se}, and entity {nv} starts at {ns},
        which are overlapping. Currently, uttut doesn't support overlapping or hierachy entities.
    """.format(
        utt=utterance,
        sv=entity.value,
        se=entity.end,
        nv=next_entity.value,
        ns=next_entity.start,
    )
