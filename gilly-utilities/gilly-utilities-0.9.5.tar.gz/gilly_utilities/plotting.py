from __future__ import absolute_import, division, print_function
import sys
import time, os, warnings
import numpy as np
from datetime import datetime
import matplotlib
import matplotlib.backends
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.dates import DateFormatter, MinuteLocator, HourLocator, DayLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .system import isarray, arrlen

# Compatability for python3
if getattr(sys.version_info, 'major') == 3:
	xrange = range

def colorbar(mappable, loc="right", size="5%", pad=0.05):
    """Fixes location of colour bar to the mappable plot
    
    Parameters
    ----------
    mappable : matplotlib object
        The specific matplotlib entity you want a colour bar for. (See example for 
        for details)
    loc : str, optional
        The location you want the colour bar. The possible values are
        
        ["left"|"right"|"bottom"|"top"]
        
        Default is "right"
    size : str, float or int, optional
        Specify the size of the colour bar either as a percentage (str), or the number 
        of pixels width (float or int)
    pad : float, optional
        Specify the amount of white space padding you want between the mappable and the
        colour bar.
        
    Reference
    ---------
    http://joseph-long.com/writing/colorbars/
    
    """
    
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(mappable)
    cax = divider.append_axes(loc, size=size, pad=pad)
    
    return fig.colorbar(mappable, cax=cax)
    
def return_intersection(hist_1, hist_2):
    minima = np.minimum(hist_1, hist_2)
    intersection = np.true_divide(np.sum(minima), np.sum(hist_2))
    return intersection

def get_axis_limits(ax, scale=.85, position='upper-right'):
    """Used to position the identifier labels in the corner of images.
    e.g. '(a)' etc. 
    
    An example use with this definition is as follows:
    
        ax1.annotate("("+d[i+1-10]+")", xy=get_axis_limits(ax1))
    
    This will place an annotation in the top right corner of our subplot,
    ax1. Specifically this is used for labelling multiple plots using 
    letters. The function d[i] is a dictionary function which converts
    numbers to letters.
    
    Parameters
    ----------
    ax : plot/subplot function
        The plot or subplot that you want to scale accordingly
    scale : float, optional
        A scale function that determines as a fractional percentage the
        position from the edge of the plot (e.g. scale = 1 is at the
        edge and scale = 0.5 is centred).
    position : string, optional
        Determines the prefered location of interest releative to the
        four corners of the plot. string selections are ('upper-right',
        'upper-left', 'lower-right', 'lower-left')
        
    Returns
    -------
    x : float
        coordinate reference relative to the input plot ax in the x axis
    y: float
        coordinate reference relative to the input plot ax in the y axis
    
    """
    
    if position == 'upper-right':
        try:
            return ax.get_xlim()[1]*0.95*scale, ax.get_ylim()[1]*0.90
        except AttributeError:
            return ax.xlim()[1]*0.95*scale, ax.ylim()[1]*0.90
    elif position == 'upper-left':
        try:
            return ax.get_xlim()[1]*0.95*(1-scale), ax.get_ylim()[1]*0.90
        except AttributeError:
            return ax.xlim()[1]*0.95*(1-scale), ax.ylim()[1]*0.90
    elif position == 'lower-right':
        try:
            return ax.get_xlim()[1]*0.95, ax.get_ylim()[1]*(1-scale)
        except AttributeError:
            return ax.xlim()[1]*0.95, ax.ylim()[1]*(1-scale)
    elif position == 'lower-left':
        try:
            return ax.get_xlim()[1]*0.95, ax.get_ylim()[1]*0.95*(1-scale)
        except AttributeError:
            return ax.xlim()[1]*0.95, ax.ylim()[1]*0.95*(1-scale)
  
def unlink_wrap(dat, lims=[-np.pi, np.pi], thresh = 0.95):
    """
    Iterate over contiguous regions of `dat` (i.e. where it does not
    jump from near one limit to the other).

    This function returns an iterator object that yields slice
    objects, which index the contiguous portions of `dat`.

    This function implicitly assumes that all points in `dat` fall
    within `lims`.

    Ref. https://stackoverflow.com/a/27139390
    
    """
    jump = np.nonzero(np.abs(np.diff(dat)) > ((lims[1] - lims[0]) * thresh))[0]
    lasti = 0
    for ind in jump:
        yield slice(lasti, ind + 1)
        lasti = ind + 1
    yield slice(lasti, len(dat))

