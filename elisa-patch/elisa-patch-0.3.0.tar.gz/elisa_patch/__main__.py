# encoding: utf-8
# Created by chenghaomou at 2019-05-03

import argparse
from functools import partial
import kenlm
import logging
from elisa_patch import *

debug = logging.getLogger("Debugger")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Incorporating dictionary into machine translation script v0.3.0')

    parser.add_argument('f_parallel_flat', type=str, help='File path to  a parallel flat file')
    parser.add_argument('f_lm', type=str, help='File path to  a Ken LM model')
    parser.add_argument('f_eng_vocab', type=str, help="File path to  an English vocabulary file")
    parser.add_argument('f_lexicon', type=str, help="File path to  the lexicon file. Format: ID WORD (POS) GLOSS")
    parser.add_argument('p_lang', type=str, help='Parameter for 3-letter language code')
    parser.add_argument('p_length_ratio', type=int, default=1,
                        help='Parameter for lexicon-translation length ratio, default 1')
    parser.add_argument('p_threshold', type=float, default=0.4,
                        help='Parameter for lexicon-translation threshold, default 0.4')

    parser.add_argument('--p_pos', dest='p_pos', default=False, action='store_true',
                        help="Parameter for whether the lexicon contains POS tags or not")
    parser.add_argument('--f_uroman', type=str, help="File path to  uroman directory")
    parser.add_argument('--f_names', type=str, help="File path to  an english vocabulary file of names")
    parser.add_argument('--p_romanization', dest='p_romanization', default=False, action='store_true',
                        help="Parameter for romanization for oov extraction")
    parser.add_argument('--p_verbose', dest='p_verbose', default=False, action='store_true',
                        help='Parameter for showing log information')

    args = parser.parse_args()

    LM_FILE = args.f_lm
    ENGLISH_VOCAB_FILE = args.f_eng_vocab
    LEXICON_FILE = args.f_lexicon
    FLAT_FILE = args.f_parallel_flat
    NAMES_FILE = args.f_names
    UROMAN_FILE = args.f_uroman
    LANG_PARA = args.p_lang
    LENGTH_RATIO_PARA = args.p_length_ratio
    THRESHOLD_PARA = args.p_threshold
    ROMANIZATION_PARA = args.p_romanization

    if not args.p_verbose:
        logging.disable(logging.WARNING)

    lm = kenlm.Model(LM_FILE)
    english_vocab = load_english_vocab(ENGLISH_VOCAB_FILE)
    foreign_dict = load_lexicon_norm(LEXICON_FILE, pos=args.p_pos)

    if NAMES_FILE:
        english_vocab.update(load_english_vocab(NAMES_FILE))

    ngram_train(foreign_dict, '{}-tf-idf-model'.format(LANG_PARA))

    romanizer = None
    if UROMAN_FILE:
        romanizer = partial(romanize, romanization_path=UROMAN_FILE, language_code=LANG_PARA)

    vectorizer = pickle.loads(open("./{}-tf-idf-model".format(LANG_PARA), "rb").read())
    lev_model = LevSimilarity(foreign_dict, False, None, THRESHOLD_PARA, None)
    n_gram_model = NGramSimilarity(vectorizer, foreign_dict, False, None, THRESHOLD_PARA, lev_model)
    exact_model = ExactSimilarity(foreign_dict, False, None, THRESHOLD_PARA, n_gram_model)

    found = set()
    translated = set()

    for line in open(FLAT_FILE).readlines():
        source, target = line.strip('\n').split('\t')
        oovs = extract_oov(target, source, english_vocab=english_vocab,
                           romanization=ROMANIZATION_PARA)
        best, mods = translate_oov(target,
                                   oovs,
                                   exact_model.search,
                                   scorer=lm.score,
                                   length_ratio=LENGTH_RATIO_PARA)
        if best != target:
            for oov in oovs:
                found.add(oov)
                alt = list(mods[oov].keys())[0]
                trans = mods[oov][alt]
                if oov not in trans:
                    translated.add(oov)
                if romanizer:
                    debug.debug(f"{romanizer(oov)} -> {romanizer(alt)} : {list(trans)}")

        print(f"{source}\t{best}")

    debug.debug(f"Found {len(found)}, translated {len(translated)}")
