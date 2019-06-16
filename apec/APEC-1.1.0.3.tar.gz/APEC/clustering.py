import os, sys, numpy, pandas, scipy.io, scipy.sparse, scipy.stats, numba
import networkx, community, sklearn.metrics, sklearn.cluster
from sklearn.decomposition import PCA
import sklearn.utils.sparsefuncs
from sklearn.neighbors import kneighbors_graph
from sklearn.decomposition.truncated_svd import TruncatedSVD
from sklearn.metrics.cluster import contingency_matrix
from MulticoreTSNE import MulticoreTSNE as McTSNE
#
#
######## cluster cells with APEC algorithm
#
#
def build_accesson(project, ngroup=600, ncell=10000, npc=40):
    """
    project:  Path to the project folder.
    ngroup:   Number of accessons, default=600.
    ncell:    Limit of cell number for the dataset that use exact PCA, default=10000.
    npc:      Number of principal components used to build accesson, default=40.
    """
    reads = scipy.io.mmread(project+'/matrix/filtered_reads.mtx')
    reads = scipy.sparse.csr_matrix(reads)*1.0
    cells = pandas.read_csv(project+'/matrix/filtered_cells.csv', sep='\t', index_col=0,
                            engine='c', na_filter=False, low_memory=False)
    cells = cells.index.values
    peaks = ['peak'+str(x) for x in range(0, reads.shape[0])]
    scale = numpy.array(10000.0 / reads.sum(axis=0))[0]
    sklearn.utils.sparsefuncs.inplace_column_scale(reads, scale)
    reads.data = numpy.log2(reads.data+1)
    npc = min(npc, reads.shape[0], reads.shape[1])
    if len(cells)>ncell:
        pca_result = TruncatedSVD(n_components=npc, algorithm='arpack', random_state=0).fit_transform(reads)
    else:
        pca_result = PCA(n_components=npc, svd_solver='full').fit_transform(reads.A)
    connectivity = kneighbors_graph(pca_result, n_neighbors=10, include_self=False)
    connectivity = 0.5*(connectivity + connectivity.T)
    ward_linkage = sklearn.cluster.AgglomerativeClustering(n_clusters=ngroup, linkage='ward', connectivity=connectivity)
    y_predict = ward_linkage.fit_predict(pca_result)
    peak_labels_df = pandas.DataFrame(y_predict, index=peaks, columns=['group'])
    peak_labels_df.to_csv(project+'/matrix/Accesson_peaks.csv', sep='\t')
    groups = list(set(y_predict))
    coAccess_matrix = numpy.array([reads[numpy.where(y_predict==x)[0],:].sum(axis=0) for x in groups])
    coAccess_matrix = coAccess_matrix[:,0,:].T
    coAccess_df = pandas.DataFrame(coAccess_matrix, index=cells, columns=groups)
    coAccess_df.to_csv(project+'/matrix/Accesson_reads.csv', sep=',')
    print('build_accesson output files:')
    print(project+'/matrix/Accesson_peaks.csv')
    print(project+'/matrix/Accesson_reads.csv')
    return
#
#
def filtering(raw_matrix):
    matrix = numpy.array([x/x.sum()*1000000 for x in raw_matrix])
    gini = lambda x : 0.5 * numpy.abs(numpy.subtract.outer(x, x)).mean() / numpy.mean(x)
    if raw_matrix.shape[0]<=10000:
        coef_gini = numpy.array([gini(x) for x in matrix.T])
    else:
        coef_gini = numpy.array([len(numpy.where(x>0)[0]) for x in matrix.T])
    means = matrix.mean(axis=0)
    mean_cutoff = (means.mean() - numpy.std(means))*2
    kk, bb = numpy.polyfit(numpy.log10(means), coef_gini, 1)
    yy = coef_gini + numpy.log10(means) * (-kk)
    index = numpy.where((yy>bb)&(means>mean_cutoff))[0]
    matrix_filtered = matrix[:, index]
    return matrix_filtered
