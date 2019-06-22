def community_louvain(W, gamma=1, ci=None, B='modularity', seed=None):
    '''
    The optimal community structure is a subdivision of the network into
    nonoverlapping groups of nodes which maximizes the number of within-group
    edges and minimizes the number of between-group edges.
    This function is a fast an accurate multi-iterative generalization of the
    louvain community detection algorithm. This function subsumes and improves
    upon modularity_[louvain,finetune]_[und,dir]() and additionally allows to
    optimize other objective functions (includes built-in Potts Model i
    Hamiltonian, allows for custom objective-function matrices).
    
    Parameters
    ----------
    W : NxN np.array
        directed/undirected weighted/binary adjacency matrix
    gamma : float
        resolution parameter. default value=1. Values 0 <= gamma < 1 detect
        larger modules while gamma > 1 detects smaller modules.
        ignored if an objective function matrix is specified.
    ci : Nx1 np.arraylike
        initial community affiliation vector. default value=None
    B : str | NxN np.arraylike
        string describing objective function type, or provides a custom
        NxN objective-function matrix. builtin values 
            'modularity' uses Q-metric as objective function
            'potts' uses Potts model Hamiltonian.
            'negative_sym' symmetric treatment of negative weights
            'negative_asym' asymmetric treatment of negative weights
    seed : int | None
        random seed. default value=None. if None, seeds from /dev/urandom.
    Returns
    -------
    ci : Nx1 np.array
        final community structure
    q : float
        optimized q-statistic (modularity only)
    '''
    np.random.seed(seed)

    n = len(W)
    s = np.sum(W)

    #if np.min(W) < -1e-10:
    #    raise BCTParamError('adjmat must not contain negative weights')

    if ci is None:
        ci = np.arange(n) + 1
    else:
        if len(ci) != n:
            raise BCTParamError('initial ci vector size must equal N')
        _, ci = np.unique(ci, return_inverse=True)
        ci += 1
    Mb = ci.copy()
    renormalize = False
    if B in ('negative_sym', 'negative_asym'):
        renormalize = True
        W0 = W * (W > 0)
        s0 = np.sum(W0)
        B0 = W0 - gamma * np.outer(np.sum(W0, axis=1), np.sum(W0, axis=0)) / s0

        W1 = -W * (W < 0)
        s1 = np.sum(W1)
        if s1:
            B1 = W1 - gamma * np.outer(np.sum(W1, axis=1), np.sum(W1, axis=0)) / s1
        else:
            B1 = 0

    elif np.min(W) < -1e-10:
        raise BCTParamError("Input connection matrix contains negative "
            'weights but objective function dealing with negative weights '
            'was not selected')

    if B == 'potts' and np.any(np.logical_not(np.logical_or(W == 0, W == 1))):
        raise BCTParamError('Potts hamiltonian requires binary input matrix')

    if B == 'modularity':
        B = W - gamma * np.outer(np.sum(W, axis=1), np.sum(W, axis=0)) / s
    elif B == 'potts':
        B = W - gamma * np.logical_not(W)
    elif B == 'negative_sym':
        B = (B0 / (s0 + s1)) - (B1 / (s0 + s1))
    elif B == 'negative_asym':
        B = (B0 / s0) - (B1 / (s0 + s1))
    else:
        try:
            B = np.array(B)
        except:
            raise BCTParamError('unknown objective function type')

        if B.shape != W.shape:
            raise BCTParamError('objective function matrix does not match '
                                'size of adjacency matrix')
        if not np.allclose(B, B.T):
            print ('Warning: objective function matrix not symmetric, '
                   'symmetrizing')
            B = (B + B.T) / 2
    
    Hnm = np.zeros((n, n))
    for m in range(1, n + 1):
        Hnm[:, m - 1] = np.sum(B[:, ci == m], axis=1)  # node to module degree
    H = np.sum(Hnm, axis=1)  # node degree
    Hm = np.sum(Hnm, axis=0)  # module degree

    q0 = -np.inf
    # compute modularity
    q = np.sum(B[np.tile(ci, (n, 1)) == np.tile(ci, (n, 1)).T]) / s

    first_iteration = True

    while q - q0 > 1e-10:
        it = 0
        flag = True
        while flag:
            it += 1
            if it > 1000:
                raise BCTParamError('Modularity infinite loop style G. '
                                    'Please contact the developer.')
            flag = False
            for u in np.random.permutation(n):
                ma = Mb[u] - 1
                dQ = Hnm[u, :] - Hnm[u, ma] + B[u, u]  # algorithm condition
                dQ[ma] = 0

                max_dq = np.max(dQ)
                if max_dq > 1e-10:
                    flag = True
                    mb = np.argmax(dQ)

                    Hnm[:, mb] += B[:, u]
                    Hnm[:, ma] -= B[:, u]  # change node-to-module strengths

                    Hm[mb] += H[u]
                    Hm[ma] -= H[u]  # change module strengths

                    Mb[u] = mb + 1

        _, Mb = np.unique(Mb, return_inverse=True)
        Mb += 1

        M0 = ci.copy()
        if first_iteration:
            ci = Mb.copy()
            first_iteration = False
        else:
            for u in range(1, n + 1):
                ci[M0 == u] = Mb[u - 1]  # assign new modules

        n = np.max(Mb)
        b1 = np.zeros((n, n))
        for i in range(1, n + 1):
            for j in range(i, n + 1):
                # pool weights of nodes in same module
                bm = np.sum(B[np.ix_(Mb == i, Mb == j)])
                b1[i - 1, j - 1] = bm
                b1[j - 1, i - 1] = bm
        B = b1.copy()

        Mb = np.arange(1, n + 1)
        Hnm = B.copy()
        H = np.sum(B, axis=0)
        Hm = H.copy()

        q0 = q

        q = np.trace(B)  # compute modularity
    
    # Workaround to normalize
    if not renormalize:
        return ci, q/s
    else:
    return ci, q