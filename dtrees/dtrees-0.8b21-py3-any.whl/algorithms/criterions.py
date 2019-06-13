from numpy import log2, log, sum, round, nonzero, append, square, unique, power
import pandas as pd

SMALL = 1e-3


# region Entropy

def info(data, target, attr):
    """
    :param data: pandas DataFrame
    :param target: target column name
    :param attr: current attribute
    :return: entropy
    """
    data = data.loc[data[attr].notnull()]
    freq = data[target].value_counts().values
    p = freq / data.shape[0]
    return round(-sum(p * log2(p)), 3)


def splitInfo(data, target):
    freq = pd.DataFrame(data.groupby([target])['__W__'].sum()).unstack().fillna(0).values
    miss = data.loc[data[target].isnull()].shape[0]
    if miss > 0:
        freq = append(freq, [miss], axis=0)
    p = freq / data.shape[0]
    return round(-sum(p * log2(p)), 3)


def req_bits(row, N):
    n = row.sum()
    vals = row.values / n
    vals = vals[nonzero(vals)]
    return -sum(vals * log2(vals)) * (n / N)


def info_x(data, attr):
    data = data.loc[data[attr].notnull()]
    freq = pd.DataFrame(data.groupby([attr])['__W__'].sum()).unstack().fillna(0).values
    W = data['__W__'].sum()
    p = freq / W
    return round(-sum(p * log2(p)), 3)

def gainRatio(data,target,attr):
    gain = entropy(data,target,attr)
    spltInfo = splitInfo(data, attr)
    return round(gain/spltInfo,3)

def entropy(data,target,attr):
    H = info_x(data, target)
    freq = pd.DataFrame(data.groupby([attr, target])['__W__'].sum()).unstack().fillna(0)
    N = data['__W__'].sum()
    info = freq.apply(lambda row: req_bits(row, N), axis=1)
    return round(H - info.sum(),3)

def entropyCont(data,target,attr):
    data = data.loc[data[target].notnull()]
    vals = unique(data[attr].sort_values().values[:-1])
    if len(vals) <= 1:
        return 0, None
    thresholds = (vals[1:] - vals[0:-1]) / 2
    thrshShannon = {}
    for v, dv in zip(vals, thresholds):
        data['__thrsh__'] = data[attr].apply(lambda x: x >= v + dv)
        H = entropy(data, target, '__thrsh__')
        spltInfo = splitInfo(data, '__thrsh__')
        thrshShannon[v + dv] = round(H/spltInfo,3)
    bestSplit = max(thrshShannon, key=thrshShannon.get)
    d = thrshShannon[bestSplit]
    data.drop(['__thrsh__'], axis=1, inplace=True)
    return d, bestSplit


# endregion

# region Tsallis

def tsallis(data, target, attr, alpha):
    H = tsalis_x(data, target, alpha)
    freq = pd.DataFrame(data.groupby([attr, target])['__W__'].sum()).unstack().fillna(0)
    N = data['__W__'].sum()
    info = freq.apply(lambda row: req_info_t(row, N, alpha), axis=1)
    return round(H - info.sum(), 3)


def req_info_t(row, N, alpha):
    n = row.sum()
    p = row.values / n
    p = p[nonzero(p)]
    p = power(p, alpha).sum()
    return round(((1 / (alpha - 1)) * (1 - p)) * (n / N), 3)


def tsalis_x(data, target, alpha):
    data = data.loc[data[target].notnull()]
    freq = pd.DataFrame(data.groupby([target])['__W__'].sum()).unstack().fillna(0).values
    W = data['__W__'].sum()
    p = power(freq / W, alpha).sum()
    return round((1 / (alpha - 1)) * (1 - p), 3)


def tsallisCont(data, target, attr, alpha):
    data = data.loc[data[target].notnull()]
    vals = unique(data[attr].sort_values().values[:-1])
    if len(vals) <= 1:
        return 0, None
    thresholds = (vals[1:] - vals[0:-1]) / 2
    thrshTsall = {}
    for v, dv in zip(vals, thresholds):
        data['__thrsh__'] = data[attr].apply(lambda x: x >= v + dv)
        d = tsallis(data, target, '__thrsh__', alpha)
        thrshTsall[v + dv] = d
    bestSplit = max(thrshTsall, key=thrshTsall.get)
    d = thrshTsall[bestSplit]
    data.drop(['__thrsh__'], axis=1, inplace=True)
    return d, bestSplit

# endregion

# region Renyi

def renyi(data, target, attr, alpha):
    H = renyi_x(data, target, alpha)
    freq = pd.DataFrame(data.groupby([attr, target])['__W__'].sum()).unstack().fillna(0)
    N = data['__W__'].sum()
    info = freq.apply(lambda row: req_info_r(row, N, alpha), axis=1)
    return round(H - info.sum(), 3)


def req_info_r(row, N, alpha):
    n = row.sum()
    p = row.values / n
    p = p[nonzero(p)]
    p = power(p, alpha).sum()
    return round(((1 / (1-alpha)) * log(p)) * (n / N), 3)