#
#
def cluster_byAccesson(project, nc=0, norm='zscore', filter='yes'):
    """
    project:  Path to the project folder.
    nc:       Number of cell clusters, set it to 0 if users want to predict cluster number by Louvain algorithm, default=0.
    norm:     Normalization method for accesson matrix, can be 'zscore' or 'probability', default='zscore'.
    filter:   Filter high dispersion accessons or not, can be 'yes' or 'no', default='yes'.
    """
    if not os.path.exists(project+'/result'): os.popen('mkdir '+project+'/result')
    if not os.path.exists(project+'/figure'): os.popen('mkdir '+project+'/figure')
    reads_df = pandas.read_csv(project+'/matrix/Accesson_reads.csv', sep=',', index_col=0,
                               engine='c', na_filter=False, low_memory=False)
    if filter=='yes':
        normal = filtering(reads_df.values)
    else:
        normal = numpy.array([x/x.sum()*1000000 for x in reads_df.values])
    if norm=='zscore':
        normal = scipy.stats.zscore(normal, axis=1)
    elif norm=='probability':
        normal = numpy.array([x/x.sum() for x in normal])
    else:
        print("Error: norm should be zscore or probability")
    matrix = pandas.DataFrame(normal, index=reads_df.index, columns=['c_'+str(x+1) for x in numpy.arange(0, len(normal.T))])
    matrix.to_csv(project+'/matrix/normalized_Accesson_reads.csv', sep=',')
    connect = kneighbors_graph(matrix, n_neighbors=20, include_self=False)
    connectivity = 0.5*(connect + connect.T)
    if int(nc)==0:
        graph = networkx.from_numpy_matrix(connectivity.A)
        partition = community.best_partition(graph)
        cluster_df = pandas.DataFrame(partition.values(), index=matrix.index, columns=['cluster'])
        n_clust = len(list(set(partition.values())))
        print("predicted number of cell-clusters: ", n_clust)
        out_cluster = project+'/result/louvain_cluster_by_APEC.csv'
    else:
        ward_linkage = sklearn.cluster.AgglomerativeClustering(n_clusters=nc, linkage='ward', connectivity=connectivity)
        y_predict = ward_linkage.fit_predict(matrix)
        cluster_df = pandas.DataFrame(y_predict, index=matrix.index, columns=['cluster'])
        out_cluster = project+'/result/KNN_cluster_by_APEC.csv'
    cluster_df.to_csv(out_cluster, sep='\t')
    print('cluster_byAccesson output files:')
    print(out_cluster)
    return
#
#
####### compare clustering result with real cell labels or other clustering result
#
#
def cluster_comparison(cluster_csv1, cluster_csv2):
    """
    cluster_csv1:  Path to the csv file of the clustering result, or the filtered_cells.csv file in $project/matrix/.
    cluster_csv2:  Path to another clustering result.
    """
    cluster_df1 = pandas.read_csv(cluster_csv1, sep='\t', index_col=0, engine='c', na_filter=False, low_memory=False)
    cluster_df2 = pandas.read_csv(cluster_csv2, sep='\t', index_col=0, engine='c', na_filter=False, low_memory=False)
    if 'notes' in cluster_df1.columns.values: cluster_df1['cluster']=cluster_df1['notes']
    if 'notes' in cluster_df2.columns.values: cluster_df2['cluster']=cluster_df2['notes']
    clusters1 = cluster_df1['cluster'].values
    clusters2 = cluster_df2['cluster'].values
    ari = sklearn.metrics.adjusted_rand_score(clusters1, clusters2)
    nmi = sklearn.metrics.mutual_info_score(clusters1, clusters2)
    ami = sklearn.metrics.adjusted_mutual_info_score(clusters1, clusters2)
    cont_mat = contingency_matrix(clusters1, clusters2)
    print('ARI=', ari)
    print('NMI=', nmi)
    print('AMI=', ami)
    print('contingency matrix:')
    print(cont_mat)
    return
#
#
####### cluster cells with chromVAR algorithm
#
global reads, TFmotif, expected
#
def mahalanobis_transform(aMatrix):
    (nSample, nFeature) = aMatrix.shape
    am_sum = aMatrix.sum(axis=0)
    ajaMatrix = numpy.zeros((nFeature, nFeature))
    for i in range(0, nFeature):
        for j in range(0, nFeature):
            ajaMatrix[i,j] = am_sum[i] * am_sum[j]
    SaMatrix = numpy.dot(aMatrix.T, aMatrix) / float(nSample) - ajaMatrix / float(nSample**2)
    value, vector = numpy.linalg.eig(SaMatrix)
    value_inverseRoot = numpy.diag(-abs(value)**0.5)
    Sa_inverseRoot = numpy.dot(numpy.dot(vector, value_inverseRoot), vector.T)
    aMatrix_ave = aMatrix.mean(axis=0)
    aMatrix_ave = numpy.array([aMatrix_ave for i in range(0, nSample)])
    zMatrix = numpy.dot(Sa_inverseRoot, (aMatrix.T - aMatrix_ave.T))
    return zMatrix.T
