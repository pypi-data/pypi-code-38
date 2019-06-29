import functools
import math
import functools

import requests
import numpy as np
from tokenizer_tools.tagset.offset.sequence import Sequence
from tokenizer_tools.tagset.offset.span_set import SpanSet
from tokenizer_tools.tagset.offset.span import Span

from ioflow.corpus_processor.corpus_processor_base import CorpusProcessorBase
from ioflow.corpus import Corpus


def parse(obj):
    # find entity
    entity = None
    for i in obj['annotations']:
        if i['labels_type'] == 'slot':
            entity = i
            break

    # find label class_
    class_ = None
    for i in obj['annotations']:
        if i['labels_type'] == 'classify':
            class_ = i
            break

    span_set = SpanSet()
    for span in entity['entities']:
        span_obj = Span(start=int(span['start_index']), end=(int(span['start_index']) + int(span['slot_len'])), entity=span['slot_type'])
        span_set.append(span_obj)

    label = class_['classify'] if class_ else None
    seq = Sequence(text=[i for i in obj['text']], span_set=span_set, label=label)

    return seq


def get_corpus_count(config):
    r = requests.post(config['data_url'], json={'taskId': config['task_id']})
    parsed_data = r.json()
    return int(parsed_data['attr']['count'])


def get_corpus_data_by_page(config, page_index, page_size):
    r = requests.post(config['data_url'],
                      json={'taskId': config['task_id'], 'currentPage': page_index, 'pageSize': page_size})
    parsed_data = r.json()
    return parsed_data['data']


def run_then_cache_decorator(func):
    memo = None
    @functools.wraps(func)
    def wrapper(*args):
        if not memo:
            memo = func(*args)
        return memo
    return wrapper


@run_then_cache_decorator
def generator_fn(config):
    # default one
    page_size = 10000

    sentence_list = []

    corpus_count = get_corpus_count(config)
    total_page_num = math.ceil(corpus_count / page_size)

    for i in range(1, total_page_num + 1):
        print('fetch corpus > page: {}'.format(i))
        sentence_list.extend(
            get_corpus_data_by_page(config, i, page_size)
        )

    print('fetch corpus > done')

    assert len(sentence_list) == corpus_count

    print('fetch corpus > total count: {}'.format(corpus_count))

    for sentence in sentence_list:
        offset_data = parse(sentence)

        yield offset_data


def request_meta_data(config):
    r = requests.post(config['meta_data_url'], json={'taskId': config['task_id']})
    parsed_data = r.json()

    entity_data = None
    label_data = None
    for i in parsed_data['data']:
        if i['type'] == 'classify' and not label_data:
            label_data = i['labels']
        if i['type'] == 'slot' and not entity_data:
            entity_data = i['slots']

    return {'tags': entity_data, 'labels': label_data}


class HttpCorpusProcessor(CorpusProcessorBase):
    def __init__(self, config):
        super(HttpCorpusProcessor, self).__init__(config)
        self.dataset_mapping = {}

    def prepare(self):
        self.dataset_mapping[Corpus.TRAIN] = functools.partial(generator_fn, self.config)
        self.dataset_mapping[Corpus.EVAL] = None

    def get_generator_func(self, data_set):
        return self.dataset_mapping[data_set]

    def get_meta_info(self):
        return request_meta_data(self.config)


if __name__ == "__main__":
    config = {
        'data_url': 'http://10.43.10.92:8110/algo/corpusManger/getCorpusByTrainingTaskId',
        'meta_data_url': 'http://10.43.10.92:8110/algo/corpusManger/getLabelsInfoByTaskId',
        'task_id': '5ceca57b7c661383bc850fae'
    }

    processor = HttpCorpusProcessor(config)
    processor.prepare()
    gfunc = processor.get_generator_func(Corpus.TRAIN)

    for i in gfunc():
        print(i)

    meta_data = processor.get_meta_info()
    print(meta_data)
