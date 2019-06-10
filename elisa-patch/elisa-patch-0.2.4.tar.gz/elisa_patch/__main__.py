# encoding: utf-8
# Created by chenghaomou at 2019-05-03

import argparse
from functools import partial
import kenlm
import logging
from elisa_patch import *

debug = logging.getLogger("Debugger")


# def load_dictionary(path: str, pos: bool = True) -> dict:
#     res = defaultdict(set)
#
#     with open(path) as i:
#         for line in i:
#             if not pos:
#                 word, gloss = line.strip('\n').split('\t')
#             else:
#                 word, _, gloss = line.strip('\n').split('\t')
#
#             res[word.strip(' ')].add(gloss.strip(' '))
#
#     return res


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Incorporating dictionary into machine translation script v0.0.1')
    parser.add_argument('elisa_flat', type=str, help='Flat file with parallel sentences are needed to identify OOVs')
    parser.add_argument('lm', type=str, help='Ken LM model path')
    parser.add_argument('eng', type=str, help="English vocabulary file, each line is an English word")
    parser.add_argument('roman', type=str, help="romanization directory")
    parser.add_argument('dict', type=str, help="The dictionary you want to use")
    parser.add_argument('lan', type=str, help='3-letter language code')
    parser.add_argument('length_ratio', type=int, default=1, help='translation length ratio, default 1')
    parser.add_argument('threshold', type=float, default=0.4, help='translation threshold, default 0.4')
    parser.add_argument('--names', type=str, help="names in english")
    parser.add_argument('--romanization', choices=['true', 'false'], help="Romanization for oov extraction")

    args = parser.parse_args()

    LM_PATH = args.lm
    ENGLISH_VOCAB = args.eng
    DICT = args.dict
    FLAT = args.elisa_flat
    NAMES = args.names
    ROMAN = args.roman
    LAN = args.lan
    LENGTH_RATIO = args.length_ratio
    THRESHOLD = args.threshold
    ROMANIZATION = True if args.romanization == 'true' else False

    lm = kenlm.Model(LM_PATH)
    english_vocab = load_english_vocab(ENGLISH_VOCAB)
    foreign_dict = load_lexicon_norm(DICT)

    if NAMES:
        english_vocab.update(load_english_vocab(NAMES))

    ngram_train(foreign_dict, '{}-tf-idf-model'.format(LAN))

    romanizer = partial(romanize, romanization_path=ROMAN, language_code=LAN)

    vectorizer = pickle.loads(open("./{}-tf-idf-model".format(LAN), "rb").read())

    lev_model = LevSimilarity(foreign_dict, False, None, THRESHOLD, None)
    n_gram_model = NGramSimilarity(vectorizer, foreign_dict, False, None, THRESHOLD, lev_model)
    exact_model = ExactSimilarity(foreign_dict, False, None, THRESHOLD, n_gram_model)

    found = set()
    translated = set()
    for line in open(FLAT):
        source, target = line.strip('\n').split('\t')
        oovs = extract_oov(target, source, english_vocab=english_vocab, romanization=ROMANIZATION)
        best, mods = translate_oov(target,
                                   oovs,
                                   exact_model.search,
                                   scorer=lm.score,
                                   length_ratio=LENGTH_RATIO)
        if best != target:
            for oov in oovs:
                found.add(oov)
                alt = list(mods[oov].keys())[0]
                trans = mods[oov][alt]
                if oov not in trans:
                    translated.add(oov)
                debug.debug(f"{romanizer(oov)} -> {romanizer(alt)} : {list(trans)}")

        print(best)

    debug.debug(f"Found {len(found)}, translated {len(translated)}")