# This file is originall from https://github.com/jtambasco/gnuplotpy

import os
import time
import shutil as sh
import numpy as np
import subprocess
import re
import tempfile

import matplotlib as mpl
import matplotlib.pyplot as plt

init_pgfplots_ = False

def _read_line(filename, line_number):
    s = None
    with open(filename, 'r') as fs:
        for i, line in enumerate(fs.readlines()):
            if i == line_number:
                s = line
    return s

class _GnuplotDeletingFile:
    def __init__(self, filename):
        self.name = filename

    def __del__(self):
        os.remove(self.name)

class _GnuplotScriptTemp(_GnuplotDeletingFile):
    def __init__(self, gnuplot_cmds):
        _GnuplotDeletingFile.__init__(self, '.tmp_gnuplot.gpi')
        with open(self.name, 'w') as fs:
            fs.write(gnuplot_cmds)

class _GnuplotDataTemp(_GnuplotDeletingFile):
    def __init__(self, *args):
        _GnuplotDeletingFile.__init__(self, '.tmp_gnuplot_data.dat')
        data = np.array(args).T
        with open(self.name, 'wb') as fs:
            np.savetxt(fs, data, delimiter=',')

class _GnuplotDataZMatrixTemp(_GnuplotDeletingFile):
    def __init__(self, z_matrix):
        _GnuplotDeletingFile.__init__(self, '.tmp_gnuplot_data_z_matrix.dat')
        with open(self.name, 'wb') as fs:
            np.savetxt(fs, z_matrix, '%.3f', delimiter=',')

#def gnuplot( script, args_dict={}, data=[]):
def gnuplot( script, **kwargs ):
    '''
    Call a Gnuplot script, passing it arguments and
    datasets.

    Args:
        script(str): The name of the Gnuplot script or the text
        args_dict(dict): A dictionary of parameters to pass
            to the script.  The `key` is the name of the variable
            that the `item` will be passed to the Gnuplot script
            with.
        data(list): A list of lists containing lists to be plotted.
            The lists can be accessed by plotting the variable
            `data` in the Gnuplot script.  The first list in the
            list of lists corresponds to the first column in data,
            and so on.
    Returns:
        str: The Gnuplot command used to call the script.
    '''

    if os.path.exists( script ):
        with open( script ) as f:
            script = f.read( )

    for k in kwargs:
        v = kwargs[k]
        script = script.replace( '@%s@' % k, v )

    # Find rest of the macros.
    for m in re.findall( r'@\S+?@', script ):
        script = script.replace( m, kwargs.get( m.replace( '@',''), '' ) ) 

    # if first argument is a long string then save the string to current
    # directory before running the command.
    # First escape all char.
    script = script.replace( r'"', r"'" ).replace( ';', '' )
    script = ';'.join( filter(None, script.split( '\n' )) );
    script += ';exit;'
    scriptName = '.gnuplot_script'
    with open( scriptName, 'w' ) as f:
        f.write( script )

    while not os.path.isfile( scriptName ):
        time.sleep( 0.0001 )

    subprocess.Popen( [ 'gnuplot', scriptName ] )
    return True

def nx_draw( graph, program = 'neato', ax = None ):
    """Draw to PNG using graphviz (default = neato).
    """
    import matplotlib.image as mpimg
    from networkx.drawing.nx_agraph import write_dot
    fh, dotfile = tempfile.mkstemp( )
    pngfile = '%s.png' % dotfile
    write_dot( graph, dotfile )
    if ax is not None:
        subprocess.check_output([ program,  "-Tpng",  dotfile, "-o", pngfile], shell=False)
        if os.path.exists( pngfile ):
            im = mpimg.imread( pngfile )
            ax.imshow( im, interpolation = 'none' )
        else:
            raise UserWarning( 'Failed to draw graph using %s' % program)

def matrix_plot( img, xvec, yvec, ax = None, **kwargs ):
    if ax is None:
        ax = plt.subplot( 111 )

    img = np.matrix( img )
    nc, nr = img.shape
    im = ax.imshow( img
            , interpolation = kwargs.get( 'interpolation', 'none')
            , aspect = kwargs.get( 'aspect', 'auto' ) 
            , cmap = kwargs.get( 'cmap', 'viridis' )
            )

    # apply ticks and labels
    xticks = kwargs.get( 'xticks', [] )
    yticks = kwargs.get( 'yticks', [] )
    if not xticks:
        nticks = kwargs.get( 'num_xticks', kwargs.get( 'num_ticks', 5) )
        xticks = [(i, xvec[int(i)]) for i in np.linspace(0, len(xvec)-1, nticks)]

    xpos, xlabels = zip(*xticks)
    ax.set_xticks(xpos)
    ax.set_xticklabels( [ r'%s' % x for x in xlabels] )

    if not yticks:
        nticks = kwargs.get( 'num_yticks', kwargs.get( 'num_ticks', 5) )
        yticks = [(i, yvec[int(i)]) for i in np.linspace(0, len(yvec)-1, nticks)]

    ypos, ylabels = zip(*yticks)
    ax.set_yticks(ypos)
    ax.set_yticklabels( [ r'%s' % y for y in ylabels] )

    ax.set_xlabel( kwargs.get( 'xlabel', 'NA' ) )
    ax.set_ylabel( kwargs.get( 'ylabel', 'NA' ) )

    if kwargs.get( 'colorbar', True):
        plt.colorbar( im, ax = ax )
    return im

