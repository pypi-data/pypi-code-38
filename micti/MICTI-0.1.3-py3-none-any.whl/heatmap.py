import seaborn as sns; sns.set(color_codes=True)
import numpy as np
import matplotlib.pyplot as plt
def heatmap(data, cluster_marker=None, color_label=None, row_names=None, col_names=None, row_color=None, col_color=None, row_cluster=False, col_cluster=False, cbar_kws=None):
        
    g = sns.clustermap(data,row_colors=row_color,col_colors=col_color, row_cluster=False, col_cluster=False, z_score=0, cmap="mako", robust=True, figsize=(8,8))   
    
    #color_labell=dict(sorted(color_label.items()))
    for label in sorted(color_label.keys()):
        g.ax_col_dendrogram.bar(0, 0, color=color_label[label],
                            label=label, linewidth=0)
    
    g.ax_col_dendrogram.legend(loc="center", ncol=6)
    
    g.cax.set_position([.15, .2, .03, .45])
    
    return g





