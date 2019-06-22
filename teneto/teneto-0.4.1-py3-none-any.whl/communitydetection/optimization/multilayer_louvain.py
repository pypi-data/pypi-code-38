def temporal_community(G,omega=1,gamma=1,randomseed=None):

    #Inititialization
    np.random.seed(randomseed)
    #for t in np.arange()
    B = np.zeros(np.shape(G))

    for g in range(0,G.shape[-1]):
        C = louvain(G[:,:,g],randomseed)
        Bs = np.zeros(G[:,:,g].shape)
        for c in np.unique(C):
            fid = np.where(C==c)
            Bs[np.ix_(fid[0],fid[0])]=1
        B[:,:,g] = Bs

    #B[np.arange(0,3),np.arange(3,6)]=1

    # This create a string of the block matrix that is to be created.
    strbuild = '['
    for g in range(0,B.shape[-1]):
        strbuild += '['
        strbuild += 'None,'*(g-1)
        if g != 0:
            strbuild += 'np.array(np.matlib.identity(B.shape[0])*omega),'
        strbuild += 'B[:,:,' + str(g) + '],'
        if g != B.shape[-1]-1:
            strbuild +='np.array(np.matlib.identity(B.shape[0])*omega),'
        strbuild += 'None,'*(B.shape[-1]-2-g)
        strbuild += '],'
    strbuild += ']'
    if B.shape[-1]>2:
        Bbmat = sp.sparse.bmat(eval(strbuild))
        Gsp=sp.sparse.csr_matrix(Bbmat)
    elif B.shape[-1]==2:
        Gden = eval(strbuild)
        Gden = np.vstack([np.hstack(Gden[0]),np.hstack(Gden[1])])
        Gsp=sp.sparse.csr_matrix(Gden)
    else:
        raise ValueError('Only one layer detected')

    C=louvain(Gsp)
    C=C.reshape(G.shape[-1],G.shape[0]).transpose()
    return C
