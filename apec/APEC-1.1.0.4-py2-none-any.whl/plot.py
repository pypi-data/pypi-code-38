import numpy,pandas,copy,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn
#
global colors
colors = numpy.array(['pink', 'red', '#377eb8', 'green', 'skyblue', 'lightgreen', 'gold',
                      '#ff7f00', '#000066', '#ff3399', '#a65628', '#984ea3', '#999999',
                      '#e41a1c', '#dede00', 'b', 'g', 'c', 'm', 'y', 'k',
                      '#ADFF2F', '#7CFC00', '#32CD32', '#90EE90', '#00FF7F', '#3CB371',
                      '#008000', '#006400', '#9ACD32', '#6B8E23', '#556B2F', '#66CDAA',
                      '#8FBC8F', '#008080', '#DEB887', '#BC8F8F', '#F4A460', '#B8860B',
                      '#CD853F', '#D2691E', '#8B4513', '#A52A2A', '#778899', '#2F4F4F',
                      '#FFA500', '#FF4500', '#DA70D6', '#FF00FF', '#BA55D3', '#9400D3',
                      '#8B008B', '#9370DB', '#663399', '#4B0082'])
#
def weighted_tsne(matrix, clusters, rs, wt):
    cell_types = list(set(clusters['cluster']))
    adjusted = copy.deepcopy(matrix)
    for ctype in cell_types:
        cluster_cells = numpy.where(clusters['cluster']==ctype)[0]
        weight = adjusted[cluster_cells, :].mean(axis=0) * float(wt)
        adjusted[cluster_cells, :] = numpy.array([x+weight for x in adjusted[cluster_cells, :]])
    if matrix.shape[0]<=10000:
        from sklearn.manifold import TSNE
        tsne_result = TSNE(n_components=2, random_state=rs).fit_transform(adjusted)
    else:
        from MulticoreTSNE import MulticoreTSNE as McTSNE
        tsne_result = McTSNE(n_components=2, random_state=rs).fit_transform(adjusted)
    return tsne_result
#
#
def define_files(project, matrix_type, cell_label, cluster):
    if matrix_type=='APEC':
        reads_file = project+'/matrix/normalized_Accesson_reads.csv'
#        reads_file = project+'/matrix/Accesson_reads.csv'
    elif matrix_type=='chromVAR':
        reads_file = project+'/result/deviation_chromVAR.csv'
    else:
        print("Error: wrong <matrix_type>, should be 'APEC' or 'chromVAR' !")
        sys.exit()
    cluster_file = project+'/result/'+cluster+'_cluster_by_'+matrix_type+'.csv'
    if cell_label=='notes':
        cells_file = project+'/matrix/filtered_cells.csv'
    elif cell_label=='cluster':
        cells_file = cluster_file
    else:
        print("Error: wrong <cell_label>, should be 'notes' or 'cluster' !")
        sys.exit()
    return reads_file, cells_file, cluster_file
#
#
def plot_tsne(project,
              matrix_type='APEC',   # ='APEC' or 'chromVAR'
              cell_label='notes',   # ='notes' or 'cluster'
              cluster='louvain',   # ='louvain' or 'KNN'
              rs=0,    # random_state for tSNE
              wt=0.2    # Weight coefficient
              ):
    """
    project:        Path to the project folder.
    matrix_type:    Type of input matrix, can be 'APEC' or 'chromVAR', default='APEC'.
                    If matrix_type='APEC', it will use accesson matrix yielded by clustering.cluster_byAccesson();
                    if matrix_type='chromVAR', it will use deviation matrix yielded by clustering.cluster_byMotif().
    cell_label:     Color labels for cells, can be 'notes' or 'cluster', default='notes'.
    cluster:        Clustering algorithm used in clustering.cluster_byXXX(), can be 'louvain' or 'KNN', default='louvain'.
    rs:             Random state seed for TSNE analysis, default=0.
    wt:             Weight coefficient for TSNE analysis, default=0.2.
    """
    reads_file, cells_file, cluster_file = define_files(project, matrix_type, cell_label, cluster)
    reads_df = pandas.read_csv(reads_file, sep=',', index_col=0,
                               engine='c', na_filter=False, low_memory=False)
    if matrix_type=='chromVAR': reads_df = reads_df.T
    cells_df = pandas.read_csv(cells_file, sep='\t', index_col=0)
    cluster_df = pandas.read_csv(cluster_file, sep='\t', index_col=0)
    reads_df, cluster_df = reads_df.loc[cells_df.index.values], cluster_df.loc[cells_df.index.values]
    tsne_result = weighted_tsne(reads_df.values, cluster_df, rs, wt)
    tsne_df = pandas.DataFrame(tsne_result, index=cells_df.index, columns=['TSNE1', 'TSNE2'])
    out_tsne = project+'/result/TSNE_by_'+matrix_type+'.csv'
    tsne_df.to_csv(out_tsne, sep='\t')