def date_ticks(ay, daterange):
    """Fixes ticks for time-series data.
    
    Parameters
    ----------
    ay : Matplotlib axis
        Provide the current axis for your Matplotlib plot that you want to change the axis for. 
        E.g. use ay = plt.gca()
    daterange : tuple, list or ndarray
        The upper and lower date range limits that you want to plot for inside a tuple, list or
        ndarray. E.g. (datetime(2018,1,1,12,0,0), datetime(2018,1,2,0,0,0)). Each element must
        contain either a python datetime or a numpy datetime64 object.    
    """
    
    #Check attributes
    if not isinstance(ay, plt.matplotlib.axes._axes.Axes): raise ValueError("[gu.date_ticks] ay parameter must be a matplotlib subplot. We got %s" % type(ay))
    if isinstance(daterange, (tuple, list, np.ndarray)):
        if len(daterange) != 2: raise ValueError("[gu.date_ticks] daterange parameter must have a length of 2, specifying the date boundaries you are plotting")
        if isinstance(daterange[0], (datetime, np.datetime64)):
            daterange = np.array(daterange).astype(datetime)
        else:
            raise ValueError("[gu.date_ticks] daterange parameter must contain python datetime or numpy datetime64 objects. We got (%s, %s)" % (type(daterange[0]), type(daterange[1])))
    else:
        raise ValueError("[gu.date_ticks] daterange parameter must be either a tuple, list or numpy array. We got %s" % type(daterange))
        
    TimeLength = (daterange[1] - daterange[0]).total_seconds() + 1
    if TimeLength/86400 <= 2:
        """Short Range: ~Single Day"""
        myFmt = DateFormatter('%H:%M')
        ay.xaxis.set_major_formatter(myFmt)
        ay.xaxis.set_major_locator(MinuteLocator(interval=int(np.floor((TimeLength/60)/6))))
    elif TimeLength/86400 <= 7:
        """Medium Range: ~Multiple Days"""
        myFmt = DateFormatter('%Y-%m-%d %H:%M') #Use this when plotting multiple days (e.g. monthly summary)
        ay.xaxis.set_major_formatter(myFmt)
        ay.xaxis.set_major_locator(HourLocator(interval=int(round((TimeLength/3600)/6))))
    else:
        """Long Range: ~Months"""
        myFmt = DateFormatter('%Y-%m-%d') #Use this when plotting multiple days (e.g. monthly summary)
        ay.xaxis.set_major_formatter(myFmt)
        ay.xaxis.set_major_locator(DayLocator(interval=int(round((TimeLength/86400)/6))))
    ay.set_xlabel('Time (UTC) between ' + daterange[0].strftime('%d/%m/%Y %H:%M:%S') + " and " + daterange[1].strftime('%d/%m/%Y %H:%M:%S'))
    
def backend_changer(backend='Qt4Agg', verbose=False):
    """Changes the Matplotlib back-end as certain configurations of code can stop any plots
    being created. E.g. using 'screen' in an interactive terminal requires 'Agg' back-end.
    Running PG_Quickplotter directly from the command line can use the default back-end of 
    'Qt4Agg'
    
    Parameters
    ----------
    backend : str, optional, default = 'Qt4Agg'
        The matplotlib backend name you want to change to. The options available can be found
        by running 
    """
    
    if isinstance(backend, str):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            plt.switch_backend(backend)
    else:
        raise ValueError("[_backend_changer] Backend needs to be a string. We got %s. Use _backend_checker to see that available Matplotlib backends for your system." % backend)
    
    if verbose is True: print("[INFO] Matplotlib backend has been changed to %s" % backend)
    