#
def single_sampling(par):
    GC_bias, peak_reads, nStep, sd, iIter = par[0], par[1], par[2], par[3], par[4]
    numpy.random.seed(12345+iIter)
    bias_step = (GC_bias.max() - GC_bias.min()) / float(nStep)
    read_step = (peak_reads.max() - peak_reads.min()) / float(nStep)
    sample = numpy.zeros(len(GC_bias),dtype=numpy.int)
    for ibias,bias_i in enumerate(GC_bias):
        bias_iIndex = int((bias_i - GC_bias.min()) // bias_step)
        read_iIndex = int((peak_reads[ibias] - peak_reads.min()) // read_step)
        bias_iIndex = min(nStep-1, max(0, bias_iIndex))
        read_iIndex = min(nStep-1, max(0, read_iIndex))
        peaks_inGrid = numpy.array([])
        ncount = 0
        while (len(peaks_inGrid)<=0) & (ncount<1000):
            ncount += 1
            bias_jIndex = bias_iIndex + int(numpy.rint(numpy.random.randn()*sd))
            read_jIndex = read_iIndex + int(numpy.rint(numpy.random.randn()*sd))
            while (bias_jIndex<0)|(bias_jIndex>=nStep):
                bias_jIndex = bias_iIndex + int(numpy.rint(numpy.random.randn()*sd))
            while (read_jIndex<0)|(read_jIndex>=nStep):
                read_jIndex = read_iIndex + int(numpy.rint(numpy.random.randn()*sd))
            bias_jStart = GC_bias.min() + bias_jIndex * bias_step
            read_jStart = peak_reads.min() + read_jIndex * read_step
            bias_jBin = numpy.where((bias_jStart<=GC_bias)&(GC_bias<bias_jStart+bias_step))[0]
            read_jBin = numpy.where((read_jStart<=peak_reads)&(peak_reads<read_jStart+read_step))[0]
            peaks_inGrid = numpy.intersect1d(bias_jBin, read_jBin)
        if ncount<1000:
            sample[ibias] = numpy.random.choice(peaks_inGrid)
        else:
            sample[ibias] = ibias
    return sample
#
def batch_sampling(GC_bias, peak_reads, nStep, sd, nIteration, np):
    from multiprocessing import Pool
    matrix = numpy.vstack((GC_bias, peak_reads)).T
    matrix = mahalanobis_transform(matrix)
    GC_bias, peak_reads = matrix.T[0,:], matrix.T[1,:]
    kIterations = numpy.arange(0, nIteration, 1, dtype=int)
    parameters = []
    for iIter in kIterations:
        parameters.append([GC_bias, peak_reads, nStep, sd, iIter])
    pool = Pool(np)
    samples = pool.map(single_sampling, parameters)
    pool.close()
    pool.join()
    return numpy.array(samples)
#
def expected_matrix(GC_bias):
    (nCell, nPeak) = reads.shape   # X_matrix
    (nTF, nPeak) = TFmotif.shape   # M_matrix
    reads_sum = reads.sum()
    row_sum = reads.sum(axis=0)
    col_sum = reads.sum(axis=1)
    E_matrix = numpy.outer(col_sum, row_sum) / reads_sum
    return E_matrix
#
def deviation(MM, BB, XX, EE):
    MM = numpy.dot(MM, BB.T)
    YY = numpy.dot(MM, XX.T) - numpy.dot(MM, EE.T)
    denom = numpy.dot(MM, EE.T)
    YY = YY / denom
    return YY
#
def raw_deviation():
    (nCell, nPeak) = reads.shape
    (nTF, nPeak) = TFmotif.shape
    B_matrix = numpy.diag(numpy.ones(nPeak))
    raw_dev = deviation(TFmotif, B_matrix, reads, expected)
    return raw_dev
#
#
def initiation(project):
    global reads, TFmotif
    reads = scipy.io.mmread(project+'/matrix/filtered_reads.mtx')
    reads = scipy.sparse.csr_matrix(reads).T
    reads = reads.A + 0.0001
    cells = pandas.read_csv(project+'/matrix/filtered_cells.csv', sep='\t', index_col=0,
                   engine='c', na_filter=False, low_memory=False)
    cell_names = cells.index.values
    TFmotif_df = pandas.read_csv(project+'/matrix/motif_filtered.csv', sep=',', index_col=0)
    TFmotif_origin = TFmotif_df.values.T
    TFnames = TFmotif_df.columns.values
    print('read-counts matrix:', reads.shape)
    print('TFmotif matrix:', TFmotif_origin.shape)
    GC_bias = numpy.array([float(x.split()[3]) for x in open(project+'/peak/transposase_bias_filtered.bed').readlines()])
    TFmotif = numpy.asarray([x for x in TFmotif_origin if x.sum() > 0])
    TFmotif[numpy.where(TFmotif > 0)] = 1
    TFnames = [x for i,x in enumerate(TFnames) if TFmotif_origin[i, :].sum() > 0]
    return TFmotif, reads, TFnames, cell_names, GC_bias
#
def permuted_sampling(GC_bias, ns=50, np=1):
    peak_reads = numpy.log10(reads.sum(axis=0)+1.0)
    ngrid, std = 50, 1
    samples = batch_sampling(GC_bias, peak_reads, ngrid, std, ns, np)
    print('permuted sampling done!')
    return samples
#
def get_raw_deviation(project, GC_bias):
    global expected
    expected = expected_matrix(GC_bias)
    raw_dev = raw_deviation()
    numpy.savetxt(project+'/result/raw_deviation.txt', raw_dev)
    print('raw deviation done!')
    return expected, raw_dev
#
def background_deviation(par):
    iIter, sample = par[0], par[1]
    numpy.random.seed(12345+iIter)
    (nCell, nPeak) = reads.shape
    (nTF, nPeak) = TFmotif.shape
    background_dev = numpy.zeros((nTF, nCell))
    B_matrix = numpy.zeros((nPeak, nPeak))
    for iPeak in range(0, nPeak):
        B_matrix[iPeak, int(sample[iPeak])] = 1
    background_dev = deviation(TFmotif, B_matrix, reads, expected)
    return background_dev
#
def corrected_deviation(project, samples, TFnames, cell_names, ns, np):
    from multiprocessing import Pool
    kIterations = numpy.arange(0, ns, 1, dtype=int)
    par = []
    for k in kIterations:
        par.append([k, samples[k]])
    pool = Pool(np)
    bg_dev = pool.map(background_deviation, par)
    pool.close()
    pool.join()
    bg_dev = numpy.array(bg_dev)
    print('background deviations done!')
    bg_dev_mean = bg_dev.mean(axis=0)
    bg_dev_std = bg_dev.std(axis=0)
    raw_dev = numpy.loadtxt(project+'/result/raw_deviation.txt')
    corrected_dev = (raw_dev - bg_dev_mean) / bg_dev_std
    dev_df = pandas.DataFrame(corrected_dev, index=TFnames, columns=cell_names)
    dev_df.to_csv(project+'/result/deviation_chromVAR.csv', sep=',')
    print('corrected_deviation output files:')
    print(project+'/result/deviation_chromVAR.csv')
    return
#
#
def cluster_byMotif(project, nc=0, ns=50, np=4):
    """
    project:  Path to the project folder.
    nc:       Number of cell clusters, set it to 0 if users want to predict cluster number by Louvain algorithm, default=0.
    ns:       Number of permuted sampling, default=50.
    np:       Number of CPU cores used for parallel calculation, default=4.
    """
    TFmotif, reads, TFnames, cell_names, GC_bias = initiation(project)
    samples = permuted_sampling(GC_bias, ns, np)
    expected, raw_dev = get_raw_deviation(project, GC_bias)
    corrected_deviation(project, samples, TFnames, cell_names, ns, np)
#
    if not os.path.exists(project+'/result'): os.popen('mkdir '+project+'/result')
    if not os.path.exists(project+'/figure'): os.popen('mkdir '+project+'/figure')
    reads_df = pandas.read_csv(project+'/result/deviation_chromVAR.csv', sep=',', index_col=0,
                   engine='c', na_filter=False, low_memory=False)
    matrix = reads_df.T
    connect = kneighbors_graph(matrix, n_neighbors=20, include_self=False)
    connectivity = 0.5*(connect + connect.T)
    if int(nc)==0:
        graph = networkx.from_numpy_matrix(connectivity.A)
        partition = community.best_partition(graph)
        cluster_df = pandas.DataFrame(partition.values(), index=matrix.index, columns=['cluster'])
        n_clust = len(list(set(partition.values())))
        print("predicted number of cell-clusters: ", n_clust)
        out_cluster = project+'/result/louvain_cluster_by_chromVAR.csv'
    else:
        ward_linkage = sklearn.cluster.AgglomerativeClustering(n_clusters=nc, linkage='ward', connectivity=connectivity)
        y_predict = ward_linkage.fit_predict(matrix)
        cluster_df = pandas.DataFrame(y_predict, index=matrix.index, columns=['cluster'])
        out_cluster = project+'/result/KNN_cluster_by_chromVAR.csv'
    cluster_df.to_csv(out_cluster, sep='\t')
    print('cluster_byMotif output files:')
    print(out_cluster)
    return
#
#
#
#
