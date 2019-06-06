import pandas
import numpy as np
import statsmodels.stats.multitest as smm

from scipy.stats import hypergeom
from goenrichment.graph import ancestors


def calculate(godb, query,
              alpha=0.05,
              min_category_depth=4,
              min_category_size=3,
              max_category_size=500):
    """
    Calculate the GO enrichment from a list of gene IDs
    :param df: Pandas dataframe with genes IDs
    :param gene_id_column: Gene ID column on the data frame
    :param geneGoDB: geneGoDB data structure
    :param name_space: GO name space
    :return: Pandas data frame
    """
    vals = []
    pvalues = []
    N = len(set(query))
    terms, nodes = zip(*godb['graph'].nodes(data=True))
    for node in nodes:
        category = node['genes']
        n = len(category)
        hits = query.intersection(category)
        k = len(hits)
        if k > 0 and \
                (node.get('depth', 0) >= min_category_depth or
                 len(list(godb['graph'].predecessors(node['id']))) == 0) \
                and min_category_size <= n <= max_category_size:
            p = hypergeom.sf(k - 1, godb['M'], n, N)
            pvalues.append(p)
            vals.append((node['id'], node['name'], node['namespace'], p, k, n, node['depth']))
    correction = smm.multipletests(pvalues, alpha=alpha, method='fdr_bh')
    df = pandas.DataFrame(vals, columns=['term', 'name', 'namespace', 'p', 'k', 'n', 'depth'])
    df['accepted'] = correction[0]
    df['q'] = correction[1]
    df['-1.0log(q)'] = -1.0 * np.log10(correction[1])
    df = df[['term', 'name', 'namespace', 'depth', 'k', 'n', 'p', 'q', '-1.0log(q)', 'accepted']]

    nodes = set()
    index = []
    for i, r in df.sort_values('depth', ascending=False).iterrows():
        if r['term'] not in nodes and r['q'] <= alpha:
            index.append(i)
            nodes.update(ancestors(r['term'], godb['graph']))
    return df.loc[index].sort_values('q', ascending=False)
