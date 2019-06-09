from datetime import datetime
from geopy.distance import geodesic
import math


def printmsg(msg):
    """Prints messages to the terminal with date and timestamp.

    Parameters
    ----------
    msg : str
        The message to write out.
    """
    print('%s - %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))


def genericerror(filetype='file'):
    """Prints a standard message for a generic error using the `gpx2dzg.functions.printmsg()` function.
    This is called from functions in `gpx2dzg.io`.

    Parameters
    ----------
    filetype : str
        The type of file this message is about. Used to format error string.
    """
    printmsg('please attach this %s to a new github issue (https://github.com/iannesbitt/gpx2dzg/issues/new)' % filetype)
    printmsg('        or send it to ian.nesbitt@gmail.com in order to have the format assessed. please also')
    printmsg('        include the output of the program (i.e. copy and paste this text and the text above in')
    printmsg('        the message) as this will drastically speed up my ability to help you! thanks!')
    printmsg('  ~!~>  I am happy to help but please note that I am not responsible for the content of your')
    printmsg('  ~!~>  files, only the working-ness of this software. I appreciate your understanding!')


def gpxerror(e=''):
    """Prints an error message then calls `gpx2dzg.functions.genericerror()` and passes `filetype='GPX'`.

    Parameters
    ----------
    e : str
        The error message to print.
    """
    printmsg('ERROR TEXT: %s' % e)
    genericerror('GPX')


def dzxerror(e=''):
    """Prints an error message then calls `gpx2dzg.functions.genericerror()` and passes `filetype='DZX'`.

    Parameters
    ----------
    e : str
        The error message to print.
    """
    printmsg('ERROR TEXT: %s' % e)
    genericerror('DZX')


def writeerror(e=''):
    """Prints an error message then calls `gpx2dzg.functions.genericerror()` and passes `filetype='GPX'`.

    Parameters
    ----------
    e : str
        The error message to print.
    """
    printmsg('ERROR: could not write the file because you do not have write permission in this directory.')
    printmsg('ERROR TEXT: %s' % e)


def dd2dms(dd): # credit to stackoverflow user Erik L (https://stackoverflow.com/a/10286690/4648080)
    """
    Converts decimal degrees to a tuple containing degrees, minutes, and seconds (DMS). For the purpose of
    this software, the decimal in seconds is removed in order to create a NMEA-friendly string.

    Parameters
    ----------
    dd : float
        The decimal degree value to convert to DMS.

    Credit to StackOverflow user Erik L (https://stackoverflow.com/a/10286690/4648080) for this function.
    """
    is_positive = dd >= 0
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600,60)
    degrees,minutes = divmod(minutes,60)
    degrees = degrees if is_positive else -degrees
    return (degrees,minutes,str(seconds).replace('.',''))


def course(pointA, pointB): # credit to github user jeromer (https://gist.github.com/jeromer/2005586)
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float

    Credit to GitHub user jeromer (https://gist.github.com/jeromer/2005586) for this function.
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def mean(n):
    '''Calculates arithmetic mean for a list of numbers.

    Parameters
    ----------
    n : list
        List of numbers for which to calculate mean.

    Returns
    -------

    float
        Value of arithmetic mean.
    '''
    return float(sum(n)) / max(len(n), 1)


def distance_speed_time(gpx=None):
    """Converts list of GPX waypoints to lists of distances and speeds (in meters and meters per second) from the origin (0).

    Parameters
    ----------
    gpx : gpxpy.GPX
        The list of GPX waypoints to process.

    Returns
    -------
    list
        A list of distances (in meters) from the origin for plotting.

    """
    i = 0
    dist = [0]
    spd = []
    times = [0]
    for pt in gpx.waypoints:
        lat = pt.latitude
        lon = pt.longitude
        time = pt.time
        if i > 0:
            dist.append(geodesic((lat, lon), (lat0, lon0)).meters + dist[-1])
            spd.append(geodesic((lat, lon), (lat0, lon0)).meters / (time - time0).seconds)
            times.append((time - time0).seconds + times[-1])
        lat0 = lat
        lon0 = lon
        time0 = time
        i += 1
    return dist, spd, times


def ms2kt(speed=0.):
    '''
    Converts speed in meters per second to knots.

    Parameters
    ----------
    speed : float
        Speed in meters per second to be converted.

    Returns
    -------
    float
        Speed in knots (1 kt = 0.514444444 m/s).
    '''
    return speed/0.514444444


def sog(lat0=0, lon0=0, time0=datetime.now(), lat1=0, lon1=0, time1=datetime.now()):
    """
    Converts a pair of latitude, longitude, and time points to speed over ground in knots.

    Parameters
    ----------
    lat0 : float
        The latitude at `time0`.
    lon0 : float
        The longitude at `time0`.
    lat1 : float
        The latitude at `time1`.
    lat1 : float
        The longitude at `time0`.
    time0 : datetime
        The initial time, when time=0.
    time1 : datetime
        The pursuant time, when time=1.

    Returns
    -------
    float
        Returns speed over ground in knots.
    """

    # sog is m/s. need to convert to kts.
    sog = geodesic((lat1, lon1), (lat0, lon0)).meters / (time1 - time0).seconds

    return ms2kt(speed=sog)

def drop(marks=[], drops=[]):
    """
    Takes a list of positional index values to drop from a DZT/DZX mark list. Returns the list without the dropped values.
    The list can include negative integer positional values, which are converted to positive positional values.
    List drops are done in descending order (high to low).

    Parameters
    ----------
    marks : list
        The list of mark values to drop from.
    drops : list
        The list of indices to drop.

    Returns
    -------
    list
        A list of mark values sans the ones dropped.
    """
    i = 0
    for index in drops: # a tricky bit of code to make sure the index is inbounds
        if (index > 0) and (index < len(marks)-1): # first we check to see if it's positive and in range
            pass
        elif (len(marks) - abs(index) > 0) and (len(marks) - abs(index) < len(marks)-1): # then if it's negative, we check that the list length minus absolute value is in range
            drops[i] = len(marks) - abs(index) # if so, we convert to positive (required for sort, see below)
        else:
            printmsg('WARNING: cannot drop the start point (0 or %s) or before, or the end point (%s or -1) or after. (ignoring [%s])' % (-len(marks), len(marks)-1, index))
            del drops[i] # if not, we delete it from the drops list
        i += 1

    drops.sort(reverse=True) # this is necessary to make sure we delete the right things (indices higher than deleted value change, so we go high to low to avoid problems)

    dropped = [] # keeping track of drops
    for index in drops:
        del marks[index]
        dropped.append(index)

    if len(dropped) > 0:
        printmsg('dropped indices %s from DZT/DZX marks' % dropped)
    else:
        printmsg('no DZT/DZX marks were dropped.')

    return marks