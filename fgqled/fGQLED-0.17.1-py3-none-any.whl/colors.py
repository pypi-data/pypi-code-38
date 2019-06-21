import numpy as np
from matplotlib import cm

def get_colors(N, cmap_name='plasma'):
    cmap = cm.get_cmap(cmap_name)
    color_id = np.linspace(0, 1, N+10)
    colors = []
    for ii in color_id:
        colors.append(cmap(ii))
    colors = colors[5:-5]
    return colors