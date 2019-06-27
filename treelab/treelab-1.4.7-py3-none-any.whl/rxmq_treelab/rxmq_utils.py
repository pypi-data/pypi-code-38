import re
from functools import reduce

from rx.subjects import ReplaySubject


def _topic_to_regex(topic: str):
    """
    Convert topic to regex expression
    :param topic:
    :return:
    """
    
    def reduce_func(result, segment, index, arr):
        res = ''
        if arr[index - 1]:
            res = '\\.\\b' if arr[index - 1] != '#' else '\\b'
        if segment == '#':
            res += '[\\s\\S]*'
        elif segment == '*':
            res += '[^.]+'
        else:
            res += segment
        return result + res
    
    return reduce(reduce_func, topic.split('.'))


def compare_topics(topic: str, existing_topic: str) -> bool:
    """
    Compares given topic with existing topic
    :param topic:
    :param existing_topic:
    :return:
    """
    if all([c not in existing_topic for c in ['#', '*']]):
        return topic == existing_topic
    pattern = _topic_to_regex(existing_topic)
    pattern = re.compile(pattern)
    is_match = bool(pattern.match(topic))
    
    return is_match


def find_subject_by_name(subjects: dict, name) -> ReplaySubject:
    """
    
    :param subjects:
    :param name:
    :return:
    """
    if name in subjects:
        return subjects[name]
