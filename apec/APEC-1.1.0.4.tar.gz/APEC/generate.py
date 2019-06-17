import numpy,pandas,os,sys,time,scipy.io,scipy.sparse,scipy.stats
#import numba
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn
from sklearn.decomposition import PCA
#
#
######## generate pseudotime trajectory by calling monocle
#
#
def monocle_trajectory(project, npc=5):
    """
    project:  Path to the project folder.
    npc:      Number of principal components used to build trajectory, default=5.
    """
    from rpy2.robjects.packages import importr
    from rpy2 import robjects
    reads_csv = project+'/matrix/Accesson_reads.csv'
    reads = pandas.read_csv(reads_csv, sep=',', index_col=0, engine='c', na_filter=False, low_memory=False)
    accessons = pandas.read_csv(project+'/matrix/Accesson_peaks.csv', sep='\t', index_col=0)
    matrix = numpy.around(reads.values, decimals=6)
    normal = numpy.array([x/x.sum()*1000000 for x in matrix])
    reads = pandas.DataFrame(normal, index=reads.index.values, columns=reads.columns.values)
#
    pca_result = PCA(n_components=npc, svd_solver='full').fit_transform(reads)
    reads = pandas.DataFrame(pca_result[:, :npc], columns=['pc'+str(x) for x in numpy.arange(0,npc)], index=reads.index)
    celltype_df = pandas.read_csv(project+'/matrix/filtered_cells.csv', sep='\t', index_col=0)
    input_csv = project+'/matrix/monocle_reads.csv'
    cells_csv = project+'/matrix/monocle_cells.tsv'
    peaks_csv = project+'/matrix/monocle_peaks.tsv'
    trajectory_csv = project+'/result/monocle_trajectory.csv'
    reduced_csv = project+'/result/monocle_reduced_dimension.csv'
    peaks_df = pandas.DataFrame(reads.columns.values, index=reads.columns.values, columns=['gene_short_name'])
    peaks_df.to_csv(peaks_csv, sep='\t')
    celltype_df.to_csv(cells_csv, sep='\t')
    reads.T.to_csv(input_csv, sep=',')
#
    importr("monocle")
    expr_matrix = robjects.r('read.csv')(input_csv, header=True, sep=',', **{'row.names':1, 'check.names':False})
    cells = robjects.r('read.delim')(cells_csv, **{'row.names':1})
    genes = robjects.r('read.delim')(peaks_csv, **{'row.names':1})
    pd = robjects.r('new')("AnnotatedDataFrame", data=cells)
    fd = robjects.r('new')("AnnotatedDataFrame", data=genes)
    matrix = robjects.r('as.matrix')(expr_matrix)
    negbinomial_size = robjects.r('negbinomial.size')()
    HSMM = robjects.r('newCellDataSet')(matrix, phenoData=pd, featureData=fd, expressionFamily=negbinomial_size)
    HSMM = robjects.r('estimateSizeFactors')(HSMM)
    HSMM = robjects.r('reduceDimension')(HSMM, max_components=3, norm_method='none', num_dim=20, reduction_method='DDRTree')
    HSMM = robjects.r('orderCells')(HSMM)
    robjects.r('write.csv')(HSMM.slots['reducedDimS'], reduced_csv)
    phenoData = HSMM.slots['phenoData']
    robjects.r('write.csv')(phenoData.slots['data'], trajectory_csv)
    print('monocle_trajectory output files:')
    print(trajectory_csv)
    print(reduced_csv)
    return