def init_pgfplots( ):
    global init_pgfplots_
    if init_pgfplots_:
        return 
    mpl.use('pgf')
    mpl.rcParams['text.latex.preamble'] = [
            #  r'\usepackage{libertine}'
            r'\usepackage{newtxmath}'
            , r'\usepackage[sfdefault,scale=0.9]{FiraSans}'
            #  , r'\usepackage[default,scale=0.9]{opensans}'
            , r'\usepackage[]{eulervm}'
            ]
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['lines.linewidth'] = 1

    # The following settings allow you to select the fonts in math mode.
    mpl.rcParams['mathtext.fontset'] = 'stixsans'
    mpl.rcParams['mathtext.default'] = 'regular'
    # AXES
    mpl.rcParams['axes.labelsize'] =  'x-small'
    mpl.rcParams['axes.formatter.use_mathtext'] = True
    mpl.rcParams['axes.formatter.min_exponent'] = 0
    mpl.rcParams['axes.formatter.useoffset'] = True  
    mpl.rcParams['axes.formatter.offset_threshold'] = 4  

    mpl.rcParams['axes.spines.left'] = True 
    mpl.rcParams['axes.spines.bottom'] = True
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.right'] = False

    mpl.rcParams['axes.autolimit_mode'] = 'data' 
    mpl.rcParams['axes.xmargin' ] = 0.1 
    mpl.rcParams['axes.ymargin' ] = 0.1 

    # TICKS
    # see http://matplotlib.org/api/axis_api.html#matplotlib.axis.Tick
    mpl.rcParams['xtick.labelsize'] = 'small'
    mpl.rcParams['xtick.direction'] = 'inout' 
    mpl.rcParams['ytick.labelsize'] = 'small' 
    mpl.rcParams['ytick.direction'] = 'inout'

    # Legend
    mpl.rcParams['legend.loc']         = 'best'
    mpl.rcParams['legend.frameon']     = False  
    mpl.rcParams['legend.framealpha']  = 0     
    mpl.rcParams['legend.fancybox']    = True 
    mpl.rcParams['legend.fontsize']    = 'small'
    mpl.rcParams['legend.borderpad']   = 0
    init_pgfplots_ = True

def pgfplots( df, xname, yname, ax, **kwargs):
    """Plot normal x-y curve like with pdfplots like settings.
    Also put valus into a dataframe and return it so it can be saved into 
    a csv file.
    """
    init_pgfplots()
    ax.plot(df[xname], df[yname]
            #  , kwargs.get('plot_style', '-')
            , **kwargs.get('Line2D', {})
            )

    defaultLegendOptions = dict( 
            bbox_to_anchor=(1,1)
            , loc = 'upper left' 
            , fontsize = 'x-small'
            )
    defaultLegendOptions.update( kwargs.get( 'legend_option', {}) )
    if kwargs.get('legend', ''):
        ax.legend( **defaultLegendOptions )

    if kwargs.get('xlabel', ''):
        ax.set_xlabel( kwargs['xlabel'] )
    if kwargs.get('ylabel', ''):
        ax.set_ylabel( kwargs['ylabel'] )
    if kwargs.get('title', '' ):
        ax.set_title( kwargs.get('title', '' ), fontsize='small' )

    # Add label. 
    if kwargs.get( 'label', '' ):
        ax.text( -0.2, 1.25, r'\textbf{%s}' % kwargs['label']
                , fontsize='medium' 
                , transform = ax.transAxes
            )

def phase_plot( x, y, ax):
    import math
    print( "[WARN ] This function has not been tested." )
    ax.plot(x, y)
    X, Y = np.meshgrid(x, y)
    U, V = np.zeros(X.shape), np.zeros(Y.shape)
    for i, xx in enumerate(x):
        for j, yy in enumerate(y):
            l = (xx**2 + yy**2)**0.5
            theta = math.atan2(yy, xx)
            U[i,j] = xx + l * math.cos(theta)
            V[i,j] = yy + l * math.sin(theta)
    ax.quiver(X, Y, U, V)

def simple_axis(ax):
    # Create a simple axis.
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

def test():
    ax = plt.subplot(111)
    phase_plot( [-1, 0, 1,2,3], [3, 1, 0.1, 0.2, 0.4], ax)
    plt.show()


if __name__ == '__main__':
    test()
