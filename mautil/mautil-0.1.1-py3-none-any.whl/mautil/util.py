import os, sys, argparse, time, json, re
import numpy as np
import pickle
from contextlib import contextmanager
from collections import OrderedDict, defaultdict

def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("|".join(map(re.escape, dict.keys())))
    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 

def load_dump(fpath):
    with open(fpath, 'rb') as f:
        data = pickle.load(f)
    return data


def dump(data, fpath):
    with open(fpath, 'wb') as f:
        pickle.dump(data, f)


def load_json(fpath):
    with open(fpath) as f:
        dictionary = json.load(f)
    return dictionary


def dump_json(dictionary, fpath):
    with open(fpath, 'w') as f:
        json.dump(dictionary, f)


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def beam_top(scores, n):
    """

    :param scores: [batch_size, beam_size, N]
    :param n: fetch top n
    :return:
    """
    batch_size, beam_size, N = scores.shape
    batch_inds = np.arange(batch_size)
    scores = np.reshape(scores, [batch_size, -1])  # [batch_size, beam_size*N]
    inds = np.argpartition(scores, -n, -1)[:, -n:]
    scores = scores[batch_inds[:, None], inds]
    sort_ind = np.argsort(scores, -1)
    scores = scores[batch_inds[:, None], sort_ind]
    inds = inds[batch_inds[:, None], sort_ind]  # [batch_size, n]
    beam_ids = inds // N
    inds = inds % N
    return inds, beam_ids, scores

def beam_search(loop_func, beam_size, max_len, init_inputs, init_inds, stop=None, return_top=True):
    """

    :param loop_func
            inputs: next_input,  next_inds [batch_size]
            return: score[batch_size, N], next_input

    :param batch_size:
    :param beam_size:
    :param init_inputs:
    :param max_len:
    :param stop: EOS id
    :return: seqs:[batch_size, beam_size, max_len], lens:[batch_size, beam_size]
    """
    batch_size = init_inputs.shape[0]
    batch_inds = np.arange(batch_size)
    beam_next_inputs = np.stack([init_inputs] * beam_size, 1)
    beam_next_inds = np.stack([init_inds] * beam_size, 1)
    lens = np.zeros([batch_size, beam_size], dtype=np.int32)
    beam_scores = None
    inds = []
    beam_ids = []
    beam_stops = np.zeros([batch_size, beam_size], dtype=np.bool)

    for step in range(max_len):
        scores = [];
        next_inputs = []
        for i in range(beam_size):
            score, next_input = loop_func(beam_next_inputs[:,i], beam_next_inds[:, i])  # score:[batch_size, N], next_input:[batch_size, ::]
            scores.append(score)
            next_inputs.append(next_input)
            #if step==0:  # init
            #    break
        scores = np.stack(scores, 1)  # [batch_size, beam_size, N]
        next_inputs = np.stack(next_inputs, 1)  # [batch_size, beam_size, ::]

        N = scores.shape[-1]
        if beam_scores is None:
            #beam_scores = np.zeros([batch_size, beam_size, N])
            beam_scores = np.zeros(scores.shape)
        scores += beam_scores
        step_inds, step_beam_ids, step_beam_scores = beam_top(scores, beam_size)  # [batch_size, beam_size]
        beam_scores = np.expand_dims(step_beam_scores, -1)
        beam_next_inputs = next_inputs[batch_inds[:, None], step_beam_ids]
        beam_next_inds = step_inds
        if stop is not None:
            beam_stops = beam_stops[batch_inds[:, None], step_beam_ids]
            beam_stops = np.logical_or(beam_stops, step_inds == stop)
            if np.all(beam_stops):
                break
            lens = lens[batch_inds[:, None], step_beam_ids]
            lens[~beam_stops] += 1
        inds.append(step_inds)
        beam_ids.append(step_beam_ids)

    seqs = beam_get_seqs(inds, beam_ids, batch_inds)
    if return_top:
        seqs = seqs[:, -1, :]
        lens = lens[:, -1]
    return seqs, lens