#
#
######## generate pseudotime trajectory by calling paga
#
#
def paga_trajectory(project, cell_label='notes', npc=5):
    """
    project:        Path to the project folder.
    cell_label:     Color labels for cells, can be 'notes' or 'cluster', default='notes'.
    npc:            Number of principal components used to build trajectory, default=5.
    """
    import scanpy,anndata
    matrix_df = pandas.read_csv(project+'/matrix/Accesson_reads.csv', sep=',', index_col=0,
                                engine='c', na_filter=False, low_memory=False)
    normal = numpy.array([x/x.sum()*1000000 for x in matrix_df.values])
    matrix_df = pandas.DataFrame(normal, index=matrix_df.index.values, columns=matrix_df.columns.values)
    if cell_label=='notes':
        cells_csv = project+'/matrix/filtered_cells.csv'
    elif cell_label=='cluster':
        cells_csv = project+'/result/louvain_cluster_by_APEC.csv'
    else:
        print("Error: wrong <cell_label>, should be 'notes' or 'cluster' !")
        sys.exit()
    cells_df = pandas.read_csv(cells_csv, sep='\t', index_col=0)
    if cell_label=='cluster':
        cells_df[cell_label] = ['cluster_'+str(x) for x in cells_df[cell_label]]
    accessons = matrix_df.columns.values
    acces_df = pandas.DataFrame(accessons, index=['acc_'+str(x) for x in accessons], columns=['index'])
    adata = anndata.AnnData(matrix_df.values, obs=cells_df, var=acces_df)
    scanpy.pp.recipe_zheng17(adata, n_top_genes=len(adata.var), log=False)
    scanpy.tl.pca(adata, svd_solver='arpack')
    scanpy.pp.neighbors(adata, n_neighbors=10, n_pcs=npc)
    scanpy.tl.diffmap(adata)
    scanpy.pp.neighbors(adata, n_neighbors=10, use_rep='X_diffmap')
    scanpy.tl.paga(adata, groups=cell_label)
    fig0, ax0 = plt.subplots(1, 1, figsize=(10,10))
    scanpy.pl.paga(adata, color=cell_label, ax=ax0, show=False)
    outfig0 = project+'/figure/paga_skeleton_with_'+cell_label+'_label.pdf'
    fig0.savefig(outfig0, bbox_inches='tight')
    scanpy.tl.draw_graph(adata, init_pos='paga')
    fig, ax = plt.subplots(1, 1, figsize=(10,10))
    scanpy.pl.draw_graph(adata, color=cell_label, legend_loc='on data', ax=ax, show=False)
    outfig = project+'/figure/paga_trajectory_with_'+cell_label+'_label.pdf'
    fig.savefig(outfig, bbox_inches='tight')
    print('paga_trajectory output files:')
    print(outfig0)
    print(outfig)
    return
#
#
######## generate gene score from nearby peaks
#
#
def get_tss_region(project, genome_gtf):
    genome_df = pandas.read_csv(genome_gtf, sep='\t', index_col=0)
    genes = list(set(genome_df['name2']))
    genes.sort()
    genome_df.index = genome_df['name']
    names, tss = [], []
    for symbol in genes:
        sub_df = genome_df.loc[genome_df['name2']==symbol]
        if len(sub_df.index.values)>=1:
            chrom = list(set(sub_df['chrom'].values))
            strand = list(set(sub_df['strand'].values))
            if len(chrom)==1:
                if strand[0]=='+':
                    starts = list(set(map(str, sub_df['txStart'].values)))
                    start = ','.join(starts)
                elif strand[0]=='-':
                    starts = list(set(map(str, sub_df['txEnd'].values)))
                    start = ','.join(starts)
                names.append(symbol)
                tss.append([chrom[0], start])
    tss = numpy.array(tss)
    tss_df = pandas.DataFrame(tss, index=names, columns=['chrom', 'tss'])
    tss_df.to_csv(project+'/peak/genes_tss_region.csv', sep='\t')
    return
#
#
def get_tss_peaks(project, distal=20000):
    peaks = [[x.split()[0], (int(x.split()[1])+int(x.split()[2]))/2]
             for x in open(project+'/peak/top_filtered_peaks.bed').readlines()]
    peaks_df = pandas.DataFrame(peaks, index=[str(x) for x in numpy.arange(0,len(peaks))],
                                columns=['chrom', 'center'])
    tss_df = pandas.read_csv(project+'/peak/genes_tss_region.csv', sep='\t', index_col=0)
    for gene in tss_df.index.values:
        chrom, tsses = tss_df.ix[gene, 'chrom'], tss_df.ix[gene, 'tss']
        tsses = map(int, tsses.split(','))
        chr_peaks = peaks_df.loc[peaks_df['chrom']==chrom]
        proxim_peaks, distal_peaks = [], []
        for tss in tsses:
            peaks1 = chr_peaks.loc[abs(chr_peaks['center']-tss)<=2000].index.values
            peaks2 = chr_peaks.loc[abs(chr_peaks['center']-tss)<=distal].index.values
            proxim_peaks.extend(peaks1)
            distal_peaks.extend(peaks2)
        proxim_peaks = list(set(proxim_peaks))
        distal_peaks = list(set(distal_peaks)-set(proxim_peaks))
        if len(proxim_peaks)==0: proxim_peaks = ['NONE']
        if len(distal_peaks)==0: distal_peaks = ['NONE']
        proxim_peaks = ';'.join(proxim_peaks)
        tss_df.ix[gene, 'proximal'] = proxim_peaks
        distal_peaks = ';'.join(distal_peaks)
        tss_df.ix[gene, 'distal'] = distal_peaks
    tss_df.to_csv(project+'/peak/genes_TSS_peaks.csv', sep='\t')
    return