#
    cTypes = list(set(cells_df[cell_label]))
    cTypes.sort()
    fig2, axes = plt.subplots(1, figsize=(15,15))
    for ict,ct in enumerate(cTypes):
        index = numpy.where(cells_df[cell_label]==ct)[0]
        axes.scatter(tsne_result[index, 0], tsne_result[index, 1], c=colors[ict], label=ct, s=50)
    axes.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    outfig2 = project+'/figure/TSNE_by_'+matrix_type+'_with_'+cell_label+'_label.pdf'
    fig2.savefig(outfig2, bbox_inches='tight')
    plt.close()
    print('plot_tsne output files:')
    print(out_tsne)
    print(outfig2)
    return
#
#
def plot_umap(project,
              matrix_type='APEC',   # ='APEC' or 'chromVAR'
              cell_label='notes',   # ='notes' or 'cluster'
              cluster='louvain',   # ='louvain' or 'KNN'
              rs=0    # random_state for UMAP
              ):
    """
    project:        Path to the project folder.
    matrix_type:    Type of input matrix, can be 'APEC' or 'chromVAR', default='APEC'.
                    If matrix_type='APEC', it will use accesson matrix yielded by clustering.cluster_byAccesson();
                    if matrix_type='chromVAR', it will use deviation matrix yielded by clustering.cluster_byMotif().
    cell_label:     Color labels for cells, can be 'notes' or 'cluster', default='notes'.
    cluster:        Clustering algorithm used in clustering.cluster_byXXX(), can be 'louvain' or 'KNN', default='louvain'.
    rs:             Random state seed for UMAP analysis, default=0.
    """
    import umap
    reads_file, cells_file, cluster_file = define_files(project, matrix_type, cell_label, cluster)
    reads_df = pandas.read_csv(reads_file, sep=',', index_col=0,
                             engine='c', na_filter=False, low_memory=False)
    cells_df = pandas.read_csv(cells_file, sep='\t', index_col=0)
    if matrix_type=='chromVAR': reads_df = reads_df.T
    reads_df = reads_df.loc[cells_df.index.values]
    umap_result = umap.UMAP(n_components=2, random_state=rs).fit_transform(reads_df.values)
    umap_df = pandas.DataFrame(umap_result, index=cells_df.index, columns=['UMAP1', 'UMAP2'])
    out_umap = project+'/result/UMAP_by_'+matrix_type+'.csv'
    umap_df.to_csv(out_umap, sep='\t')
#
    cTypes = list(set(cells_df[cell_label]))
    cTypes.sort()
    fig2, axes = plt.subplots(1, figsize=(15,15))
    for ict,ct in enumerate(cTypes):
        index = numpy.where(cells_df[cell_label]==ct)[0]
        axes.scatter(umap_result[index, 0], umap_result[index, 1], c=colors[ict], label=ct, s=50)
    axes.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    outfig = project+'/figure/UMAP_by_'+matrix_type+'_with_'+cell_label+'_label.pdf'
    fig2.savefig(outfig, bbox_inches='tight')
    plt.close()
    print('plot_umap output files:')
    print(out_umap)
    print(outfig)
    return
