import pandas as pa
import numpy as np
from scipy.sparse import csr_matrix, isspmatrix
from MICTI import MARKERS
from MICTI import normalize
from MICTI import GeoMinner
import sys

def MICTI(sparceMatrix,geneNames,cellNames,k=None,cluster_assignment=None, th=0,normalized=True, UMI=False, ensembel=False, organisum="hsapiens"):
    #check sparcity of the matrix
    if(sparceMatrix.shape[0]!=len(cellNames)):
        print("The number of cells and the given cell names does not match")
        sys.exit()
    elif(sparceMatrix.shape[1]!=len(geneNames)):
        print("The number of genes and the given gene names does not match")
        sys.exit()
    else:
        #check cluster assignment if it is provided by the user
        if(cluster_assignment is not None):
            if(len(cluster_assignment)!=len(cellNames)):
                print("the number of cells and cluster assignment does not match")
                sys.exit()
            else:
                labelMatrix=pa.get_dummies(cluster_assignment)
                labelArray=np.argwhere(np.array(labelMatrix))[:,1]
                kk=len(set(labelArray))
                cluster_labels=sorted(list(set(cluster_assignment)))
        else:
            labelArray=None
            cluster_labels=None
            kk=k
        if(normalized):
            #change to sparce matrix if the data is not in a sparce matrix format        
            if not isspmatrix(sparceMatrix):
                sparceMatrix=csr_matrix(sparceMatrix)
        else:
            if not isspmatrix(sparceMatrix):
                if(UMI):
                    sparceMatrix=normalize.normalizeUMIWithscalefactor(sparceMatrix)
                else:
                    sparceMatrix,geneNames=normalize.getTPM(sparceMatrix.T,gene_Names=geneNames,ensembol_gene=ensembel)
                    #print(sparceMatrix.shape)
                    
                sparceMatrix=csr_matrix(sparceMatrix)
            else:
                sparceMatrix=normalize.normalizeUMIWithscalefactor(sparceMatrix)
                sparceMatrix=csr_matrix(sparceMatrix)
        #creat micti object
        micti_obj=MARKERS.MICTI(sparceMatrix,geneNames,cellNames,k=kk,cluster_label=cluster_labels,cluster_assignment=labelArray, th=th, ensembel=ensembel, organisum=organisum)
    return micti_obj