#
#
def get_score_from_peaks(project):
    tss_df = pandas.read_csv(project+'/peak/genes_TSS_peaks.csv', sep='\t', index_col=0)
    reads = scipy.sparse.csr_matrix(scipy.io.mmread(project+'/matrix/filtered_reads.mtx')).T
    cells_df = pandas.read_csv(project+'/matrix/filtered_cells.csv', sep='\t', index_col=0)
    all_peaks = numpy.arange(0, reads.shape[1])
    genes, score = [], []
    for igene,gene in enumerate(tss_df.index.values):
        distal = tss_df.loc[gene, 'distal'].split(';')
        proximal = tss_df.loc[gene, 'proximal'].split(';')
        if distal==['NONE']:
            distal = []
        else:
            distal = list(map(int, distal))
        if proximal==['NONE']:
            proximal = []
        else:
            proximal = list(map(int, proximal))
        distal = list(set(distal).union(set(proximal)))
        distal = list(set(distal).intersection(set(all_peaks)))
        if len(distal)>0:
            signal = reads[:, distal].A.mean(axis=1)
            genes.append(gene)
            score.append(signal)
    score = numpy.array(score)
    score_df = pandas.DataFrame(score, index=genes, columns=cells_df.index)
    score_per_cell = score.sum(axis=0)
    R_wave = [numpy.log(x*10000.0/score_per_cell[i]+1) for i,x in enumerate(score.T)]
    R_wave = numpy.array(R_wave)
    normal_df = pandas.DataFrame(R_wave.T, index=genes, columns=cells_df.index)
    normal_df.to_csv(project+'/matrix/genes_scored_by_TSS_peaks.csv', sep=',')
    return
#
#
#
#@numba.jit()
def nearby_genes(project, genome_gtf, distal=20000):
    """
    project:     Path to the project folder.
    genome_gtf:  hg19_RefSeq_genes.gtf or mm10_RefSeq_genes.gtf in reference folder
    distal:      Genome distance for distal region, default=20000.
    """
    peaks = [[x.split()[0], (int(x.split()[1])+int(x.split()[2]))/2]
             for x in open(project+'/peak/top_filtered_peaks.bed').readlines()]
    peaks_df = pandas.DataFrame(peaks, index=['peak'+str(x) for x in numpy.arange(0,len(peaks))],
                                columns=['chrom', 'center'])
    get_tss_region(project, genome_gtf)
    tss_df = pandas.read_csv(project+'/peak/genes_tss_region.csv', sep='\t', index_col=0)
    for ipeak,peak in enumerate(peaks_df.index.values):
        chrom, center = peaks_df.loc[peak, 'chrom'], peaks_df.loc[peak, 'center']
        sub_tss_df = tss_df.loc[tss_df['chrom']==chrom]
        close_genes = []
        for gene in sub_tss_df.index.values:
            positions = numpy.array(list(map(int, sub_tss_df.loc[gene, 'tss'].split(','))))
            close_index = numpy.where(abs(positions-center)<=distal)[0]
            if len(close_index)>0:
                close_genes.append(gene)
        if len(close_genes)>0:
            peaks_df.loc[peak, 'nearby_genes'] = ';'.join(close_genes)
        else:
            peaks_df.loc[peak, 'nearby_genes'] = 'NONE'
        if ipeak%1000==0: print(ipeak, close_genes)
    peaks_df.to_csv(project+'/peak/peaks_nearby_genes.csv', sep='\t')
    print('nearby_genes output files:')
    print(project+'/peak/peaks_nearby_genes.csv')
    return
#
#
def gene_score(project, genome_gtf='', distal=20000):
    """
    project:     Path to the project folder.
    genome_gtf:  Path to hg19_RefSeq_genes.gtf or mm10_RefSeq_genes.gtf in $reference folder.
    distal:      Genome distance for distal region, default=20000.
    """
    get_tss_region(project, genome_gtf)
    get_tss_peaks(project, distal=20000)
    get_score_from_peaks(project)
    print('gene_score output files:')
    print(project+'/peak/genes_TSS_peaks.csv')
    print(project+'/matrix/genes_scored_by_TSS_peaks.csv')
    return
