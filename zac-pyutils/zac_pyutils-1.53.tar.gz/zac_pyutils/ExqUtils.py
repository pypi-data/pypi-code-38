import logging
import datetime
import itertools
from collections import deque

INFO = logging.INFO
WARN = logging.WARN
ERROR = logging.ERROR
DEBUG = logging.DEBUG


def load_file_as_iter(path):
    with open(path, "r+") as f:
        for i in f:
            yield i


def padding(tokens_inp, pad_len=-1, pad="__PAD__"):
    return (tokens_inp + [pad]*pad_len)[:pad_len]


def padding_autoMax(tokens_list_inp, pad="__PAD__"):
    pad_len = max([len(i) for i in tokens_list_inp])
    return [(tokens+[pad]*pad_len)[:pad_len] for tokens in tokens_list_inp]

def zprint(message):
    new_m = "|{}| {}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message)
    print(new_m)


def get_logger(log_file):
    logger = logging.Logger("logger to {}".format(log_file))
    hdlr = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(levelname)s %(lineno)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    return logger


def log2file(message, logger, level=logging.INFO, verbose=False):
    new_m = "|{}| {}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message)
    logger.log(level, new_m)
    if verbose: print(new_m)


def map_on_iter(iter_item, function, chunk_size=100):
    dq = deque()
    while True:
        target = list(itertools.islice(iter_item, chunk_size))
        if len(target) > 0:
            dq.append(function(target))
        else:
            break
    return flat(list(dq))


def flat(inp_list):
    return [item for sublist in inp_list for item in sublist]