#
#
def correlation(project,
                matrix_type='APEC',   # ='APEC' or 'chromVAR'
                cell_label='notes',   # ='notes' or 'cluster'
                cluster='louvain',   # ='louvain', 'hierachy' or 'KNN'
                clip=[-1,6]   # =[min,max] or 'none'
                ):
    """
    project:        Path to the project folder.
    matrix_type:    Type of input matrix, can be 'APEC' or 'chromVAR', default='APEC'.
                    If matrix_type='APEC', it will use accesson matrix yielded by clustering.cluster_byAccesson();
                    if matrix_type='chromVAR', it will use deviation matrix yielded by clustering.cluster_byMotif().
    cell_label:     Color labels for cells, can be 'notes' or 'cluster', default='notes'.
    cluster:        Clustering algorithm used in clustering.cluster_byXXX(), can be 'louvain' or 'KNN' or 'hierachy', default='louvain'.
    clip:           Clip range for the input matrix, can be [min, max] or 'none', default=[-1, 6].
    """
    import seaborn
    reads_file, cells_file, cluster_file = define_files(project, matrix_type, cell_label, cluster)
    reads_df = pandas.read_csv(reads_file, sep=',', index_col=0,
                               engine='c', na_filter=False, low_memory=False)
    if cluster=='hierachy': cells_file = project+'/matrix/filtered_cells.csv'
    cells_df = pandas.read_csv(cells_file, sep='\t', index_col=0)
    if cluster in ['louvain', 'KNN']:
        cluster_df = pandas.read_csv(cluster_file, sep='\t', index_col=0)
        cluster_df = cluster_df.sort_values('cluster')
        cells_df = cells_df.loc[cluster_df.index.values]
    elif cluster!='hierachy':
        print("Error: wrong input parameter for <cluster> !")
        sys.exit()
    if matrix_type=='chromVAR':
        reads_df = reads_df.T
    elif matrix_type!='APEC':
        print("Error: wrong input parameter for <matrix_type> !")
        sys.exit()
    reads_df = reads_df.loc[cells_df.index.values]
