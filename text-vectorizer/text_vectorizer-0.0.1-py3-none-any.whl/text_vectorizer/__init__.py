#
"""
TextVectorizer

Just like TFIDFVectorizer
"""

from copy import deepcopy
from collections import Counter
import numpy as np
from sklearn.base import BaseEstimator
from tqdm import tqdm


PAD = '<PAD>'
SOS = '<SOS>'
EOS = '<EOS>'
UNK = '<UNK>'


class TextVectorizer(BaseEstimator):
    """
    https://scikit-learn.org/stable/modules/generated/sklearn.base.BaseEstimator.html#sklearn.base.BaseEstimator
    """

    def __init__(self, **param):
        self.word2ind = {}
        self.ind2word = {
            0: PAD,
            1: SOS,
            2: EOS,
            3: UNK,
        }
        self.length = len(self.ind2word)
        self.set_params(**param)

    def get_params(self, deep=False):
        if deep:
            return deepcopy(self.params)
        return self.params

    def set_params(self, **params):
        self.params = {
            'verbose': 0,
            'max_len': None,
            'max_features': None,
        }
        for k in params:
            self.params[k] = params[k]

    def fit(self, raw_documents, y=None):
        max_features = self.params.get('max_features', None)
        verbose = self.params.get('verbose', 0)
        if verbose:
            raw_documents = tqdm(raw_documents)
        counter = Counter()
        for doc in raw_documents:
            counter.update([
                word for word in doc.split(' ')
                if word
            ])
        if isinstance(max_features, int):
            counter = counter.most_common(max_features)
        else:
            counter = list(counter.items())
        for word, _ in counter:
            self.word2ind[word] = self.length
            self.ind2word[self.length] = word
            self.length += 1

    def fit_transform(self, raw_documents, y=None):
        self.fit(raw_documents)
        return self.transform(raw_documents)

    def __len__(self):
        return self.length

    def transform(self, raw_documents, copy=False):
        verbose = self.params.get('verbose', 0)
        gen = self.transform_generator(
            raw_documents, batch_size=1, forever=False)
        if verbose:
            gen = tqdm(gen)
        ret = []
        for x in gen:
            ret.append(x[0])
        return np.array(ret)

    def transform_generator(self, raw_documents, batch_size=32, forever=True):
        max_len = self.params.get('max_len', None)
        batch = []
        while True:
            for doc in raw_documents:
                sent = []
                for word in doc.split(' '):
                    if word:
                        if word in self.word2ind:
                            sent.append(self.word2ind[word])
                        else:
                            sent.append(3)
                if max_len and len(sent) < max_len:
                    sent += [0] * (max_len - len(sent))
                batch.append(np.array(sent))
                if len(batch) >= batch_size:
                    yield np.array(batch)
                    batch = []
            if not forever:
                break

    def inverse_transform(self, X):
        ret = []
        for x in X:
            sent = []
            for xx in x:
                if xx > 0 and xx in self.ind2word:
                    sent.append(self.ind2word[xx])
            ret.append(sent)
        return ret


if __name__ == '__main__':
    docs = [
        'I love you',
        'I hate you very much',
        'I need you',
    ]
    tv = TextVectorizer()
    tv.fit(docs)
    embs = tv.transform(docs)
    print(embs)
    iembs = tv.inverse_transform(embs)
    print(iembs)

    tv = TextVectorizer(verbose=1, max_len=5)
    tv.fit(docs)
    embs = tv.transform(docs)
    print(embs)
    iembs = tv.inverse_transform(embs)
    print(iembs)

    tv = TextVectorizer(verbose=1, max_len=5, max_features=2)
    tv.fit(docs)

    for i, x in enumerate(tv.transform_generator(docs, batch_size=2)):
        print(x)
        if i >= 2:
            break