def backend_checker(show_supported=False, show_valid=False):
    """Checks the available back-ends in Matplotlib and then tests each supported back-end
    to see if they can actually be used in the environments configurations"""

    def is_backend_module(fname):
        """Identifies if a filename is a Matplotlib backend module"""
        return fname.startswith('backend_') and fname.endswith('.py')

    def backend_fname_formatter(fname): 
        """Removes the extension of the given filename, then takes away the leading 'backend_'."""
        return os.path.splitext(fname)[0][8:]

    # get the directory where the back-ends live
    backends_dir = os.path.dirname(matplotlib.backends.__file__)

    # filter all files in that directory to identify all files which provide a backend
    backend_fnames = filter(is_backend_module, os.listdir(backends_dir))

    backends = [backend_fname_formatter(fname) for fname in backend_fnames]

    if show_supported is True: print("Supported Backends: \t %s " % backends)

    #Validate Back-ends
    backends_valid = []
    for b in backends:
        try:
            plt.switch_backend(b)
            backends_valid += [b]
        except:
            continue

    if show_valid is True: print("Valid Backends: \t %s" % backends_valid)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        #Try Back-ends Performance
        backends_available = []
        backends_fps = []
        for b in backends_valid:
            try:
                #plt.ion()                                #Turn on interactive mode
                
                plt.switch_backend(b)                    #Switch back-end to test

                plt.clf()
                tstart = time.time()                       #For time keeping
                x = np.arange(0,2*np.pi,0.01)           #X Array
                line, = plt.plot(x,np.sin(x))
                for i in xrange(1,50):
                    line.set_ydata(np.sin(x+i/10.0))    #Update the data
                    plt.draw()                             #Redraw the canvas

                #plt.ioff()
                
                #If nothing went wrong during FPS check then this is a viable back-end to use
                backends_available.append(b)
                backends_fps.append(50/(time.time()-tstart))
            except:
                pass
    
    #Sort lists
    backends_fps, backends_available = (list(t) for t in zip(*sorted(zip(backends_fps, backends_available), reverse=True)))
    
    print("Available Backends to use with Matplotlib\n-----------------------------------------\n")
    print("Backend         FPS\n---------------------------")
    for backend, fps in zip(backends_available, backends_fps):
        print("%s       \t%.4f" % (backend, fps))

def fixed_aspect_ratio(ax, ratio=1, adjustable=None, xscale='linear', yscale='linear'):
    """
    Set a fixed aspect ratio on Matplotlib plots regardless of axis 
    units. Can handle all scale types (e.g. linear-linear, log-log
    and semilog plots).
    
    Notes
    -----
    This function must be called after all plotting has been completed.
    i.e. just before plt.savefig and time_axis if used.
    
    Reference
    ---------
    https://stackoverflow.com/a/37340384
    https://stackoverflow.com/a/39807336
    https://stackoverflow.com/a/24538164
    """
    
    # Check if minor ticks were enabled
    if len(ax.xaxis.get_minor_ticks()) > 0:
        minor_ticks = True
    else:
        minor_ticks = False

    # Set scales for both axes
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
    
        if xscale == yscale:
            if isinstance(ax, np.ndarray):
                ax = ax.ravel()
                
                for subplot in ax:
                    #Get axis limits
                    xvals, yvals = (subplot.get_xlim(), subplot.get_ylim())
                    
                    #Compute axis range
                    xrange = xvals[1] - xvals[0] if xscale == 'linear' else np.log(xvals[1]) - np.log(xvals[0])
                    yrange = yvals[1] - yvals[0] if yscale == 'linear' else np.log(yvals[1]) - np.log(yvals[0])
                    
                    #Force aspect
                    subplot.set_aspect(ratio*(xrange/yrange), adjustable=adjustable)
            else:
                #Get axis limits
                xvals, yvals = (ax.get_xlim(), ax.get_ylim())
                
                #Compute axis range
                xrange = xvals[1] - xvals[0] if xscale == 'linear' else np.log(xvals[1]) - np.log(xvals[0])
                yrange = yvals[1] - yvals[0] if yscale == 'linear' else np.log(yvals[1]) - np.log(yvals[0])

                #Force aspect
                ax.set_aspect(ratio*(xrange/yrange), adjustable=adjustable)

        # Add support for mixed scale axes in Matplotlib
        elif xscale != yscale:

            # Get the figure size in real coordinates:
            f = plt.gcf()
            fwidth = f.get_figwidth()
            fheight = f.get_figheight()

            # get the axis size and position in relative coordinates
            # this gives a BBox object
            bb = ax.get_position()

            # calculate them into real world coordinates
            axwidth = fwidth * (bb.x1 - bb.x0)
            axheight = fheight * (bb.y1 - bb.y0)

            # if the axis is wider than tall, then it has to be narrower
            if axwidth > axheight:
                # calculate the narrowing relative to the figure
                narrow_by = (axwidth - axheight) / fwidth
                
                # move bounding box edges inwards the same amount to give the correct width
                bb.x0 += narrow_by / 2
                bb.x1 -= narrow_by / 2
                
            # else if the axis is taller than wide, make it vertically smaller
            # works the same as above
            elif axheight > axwidth:
                shrink_by = (axheight - axwidth) / fheight
                bb.y0 += shrink_by / 2
                bb.y1 -= shrink_by / 2
            
            # Set the new position for the plot
            ax.set_position(bb)

        else:
            raise ValueError("Something went really wrong. xscale != yscale and xscale == yscale was found to be both False!")

    # Turn on minor_ticks if previously set
    if minor_ticks:
        ax.minorticks_on()

    return    

