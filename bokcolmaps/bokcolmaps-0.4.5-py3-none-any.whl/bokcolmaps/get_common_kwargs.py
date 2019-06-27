'''get_common_kwargs function definition'''


def get_common_kwargs(**kwargs):

    '''Get common kwargs for ColourMap, SpotPlot and derived classes'''

    palette = kwargs.get('palette', 'Viridis256')
    cfile = kwargs.get('cfile', 'jet.txt')
    xlab = kwargs.get('xlab', 'x')
    ylab = kwargs.get('ylab', 'y')
    zlab = kwargs.get('zlab', 'Index')
    dmlab = kwargs.get('dmlab', 'Data')
    rmin = kwargs.get('rmin', None)
    rmax = kwargs.get('rmax', None)
    xran = kwargs.get('xran', None)
    yran = kwargs.get('yran', None)

    return palette, cfile, xlab, ylab, zlab,\
        dmlab, rmin, rmax, xran, yran
