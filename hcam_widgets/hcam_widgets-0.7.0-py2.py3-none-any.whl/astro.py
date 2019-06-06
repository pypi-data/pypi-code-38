# Some utility tools to handle rising and setting etc.
from __future__ import print_function, unicode_literals, absolute_import, division
import warnings
import numpy as np
from numpy.polynomial.polynomial import polyval

# astropy
from astropy import coordinates as coord
from astropy.time import Time
from astropy import units as u

MAGIC_TIME = Time(-999, format='jd')


def _equation_of_time(t):
    """
    Find the difference between apparent and mean solar time

    Parameters
    ----------
    t : `~astropy.time.Time`
        times (array)

    Returns
    ----------
    ret1 : `~astropy.units.Quantity`
        the equation of time
    """

    # Julian centuries since J2000.0
    T = (t - Time("J2000")).to(u.year).value / 100

    # obliquity of ecliptic (Meeus 1998, eq 22.2)
    poly_pars = (84381.448, 46.8150, 0.00059, 0.001813)
    eps = u.Quantity(polyval(T, poly_pars), u.arcsec)
    y = np.tan(eps/2)**2

    # Sun's mean longitude (Meeus 1998, eq 25.2)
    poly_pars = (280.46646, 36000.76983, 0.0003032)
    L0 = u.Quantity(polyval(T, poly_pars), u.deg)

    # Sun's mean anomaly (Meeus 1998, eq 25.3)
    poly_pars = (357.52911, 35999.05029, 0.0001537)
    M = u.Quantity(polyval(T, poly_pars), u.deg)

    # eccentricity of Earth's orbit (Meeus 1998, eq 25.4)
    poly_pars = (0.016708634, -0.000042037, -0.0000001267)
    e = polyval(T, poly_pars)

    # equation of time, radians (Meeus 1998, eq 28.3)
    eot = (y * np.sin(2*L0) - 2*e*np.sin(M) + 4*e*y*np.sin(M)*np.cos(2*L0) -
           0.5*y**2 * np.sin(4*L0) - 5*e**2 * np.sin(2*M)/4) * u.rad
    return eot.to(u.hourangle)


def _astropy_time_from_LST(t, LST, location, prev_next):
    """
    Convert a Local Sidereal Time to an astropy Time object.

    The local time is related to the LST through the RA of the Sun.
    This routine uses this relationship to convert a LST to an astropy
    time object.

    Returns
    -------
    ret1 : `~astropy.time.Time`
        time corresponding to LST
    """
    # now we need to figure out time to return from LST
    raSun = coord.get_sun(t).ra

    # calculate Greenwich Apparent Solar Time, which we will use as ~UTC for now
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        # ignore astropy deprecation warnings
        lon = location.longitude
    solarTime = LST - raSun + 12*u.hourangle - lon

    # assume this is on the same day as supplied time, and fix later
    first_guess = Time(
        u.d*int(t.mjd) + u.hour*solarTime.wrap_at('360d').hour,
        format='mjd'
    )

    # Equation of time is difference between GAST and UTC
    eot = _equation_of_time(first_guess)
    first_guess = first_guess - u.hour * eot.value

    if prev_next == 'next':
        # if 'next', we want time to be greater than given time
        mask = first_guess < t
        rise_set_time = first_guess + mask * u.sday
    else:
        # if 'previous', we want time to be less than given time
        mask = first_guess > t
        rise_set_time = first_guess - mask * u.sday
    return rise_set_time


def _rise_set_trig(t, target, location, prev_next, rise_set):
    """
    Crude time at next rise/set of ``target`` using spherical trig.

    This method is ~15 times faster than `_calcriseset`,
    and inherently does *not* take the atmosphere into account.

    The time returned should not be used in calculations; the purpose
    of this routine is to supply a guess to `_calcriseset`.

    Parameters
    ----------
    t : `~astropy.time.Time` or other (see below)
        Time of observation. This will be passed in as the first argument to
        the `~astropy.time.Time` initializer, so it can be anything that
        `~astropy.time.Time` will accept (including a `~astropy.time.Time`
        object)

    target : `~astropy.coordinates.SkyCoord`
        Position of target or multiple positions of that target
        at multiple times (if target moves, like the Sun)

    location : `~astropy.coordinates.EarthLocation`
        Observatory location

    prev_next : str - either 'previous' or 'next'
        Test next rise/set or previous rise/set

    rise_set : str - either 'rising' or 'setting'
        Compute prev/next rise or prev/next set

    Returns
    -------
    ret1 : `~astropy.time.Time`
        Time of rise/set
    """
    dec = target.transform_to(coord.ICRS).dec
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        # ignore astropy deprecation warnings
        lat = location.latitude
    cosHA = -np.tan(dec)*np.tan(lat.radian)
    # find the absolute value of the hour Angle
    HA = coord.Longitude(np.fabs(np.arccos(cosHA)))
    # if rise, HA is -ve and vice versa
    if rise_set == 'rising':
        HA = -HA
    # LST = HA + RA
    LST = HA + target.ra

    return _astropy_time_from_LST(t, LST, location, prev_next)


