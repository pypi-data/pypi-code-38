import HTSeq
import numpy as np
import itertools

def loadGTF(filename,ftype='exon',end_included=True,slice_start=0,slice_end=None):
    """
        load a gtf file into a hash table with features
        return 
            hash[tx_id]=list of features for this tx
            gas (GenomicArrayOfSets) holding exon intervals and gene names
        input parameters
            ftype: the feature type to extract from the GTF file
            end_included= (True for UCSC GFT files. see HTSeq documentation -*$&%@$~.>%$ if you can understand it)
            slice_start=0,slice_end=None # slicing the GTF file - default is not to slice
        
    """
    tx_hash=dict()
    gas = HTSeq.GenomicArrayOfSets( "auto", stranded=True )
    gtf_reader=HTSeq.GFF_Reader(filename, end_included=end_included)
    for feature in itertools.islice(gtf_reader,slice_start,slice_end):
        if ftype is not None:
            if feature.type!=ftype:
                continue
        if feature.iv.length<1:
            continue
        tx_name = feature.attr['transcript_id']
        # update hash table
        if tx_name in tx_hash:
            tx_hash[tx_name].append(feature)
        else:
            tx_hash[tx_name]=[feature]
        # update gas with the interval
        gas[ feature.iv ] += feature.name
    return tx_hash, gas
    

# creating a copy of a feature object
def GenomicFeatureFromOther(other):
    tmp = HTSeq.GenomicFeature(other.name, other.type, other.iv.copy())
    try:
        tmp.source = other.source
        tmp.attr=other.attr
        tmp.frame=other.frame
        #tmp.name=other.name
        tmp.score=other.score
    except:
        pass
    return tmp    
    
# finding the TES taking into account strand
def getTES(exons):
    """
        finding the TES taking into account strand
        exons = list(features)
    """
    
    strand = exons[0].iv.strand # assuming all features are on the same strand
    ex3ends = [ex.iv.start if strand =='-' else ex.iv.end for ex in exons]
    # which of the exons is the last one?
    TES = np.min(ex3ends) if strand=='-' else max(ex3ends)
    return TES

# return the index to the last exon taking into account strand
def getLastExonIdx(exons):
    """
        return the index to the last exon taking into account strand
        exons = list(features)
    """
    strand = exons[0].iv.strand # assuming all features are on the same strand
    ex3ends = [ex.iv.start if strand =='-' else ex.iv.end for ex in exons]
    loc=np.argmin(ex3ends) if strand=='-' else np.argmax(ex3ends)
    return loc

def findExonWindow(exon,gas,max_w3,safety_margin=0):
    """
        new_exon, min_w3_size = findExonWindow(exon,gas,max_w3,safety_margin=0)
        find the largest w3 window by which to extend the exon to the 3" direction which does not
        intersects any other exon (of any gene including the current one)
            max_w3 is the max window size
            gas = genomicArrayOfSets which holds the intervals of all exons
            safety_margin = # of base pairs to keep away from the next exon
        return window_size, new_extened_exon
        
        algorithm
            enlarge the max_w3 by the safety margin -> mrg_w3
            if there are no intesections on mrg_w3 -> enlarge the exon with original w3
            else, 
                find the min w3 window that does not overlaps any other exon -> min_w3
                subtract the margin min_w3-margin -> sml_w3
                enlarge by sml_w3 if sml_w3>0
            
    """
    
    new_exon = GenomicFeatureFromOther(exon)
    strand = exon.iv.strand
    if strand=='+':
        end = new_exon.iv.end+(max_w3+safety_margin)
        start = new_exon.iv.end
        TES = new_exon.iv.end
    elif strand=='-':        
        start = new_exon.iv.start-(max_w3+safety_margin)
        end = new_exon.iv.start
        TES = new_exon.iv.start
    else:
        print 'Error: strand is not defined!'
        raise valueError  
    
    # create the interval for the new extension
    ext_iv=HTSeq.GenomicInterval(new_exon.iv.chrom, start, end ,strand)

    distances=[max_w3+safety_margin]# will hold all distances from all overlapping exons
                    # then the min of the array will give the min distance to the TES

    for iv, step_set in gas[ext_iv].steps():
        #print iv, step_set 
        if len(step_set)>0:
            if strand=='+':
                distances.append(iv.start-TES)
            else:
                distances.append(TES-iv.end)
    min_w3_size = np.min(distances)
    # debug
    # print "\tmin_w3_size=",min_w3_size
    # just in case
    if min_w3_size<0:
        print "<min_w3_size> this should not happen!"
        raise valueError
    # correct the min distance by subtracting the added margin
    min_w3_size_corrected = min_w3_size-safety_margin
    if min_w3_size_corrected<0:
        # this means that the distance to the next exon is smaller than the margin 
        # and no change will be applied
        min_w3_size_corrected=0 
    
    # updating the last exon
    if strand=='+':
        new_exon.iv.end = new_exon.iv.end+min_w3_size_corrected
    elif strand=='-':
        new_exon.iv.start = new_exon.iv.start-min_w3_size_corrected
    else:
        print 'Error: strand is not defined!'
        raise valueError
    # debug
    # print "\t",distances
    return new_exon, min_w3_size_corrected    
    