def get_aspect(ax=None):
    """Gets aspect ratio of an axes
    
    Ref: https://stackoverflow.com/a/41597178/8765762"""

    if ax is None:
        ax = plt.gca()
    fig = ax.figure

    ll, ur = ax.get_position() * fig.get_size_inches()
    width, height = ur - ll
    axes_ratio = height / width
    aspect = axes_ratio / ax.get_data_ratio()

    return aspect
                        
def fake_colorbar():
    """Creates a fake mappable object used in creating space for a colorbar object. Useful when
    plotting multiple sub-plots with some sub-plots not requiring a colorbar."""
    
    Z = [[0,0],[0,0]]
    levels = np.arange(0,10,1)
    im = plt.contourf(Z, levels)
    
    return im
    
def hide_axis(plt=None, ax=None, x_or_y=None, remove_gridlines=False, remove_labels=False):
    """
    Removes axis of a Matplotlib plot.
    
    Parameters
    ----------
    plt : matplotlib figure
        The figure to modify. N.B. Either plt or ax can be specified,
        not both.
    ax : matplotlib axis
        The axis to modify. N.B. Either plt or ax can be specified,
        not both.
    x_or_y : str
        The x or y coordinates to modify.
    remove_gridlines : bool, optional, default = False
        Specify whether to fully hide the x or y axis. If set to False 
        then just the tick labels are hidden and not the ticks 
        themselves.
    
    References
    ----------
    Stackoverflow : Hiding axis text in matplotlib plots
    """
    
    if plt is None and ax is None: raise ValueError("[gu.hide_axis]: Must specify either plt or ax plots.")
    if plt is not None and ax is not None: raise ValueError("[gu.hide_axis]: Can only specify either plt or ax, not both.")
    if x_or_y is None: raise ValueError("[gu.hide_axis]: x_or_y only takes either 'x' or 'y'.")
    
    if plt is not None: ax = plt.gca()
    
    if x_or_y == 'x':
        if remove_gridlines:
            ax.axes.get_xaxis().set_ticks([])
        elif not remove_gridlines:
            ax.axes.get_xaxis().set_ticklabels([])
        else:
            raise ValueError("remove_gridlines is a boolean parameter and accepts either True or False")
            
        if remove_labels:
            ax.set_xlabel("")
            
    elif x_or_y == 'y':
        if remove_gridlines:
            ax.axes.get_yaxis().set_ticks([])
        elif not remove_gridlines:
            ax.axes.get_yaxis().set_ticklabels([])
        else:
            raise ValueError("remove_gridlines is a boolean parameter and accepts either True or False")
            
        if remove_labels:
            ax.set_ylabel("")
            
    else:
        raise ValueError("x_or_y only takes either 'x' or 'y'.")
        
    return