def beam_get_seqs(inds, beam_ids, batch_inds):
    inds = inds[::-1]; beam_ids = beam_ids[::-1]
    seqs = [inds[0]]
    for i in range(len(inds)-1):
        seqs.append(inds[i+1][batch_inds[:, None], beam_ids[i]])
        beam_ids[i+1] = beam_ids[i+1][batch_inds[:, None], beam_ids[i]]
    seqs = seqs[::-1]
    seqs = np.stack(seqs, -1)

    return seqs


def timestamp():
    return time.strftime('%Y%m%d%H%M%S')

@contextmanager
def timer(name):
    t0 = time.time()
    yield
    print('[{}] done in {} s'.format(name, time.time()-t0))


class ArgParser(object):
    @staticmethod
    def add_args(parser):
        parser.add_argument("-m", "--method_name", help="run method name")

    @classmethod
    def load_args(cls):
        parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                         formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
        cls.add_args(parser)
        args = parser.parse_args()
        return args


def parse_model_name(model_names):
    return model_names.replace(' ', '').split(',')


def create_model(name, args, cls, seed=None):
    if args.suffix is not None:
        name = name + '_' + args.suffix
    cfg = {}
    if seed is not None:
        cfg['seed'] = seed
    for k, v in args.__dict__.items():
        if v is not None:
            cfg[k] = v
    model = cls(name=name, cfg=cfg)
    return model


class TrainArgParser(ArgParser):

    @staticmethod
    def add_args(parser):
        parser.add_argument("-m", "--method_or_model", help="run method or model name")
        parser.add_argument("-scoring", "--scoring", action="store_true", help="run score after train")
        parser.add_argument("-nv", "--no_validate", action="store_true", help="do not do validation")
        parser.add_argument("-ov", "--only_validate", action="store_true", help="only do validation")
        parser.add_argument("-nt", "--no_train", action="store_true", help="do not do train")
        parser.add_argument("-ntest", "--no_test", action="store_true", help="do not pred test")
        parser.add_argument("-predicting", "--predicting", action="store_true", help="run predict after train")
        parser.add_argument("-dataset", "--dataset", help="dataset")
        parser.add_argument("-brcfg", "--batch_reader_cfg", type=json.loads, help="data reader cfg")
        parser.add_argument("-d", "--debug", action="store_true", help="debug")
        parser.add_argument("-save", "--save_model", action="store_true", help="save model after train")
        parser.add_argument("-save_log", "--save_log", action="store_true", help="save log to file")
        parser.add_argument("-save_epoch", "--save_epoch", type=int, default=10000000, help="save per epochs")
        parser.add_argument("-ms", "--model_names", help="model names")
        parser.add_argument("-restore", "--restore", action="store_true", help="save")
        parser.add_argument("-s", "--global_step", help="restore global_step")
        parser.add_argument("-suf", "--suffix", help="suffex model name")
        parser.add_argument("-fprefix", "--fprefix", default='', help="prefix of generated name")
        parser.add_argument("-es", "--es", type=float, help="early stop value")
        parser.add_argument("-ed", "--emb_dim", type=int, help="embedding dim")
        parser.add_argument("-lr", "--lr", type=float, help="learning rate")
        parser.add_argument("-l2", "--l2", type=float, help="l2 regularize")
        parser.add_argument("-bs", "--batch_size", type=int, help="batch_size")
        parser.add_argument("-dp", "--dropout", type=float, help="drop out(keep prob)")
        parser.add_argument("-mc", "--min_cnt", type=int, help="minimum count")
        parser.add_argument("-vp", "--vp", type=float, help="valid_percent")
        parser.add_argument("-kfid", "--kfid", help="k fold ID")
        parser.add_argument("-kn", "--kn", type=int, help="k fold num")
        parser.add_argument("-epochs", "--epochs", type=int, help="training epochs")
        parser.add_argument("-tp", "--train_pct", type=float, help="data percent used for train")
        parser.add_argument("-vb", "--verbose", type=int, help="verbose per num of batch")