# extend the last exon by w3 (away from the gene)
# note however that the window size will be altered if it intersects with a another exon
def extendLastExon(exons,gas,w3,safety_margin=0):
    strand = exons[0].iv.strand # assuming all features are on the same strand
    loc=getLastExonIdx(exons)
    # check if the start < (w3+safety_margin) (to avoid negative start position) if so return the original
    if exons[loc].iv.start - (w3+safety_margin) < 0:
        return exons
    # get an extened exon (creates a copy of the last exon and extend)
    new_exon, min_w3_size = findExonWindow(exons[loc],gas,w3,safety_margin)
    # update exons
    exons_new=[item for item in exons]
    exons_new[loc]=new_exon
    return exons_new      
    
def getUTRexons_rna_window(exons, gas, W3, W5, safety_margin=0):
    """
        this version defines the window to search for UTR on the RNA
        it counts exon's length from 3" to 5" until W5 bp are accumulated
        this simulates fragments from the 3"UTR on the RNA transcript
        input parameters
            exons = list of feature representing a single transcript
            gas = GenomicArrayOfSets for all features in the gtf file
            W5 the window to extend the 3" UTR exon to the 5" direction on the mRNA
            W3 the window by which to extend the 3" UTR exon away from the transcript on the DNA
            safety_margin = when extending the 3"UTR this is the # of base pairs to keep away from the next exon (strand specific).
                            for example extending the 3"UTR might hit the next gene (@ 5") 
        return 
            new exon list with selected exons from the 3" end that reach the W5 window
            the last exon might be extended by W3 or less 
    """
    # globals
    strand = exons[0].iv.strand
    crm = exons[0].iv.chrom
    # main
    TES = getTES(exons)
    # sort the exons last to 1st strand specific
    Isort = np.argsort([item.iv.start for item in exons])
    if strand == '+':
        Isort=Isort[::-1]
    # go from last to 1st exon and accumulate the length until you get at least W5
    accum_len=0
    utr_exons=[]
    for i in Isort:
        utr_exons.append(exons[i])
        accum_len+=exons[i].iv.length
        if accum_len>=W5:
            utr_exons[-1] = cut_w5_exon(utr_exons[-1], W5, accum_len, strand)
            break    
    # extend the last exone by W3 and return
    return extendLastExon(utr_exons,gas,W3,safety_margin)   

def cut_w5_exon(exon, W5, total_length, strand):
    new_exon = GenomicFeatureFromOther(exon)
    cut_number = total_length-W5
    if strand == '+':
        new_exon.iv.start += cut_number #the length is changed automatically.
    else:
        new_exon.iv.end -= cut_number
    return new_exon

