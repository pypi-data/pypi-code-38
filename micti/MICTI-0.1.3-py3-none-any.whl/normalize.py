import numpy as np 
import pandas as pa
from scipy.sparse import csr_matrix, isspmatrix
import pyensembl 
from pyensembl import EnsemblRelease

def normalizeUMIWithscalefactor(data, scale_factor=10e6):
    cellNormalizedData=np.log(1+(data/np.sum(data,axis=1)[0]))*scale_factor
    return(cellNormalizedData)

def gene_Length(list_of_genes, ensembl_id=True, Ensembl_Release=75):
    gn=EnsemblRelease(Ensembl_Release)
    if ensembl_id:
        gene_pos=list(map(gn.locus_of_gene_id, list_of_genes))
        gene_pos_end=[i.end for i in gene_pos]
        gene_pos_start=[i.start for i in gene_pos]
        
    else:
        gene_pos=list(map(gn.loci_of_gene_names, list_of_genes))
        gene_pos_end=[i[0].end for i in gene_pos]
        gene_pos_start=[i[0].start for i in gene_pos]

    gene_len=np.array(gene_pos_end)-np.array(gene_pos_start)
    return pa.DataFrame({'gene_names':list_of_genes, "gene_length":gene_len/1000})    

def getTPM(rowCountData, gene_Names=None, index_column=None, ensembol_gene=False, Ensembl_release=75):

    if(isspmatrix(rowCountData)):
        rowCountData=pa.DataFrame(rowCountData.toarray())
        rowCountData.index=gene_Names
        
    else:
        if index_column is not None:
            rowCountData.index=rowCountData[index_column]
            rowCountData=rowCountData.drop([index_column], axis=1)

    if ensembol_gene:
        known_genes=list(map(pyensembl.common.is_valid_ensembl_id,gene_Names)) 
        rowCountData=rowCountData.iloc[known_genes,:]
        
        rowCountData.index=np.array(gene_Names)[np.array(known_genes)]
        
        gene_length=gene_Length(gene_Names, ensembl_id=ensembol_gene, Ensembl_Release=Ensembl_release) 
    else:

        gene_length=gene_Length(gene_Names, ensembl_id=ensembol_gene, Ensembl_Release=Ensembl_release) 
        
    if(gene_length.shape[0]==rowCountData.shape[0]):
        
        count_data_RKB=rowCountData.div(list(gene_length["gene_length"]), axis=0)
    
        count_data_TPM=np.array(count_data_RKB)/ np.array(rowCountData.sum(axis=0)).reshape((1,len(rowCountData.sum(axis=0))))
    
        count_data_TPM=pa.DataFrame(count_data_TPM*10e6)
        count_data_TPM.index=list(rowCountData.index)
        count_data_TPM.columns=list(rowCountData.columns)
    
        count_data_TPM=count_data_TPM[(count_data_TPM.T != 0).any()].dropna(axis=0)
    else:
        print("one or more gene ids are not annoatated under", Ensembl_Release, "Please use different release")
        
    return count_data_TPM.T, list(count_data_TPM.index)

def ENSEMBLID_to_geneSymbol(ENSEMBL, Ensembl_Release=75):        
    data=EnsemblRelease(Ensembl_Release)
    if type(ENSEMBL) is list:
        Genes=list(map(data.gene_name_of_gene_id,ENSEMBL))
    else:
        Genes=data.gene_name_of_gene_id(ENSEMBL)
    return Genes