def renyi_x(data, target, alpha):
    data = data.loc[data[target].notnull()]
    freq = pd.DataFrame(data.groupby([target])['__W__'].sum()).unstack().fillna(0).values
    W = data['__W__'].sum()
    p = power(freq / W, alpha).sum()
    return round((1 / (1-alpha)) * log(p), 3)


def renyiCont(data, target, attr, alpha):
    data = data.loc[data[target].notnull()]
    vals = unique(data[attr].sort_values().values[:-1])
    if len(vals) <= 1:
        return 0, None
    thresholds = (vals[1:] - vals[0:-1]) / 2
    thrshRenyi = {}
    for v, dv in zip(vals, thresholds):
        data['__thrsh__'] = data[attr].apply(lambda x: x >= v + dv)
        d = renyi(data, target, '__thrsh__', alpha)
        thrshRenyi[v + dv] = d
    bestSplit = max(thrshRenyi, key=thrshRenyi.get)
    d = thrshRenyi[bestSplit]
    data.drop(['__thrsh__'], axis=1, inplace=True)
    return d, bestSplit

# endregion

# region C4.5 numerical attribute handle

def set_threshold(values, curr_thrsh):
    """
    It's a strange point in every C4.5 implementation. We will continue the tradition
    """
    newThrsh = -max(values)
    for v in values:
        tempValue = v
        if (tempValue > newThrsh) & (tempValue <= curr_thrsh):
            newThrsh = tempValue
    return newThrsh


def distrEntropy(data, attr, target, q=2):
    data = data.loc[data[attr].notnull()]
    freq = data.groupby(target)['__W__'].sum().values
    v = sum(freq * log(freq))
    w = data['__W__'].sum()
    return (w * log(w) - v) / (log(2) * (q - 1))


def _splitEntropy_(data, attr, thrsh, W):
    unknown = W - data.loc[data[attr].notnull()]['__W__'].sum()
    leftSubs = data.loc[data[attr] <= thrsh]
    rightSubs = data.loc[data[attr] > thrsh]
    w1 = leftSubs['__W__'].sum()
    w2 = rightSubs['__W__'].sum()
    h = - w1 * log(w1) - w2 * log(w2)
    if unknown > 0:
        h -= unknown * log(unknown)
    h += W * log(W)
    return round(h / log(2), 3)

# endregion

# region Gini

def gini_x(data, attr):
    data = data.loc[data[attr].notnull()]
    freq = pd.DataFrame(data.groupby([attr])['__W__'].sum()).unstack().fillna(0)
    W = data['__W__'].sum()
    g = 1 - square(freq.values / W).sum()
    return round(g, 3)


def req_info_g(row, N):
    n = row.sum()
    p = row.values / n
    p = p[nonzero(p)]
    p = 1 - square(p).sum()
    return round(p * (n / N), 3)


def gini(data, target, attr):
    """
    :param data: pandas DataFrame
    :param target: target column name
    :param attr: current attribute
    :return: Gini index
    """
    H = gini_x(data, target)
    freq = pd.DataFrame(data.groupby([attr, target])['__W__'].sum()).unstack().fillna(0)
    N = data['__W__'].sum()
    info = freq.apply(lambda row: req_info_g(row, N), axis=1)
    return round(H - info.sum(), 3)


def giniCont(data, target, attr):
    """
    :param data: pandas DataFrame
    :param target: target column name
    :param attr: current attribute
    :return: Gini index
    """
    data = data.loc[data[target].notnull()]
    vals = unique(data[attr].sort_values().values[:-1])
    if len(vals) <= 1:
        return 0, None
    thresholds = (vals[1:] - vals[0:-1]) / 2
    thrshGini = {}
    for v, dv in zip(vals, thresholds):
        data['__thrsh__'] = data[attr].apply(lambda x: x >= v + dv)
        g = gini(data, target, '__thrsh__')
        thrshGini[v + dv] = g
    bestSplit = max(thrshGini, key=thrshGini.get)
    g = thrshGini[bestSplit]
    data.drop(['__thrsh__'], axis=1, inplace=True)
    return g, bestSplit


# endregion

# region Donskoy

def D(data, target, attr):
    T = data[target].unique()
    freq = pd.DataFrame(data.groupby([target, attr])['__W__'].sum()).unstack().fillna(0)
    columns = freq.columns.values
    D_value = 0
    for i, col in enumerate(columns[:-1], 1):
        f = freq[col]
        for t in T:
            k = f[t]
            ind = freq.index.isin([t])
            vals = freq[~ind][columns[i:]].values.ravel()
            D_value += sum(k * vals)
    return D_value


def D_cont(data, target, attr):
    data = data.loc[data[target].notnull()]
    vals = unique(data[attr].sort_values().values[:-1])
    if len(vals) <= 1:
        return 0, None
    thresholds = (vals[1:] - vals[0:-1]) / 2
    thrshDonsky = {}
    for v, dv in zip(vals, thresholds):
        data['__thrsh__'] = data[attr].apply(lambda x: x >= v + dv)
        d = D(data, target, '__thrsh__')
        thrshDonsky[v + dv] = d
    bestSplit = max(thrshDonsky, key=thrshDonsky.get)
    d = thrshDonsky[bestSplit]
    data.drop(['__thrsh__'], axis=1, inplace=True)
    return d, bestSplit

# endregion