# main interface
# --------------
"""
W3=100; W5=1000
filename = 'genes.gtf'
print "loading:", filename
tx_hash,gas=loadGTF(filename,slice_start=0,slice_end=None)
outfile = 'genes.utrs2.gtf'
fid=open(outfile,'w')
print 'loopping over all Tx ...'
for tx_id in tx_hash:
    exons = tx_hash[tx_id]
    utr_exons = getUTRexons_rna_window(exons, gas, W3, W5)
    for item in utr_exons:
        fid.write(item.get_gff_line())
fid.close()
"""

def getGeneExtensionPairs(selected_genes_file):
    """
        input is a tab delimited file, containing 2 columns: 
        column 1 is the gene name 
        column 2 is the window in bp by which to extend the 3" UTR exon away from the transcript on the DNA (will replace the default W3 for that specific gene)
    """
    genes = dict()
    if selected_genes_file is None:
        return genes
    with open(selected_genes_file,'r') as f:
        for line in f:
            line_arr = line.split("\t")
            genes[line_arr[0]] = int(line_arr[1])
    return genes


import argparse
def parseArgs():
    parser = argparse.ArgumentParser(description='This module manipulates GFT files by selecting a subset of the exons that represent the 3" UTRs')
    parser.add_argument('--input-gtf', help='Input gtf filename (read)', required=True)
    parser.add_argument('--output-gtf', help='Output gtf filename (write)', required=True)
    parser.add_argument('--gtf-end-included', nargs='?',default=True, help='True for UCSC GFT files. see HTSeq documentation - if you can understand it', required=False)
    parser.add_argument('--w3', help='The window in bp by which to extend the 3" UTR exon away from the transcript on the DNA (100 is a good number)',required=True)
    parser.add_argument('--w5', help='The window in bp by which to extend or cut the 3" UTR exon towards the 5" direction on the mRNA',required=True)
    parser.add_argument('--ig-margin', help='The intergenic safety margin. When extending the 3"UTR this is the number of base pairs to keep away from the next exon (50 is a good number).',required=True)
    parser.add_argument('--selected-genes', help='Input tab-delimited file containing list of genes that need to be extended, in the format: <gene_name>    <number of bps to add to 3"UTR>', required=False);    
    args = parser.parse_args()
    return args

def printArgs():
    args = parseArgs()
    print '--input-gtf: ',args.input_gtf
    print '--output-gtf: ',args.output_gtf
    print '--gtf-end-included: ',args.gtf_end_included
    print '--w3: ', args.w3
    print '--w5: ', args.w5
    print '--ig-margin: ', args.ig_margin
    print '--selected-genes: ', args.selected_genes
    
if __name__ == "__main__":
    args = parseArgs()
    w3=int(args.w3)
    w5=int(args.w5)
    safety_margin=int(args.ig_margin)
    # loading the gtf file
    print 'Loading GTF file:',args.input_gtf
    print 'Assuming HTSeq::end-included =',args.gtf_end_included
    tx_hash,gas=loadGTF(args.input_gtf,end_included=args.gtf_end_included,slice_start=0,slice_end=None)
    genes_list = getGeneExtensionPairs(args.selected_genes)
    
    # looping over all transcripts
    print 'looping over all Tx ...'
    print 'using the following default window parameters:'
    print '--w3: ', args.w3
    print '--w5: ', args.w5
    print '--ig-margin: ', args.ig_margin    
    fid=open(args.output_gtf,'w')
    for tx_id in tx_hash:
        exons = tx_hash[tx_id]
        # if gene is not given as input, then use the default w3
        gene_name = exons[0].attr['gene_name']        
        w3 = genes_list[gene_name] if (gene_name in genes_list.keys()) else int(args.w3)
        utr_exons = getUTRexons_rna_window(exons, gas, w3, w5, safety_margin=safety_margin)
        sum=0#Debug
        for item in utr_exons:
            sum+=item.iv.length#Debug
            fid.write(item.get_gff_line())
#        print sum #Debug
    fid.close()

# sum = 0
# for item in utr_exons:
#     sum += item.iv.length
#     print item.name, item.iv.start, item.iv.end, item.iv.strand, item.iv.length, 'enlarge'
#     fid.write(item.get_gff_line())
# print 'end transcript, sum is: ', sum
