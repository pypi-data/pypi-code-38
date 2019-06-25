import os, sys
import getopt
import gpx2dzg.functions as fx
import gpx2dzg.help as help
import gpx2dzg.io as io
import gpx2dzg.plot as px

def convert(dzx='', gpx='', write=False, plot=False, drops=[]):
    """The main conversion function in `gpx2dzg`.

    Parameters
    ----------
    dzx : str
        The path of the DZX or DZT file to read. Also specifies the directory where the DZG will be created if `write=True` and mark counts match.
    gpx : str
        The path of the GPX file to read.
    write : bool
        Tells `gpx2dzg` whether to write a DZG file (but only if mark counts match between GPX and DZX/DZT).
    plot : bool
        Tells `gpx2dzg` whether to force the creation of a sanity check plot.
    drops : list
        List of integers. Tells `gpx2dzg` to drop mark values at this list of DZX/DZT integer index locations.

    Returns
    -------
    bool
        True if mark counts match, False otherwise.
    """
    if os.path.exists(dzx) == False:
        fx.printmsg('ERROR: specified dzx/dzt file does not exist. exiting.')
        sys.exit(2)
    if os.path.exists(gpx) == False:
        fx.printmsg('ERROR: specified gpx file does not exist. exiting.')
        sys.exit(2)
    fx.printmsg('dzx file: %s' % dzx)
    fx.printmsg('gpx file: %s' % gpx)

    dzxmarks, gpxmarks = [], []

    if '.dzx' in dzx.lower():
        dzxmarks = io.readdzx(dzx=dzx)
        fx.printmsg('found %s dzx marks' % len(dzxmarks))
    elif '.dzt' in dzx.lower():
        dzxmarks = io.readSIR3k(dzt=dzx)
        fx.printmsg('found %s dzt marks' % len(dzxmarks))

    gpxmarks = io.readgpx(gpx=gpx)
    fx.printmsg('found %s gpx marks' % len(gpxmarks.waypoints))

    origdzxnum = list(range(0,len(dzxmarks)))
    if len(drops) > 0:
        fx.drop(marks=dzxmarks, drops=drops)
        fx.drop(marks=origdzxnum, drops=drops)

    if len(gpxmarks.waypoints) == len(dzxmarks):
        fx.printmsg('mark counts match!')
        if write:
            fx.printmsg('outputting to DZG now (same directory and name as the DZX/DZT)')
            fx.printmsg('if a DZG already exists, another will be written with "-gpx2dzg" in the name.')
            dzg = os.path.splitext(dzx)[0] + '.DZG'
            if os.path.exists(dzg):
                dzg = os.path.splitext(dzx)[0] + '-gpx2dzg.DZG'
            fx.printmsg('output file: %s' % dzg)
            io.write(dzg=dzg, dzxmarks=dzxmarks, gpxmarks=gpxmarks)
        else:
            fx.printmsg('no DZG write specified. skipping...')
        success = True
    else:
        fx.printmsg('mark counts do not match. foregoing write and generating sanity check plot.')
        plot = True
        success = False

    if plot:
        px.sanityplot(dzx=dzxmarks, dzxnum=origdzxnum, dzxname=dzx, gpx=gpxmarks, gpxname=gpx)

    return success

def main():
    """The argument parsing function for command line calls. Takes no parameters, but reads command line flags and arguments.

    Passes arguments to the `convert()` function.
    """
    dzx, gpx = None, None
    plot, write = False, False
    drops = []

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'hwpr:d:g:', ['help', 'write', 'plot', 'drop=' 'dzx=', 'gpx='])
    except getopt.GetoptError as e:
        fx.printmsg('ERROR: invalid argument(s) supplied')
        fx.printmsg('error text: %s' % e)
        fx.printmsg(help.help_text)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'): # the help case
            fx.printmsg(help.help_text)
            sys.exit()
        if opt in ('-d', '--dzx'): # dzx or dzt input file
            if arg:
                dzx = arg
                if '~' in dzx:
                    dzx = os.path.expanduser(dzx) # if using --input=~/... tilde needs to be expanded
        if opt in ('-g', '--gpx'): # gpx input file
            if arg:
                gpx = arg
                if '~' in gpx:
                    gpx = os.path.expanduser(gpx) # if using --input=~/... tilde needs to be expanded
        if opt in ('-r', '--drop'):
            if arg:
                try:
                    drops = list(int(i) for i in list(arg.strip('(){}[]').split(',')))
                except Exception as e:
                    fx.printmsg('ERROR: list of drops is likely formatted incorrectly. try "-r [1,2,4,-2]"')
                    fx.printmsg('full error text: %s' % e)
                    sys.exit(2)

        if opt in ('-p', '--plot'): # plot
            plot = True
        if opt in ('-w', '--write'): # write a dzg
            write = True
    if dzx and gpx:
        convert(dzx=dzx, gpx=gpx, plot=plot, write=write, drops=drops)
    elif dzx:
        fx.printmsg('only DZX input specified. gpx2dzg will search for an identically named GPX...')
        gpx = os.path.splitext(dzx)[0] + '.gpx'
        convert(dzx=dzx, gpx=gpx, plot=plot, write=write, drops=drops)
    else:
        fx.printmsg('ERROR: no input files specified')
        sys.exit(2)


if __name__ == '__main__':
    """This directs command line calls to the argument parsing function `main()`.
    """
    main()