#
    cTypes = list(set(cells_df[cell_label]))
    cTypes.sort()
    lut = dict(zip(cTypes, colors[:len(cTypes)]))
    row_colors = cells_df[cell_label].map(lut)
    cmap = seaborn.diverging_palette(h_neg=210, h_pos=350, s=90, l=30, as_cmap=True)
    seaborn.set(font_scale=1.2)
    if clip=='none':
        corr = numpy.corrcoef(reads_df.values)
    else:
        corr = numpy.corrcoef(numpy.clip(reads_df.values, clip[0], clip[1]))
    corr_df = pandas.DataFrame(corr, index=reads_df.index, columns=reads_df.index)
    if cluster in ['louvain', 'KNN']:
        fig0 = seaborn.clustermap(corr_df, cmap=cmap, row_cluster=False, col_cluster=False,
                                  row_colors=row_colors, figsize=(20,20))
    elif cluster=='hierachy':
        fig0 = seaborn.clustermap(corr_df, method='ward', metric='euclidean', cmap=cmap,
                                  row_colors=row_colors, figsize=(20,20))
    plt.setp(fig0.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
    plt.setp(fig0.ax_heatmap.xaxis.get_majorticklabels(), rotation=90)
    outfig = project+'/figure/cell_cell_correlation_by_'+matrix_type+'_with_'+cluster+'_clustering.png'
    fig0.savefig(outfig, bbox_inches='tight')
    plt.close()
    print('correlation output files:')
    print(outfig)
    return
#
#
def plot_trajectory(project,
                    cell_label='notes',   # ='notes', 'cluster', 'State'
                    cluster='louvain',   # ='louvain' or 'KNN'
                    angles=[30,30]    # =[alpha, beta]
                    ):
    """
    project:        Path to the project folder.
    cell_label:     Color labels for cells, can be 'notes' or 'cluster', default='notes'.
    cluster:        Clustering algorithm used in clustering.cluster_byXXX(), can be 'louvain' or 'KNN', default='louvain'.
    angles:         Rotation angles for 3D trajectory, e.g. [100,20], default=[30,30].
    """
    if cell_label=='notes':
        cells_file = project+'/matrix/filtered_cells.csv'
        cells_df = pandas.read_csv(cells_file, sep='\t', index_col=0)
    elif cell_label=='cluster':
        cells_file = project+'/result/'+cluster+'_cluster_by_APEC.csv'
        cells_df = pandas.read_csv(cells_file, sep='\t', index_col=0)
    elif cell_label=='State':
        cells_file = project+'/result/monocle_trajectory.csv'
        cells_df = pandas.read_csv(cells_file, sep=',', index_col=0)
    else:
        print("Error: wrong <cell_label>, should be 'notes' or 'cluster' !")
        sys.exit()
    reduced_df = pandas.read_csv(project+'/result/monocle_reduced_dimension.csv', sep=',', index_col=0)
    fig = plt.figure(1, figsize=(10,10))
    ax = fig.add_subplot(111, projection='3d')
    cell_types = list(set(list(cells_df[cell_label].values)))
    cell_types.sort()
    for itype,ctype in enumerate(cell_types):
        cells = cells_df.loc[cells_df[cell_label]==ctype].index.values
        ax.scatter(reduced_df.loc[1,cells], reduced_df.loc[2,cells], reduced_df.loc[3,cells],
                   c=colors[itype], edgecolors='none', s=20, label=cell_types[itype])
    ax.view_init(angles[0], angles[1])
    ax.set_xlim(reduced_df.iloc[0].min()-0.02, reduced_df.iloc[0].max()+0.02)
    ax.set_ylim(reduced_df.iloc[1].min()-0.02, reduced_df.iloc[1].max()+0.02)
    ax.set_zlim(reduced_df.iloc[2].min()-0.02, reduced_df.iloc[2].max()+0.02)
    ax.legend(fontsize=20, bbox_to_anchor=(1.0, 1.0))
    outfig = project+'/figure/pseudotime_trajectory_with_'+cell_label+'_label.pdf'
    fig.savefig(outfig, bbox_inches='tight')
    plt.close()
    print('plot_trajectory output files:')
    print(outfig)
    return
#
#
def plot_feature(project,
                 space='tsne',   # ='tsne' or 'umap' or 'trajectory'
                 feature='accesson',   # ='accesson' or 'motif' or 'gene'
                 matrix_type='APEC',   # ='APEC' or 'chromVAR'
                 name='1',    # = name of accesson/motif/gene
                 clip='none',    # = None or [min,max]
                 angles=[30,30],    # = [alpha, beta]
                 ):
    """
    project:        Path to the project folder.
    space:          In which space we draw the feature, can be 'tsne' or 'umap' or 'trajectory', default='tsne'.
                    If space='tsne', run plot.plot_tsne() first;
                    if space='umap', run plot.plot_umap() first;
                    if space='trajectory', run generate.monocle_trajectory() first.
    feature:        Type of the feature, can be 'accesson' or 'motif' or 'gene', default='accesson'.
                    If feature='accesson', run clustering.cluster_byAccesson() first;
                    if feature='motif', run clustering.cluster_byMotif() first;
                    if feature='gene', run generate.gene_expression() first.
    matrix_type:    Type of input matrix for tSNE/UMAP, can be 'APEC' or 'chromVAR', default='APEC'.
                    If matrix_type='APEC', it will use tSNE/UMAP result of APEC;
                    if matrix_type='chromVAR', it will use tSNE/UMAP result of chromVAR.
    name:           Name of the feature.
                    If feature='accesson', name=accesson number, i.e. '1';
                    if feature='motif', name=motif symbol, i.e. 'GATA1';
                    if feature='gene', name=gene symbol, i.e. 'CD36'.
    clip:           Clip range for the input matrix, can be [min, max] or 'none', default='none'.
    angles:         Rotation angles for 3D trajectory, e.g. [100,20], default=[30,30].
    """
    if space=='trajectory':
        space_df = pandas.read_csv(project+'/result/monocle_reduced_dimension.csv', sep=',', index_col=0).T
    else:
        space_df = pandas.read_csv(project+'/result/'+space.upper()+'_by_'+matrix_type+'.csv', sep='\t', index_col=0)
    matrix, cells = space_df.values, space_df.index.values
    if feature=='motif':
        reads_df = pandas.read_csv(project+'/result/deviation_chromVAR.csv', sep=',', index_col=0,
                                   engine='c', na_filter=False, low_memory=False).T
        motifs = []
        for tf in reads_df.columns.values:
            names = tf.split('-')[:-1]
            if name in names: motifs.append(tf)
        print(motifs)
        if len(motifs)==0:
            print("No corresponding marker!")
            sys.exit()
        else:
            reads = reads_df.ix[cells, motifs].values.sum(axis=1)
    elif feature=='gene':
        reads_df = pandas.read_csv(project+'/matrix/gene_expression.csv', sep=',', index_col=0,
                                   engine='c', na_filter=False, low_memory=False)
        gene = list(set([name]).intersection(set(reads_df.columns.values)))
        if len(gene)==0:
            print("No corresponding marker!")
            sys.exit()
        else:
            reads = reads_df.loc[cells, gene].values.sum(axis=1)
    elif feature=='accesson':
        reads_df = pandas.read_csv(project+'/matrix/Accesson_reads.csv', sep=',', index_col=0,
                   engine='c', na_filter=False, low_memory=False)
        normal = numpy.array([x/x.sum()*10000 for x in reads_df.values])
        reads_df = pandas.DataFrame(normal, index=reads_df.index, columns=reads_df.columns)
        reads = reads_df.loc[cells, name].values
#    print(reads.shape)
    order = numpy.argsort(reads)
    if clip!='none':
        reads = numpy.clip(reads, clip[0], clip[1])
#
    if space=='trajectory':
        clist = ['blue', 'silver', 'red']
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list('mylist', clist, N=256)
        fig1 = plt.figure(1, figsize=(12,10))
        ax = fig1.add_subplot(111, projection='3d')
        im = ax.scatter(matrix[order,0], matrix[order,1], matrix[order,2], cmap=cmap, c=reads[order], edgecolors='none', s=10)
        ax.view_init(angles[0], angles[1])
        cbar = plt.colorbar(im, shrink=0.15, ticks=[reads.min(), reads.max()], aspect=8)
        cbar.ax.set_yticklabels([round(reads.min(),2), round(reads.max(),2)])
        width = matrix[:,0].max()-matrix[:,0].min()
        height = matrix[:,1].max()-matrix[:,1].min()
        rad = matrix[:,2].max()-matrix[:,2].min()
        ax.set_xlim((matrix[:,0].min()-0.01*width, matrix[:,0].max()+0.01*width))
        ax.set_ylim((matrix[:,1].min()-0.01*height, matrix[:,1].max()+0.01*height))
        ax.set_zlim((matrix[:,2].min()-0.01*rad, matrix[:,2].max()+0.01*rad))
        ax.set_zticks([])
    else:
        fig1 = plt.figure(1, figsize=(6,5))
        ax = fig1.add_subplot(111)
        im = ax.scatter(matrix[order,0], matrix[order,1],  cmap='Spectral_r', c=reads[order], edgecolors='none', s=20)
        cbar = plt.colorbar(im, shrink=0.15, ticks=[reads.min(), reads.max()], aspect=8)
        cbar.ax.set_yticklabels([round(reads.min(),2), round(reads.max(),2)])
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(feature+'    '+name)
    outfig = project+'/figure/'+feature+'_'+name+'_on_'+space+'_by_'+matrix_type+'.pdf'
    fig1.savefig(outfig, bbox_inches='tight')
    plt.close()
    print('plot_feature output files:')
    print(outfig)
    return
#
#
#
