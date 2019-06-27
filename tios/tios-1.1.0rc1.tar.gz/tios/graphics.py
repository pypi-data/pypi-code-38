import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import numpy as np


def plot_monitors(fname, dic, xkey, size=(8,8)):
    '''
    Make an image file from the monitors data
    '''
    x = list(dic.pop(xkey))
    xyz = dic.pop('xyz', None)
    fig, axarr = plt.subplots(len(dic), sharex=True, figsize=size)
    plt.subplots_adjust(wspace=0, hspace=0)
    xmin = float(min(x))
    xmax = float(max(x))
    axarr[0].set_xlim([xmin, xmax])
    axarr[-1].set_xlabel('time (ps)')
    for ax, key in zip(axarr, dic.keys()):
        ax.set_ylabel(key)
        y = list(dic[key])
        ymin = float(min(y))
        ymax = float(max(y))
        yrange = ymax - ymin
        ax.set_ylim([ymin - 0.1 * yrange, ymax + 0.1 * yrange])
        ax.yaxis.set_ticks([ymin, ymax])
        ax.fill_between(x, ymin - 0.1 * yrange, y)
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()

def element_colour(e):
    ec = {
        'C' : (0,0,0),
        'N' : (0, 0, 255),
        'O' : (255, 0, 0),
        'H' : (0, 255, 255),
        'S' : (255, 0, 255),
        'P' : (255, 255, 0)
        }
    if e in ec:
        return ec[e]
    else:
        return (128, 128, 128)

def plot_molecule(outfile, traj, selection=None, frame=0, size=(4,3)):
    '''
    Produce a simple wireframe image of the trajectory frame.
    '''
    imgsize = max(size) * 96 # assume 96 dpi
    if selection is not None:
        sel = traj.topology.select(selection)
        traj.topology = traj.topology.subset(sel)
        traj.xyz = traj.xyz[:, sel]
    elements = [a.element.symbol for a in traj.topology.atoms]
    bonds = [(b[0].index, b[1].index) for b in traj.topology.bonds]
    xy = traj.xyz[frame, :, :2]

    supersample = 4
    linewidth = 2

    molimg(outfile, xy, elements, bonds, imgsize=imgsize, 
           supersample=supersample, linewidth=linewidth)

def molimg(imgfile, xy, elements, bonds, imgsize=400, 
           supersample=4, linewidth=1):
    '''
    Produce a wireframe image of a molecule and save to file.
    Uses PIL rather than matplotlib as it is faster.
    '''

    xy = xy - xy.min(axis=0)
    xy = xy / xy.max()
    xy -= ((xy.max(axis=0) - 1) / 2)
    ixy = (xy * imgsize * supersample).astype(np.int)
    ims = int(imgsize * supersample)
    imgsize = int(imgsize)

    im = Image.new('RGB', (ims, ims), color=(255, 255, 255))
    draw = ImageDraw.Draw(im)
    lw = linewidth * supersample
    for b in bonds:
        start = tuple(ixy[b[0]])
        end = tuple(ixy[b[1]])
        mid = tuple((ixy[b[0]] + ixy[b[1]]) / 2)
        draw.line((start, mid), fill=element_colour(elements[b[0]]), width=lw)
        draw.line((end, mid), fill=element_colour(elements[b[1]]), width=lw)

    im = im.resize((imgsize, imgsize), resample=Image.BICUBIC)
    im.save(imgfile, 'PNG')
