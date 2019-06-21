# encoding: utf-8
# Created by chenghaomou at 2019-05-01
import os
import pickle
import subprocess
import unidecode as unidecode

from collections import defaultdict
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer


@lru_cache(None)
def is_ascii(string: str) -> bool:
    return all(ord(c) < 128 for c in string)


@lru_cache(None)
def romanize(string: str, romanization_path: str, language_code: str) -> str:
    cmd = '{}'.format(os.path.join(romanization_path, "bin/uroman.pl"))
    result = subprocess.run([cmd, '-l', language_code], input=string, stdout=subprocess.PIPE, encoding='utf-8')
    return unidecode.unidecode(result.stdout.strip('\n'))


def load_lexicon_norm(path: str, pos: bool = False) -> dict:
    res = defaultdict(set)
    with open(path) as i:
        for line in i:
            if not pos:
                _, word, gloss = line.strip('\n').split('\t')
            else:
                _, word, _, gloss = line.strip('\n').split('\t')

            res[word.strip(' ')].add(gloss.strip(' '))

    return res


def load_english_vocab(path: str) -> set:
    vocab = set(map(lambda x: x.strip('\n').strip().lower(), open(path).readlines()))
    return set(w for w in vocab if is_ascii(w) and ' ' not in w)


def google_translate(text: str, source: str, target: str = "en", credentials: str = None) -> dict:
    from google.cloud import translate
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

    translate_client = translate.Client()
    translation = translate_client.translate(text, source_language=source, target_language=target)
    return translation['translatedText']


def cosine_dist(matrix, vector):
    """
    Compute the cosine distances between each row of matrix and vector.
    """
    import scipy
    v = vector.reshape(1, -1)
    return scipy.spatial.distance.cdist(matrix, v, 'cosine').reshape(-1)


def ngram_train(dictionary: dict, model_path):
    vectorizer = TfidfVectorizer(lowercase=False, ngram_range=(1, 3), analyzer='char')
    words = dictionary.keys()
    vectorizer.fit(words)

    with open(model_path, "wb") as o:
        o.write(pickle.dumps(vectorizer))


def lexicon_translation_cache(func):
    mem = {}

    def wrapper(*args, **kargs):
        token = args[0]
        if token not in mem:
            mem[token] = func(*args, **kargs)
        return mem[token]

    return wrapper
