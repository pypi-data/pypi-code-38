# deal with headers from GTC
from __future__ import print_function, unicode_literals, absolute_import, division
import warnings
import re

from astropy.io import fits
from astropy.table import Table
from astropy.coordinates import Longitude
from astropy import units as u
from astropy.time import Time


VARIABLE_GTC_KEYS = [
    'LST', 'ROTATOR', 'PARANG', 'DOME_AZ', 'AZIMUTH', 'ELEVAT', 'AIRMASS',
    'TELFOCUS', 'T_TUBE', 'T_PRIM', 'M2UX', 'M2UY', 'M2UZ', 'M2RX',
    'HUMIN', 'HUMOUT', 'TAMBIENT', 'PRESSURE', 'HUMIDITY', 'WINDSPEE', 'WINDDIRE', 'DEWPOINT'
]


def yield_three(iterable):
    """
    From some iterable, return three items, bundling all extras into last one.
    """
    return iterable[0], iterable[1], iterable[2:]


def parse_hstring(hs):
    """
    Parse a single item from the telescope server into name, value, comment.
    """
    # split the string on = and /, also stripping whitespace and annoying quotes
    name, value, comment = yield_three(
        [val.strip().strip("'") for val in filter(None, re.split("[=/]+", hs))]
    )

    # if comment has a slash in it, put it back together
    try:
        len(comment)
    except:
        pass
    else:
        comment = '/'.join(comment)
    return name, value, comment


def create_header_from_telpars(telpars):
    """
    Create a list of fits header items from GTC telescope pars.

    The GTC telescope server gives a list of string describing
    FITS header items such as RA, DEC, etc.

    Arguments
    ---------
    telpars : list
        list returned by server call to getTelescopeParams
    """
    # pars is a list of strings describing tel info in FITS
    # style, each entry in the list is a different class of
    # thing (weather, telescope, instrument etc).

    # first, we munge it into a single list of strings, each one
    # describing a single item whilst also stripping whitespace
    pars = [val.strip() for val in (';').join(telpars).split(';')
            if val.strip() != '']

    # apply parse_hstring to everything in pars
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', fits.verify.VerifyWarning)
        hdr = fits.Header(map(parse_hstring, pars))

    return hdr


def create_gtc_header_table():
    t = Table(names=['MJD'] + VARIABLE_GTC_KEYS)
    return t


def add_gtc_header_table_row(t, telpars):
    """
    Add a row with current values to GTC table

    Arguments
    ---------
    t : `~astropy.table.Table`
        The table to append row to
    telpars : list
        list returned by server call to getTelescopeParams
    """
    now = Time.now().mjd
    hdr = create_header_from_telpars(telpars)

    # make dictionary of vals to put in table
    vals = {k: v for k, v in hdr.items() if k in VARIABLE_GTC_KEYS}
    vals['MJD'] = now
    # store LST as hourangle
    vals['LST'] = Longitude(vals['LST'], unit=u.hour).hourangle
    t.add_row(vals)
