something is an ID when:
- multisets, when there is high value overlap with another key OR same name of var
- low linear correlation(comparatively?)
- first, or last var index?
- all unique values, or groups

something is continuous when:
- numeric, more than 10 values, has some linear correlation?

something is discrete when:
- numeric, < 10 values, has some linear correlation

something is categorical when:
- string, number of unique values < 100
- numeric, number of unique values < 10, no correlation(difference with discrete is if we want to sparse it)

something is corpus when:
- string, after CountVect it has overlap contains spaces probably

something is a date when:
- can be parsed as date, either - , / or ' '
- year:
    max 100 unique values, all between 1900 - 2100
- month:
    1 - 12 only, and year found
- day:
    1 - 31, and month or year found


numeric, ID                    converts to        empty
numeric, continuous            converts to        scale(float(1)), sparse(ohe(bins(m)))
numeric, discrete              converts to        scale(float(1)), sparse(ohe(m))
numeric, categorical           converts to        ohe(m), sparse(ohe(m))
numeric, date                  converts to
string, categorical            converts to        ohe(m), sparse(ohe(m))
string, corpus                 converts to
string, ID                     converts to
date                           converts to        float(4), sparse(Y, M, D, S)


numeric, continuous, nomiss       impute, scale
numeric, continuous, miss
numeric, discrete, nomiss
numeric, discrete, miss
numeric, date, nomiss
numeric, date, miss
string, categorical
string, corpus

import scipy.sparse

scipy.sparse.csr_matrix(X)

decide if ID, 'probably no ID, otherwise most likely: <>', 'most likely <>'


def is_sorted(l):
    return all(l[i] <= l[i + 1] for i in range(len(l) - 1))


def is_float(x)
    try:
        if int(x) != float(x):
            return True
    except ValueError:
        pass
    return False


def find_id_in_df(m, columns=None):
    ids = []
    mscore = 0
    for i, c in enumerate(m.T):
        c = c[:10000]
        if is_float(c[0]):
            continue
        score = 0
        if columns is not None:
            if 'id' in columns[i].lower():
                score += 1
        if is_sorted(c):
            score += 1
        # even if 'nan' it wouldn't be likely to be id
        if len(c) == len(set(c)):
            score += 1
        ids.append((i, score))
        mscore = max(mscore, score)
    if mscore > 0:
        return [i[0] for i in ids if mscore == i[1]]
    return None


#

(dense, string, categorical):
string, categorical -> DictVectorizer(sparse=False)
(sparse, string, categorical):
string, categorical -> DictVectorizer(sparse=False)

sniffer.consider_max_values

from collections import namedtuple

allowed_subclasses = namedtuple('AllowedSubclasses',
                                'id continuous discrete categorical date corpus')
allowed_subclasses.__new__.__defaults__ = (None, None, None, None, None, None)
