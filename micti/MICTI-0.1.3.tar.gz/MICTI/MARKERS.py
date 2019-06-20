from . import Kmeans
from . import GM 
from . import radarPlot
from . import heatmap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pa
from scipy.sparse import csr_matrix, isspmatrix
from scipy.sparse import csgraph
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise_distances
import mpl_toolkits.mplot3d.axes3d as p3
import pylab as p
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
import sys
import os
import time
from matplotlib.lines import Line2D
from matplotlib.pyplot import cm
from collections import Counter
from gprofiler import gprofiler
import copy
import operator
import scipy
import seaborn as sns
import random
from gensim.models import HdpModel,LdaModel
from sklearn import cluster
from sklearn.neighbors import kneighbors_graph
from sklearn import metrics

class MICTI:
    def __init__(self,data,geneNames,cellNames,k=None,cluster_label=None,cluster_assignment=None, th=0,seed=None, ensembel=False, organisum="hsapiens"):
        self.data=data
        self.k=k
        self.th=th
        self.geneNames=geneNames
        self.cellNames=cellNames
        self.seed=seed
        self.ensembl=ensembel
        self.organsm=organisum
        self.cluster_assignment=cluster_assignment
        self.cluster_label=cluster_label
        self.color=cluster_assignment
        self.color_dict={}
        self.data_ICF=self.ICF(self.data)
        self.initialize_colors()
        

    def get_cluster_assignment(self):
        return self.cluster_assignment
    
    def initialize_colors(self):
        
        colors=['#ffe119','#0082c8','#f58231','#911eb4','#46f0f0','#f032e6','#d2f53c','#fabebe','#008080','#e6beff',
                '#aa6e28','#fffac8','#800000','#aaffc3','#808000','#ffd8b1','#000080','#808080','#FFFFFF','#000000'][:self.k]
        
        cell_type=pa.Series([self.cluster_label[j] for j in self.cluster_assignment])
        cell_type=cell_type.sort_values()
        lut2=dict(zip(cell_type.sort_values().unique(), colors))
        lut2=dict(sorted(lut2.items()))
        col_colors= cell_type.map(lut2)
        col_colors.index=pa.Series(self.cellNames)[cell_type.index]
        
        mycol=[{k:tuple(np.array(self.hex_to_rgb(v))/255)} for k, v in lut2.items()]
        self.color_dict={}
        [self.color_dict.update(c) for c in mycol]

        self.color=[lut2[self.cluster_label[i]] for i in self.cluster_assignment]
        self.color_dict=lut2
        return None

    def cellMatrix2cellCorpus(self, datamatrix):
        cell_Courpus=[]
        for k in range(datamatrix.shape[0]):
            cell_Courpus.append([(i,j) for i, j in enumerate(datamatrix.iloc[k,:])])

        id2gene={i:j for i,j in enumerate(datamatrix.columns)}
        id2cell={i:j for i,j in enumerate(datamatrix.index)}
        return cell_Courpus, id2gene, id2cell

    def gene_symbol_to_ENSEMBLID(self, symbol, organisum="hsapiens"):
        if(organisum=="hsapiens"):
            genes=pa.read_csv("https://media.githubusercontent.com/media/insilicolife/micti/master/data/mart_export_stable_genes_human.txt", sep="\t")
            genes.index=genes["Gene name"] 
            ENSEBMLID=genes.loc[symbol,"Gene stable ID"]
            Genes=ENSEBMLID.dropna().drop_duplicates()
        elif(organisum=="mmusculus"):
            genes=pa.read_csv("https://media.githubusercontent.com/media/insilicolife/micti/master/data/mart_export_mouse_stable_gene.txt", sep="\t")
            genes.index=genes["Gene name"] 
            ENSEBMLID=genes.loc[symbol,"Gene stable ID"]
            Genes=ENSEBMLID.dropna().drop_duplicates()
        else:
            Genes=symbol
            #print("give organisum")
            
        return Genes
    
    def ENSEMBLID_to_geneSymbol(self, ENSEMBL, organisum="hsapiens"):
        if(organisum=="hsapiens"):
            genes=pa.read_csv("https://media.githubusercontent.com/media/insilicolife/micti/master/data/mart_export_stable_genes_human.txt", sep="\t")
            genes.index=genes["Gene stable ID"] 
            gene_symbol=genes.loc[ENSEMBL,"Gene name"]
            Genes=gene_symbol.dropna().drop_duplicates()
        elif(organisum=="mmusculus"):
            genes=pa.read_csv("https://media.githubusercontent.com/media/insilicolife/micti/master/data/mart_export_mouse_stable_gene.txt", sep="\t")
            genes.index=genes["Gene stable ID"] 
            gene_symbol=genes.loc[ENSEMBL,"Gene name"]
            Genes=gene_symbol.dropna().drop_duplicates()
        else:
            Genes=ENSEMBL
            #print("give organisum")
        return Genes
    
    def ICF(self,data):
        
        matrixx=pa.DataFrame((data.T.toarray()))
        totalCells=matrixx.shape[1]
        idf=np.log(totalCells/np.array(matrixx[matrixx > self.th].count(axis=1).add(1)))
        icf_matrix=matrixx.T*np.array(idf)
        return np.array(icf_matrix) 
    
    def get_Visualization(self,dim=2,method="PCA"):
        
        if method=="PCA":
                if dim>3:
                        print ("Please give at most three dimentions")
                else:
                        svd = TruncatedSVD(n_components=dim)
                        if isspmatrix(self.data):
                            svd_fit = svd.fit(self.data.toarray())
                            svdTransform=svd.fit_transform(self.data.toarray())
                        else:
                            svd_fit = svd.fit(self.data)
                            svdTransform=svd.fit_transform(self.data)
                                
                        if dim==3:
                                fig=p.figure()
                                ax = p3.Axes3D(fig)
                                ax.scatter(svdTransform[:,0], svdTransform[:,1], svdTransform[:,2], c=self.color)
                                ax.set_xlabel("PCA1")
                                ax.set_ylabel("PCA2")
                                ax.set_zlabel("PCA3")
                                fig.add_axes(ax)
                                p.show()
                        elif dim==2:
                                plt.scatter(svdTransform[:,0], svdTransform[:,1], c=self.color)
                                plt.xlabel("PCA1")
                                plt.ylabel("PCA2")
                                plt.suptitle("MICTI with k={0:d}".format(self.k), fontsize=8)
                                plt.legend(bbox_to_anchor=(1.65, 1.65), loc='center', ncol=1)
                                plt.legend(list(self.cluster_assignment))
                                plt.show()
                        else:
                                print ("dimentionality error")
        elif method=="tsne":

                if dim>3:
                        print ("Please give at most three dimentions")
                else:
                        svd = TruncatedSVD(n_components=5)
                        if isspmatrix(self.data):
                            svd_fit = svd.fit(self.data.toarray())
                            svdTransformTsne=svd.fit_transform(self.data.toarray())
                        else:
                            svd_fit = svd.fit(self.data)
                            svdTransformTsne=svd.fit_transform(self.data)
                            
                        X_tsne=TSNE(n_components=dim, random_state=0)
                        x_tsne=X_tsne.fit_transform(svdTransformTsne)
                        if dim==3:
                                fig=p.figure()
                                ax = p3.Axes3D(fig)
                                ax.scatter(x_tsne[:,0], x_tsne[:,1], x_tsne[:,2], c=self.color)
                                ax.set_xlabel("tsne1")
                                ax.set_xlabel("tsne2")
                                ax.set_xlabel("tsne3")
                                fig.add_axes(ax)
                                p.show()
                        elif dim==2:
                                data = pa.DataFrame(columns=['tsne_1','tsne_2','cell type'])
                                data['cell type']=[self.cluster_label[i] for i in list(self.cluster_assignment)]
                                
                                data['tsne_1']=x_tsne[:,0]
                                data['tsne_2']=x_tsne[:,1]
                                
                                if len(self.color_dict)>0:
                                    facet = sns.lmplot(data=data, x='tsne_1', y='tsne_2', hue='cell type', fit_reg=False, legend=True, legend_out=True, palette=self.color_dict, order=5)
                                else:
                                    facet = sns.lmplot(data=data, x='tsne_1', y='tsne_2', hue='cell type', fit_reg=False, legend=True, legend_out=True)
                             
                                plt.savefig("MICTI_Plot.pdf", format="pdf", dpi=300, bbox_inches='tight')
                                plt.show()
                        else:
                                print ("dimetionality error")
        else:
                print ("Please give method==pca or method=tsne")

        
    def get_cluster_data(self, cluster_number):
        return self.data.toarray()[np.in1d(np.array(self.cluster_assignment), cluster_number),:], self.cellNames[np.in1d(np.array(self.cluster_assignment), cluster_number)]
    
    def get_cluster_ICF_data(self, cluster_number):
        return self.ICF(self.data[np.in1d(np.array(self.cluster_assignment), cluster_number),:])
    
    def get_cluster_CF_data(self,cluster_number):
        return self.CF(self.data[np.in1d(np.array(self.cluster_assignment), cluster_number),:]) 
    
    def get_selected_cluster_marker(self, clusters):
        
        datta=self.data[np.in1d(np.array(self.cluster_assignment), clusters),:]
        index=self.cluster_assignment[np.in1d(np.array(self.cluster_assignment), clusters)]
        dat_common=self.CF(datta)
        dat_identity=self.ICF(datta)
        idd_com=[] 
        idd_j=[]
        for j in clusters:
            datt=dat_identity[np.in1d(np.array(index), [j]),:]
            idxx=np.mean(datt, axis=0)
            idxx=np.array(idxx).reshape(idxx.shape[0],)
            idx = idxx.argsort()[::-1]
            iD=[]
            print('Cluster identifier',j)
            if self.ensembl:
                for i in range(18): # Print each gene along with the feature-encoding weight
                    print('{0:s}:{1:.2e}'.format(list(self.ENSEMBLID_to_geneSymbol([self.geneNames[idx[i]]]))[0], idxx[idx[i]]))
                    iD.append(list(self.ENSEMBLID_to_geneSymbol([self.geneNames[idx[i]]]))[0])
            else:
                for i in range(18): # Print each gene along with the feature-encoding weight
                    print('{0:s}:{1:.2e}'.format(self.geneNames[idx[i]], idxx[idx[i]]))
                    iD.append(self.geneNames[idx[i]])
            idd_j.append(iD)
            
        return datt, idxx

    def get_gene_over_representation(self,topn=10):
        enrichmentTable={}    
        for i in range(self.k):
            top10Genes=[] 
            print('Cluster {0:s} ({1:d} cells)'.format(self.cluster_label[i], int(np.sum(self.cluster_assignment==i))))
            idxx=np.mean(self.data_ICF[self.cluster_assignment==i,:], axis=0)
            idxx=np.array(idxx).reshape(idxx.shape[0],)
            idx = idxx.argsort()[::-1]
            for j in range(topn): 
                top10Genes.append(self.geneNames[idx[j]])
            
            if self.ensembl:
                top10Genes=list(self.ENSEMBLID_to_geneSymbol(top10Genes,organisum=self.organsm))
                print(top10Genes)
            else:
                top10Genes=top10Genes
                print(top10Genes)
            enrichment = gprofiler(top10Genes, organism=self.organsm)
            enrichmentTable[i]=enrichment.sort_values(by=['p.value'])[["term.id","p.value","domain","term.name","intersection"]]
            print('')
        return enrichmentTable
    
    def get_MICTI_standardized_mean_over_var(self, clusters):
        
        datta=self.data_ICF[np.in1d(np.array(self.cluster_assignment), clusters),:]
        ccc=np.array(pa.DataFrame(datta).loc[~(pa.DataFrame(datta)==0).all(axis=0)])
        val=np.mean(ccc, axis=0)/(np.log(np.var(ccc, axis=0)+2))
        z_score=(val-np.mean(val))/np.sqrt(np.var(val))
        return z_score
    
    def calculate_pvalue(self, scores):
        return 2*(1-scipy.special.ndtr(abs(scores)))
    def FDR_BH(self, p):
        """Benjamini-Hochberg p-value correction for multiple hypothesis testing."""
        p = np.asfarray(p)
        by_descend = p.argsort()[::-1]
        by_orig = by_descend.argsort()
        steps = float(len(p)) / np.arange(len(p), 0, -1)
        q = np.minimum(1, np.minimum.accumulate(steps * p[by_descend]))
        return q[by_orig]
    def marker_gene_FDR_p_value(self, clusterNo):
        z_score=self.get_MICTI_standardized_mean_over_var(clusterNo)
        p_val=self.calculate_pvalue(z_score)
        FDR_pvalue=self.FDR_BH(p_val)
        result=pa.DataFrame({"Z_scores":z_score,"p_value":p_val,"Adj P-value":FDR_pvalue}, index=self.geneNames)
        return result.sort_values("Adj P-value")
    
    def get_gene_over_representation_for_topn_genes(self,topn=10):
        enrichmentTable={}    
        for i in range(self.k):
            
            print('Cluster {0:s} ({1:d} cells)'.format(str(self.cluster_label[i]), int(np.sum(self.cluster_assignment==i))))
            genes=list(self.marker_gene_FDR_p_value(i).index)
            top10Genes=genes[:topn]
            
            if self.ensembl:
                top10Genes=list(self.ENSEMBLID_to_geneSymbol(top10Genes,organisum=self.organsm))
                print(top10Genes)
            else:
                top10Genes=top10Genes
                print(top10Genes)
            enrichment = gprofiler(top10Genes, organism=self.organsm)
            enrichmentTable[i]=enrichment.sort_values(by=['p.value'])[["term.id","p.value","domain","term.name","intersection"]]
            print('')
        return enrichmentTable
    def get_gene_list_over_representation_analysis(self, gene_list):
        enrichment = gprofiler(gene_list, organism=self.organsm)
        enrichmentTable=enrichment.sort_values(by=['p.value'])
        return enrichmentTable
    def get_markers_by_Pvalues_and_Zscore(self,cluster,threshold_pvalue=.01, threshold_z_score=0):
        result=self.marker_gene_FDR_p_value(cluster)
        genenames=result.loc[list(np.array(result["Adj P-value"]<threshold_pvalue) & np.array(result["Z_scores"]>threshold_z_score)),:].sort_values("Adj P-value")
        genenames = genenames[~genenames.index.duplicated(keep='first')]
        return genenames
    
    def cluster_cells(self, numberOfCluster=None,subspace=False, min_sample=10, method="kmeans", maxiter=10e3, alpha=1, gamma=1, eta=0.01, eps=0.5, min_samples=5, metric='euclidean', xi=.05, min_cluster_size=.05):
        
        if(subspace==False):
            data=self.data
        else:
            svd = TruncatedSVD(n_components=500)
            data=svd.fit_transform(mictiObject_1.data.toarray())
            
        if method=="kmeans":
            kmean=Kmeans.Kmeans(data, numberOfCluster, self.geneNames, self.cellNames)
            _, self.cluster_assignment=kmean.kmeans_multiple_runs(maxiter,5)
            self.k=len(set(self.cluster_assignment))
        elif method=="GM":
            EM_GM=GM.GM(data, numberOfCluster, self.geneNames, self.cellNames)
            EM_GMM=EM_GM.EM_for_high_dimension()
            self.cluster_assignment=np.argmax(EM_GMM["resp"], axis=1)
            self.k=len(set(self.cluster_assignment))
        elif method=="hdp":
            corpusData=pa.DataFrame(data.toarray())
            corpusData.columns=self.geneNames
            corpusData.index=self.cellNames
            cc, id2g,id2c =self.cellMatrix2cellCorpus(corpusData)
            hdp=HdpModel(cc,id2g, alpha=alpha, gamma=gamma, eta=eta)
            tp_dist=hdp.__getitem__(cc)
            cell_tp=[max(dict(i), key=dict(i).get) for i in tp_dist]
            low_conf_cluster=np.where(np.bincount(cell_tp)<min_sample)
            filter_noise=[False if i in low_conf_cluster[0] else True for i in cell_tp]
            new_assignment=np.array([cell_tp[i] if filter_noise[i] else 100 for i in range(len(filter_noise))])
            new_assignment[new_assignment >  sorted(set(new_assignment))[-2]] = sorted(set(new_assignment))[-2]+1
            self.cluster_assignment=new_assignment
            self.k=len(new_assignment)
        elif method=="lda":
            corpusData=pa.DataFrame(data.toarray())
            corpusData.columns=self.geneNames
            corpusData.index=self.cellNames
            cc, id2g,id2c =self.cellMatrix2cellCorpus(corpusData)
            lda = LdaModel(corpus=cc, id2word=id2g, num_topics=numberOfCluster, update_every=1, passes=1, alpha=alpha, eta=eta)
            cell_type=lda.get_document_topics(cc)
            cell_type_lda=[max(dict(i), key=dict(i).get) for i in cell_type]
            self.cluster_assignment=cell_type_lda
            self.k=len(set(cell_type_lda))
        elif method=="aggl":
            aggl_clustering=cluster.AgglomerativeClustering(n_clusters=numberOfCluster).fit(data.toarray())
            self.cluster_assignment=aggl_clustering.labels_
            self.k=len(set(aggl_clustering.labels_))
        elif method=="birch":
            birch_clustering=cluster.Birch(n_clusters=numberOfCluster).fit(data.toarray())
            self.cluster_assignment=birch_clustering.predict(data.toarray())
            self.k=len(set(list(self.cluster_assignment)))
        elif method=="dbscan":
            dbscan_clustering=cluster.DBSCAN(eps=eps, min_samples=min_samples, metric=metric).fit(data.toarray())
            dbscan_lables=dbscan_clustering.labels_
            dbscan_lables[dbscan_lables <  0] = dbscan_lables.max()+1
            self.cluster_assignment=dbscan_lables
            self.k=len(set(dbscan_lables))
        elif method=="knn":
            knn_sparce_connectivity=kneighbors_graph(data.toarray(), min_sample)
            n_components, labels = csgraph.connected_components(knn_sparce_connectivity)
            labels[labels <  0] = labels.max()+1
            self.cluster_assignment=labels
            self.k=len(set(labels))
        elif method=="optics":
            optics_clustering=cluster.OPTICS(min_samples=min_samples, xi=xi, min_cluster_size=min_cluster_size, metric=metric).fit(data.toarray())
            optics_label=optics_clustering.labels_[optics_clustering.ordering_]
            optics_label[optics_label <  0] = optics_label.max()+1
            self.cluster_assignment = optics_label
            self.k=len(set(optics_label))
        self.cluster_label=[str(i) for i in range(self.k)]
        return None
    def get_Radar_plot(self):
        sig_genes=[dict({self.cluster_label[i]:list(self.get_markers_by_Pvalues_and_Zscore(i).index)}) for i in range(len(self.cluster_label))]
        
        
        sig_genes=dict(j for i in sig_genes for j in i.items())
        #sig_genes=sorted(sig_genes)
        genes_by_cell_type=[]
        data=[]
        data.append(sorted(list(sig_genes.keys())))
        
        #print(sig_genes)
        cell_typ=[self.cluster_label[j] for j in self.cluster_assignment]
        
        for k in sorted(sig_genes.keys()): 
            #print(k,v)
            genes_by_cell_type.append(sig_genes[k])
            try:
                my_data=self.get_selected_data(sig_genes[k]).T 
                if(my_data.empty):
                    data.append((k, np.array([])))
                    #data[0].remove(k)
                    continue
                my_data["cell_type"]=cell_typ
                #print(my_data.head())
                my_data=my_data.groupby("cell_type").mean().T
                my_data=(my_data.T/my_data.sum(axis=1)).T
                data.append((k, np.array(my_data)))
                del my_data
            except ValueError:
                print(k, "does not have markers")
        
        #print(genes_by_cell_type,data)
        radarPlot.radarPlot(data,genes_by_cell_type)
        
        return data,genes_by_cell_type
    
    def get_selected_data(self, geneLists):
        my_data=pa.DataFrame(self.data.toarray()).T
        my_data.index=self.geneNames
        my_data.columns=self.cellNames
        return my_data.loc[geneLists,:]
    
    def heatMap(self, cluster_marker=None, row_cluster=False, col_cluster=False):
        
        colors=['#ffe119','#0082c8','#f58231','#911eb4','#46f0f0','#f032e6','#d2f53c','#fabebe','#008080','#e6beff',
                '#aa6e28','#fffac8','#800000','#aaffc3','#808000','#ffd8b1','#000080','#808080','#FFFFFF','#000000'][:self.k]
        
        cell_type=pa.Series([self.cluster_label[j] for j in self.cluster_assignment])
        cell_type=cell_type.sort_values()
        lut2=dict(zip(cell_type.sort_values().unique(), colors))
        lut2=dict(sorted(lut2.items()))
        col_colors= cell_type.map(lut2)
        col_colors.index=pa.Series(self.cellNames)[cell_type.index]
        
        if(cluster_marker==None):
            markers=[list(self.get_markers_by_Pvalues_and_Zscore(i, threshold_pvalue=.01,threshold_z_score=0).index) for i in range(self.k)]
            markers_label=[list(np.repeat(self.cluster_label[i], len(markers[i]), axis=0)) for i in range(len(markers))]
            
            markers = pa.Series(sum(markers, []))
            markers_label=pa.Series(sum(markers_label, []))
                     
            cell_type=pa.Series([self.cluster_label[j] for j in self.cluster_assignment])
            lut = dict(zip(markers_label.sort_values().unique(), colors[:self.k]))
            row_colors = markers_label.map(lut)
            
            marker_data=self.get_selected_data(markers)
            row_colors.index=list(markers)
            
            marker_data=marker_data.T.loc[(col_colors.index),:].T
            
            marker_data=marker_data[~marker_data.index.duplicated(keep='first')]
            row_colors=row_colors[~row_colors.index.duplicated(keep='first')]
            
            mycol=[{k:tuple(np.array(self.hex_to_rgb(v))/255)} for k, v in lut2.items()]
            self.color_dict={}
            [self.color_dict.update(c) for c in mycol]
            
            g=heatmap.heatmap(marker_data, row_color=row_colors, col_color=col_colors, color_label=lut2)

            self.color=[lut2[self.cluster_label[i]] for i in self.cluster_assignment]
            self.color_dict=lut2
            plt.savefig('MICTI_heatmap.pdf', format="pdf", dpi=300, bbox_inches='tight')
            
        else:
            markers=self.get_markers_by_Pvalues_and_Zscore(cluster_marker, threshold_pvalue=.01,threshold_z_score=0).index
            
            marker_data=self.get_selected_data(list(markers))
            
            marker_data=marker_data.T.loc[(col_colors.index),:].T
            self.color_dict=lut2
            
            mycol=[{k:tuple(np.array(self.hex_to_rgb(v))/255)} for k, v in lut2.items()]
            self.color_dict={}
            [self.color_dict.update(c) for c in mycol]
            
            g=heatmap.heatmap(marker_data, row_color=None, col_color=col_colors, color_label=lut2)
            self.color=[lut2[self.cluster_label[i]] for i in self.cluster_assignment]
            
            plt.savefig('MICTI_heatmap.pdf', format="pdf", dpi=300, bbox_inches='tight')
        
        return plt.show()
    
    def cluster_extrinsic_evaluation(self, trueLable):
        
        return dict(
            Jaccard_score=metrics.jaccard_similarity_score(trueLable, self.cluster_assignment),
            FM_index=metrics.fowlkes_mallows_score(trueLable, self.cluster_assignment),
            F_measure=metrics.f1_score(trueLable, self.cluster_assignment, average="weighted"),
            V_measure=metrics.v_measure_score(trueLable, self.cluster_assignment),
            ARI=metrics.adjusted_rand_score(trueLable, self.cluster_assignment),
            AMI=metrics.adjusted_mutual_info_score(trueLable, self.cluster_assignment)
               )
    def cluster_intrinsic_evaluation(self):
       
        return dict(
            silhouette_score=metrics.silhouette_score(self.data.toarray(), self.cluster_assignment, metric='euclidean'),
            DB_index=metrics.davies_bouldin_score(self.data.toarray(), self.cluster_assignment) ,
            CH_index=metrics.calinski_harabasz_score(self.data.toarray(), self.cluster_assignment)
               )
    def hex_to_rgb(self, hex):
        hex = hex.lstrip('#')
        hlen = len(hex)
        return tuple(int(hex[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))

        
        
        
    
   
        
