
def module_degree_zscore(W, ci, flag=0):
    '''
    The within-module degree z-score is a within-module version of degree
    centrality.
    Parameters
    ----------
    W : NxN np.narray
        binary/weighted directed/undirected connection matrix
    ci : Nx1 np.array_like
        community affiliation vector
    flag : int
        Graph type. 0: undirected graph (default)
                    1: directed graph in degree
                    2: directed graph out degree
                    3: directed graph in and out degree
    Returns
    -------
    Z : Nx1 np.ndarray
        within-module degree Z-score
    '''
    _, ci = np.unique(ci, return_inverse=True)
    ci += 1

    if flag == 2:
        W = W.copy()
        W = W.T
    elif flag == 3:
        W = W.copy()
        W = W + W.T

    n = len(W)
    Z = np.zeros((n,))  # number of vertices
    for i in range(1, int(np.max(ci) + 1)):
        Koi = np.sum(W[np.ix_(ci == i, ci == i)], axis=1)
        Z[np.where(ci == i)] = (Koi - np.mean(Koi)) / np.std(Koi)

    Z[np.where(np.isnan(Z))] = 0
    return Z