def calc_riseset(t, target_name, location, prev_next, rise_set, horizon):
    """
    Time at next rise/set of ``target``.

    Parameters
    ----------
    t : `~astropy.time.Time` or other (see below)
        Time of observation. This will be passed in as the first argument to
        the `~astropy.time.Time` initializer, so it can be anything that
        `~astropy.time.Time` will accept (including a `~astropy.time.Time`
        object)

    target_name : str
        'moon' or 'sun'

    location : `~astropy.coordinates.EarthLocation`
        Observatory location

    prev_next : str - either 'previous' or 'next'
        Test next rise/set or previous rise/set

    rise_set : str - either 'rising' or 'setting'
        Compute prev/next rise or prev/next set

    location : `~astropy.coordinates.EarthLocation`
        Location of observer

    horizon : `~astropy.units.Quantity`
        Degrees above/below actual horizon to use
        for calculating rise/set times (i.e.,
        -6 deg horizon = civil twilight, etc.)

    Returns
    -------
    ret1 : `~astropy.time.Time`
        Time of rise/set
    """
    target = coord.get_body(target_name, t)
    t0 = _rise_set_trig(t, target, location, prev_next, rise_set)
    grid = t0 + np.linspace(-4*u.hour, 4*u.hour, 10)
    altaz_frame = coord.AltAz(obstime=grid, location=location)
    target = coord.get_body(target_name, grid)
    altaz = target.transform_to(altaz_frame)
    time_limits, altitude_limits = _horiz_cross(altaz.obstime, altaz.alt,
                                                rise_set, horizon)
    return _two_point_interp(time_limits, altitude_limits, horizon)


@u.quantity_input(horizon=u.deg)
def _horiz_cross(t, alt, rise_set, horizon=0*u.degree):
    """
    Find time ``t`` when values in array ``a`` go from
    negative to positive or positive to negative (exclude endpoints)

    ``return_limits`` will return nearest times to zero-crossing.

    Parameters
    ----------
    t : `~astropy.time.Time`
        Grid of times
    alt : `~astropy.units.Quantity`
        Grid of altitudes
    rise_set : {"rising",  "setting"}
        Calculate either rising or setting across the horizon
    horizon : float
        Number of degrees above/below actual horizon to use
        for calculating rise/set times (i.e.,
        -6 deg horizon = civil twilight, etc.)

    Returns
    -------
    Returns the lower and upper limits on the time and altitudes
    of the horizon crossing.
    """
    if rise_set == 'rising':
        # Find index where altitude goes from below to above horizon
        condition = (alt[:-1] < horizon) * (alt[1:] > horizon)
    elif rise_set == 'setting':
        # Find index where altitude goes from above to below horizon
        condition = (alt[:-1] > horizon) * (alt[1:] < horizon)

    if np.count_nonzero(condition) == 0:
        warnmsg = ('Target does not cross horizon={} within '
                   '8 hours of trigonometric estimate'.format(horizon))
        warnings.warn(warnmsg)

        # Fill in missing time with MAGIC_TIME
        time_inds = np.nan
        times = [np.nan, np.nan]
        altitudes = [np.nan, np.nan]
    else:
        time_inds = np.nonzero(condition)[0][0]
        times = t[time_inds:time_inds+2]
        altitudes = alt[time_inds:time_inds+2]

    return times, altitudes


@u.quantity_input(horizon=u.deg)
def _two_point_interp(times, altitudes, horizon=0*u.deg):
    """
    Do linear interpolation between two ``altitudes`` at
    two ``times`` to determine the time where the altitude
    goes through zero.

    Parameters
    ----------
    times : `~astropy.time.Time`
        Two times for linear interpolation between

    altitudes : array of `~astropy.units.Quantity`
        Two altitudes for linear interpolation between

    horizon : `~astropy.units.Quantity`
        Solve for the time when the altitude is equal to
        reference_alt.

    Returns
    -------
    t : `~astropy.time.Time`
        Time when target crosses the horizon

    """
    if not isinstance(times, Time):
        return MAGIC_TIME
    else:
        slope = (altitudes[1] - altitudes[0])/(times[1].jd - times[0].jd)
        return Time(times[1].jd - ((altitudes[1] - horizon)/slope).value,
                    format='jd')