def time_axis(date_range, plt=None, ax=None, num_ticks=6, auto_format=True, 
        xlabel=None, rotation=None, date_sep="-", time_sep=":"):
    """
    Sets up the x axis using datetime information.
    
    Parameters
    
    """

    # Error check input parameters
    if plt is None and ax is None: 
        raise ValueError("[gu.time_axis]: Must specify either plt or ax plots.")
    if plt is not None and ax is not None: 
        raise ValueError("[gu.time_axis]: Can only specify either plt or ax, not both.")
    if not isinstance(num_ticks, int):
        raise ValueError("[gu.time_axis]: num_ticks must be an integer.")
    if not isarray(date_range):
        raise ValueError("[gu.time_axis]: date_range must be array_like containing two python datetime objects")
    if not isinstance(date_range[0], datetime) or not isinstance(date_range[1], datetime):
        if isinstance(date_range[0], np.datetime64):
            date_range = (date_range[0].astype(datetime),
                    date_range[1].astype(datetime))
        else:
            raise ValueError("[gu.time_axis]: date_range must contain two python datetime objects stating the start and end dates for plotting")
    if len(date_range) != 2:
        raise ValueError("[gu.time_axis]: date_range must have a length of 2. To clarify, date_range must be array_like of length 2 containing python datetime objects which state the start and end times for plotting")
        
    if plt is not None:
        ax = plt.gca()
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        # If auto has been set for format
        if auto_format:
        
            # Calculate the time length in seconds between datetimes
            time_length = (date_range[1] - date_range[0]).total_seconds() + 1
            
            # Check time_length is bigger than 0
            if time_length == 0:
                raise ValueError("Daterange are too similar. Got interval of 0. Please increase the time between ranges. N.B. time_axis only supports second precision.")
            
            # Specify different tick requirements dependent on the number of seconds between datetimes
            if time_length/86400 <= 2:
                # Short Range: ~Single Day
                myFmt = DateFormatter('%H' + time_sep + '%M')
                ax.xaxis.set_major_formatter(myFmt)
                ax.xaxis.set_major_locator(MinuteLocator(interval=int(np.floor((time_length/60)/num_ticks))))
            elif time_length/86400 <= 7:
                # Medium Range: ~Multiple Days
                myFmt = DateFormatter('%Y' + date_sep + '%m' + date_sep + '%d %H' + time_sep + '%M')
                ax.xaxis.set_major_formatter(myFmt)
                ax.xaxis.set_major_locator(HourLocator(interval=int(round((time_length/3600)/num_ticks))))
            else:
                # Long Range: ~Months
                myFmt = DateFormatter('%Y' + date_sep + '%m' + date_sep + '%d')
                ax.xaxis.set_major_formatter(myFmt)
                ax.xaxis.set_major_locator(DayLocator(interval=int(round((time_length/86400)/num_ticks))))
            
            if xlabel is None:
                ax.set_xlabel('Time (UTC) between ' 
                        + date_range[0].strftime('%Y' + date_sep + '%m' 
                            + date_sep + '%d %H' + time_sep + '%M' 
                            + time_sep + '%S') + " and " 
                        + date_range[1].strftime('%Y' + date_sep + '%m' 
                            + date_sep + '%d %H' + time_sep + '%M' 
                            + time_sep + '%S'))
                            
            elif xlabel is not False:
                ax.set_xlabel(xlabel)
                
        # If format is not set to 'auto'
        else:
            ax.xaxis.set_major_locator(MultipleLocator(num_ticks))
            ax.set_xlabel('Time (UTC)')
    
    # Rotate the ticks as specified by rotation parameter
    if rotation is not None:
        for tick in ax.get_xticklabels():
            tick.set_rotation(rotation)
    
    # Need to draw figure before xtickslabels are populated
    #matplotlib.pyplot.draw()
    return ax.get_xticks(), [item._text for item in ax.get_xticklabels()]

def match_ticks(ax1, ax2, tick_count=5, dec_limit=2, scale='linear'):
    """
    Match the ticks for twin plots nicely
    
    Notes
    -----
    Can't be used in conjunction with fixed_aspect_ratio() for some 
    undetermined reason.
    """
    
    # Vectorise length with numpy (https://stackoverflow.com/a/44587916/8765762)
    arrlen = np.vectorize(len)
    
    ax1.set_yscale(scale)
    ax2.set_yscale(scale)
    
    for i in xrange(10):
        
        # Get y-bounds for ax1 and ax2
        ax1_ybounds = (np.linspace(*ax1.get_ybound(), num=tick_count) % 1).astype(str)
        ax2_ybounds = (np.linspace(*ax2.get_ybound(), num=tick_count) % 1).astype(str)
        
        # Calculate the length of decimal places
        ax1_ybounds_length = arrlen(ax1_ybounds)
        ax2_ybounds_length = arrlen(ax2_ybounds)
        
        # Test is within limits
        if np.all(ax1_ybounds_length - 2 < dec_limit) and np.all(ax2_ybounds_length - 2 < dec_limit):
            
            # Set y-ticks for both plots
            ax1.set_yticks(np.linspace(*ax1.get_ybound(), num=tick_count))
            ax2.set_yticks(np.linspace(*ax2.get_ybound(), num=tick_count))
            
            # Find the maximum number of decimal places
            tick_dec = np.nanmax((ax1_ybounds_length - 2, ax2_ybounds_length - 2)).astype(str)
            
            # Ensure the formatting of the ticks is consistent
            ax1.yaxis.set_major_formatter(FormatStrFormatter('%.' + tick_dec + 'f'))
            ax2.yaxis.set_major_formatter(FormatStrFormatter('%.' + tick_dec + 'f'))
            
            break
            
        else:
            
            tick_count += 1
    
    if i == 9:
        warnings.warn("Could not match up ticks correctly in match_ticks", UserWarning, stacklevel=3)        