# encoding: utf-8
# Created by chenghaomou at 2019-05-03

import argparse
from functools import partial
import kenlm
import logging
from elisa_patch import *

debug = logging.getLogger("Debugger")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Incorporating dictionary into machine translation script v0.0.1')

    parser.add_argument('parallel_flat', type=str, help='Flat file with parallel sentences are needed to identify OOVs')
    parser.add_argument('lm', type=str, help='Ken LM model path')
    parser.add_argument('eng_vocab', type=str, help="English vocabulary file, each line is an English word")
    parser.add_argument('lexicon', type=str, help="The lexicon you want to use. Format: ID WORD (POS) GLOSS")
    parser.add_argument('lang', type=str, help='3-letter language code')
    parser.add_argument('length_ratio', type=int, default=1, help='lexicon-translation length ratio, default 1')
    parser.add_argument('threshold', type=float, default=0.4, help='lexicon-translation threshold, default 0.4')

    parser.add_argument('--pos', type=bool, help="Whether the lexicon contains POS tags or not")
    parser.add_argument('--uroman', type=str, help="uroman directory")
    parser.add_argument('--names', type=str, help="english vocabulary for names")
    parser.add_argument('--romanization', choices=['true', 'false'], help="Romanization for oov extraction")

    args = parser.parse_args()

    LM_PATH = args.lm
    ENGLISH_VOCAB = args.eng_vocab
    LEXICON = args.lexicon
    FLAT = args.parallel_flat
    NAMES = args.names
    UROMAN = args.uroman
    LANG = args.lang
    LENGTH_RATIO = args.length_ratio
    THRESHOLD = args.threshold
    ROMANIZATION = True if args.romanization == 'true' else False
    lm = kenlm.Model(LM_PATH)

    english_vocab = load_english_vocab(ENGLISH_VOCAB)
    foreign_dict = load_lexicon_norm(LEXICON, pos=args.pos)

    if NAMES:
        english_vocab.update(load_english_vocab(NAMES))

    ngram_train(foreign_dict, '{}-tf-idf-model'.format(LANG))

    if UROMAN:
        romanizer = partial(romanize, romanization_path=UROMAN, language_code=LANG)

    vectorizer = pickle.loads(open("./{}-tf-idf-model".format(LANG), "rb").read())

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
                if romanizer:
                    debug.debug(f"{romanizer(oov)} -> {romanizer(alt)} : {list(trans)}")

        if romanizer:
            print(best)

    debug.debug(f"Found {len(found)}, translated {len(translated)}")