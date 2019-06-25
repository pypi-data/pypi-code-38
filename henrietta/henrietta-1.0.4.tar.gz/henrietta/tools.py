import numpy as np

def stellar_density(P, jeff):

   '''
   P = planet orbital period in days
   jeff = ratio of planet semi-major axis to stellar radius
   '''

   G = 6.67e-11 #[m^3/(kg*s^2)]

   print('The density of your star is {} g/cm^3. Sweet.'.format(np.round(((3*np.pi/G) * (1/(P*60*60*24)**2) * (jeff)**3)/1000,2)))


kepler_offset = 2454833.0
tess_offset = 2457000.0

def bjd2bkjd(t):
    '''
    Convert a
    BJD (Barycentric Julian Date)
    into a
    BKJD (Barycentric Kepler Julian Date)
    via the relationship
    BKJD = BJD - 2454833.0

    Parameters
    ----------
    t : float, array
        Time in BJD (Barycentric Julian Date), with values like 2454123.123.

    Returns
    -------
    t_kepler : float, array
        Time in BKJD (Barycentric Kepler Julian Date).
    '''
    return t - kepler_offset


def bkjd2bjd(t_kepler):
    '''
    Convert a
    BKJD (Barycentric Kepler Julian Date)
    into a
    BJD (Barycentric Julian Date)
    via the relationship
    BKJD = BJD - 2454833.0

    Parameters
    ----------
    t_kepler : float, array
        Time in BKJD (Barycentric Kepler Julian Date)

    Returns
    -------
    t : float, array
        Time in BJD (Barycentric Julian Date), with values like 2454123.123.
    '''
    return t_kepler + kepler_offset

def bjd2btjd(t):
    '''
    Convert a
    BJD (Barycentric Julian Date)
    into a
    BTJD (Barycentric TESS Julian Date)
    via the relationship
    BTJD = BJD - 2457000.0

    Parameters
    ----------
    t : float, array
        Time in BJD (Barycentric Julian Date), with values like 2454123.123.

    Returns
    -------
    t_tess : float, array
        Time in BTJD (Barycentric TESS Julian Date)
    '''
    return t - tess_offset


def btjd2bjd(t_tess):
    '''
    Convert a
    BTJD (Barycentric TESS Julian Date)
    into a
    BJD (Barycentric Julian Date)
    via the relationship
    BTJD = BJD - 2457000.0

    Parameters
    ----------
    t_tess : float, array
        Time in BTJD (Barycentric TESS Julian Date)

    Returns
    -------
    t : float, array
        Time in BJD (Barycentric Julian Date), with values like 2454123.123.
    '''
    return t_tess + tess_offset

def find_appropriate_epoch(lc, t0=0):
    '''
    For a given light curve object, convert a transit epoch (in BJD, with
    values like 2454123.123) into the right values to match the light curve's
    time_format. This handles the offsets between BKJD (Kepler) and BTJD (TESS)
    and BJD (normal Barycentric Julian Dates).

    Parameters
    ----------

    lc : lightkurve.lightcurve.LightCurve
        This is any light curve object.

    t0 : float
        This is a single time of mid-transit, expressed in
        Barycentric Julian Date (BJD) with values like 2454123.123.
    '''

    # choose the appropriate offset for the lc's time format
    if lc.time_format == 'bkjd':
        epoch = bjd2bkjd(t0)
    elif lc.time_format == 'btjd':
        epoch = bjd2btjd(t0)
    else:
        epoch = t0

    # return the epoch
    return epoch