#
#
#### generate gene expression
#
#
def annotate_peak(project, genome='hg19'):
    peaks_bed = project + '/peak/top_filtered_peaks.bed'
    annotated = project + '/peak/top_annotated_peaks.bed'
    os.popen('annotatePeaks.pl '+peaks_bed+'  '+genome+' -strand both -size given > '+annotated)
    return
#
#
def annotate_accessons(project, width=1e6, pvalue=0.01):
    peak_bed = project + '/peak/top_filtered_peaks.bed'
    accesson_csv = project + '/matrix/Accesson_peaks.csv'
    annotated_bed = project + '/peak/top_annotated_peaks.bed'
    peak_list = [[x.split()[0], (int(x.split()[1])+int(x.split()[2]))//2] for x in open(peak_bed).readlines()]
    peak_index = ['peak'+str(x) for x in range(0, len(peak_list))]
    peak_df = pandas.DataFrame(peak_list, index=peak_index, columns=['chromosome', 'base'])
    annotated_df = pandas.read_csv(annotated_bed, sep='\t', index_col=0,
                                   engine='c', na_filter=False, low_memory=False)
    annotated_df.index = ['peak'+str(x).split('-')[-1] for x in annotated_df.index.values]
    accesson_df = pandas.read_csv(accesson_csv, sep='\t', index_col=0,
                                  engine='c', na_filter=False, low_memory=False)
    accessons = list(set(accesson_df['group'].values))
    accessons.sort()
    accesson_annotate = pandas.DataFrame(columns=['genes', '-log10(P-value)'])
    gene_annotate = pandas.DataFrame(columns=['accessons', '-log10(P-value)'])
    for acc in accessons:
        accPeak_df = peak_df.loc[accesson_df.loc[accesson_df['group']==acc].index]
        genes = {}
        for peak in accPeak_df.index.values:
            chrom, base = accPeak_df.loc[peak, 'chromosome'], accPeak_df.loc[peak, 'base']
            base_up, base_down = base - width, base + width
            sameChrom_in_acc = accPeak_df.loc[accPeak_df['chromosome']==chrom]
            sameChrom_overall = peak_df.loc[peak_df['chromosome']==chrom]
            sameRegion_in_acc = numpy.where(abs(sameChrom_in_acc['base']-base)<=width)[0]
            sameRegion_overall = numpy.where(abs(sameChrom_overall['base']-base)<=width)[0]
            matrix = numpy.array([[len(sameRegion_in_acc), len(accPeak_df)-len(sameRegion_in_acc)],
                                  [len(sameRegion_overall), len(peak_df)-len(sameRegion_overall)]])
            odd, p_value = scipy.stats.fisher_exact(matrix)
            if p_value<=pvalue:
                gene_symbol = annotated_df.loc[peak, 'Gene Name']
                log10_P = -numpy.log10(p_value)
                if gene_symbol not in genes.keys():
                    genes[gene_symbol] = log10_P
                elif genes[gene_symbol] < log10_P:
                    genes[gene_symbol] = log10_P
        for gene in genes.keys():
            if gene not in gene_annotate.index.values:
                gene_annotate.loc[gene, 'accessons'] = str(acc)
                gene_annotate.loc[gene, '-log10(P-value)'] = str(genes[gene])
            else:
                gene_annotate.loc[gene, 'accessons'] += ';' + str(acc)
                gene_annotate.loc[gene, '-log10(P-value)'] += ';' + str(genes[gene])
        accesson_annotate.loc[acc, 'genes'] = ';'.join(genes.keys())
        accesson_annotate.loc[acc, '-log10(P-value)'] = ';'.join(list(map(str, genes.values())))
    accesson_annotate.to_csv(project+'/matrix/Accesson_annotated.csv', sep='\t')
    gene_annotate.to_csv(project+'/matrix/gene_annotated.csv', sep='\t')
    return
#
#
def get_gene_expression(project):
    gene_annotate = pandas.read_csv(project+'/matrix/gene_annotated.csv', sep='\t', index_col=0)
    accesson_matrix = pandas.read_csv(project+'/matrix/Accesson_reads.csv', sep=',', index_col=0,
                                      engine='c', na_filter=False, low_memory=False)
    genes, matrix = [], []
    for gene in gene_annotate.index.values:
        accessons = gene_annotate.loc[gene, 'accessons'].split(';')
        weight = list(map(float, gene_annotate.loc[gene, '-log10(P-value)'].split(';')))
        if len(accessons)>0:
            sub_matrix = accesson_matrix[accessons].values
            expression = numpy.average(sub_matrix, axis=1, weights=weight).T
            matrix.append(expression)
            genes.append(gene)
    matrix = numpy.array(matrix).T
    expression_df = pandas.DataFrame(matrix, index=accesson_matrix.index, columns=genes)
    expression_df.to_csv(project+'/matrix/gene_expression.csv', sep=',')
    return
#
#
def gene_expression(project, genome="hg19", width=1000000, pvalue=0.01):
    """
    project:     Path to the project folder.
    genome:      Genome reference for Homer, can be "hg19" or "mm10", default="hg19".
    width:       Width of Genome region for fisher exact test, default=1000000.
    pvalue:      P-value threshold for fisher exact test, default=0.01.
    """
    annotate_peak(project, genome=genome)
    annotate_accessons(project, width=width, pvalue=pvalue)
    get_gene_expression(project)
    print('gene_expression output files:')
    print(project+'/matrix/Accesson_annotated.csv')
    print(project+'/matrix/gene_annotated.csv')
    print(project+'/matrix/gene_expression.csv')
    return
#
#
######## generate motif-cell deviation matrix
#
#
def motif_search(info):
    motif, bgFile, threshold, motifFile, motifFasta, outFolder = info[0], info[1], info[2], info[3], info[4], info[5]
    motif_name = motif.split('-')[-1]
#    print(motif_name)
    fimoFile = outFolder + '/' + motif +'.fimo'
    os.popen('fimo --bgfile ' + bgFile + ' --text --thresh ' + threshold + ' --motif ' + motif_name
        + ' --no-qvalue --verbosity 1 ' + motifFile + ' ' + motifFasta + ' > ' + fimoFile)
    bedFile = outFolder + '/' + motif +'.bed'
    with open(fimoFile) as fimo, open(bedFile, 'w') as bed:
        for line in fimo:
            if line[0]=='#':
                continue
            else:
                words = line.split('\t')
                chrom = words[1].split(':')[0]
                start = int(words[1].split(':')[1].split('-')[0]) + int(words[2])
                end = int(words[1].split(':')[1].split('-')[0]) + int(words[3])
                strand, score, pvalue, name = words[4], words[5], words[6], words[0]
                newLine = chrom+'\t'+str(start)+'\t'+str(end)+'\t'+strand+'\t'+score+'\t'+pvalue+'\t'+name
                bed.write(newLine+'\n')
    os.popen('gzip ' + bedFile)
    os.popen('rm ' + fimoFile)
    return
#
#
def batch_fimo(backgroudFile, threshold, motifFile, motifFasta, outFolder, n_processor):
    from multiprocessing import Pool
    motifs = []
    with open(motifFile) as mfile:
        for line in mfile:
            words = line.split(' ')
            if words[0] == 'MOTIF':
                info = words[2][:-1]
                info = info.replace('::', '-')
                info = info.replace(' ', '-')
                info = info.replace(':', '-')
                motifs.append(info+'-'+words[1])
    nMotif = len(motifs)
    info = numpy.vstack((motifs, [backgroudFile]*nMotif, [threshold]*nMotif, [motifFile]*nMotif,
                         [motifFasta]*nMotif, [outFolder]*nMotif)).T
    pool = Pool(n_processor)
    pool.map(motif_search, info)
    pool.close()
    pool.join()
    return
#
#
def score_peaks(peaks_file, motif_folder, out_file):
    peaks_info = numpy.loadtxt(peaks_file,'str',delimiter="\t")
    files = [motif_folder+'/'+x for x in os.listdir(motif_folder)]
    files.sort()
    outData = numpy.zeros([len(peaks_info),len(files)])
    headers = []
    for i in range(0,len(files)):
        file = files[i]
        fName = file.split('/')[-1].split('.bed')[0].split('.narrowPeak')[0]
        if os.path.getsize(file)>80:
            chipData = numpy.loadtxt(file, 'str')
        else:
            chipData = []
        headers.append(fName)
        if len(chipData)>0:
            chip = {}
            for line in chipData:
                chrom, start, end = line[0], int(line[1]), int(line[2])
                if not chip.has_key(chrom):
                    chip[chrom] = [[start, end]]
                else:
                    chip[chrom].append([start, end])
            for j in range(0,len(peaks_info)):
                peakChr, peakStart, peakEnd = peaks_info[j,0], int(peaks_info[j,1]), int(peaks_info[j,2])
                try:
                    for site in chip[peakChr]:
                        if (site[0]>=peakStart) & (site[1]<=peakEnd):
                            outData[j,i]+=1
                            break
                except:
                    continue
    TFmotif_df = pandas.DataFrame(outData, index=['peak'+str(i) for i in numpy.arange(0,len(peaks_info))], columns=headers)
    TFmotif_df.to_csv(out_file, sep=',')
    return
#
#
def motif_matrix(project,
                 genome_fa='',   # =hg19_chr.fa or mm10_chr.fa
                 background='',   # =tier1_markov1.norc.txt
                 meme='',   # =JASPAR2018_CORE_vertebrates_redundant_pfms_meme.txt
                 pvalue=0.00005,   # P-value, default=0.00005
                 np=4   # Number of CPU cores, default=4
                 ):
    """
    project:     Path to the project folder.
    genome_fa:   Path to hg19_chr.fa or mm10_chr.fa in $reference folder.
    background:  Path to tier1_markov1.norc.txt in $reference folder.
    meme:        Path to JASPAR2018_CORE_vertebrates_redundant_pfms_meme.txt in $reference folder.
    pvalue:      P-value, default=0.00005.
    np:          Number of CPU cores used for parallel calculation, default=4.
    """
    top_peaks = project + '/peak/top_filtered_peaks.bed'
    trans_bias = project + '/peak/transposase_bias_filtered.bed'
    temp02_file = project + '/peak/temp02.bed'
    temp03_file = project + '/peak/temp03.bed'
    with open(top_peaks) as annotate_file, open(temp02_file, 'w') as temp02:
        for i, line in enumerate(annotate_file):
            words = line.split('\t')
            leave = words[0:3]
            temp02.write('\t'.join(leave)+'\n')
    os.popen('bedtools nuc -fi ' + genome_fa + ' -bed ' + temp02_file + ' > ' + temp03_file)
    with open(temp03_file) as temp03, open(trans_bias, 'w') as bias:
        for i, line in enumerate(temp03):
            if i>0:
                words = line.split('\t')
                leave = words[0:3] + [words[4]]
                bias.write('\t'.join(leave)+'\n')
#
    motif_folder = project + '/matrix/motif'
    peaks_file = project + '/peak/top_filtered_peaks.bed'
    if os.path.exists(motif_folder): os.popen('rm -rf ' + motif_folder)
    os.popen('mkdir ' + motif_folder)
    motifFasta = project + '/matrix/motif.fasta'
    os.popen('bedtools getfasta -fi ' + genome_fa + ' -bed ' + peaks_file + ' -fo ' + motifFasta)
    batch_fimo(background, pvalue, meme, motifFasta, motif_folder, np)
    TFmatrix_file = project + '/matrix/motif_filtered.csv'
    score_peaks(peaks_file, motif_folder, TFmatrix_file)
    print('motif_matrix output files:')
    print(TFmatrix_file)
    return
#
#
######## generate differential features
#
#
def group_cells(project, cell_label, cluster, target, vs):
    if cell_label=='notes':
        cells_csv = project+'/matrix/filtered_cells.csv'
    elif cell_label=='cluster':
        cells_csv = project+'/result/'+cluster+'_cluster_by_APEC.csv'
    else:
        print("Error: wrong <cell_label>, should be 'notes' or 'cluster' !")
        sys.exit()
    cells_df = pandas.read_csv(cells_csv, sep='\t', index_col=0)
    kCluster = target.split(',')
    if vs!='all': vsCluster = vs.split(',')
    if 'cluster' not in cells_df.columns.values:
        cells_df['cluster'] = cells_df['notes']
    else:
        kCluster = map(int, kCluster)
        if vs!='all': vsCluster = map(int, vsCluster)
    if vs=='all': vsCluster = list(set(cells_df['cluster'].values)-set(kCluster))
    cell_inCluster = cells_df.loc[cells_df['cluster'].isin(kCluster)].index.values
    cell_outCluster = cells_df.loc[cells_df['cluster'].isin(vsCluster)].index.values
    print('Cells in target cluster:', len(cell_inCluster))
    print('Cells in versus cluster:', len(cell_outCluster))
    return cell_inCluster, cell_outCluster
#
#
def differential_feature(project,
                         feature='accesson',   # ='accesson' or 'motif' or 'gene'
                         cell_label='cluster',   # ='cluster' or 'notes'
                         cluster='louvain',   # ='louvain' or 'KNN'
                         target='1',   # ='1'
                         vs='all',   # ='all' or '2' or '2,3,4'
                         pvalue=0.01,
                         log2_fold=1
                         ):
    """
    project:     Path to the project folder.
    feature:     Type of feature, can be 'accesson' or 'motif' or 'gene', default='accesson'.
                 If feature='accesson', run clustering.cluster_byAccesson() first;
                 if feature='motif', run clustering.cluster_byMotif() first;
                 if feature='gene', run generate.gene_expression() first.
    cell_label:  Cell labels used for differential analysis, can be 'notes' or 'cluster', default='cluster'.
    cluster:     Clustering algorithm used in clustering.cluster_byXXX(), can be 'louvain' or 'KNN', default='louvain'.
    target:      The target cluster that users search for differential features, default='1'.
                 if cell_label='cluster', target is one element in the 'cluster' column of XXX_cluster_by_XXX.csv file;
                 if cell_label='notes', target is one element in the 'notes' column of filtered_cells.csv file.
    vs:          Versus which clusters, can be '2,3,4' or 'all', default='all' (means all the rest clusters).
    pvalue:      P-value for student-t test, default=0.01.
    log2_fold:   Cutoff for log2(fold_change), default=1.
    """
    if feature=='accesson':
        reads_file = project+'/matrix/Accesson_reads.csv'
    elif feature=='motif':
        reads_file = project+'/result/deviation_chromVAR.csv'
    elif feature=='gene':
        reads_file = project+'/matrix/gene_expression.csv'
    else:
        print("Error: wrong <feature>, should be 'accesson' or 'motif' or 'gene' !")
        sys.exit()
    reads_df = pandas.read_csv(reads_file, sep=',', index_col=0,
                               engine='c', na_filter=False, low_memory=False)
    if feature=='motif': reads_df = reads_df.T
    cell_inCluster, cell_outCluster = group_cells(project, cell_label, cluster, target, vs)
    read_inCluster = reads_df.loc[cell_inCluster].values
    read_outCluster = reads_df.loc[cell_outCluster].values
    mean_in, mean_out = read_inCluster.mean(axis=0), read_outCluster.mean(axis=0)
    ttest, pvalues = scipy.stats.ttest_ind(read_inCluster, read_outCluster, equal_var=False)
    if feature=='motif':
        fold = mean_in - mean_out
    else:
        fold = numpy.log2((mean_in + 1e-4) / (mean_out + 1e-4))
    matrix = numpy.vstack((mean_in, mean_out, fold, pvalues)).T
    columns = ['mean_inCluster','mean_outCluster', 'log2_fold', 'p-value']
    matrix_df = pandas.DataFrame(matrix, index=reads_df.columns, columns=columns)
    matrix_df = matrix_df.loc[matrix_df['p-value'] <= float(pvalue)]
    matrix_df = matrix_df.loc[matrix_df['log2_fold'] >= float(log2_fold)]
    matrix_df = matrix_df.sort_values(by=['p-value'])
    nearby_csv = project+'/peak/peaks_nearby_genes.csv'
    if (feature=='accesson') & (os.path.exists(nearby_csv)):
        peaks_df = pandas.read_csv(project+'/matrix/Accesson_peaks.csv', sep='\t')
        nearby_genes_df = pandas.read_csv(nearby_csv, sep='\t')
        for accesson in matrix_df.index.values:
            peaks = peaks_df.loc[peaks_df['group']==int(accesson)].index.values
            genes = nearby_genes_df.loc[peaks, 'nearby_genes'].values
            genes = [str(x) for x in genes if (x!='NONE')&(type(x)==str)]
            genes = list(set(genes))
            genes.sort()
            genes = ';'.join(genes)
            matrix_df.loc[accesson, 'relevant_genes'] = genes
    out_csv = project+'/result/differential_'+feature+'_of_cluster_'+target+'_vs_'+'_'.join(vs.split(','))+'.csv'
    matrix_df.to_csv(out_csv, sep='\t')
    print('differential_feature output files:')
    print(out_csv)
#    print('Differential '+feature+' for cluster '+target+' VS '+vs+':')
#    print(feature+'\t'+'\t'.join(matrix_df.columns.values))
#    for x in matrix_df.index.values: print(str(x)+'\t'+'\t'.join(list(map(str, matrix_df.loc[x].values))))
    return
#
#
def peaks_of_accesson(project, accesson=1):
    """
    project:     Path to the project folder.
    accesson:    Number of accesson that users want to get the peak list.
    """
    peaks_df = pandas.read_csv(project+'/matrix/Accesson_peaks.csv', sep='\t', index_col=0)
    peaks_bed = numpy.array(open(project+'/peak/top_filtered_peaks.bed').readlines())
    peaks = peaks_df.loc[peaks_df['group']==accesson].index.values
    peaks_index = [int(x[4:]) for x in peaks]
    out_bed = project+'/result/accesson_'+str(accesson)+'_peaks.bed'
    with open(out_bed, 'w') as output:
        for line in peaks_bed[peaks_index]:
            words = line.split()
            output.write('\t'.join(words)+'\n')
    print('peaks_of_accesson output files:')
    print(out_bed)
    return
#
#
######## generate potential super enchancer
#
#
def search_super_enhancer(project, super_range=1000000):
    """
    project:         Path to the project folder.
    super_range:    Genome range to search for super enhancer, default=1000000.
    """
    peaks = numpy.array([x.split()[:3] for x in open(project+'/peak/top_filtered_peaks.bed').readlines()])
    chroms = list(set(peaks[:, 0]))
    chroms.sort()
    accesson_df = pandas.read_csv(project+'/matrix/Accesson_peaks.csv', sep='\t', index_col=0)
    accessons = list(set(accesson_df['group'].values))
    all_supers, all_locate, all_base = [], [], []
    for access in accessons:
        peaks_group = accesson_df.loc[accesson_df['group']==access].index.values
        peaks_index = [int(x[4:]) for x in peaks_group]
        peaks_info = peaks[peaks_index, :]
        peaks_dict = {x:[] for x in chroms}
        peaks_label = {x:[] for x in chroms}
        for ip,pp in enumerate(peaks_info):
            peaks_dict[pp[0]].append((int(pp[1])+int(pp[2]))/2)
            peaks_label[pp[0]].append(peaks_index[ip])
        peaks_label = {x:numpy.array(peaks_label[x]) for x in peaks_label.keys()}
        supers, locate, base = [], [], []
        for chrom in peaks_dict.keys():
            if len(peaks_dict[chrom])>=2:
                position = numpy.array(peaks_dict[chrom])
                super = [numpy.where(abs(position-x)<=super_range)[0] for x in position if
                      len(numpy.where(abs(position-x)<=super_range)[0])>1]
                super = ['-'.join(map(str, x)) for x in super]
                super = list(set(super))
                super = [list(map(int, x.split('-'))) for x in super]
                super_peaks = numpy.array(['-'.join(map(str, peaks_label[chrom][x])) for x in super])
                if len(super_peaks)>0:
                    for ii,ss in enumerate(super_peaks):
                        peaks_in = map(int, ss.split('-'))
                        start = peaks[peaks_in, 1:].astype(int).min()
                        end = peaks[peaks_in, 1:].astype(int).max()
                        delta = numpy.array([abs(peaks_in[i+1]-x) for i,x in enumerate(peaks_in[:-1])])
                        close = numpy.where(delta<=2)[0]
                        percent = len(close)/float(len(delta))
                        if (len(delta)>=2) & (percent>0.5) :
                            supers.append(ss)
                            locate.append(access)
                            base.append(chrom+':'+str(start)+'-'+str(end))
        all_supers.extend(supers)
        all_locate.extend(locate)
        all_base.extend(base)
    super_df = pandas.DataFrame(numpy.array([all_locate, all_base]).T, index=all_supers, columns=['peaks', 'position'])
    super_df.to_csv(project+'/result/potential_super_enhancer.csv', sep='\t')
    print('search_super_enhancer output files:')
    print(project+'/result/potential_super_enhancer.csv')
    return
#
#
