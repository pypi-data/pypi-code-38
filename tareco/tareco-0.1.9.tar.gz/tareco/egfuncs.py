from matplotlib import cm
import matplotlib
import numpy as np

def iterable(obj):
    if type(obj) == 'str':
        return False
    try:
        iter(obj)
        return True
    except TypeError:
        return False

def get_color(n):
    magma_cmap = cm.get_cmap('magma')
    norm = matplotlib.colors.Normalize(vmin=0, vmax=255)
    magma_rgb = []
    for i in range(0, 255):
       k = matplotlib.colors.colorConverter.to_rgb(magma_cmap(norm(i)))
       magma_rgb.append(k)
    magma = matplotlib_to_plotly(magma_cmap, 255)
    if n < 0 or n > 1:
        print('Choose a number between 0 and 1')
        return
    return magma[int(n*254)]

def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []
    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale
