
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import matplotlib.pyplot as plt


def styler(ax, xoffset=-0.01, yoffset=-0.01, xlabel=None, ylabel=None, yticklabels=None, xticklabels=None, title=None, legend=False, leftaxis='on', bottomaxis='on', rotatexticks=False, colorbar=None, colorbarlabel=None, cbaroffset=0.25, aspectsquare=False, fontname='Montserrat', fontweight='regular', fontcolor='gray'):
    """
    Returns matplotlib ax handle and styles according to input variables.

    Parameters
    ----------

    ax : matplotlib ax handles.
    xoffset : float
        How far to offset the x-axis.
    yoffset : flor
        How far to offset the x-axis.
    xlabel : str
        Works as ax.set_xlabel()
    ylabel : str
        Works as ax.set_ylabel()
    xticklabels : list
        Works as ax.set_xticklabels()
    yticklabels : list
        Works as ax.set_yticklabels()
    yticklabels : list
        Unit of time for xlabel. Same as contact-representation (if netin is contact, and input is unset, contact dictionary is used)
    title : str (Default: None)
        Works as ax.set_title
    legend : bool
        If true, legend is plotted
    leftaxis : bool
        If false, left ax is not drawn
    bottomaxis : bool
        If false, bottom ax is not drawn
    rotatexticks : bool
        If true, xticks are rotated 90 degrees
    colorbar : ax
        Handle of image that is to get colorbar
    colorbarlabel : str
        Label of colorbar
    cbaroffset : float (default 0.25)
        How far to offset cbar from figure
    aspectsquare : bool (default true)
        Make square aspect ration of figure.
    fontname : str (Default 'Montserrat')
        Font to use (Montserrat may have to be downloaded)
    fontweight : str
        Could be regular, bold, italics etc.
    fontcolor : str (Default 'gray')
        Color of font

    Returns
    --------
    ax : matplotlib ax handle

    """
    if yticklabels is None:
        yticklabels = [np.round(t, 3) for t in ax.get_yticks()]
    if xticklabels is None:
        xticklabels = [np.round(t, 3) for t in ax.get_xticks()]
    if bottomaxis == 'on':
        ax.spines['bottom'].set_position(('axes', xoffset))
        ax.spines['bottom'].set_color('gray')
    else:
        ax.spines['bottom'].set_color('none')
    if leftaxis == 'on':
        ax.spines['left'].set_color('gray')
        ax.spines['left'].set_position(('axes', yoffset))
    else:
        ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    if ylabel:
        ax.set_ylabel(ylabel, fontname=fontname,
                      fontweight=fontweight, color=fontcolor)
    if xlabel:
        ax.set_xlabel(xlabel, fontname=fontname,
                      fontweight=fontweight, color=fontcolor)
    if title:
        ax.set_title(title, fontname=fontname,
                     fontweight=fontweight, color=fontcolor)
    if leftaxis == 'on':
        ax.set_yticklabels(yticklabels, fontname=fontname,
                           fontweight=fontweight, color=fontcolor)
    elif leftaxis == 'off':
        ax.set_yticks([])
    if bottomaxis == 'on':
        ax.set_xticklabels(xticklabels, fontname=fontname,
                           fontweight=fontweight, color=fontcolor)
    elif bottomaxis == 'off':
        ax.set_xticks([])
    if legend == True:
        L = ax.legend(frameon=False)
        plt.setp(L.texts, fontname=fontname,
                 fontweight=fontweight, color=fontcolor)
    if rotatexticks == True:
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
    if colorbar is not None:
        ax = colorbar.axes
        fig = ax.figure
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=cbaroffset)
        cbar = fig.colorbar(colorbar, cax=cax, ticks=colorbar.get_clim())
        cbar.ax.set_yticklabels(np.round(cbar.get_ticks(), 2).tolist(
        ), fontname=fontname, fontweight=fontweight, color=fontcolor)
        if colorbarlabel is not None:
            cbar.ax.set_ylabel(colorbarlabel, fontname=fontname,
                               fontweight=fontweight, color=fontcolor)
        cbar.ax.yaxis.set_label_position('left')
    if aspectsquare == True:
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        ax.set_aspect(abs(x1-x0)/abs(y1-y0))
