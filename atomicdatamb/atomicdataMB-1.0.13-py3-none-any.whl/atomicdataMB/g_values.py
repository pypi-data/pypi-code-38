"""g-value routines."""
import glob
import os, os.path
import numpy as np
import pandas as pd
import psycopg2
import astropy.units as u
from astropy.io import ascii
from astropy import constants as const
import mathMB
from .atomicmass import atomicmass


def make_gvalue_table(con):
    """Creates and populates gvalues database table.

    Fields in the table:
        filename
        reference
        speceis
        refpt (AU)
        wavelength (A)
        velocity (km/s)
        g (1/s)
    """
    cur = con.cursor()

    # Erase the table if it is there
    cur.execute('select table_name from information_schema.tables')
    tables = [r[0] for r in cur.fetchall()]
    if 'gvalues' in tables:
        cur.execute('''DROP table photorates''')
    else:
        pass

    # Create the table
    cur.execute('''CREATE TABLE gvalues (
                     filename text,
                     reference text,
                     species text,
                     refpt float, -- AU
                     wavelength float, -- A
                     velocity float[], -- km/s
                     g float[])''')  # 1/s

    # Look up the gvalue datafiles

    datafiles = glob.glob(os.path.join(os.path.dirname(__file__), 'data',
                                       'g-values', '*.dat'))
    ref = 'Killen et al. (2009)'

    for d in datafiles:
        # Determine the species
        f = os.path.basename(d)
        sp = f.split('.')[0]

        # Determine reference point for the file
        with open(d, 'r') as f:
            # Determine the reference point
            astr = f.readline().strip()
            a = float(astr.split('=')[1])

            # Determine the wavelengths
            ww = f.readline().strip().split(':')[1:]
            wavestr = [w.strip() for w in ww]

        # Read in the data table
        data = ascii.read(d, delimiter=':', header_start=1)

        # make the vel array
        vel = np.array(data['vel'])
        q = np.argsort(vel)
        vel = vel[q]

        # Make an array of g-values for each wavelength and add the row
        for w in wavestr:
            gg = np.array(data[w])
            gg = gg[q]
            wave = float(w.strip())
            print(d, sp, wave)

            cur.execute('''INSERT into gvalues values (
                           %s, %s, %s, %s, %s, %s, %s)''',
                        (d, ref, sp, a, wave, list(vel), list(gg)))


class gValue:
    r"""Class containing g-value vs. velocity for a specified atom and
    transition.

    **Parameters**

    sp
        atomic species

    wavelength
        Wavelength of the transition

    aplanet
        Distance from the Sun. Can be given as an astropy quantity with
        distance units or as a float assumed to be in AU. Default = 1 AU

    database
        Database containing solar system information. Default =
        `thesolarsystem` which probably shouldn't be overridden.

    **Class Attributes**

    species
        The input species

    wavelength
        The input wavelength

    aplanet
        The input aplanet

    velocity
        Radial velocity deviation relative to the Sun in km/s.
        Positive values indicate
        motion away from the Sun. Given as a numpy array of astropy quantities

    g
        g-value as function of velocity in units 1/s.
    """
    def __init__(self, sp, wavelength=None, aplanet=1*u.au,
                 database='thesolarsystemmb'):

        self.species = sp
        if wavelength is None:
            assert 0
            # waves = pd.read_sql(
            #     f'''SELECT DISTINCT wavelength
            #         FROM gvalues
            #         WHERE species='{self.species}' ''', con)
            # self.wavelength = [w * u.AA for w in waves.wavelength]

        try:
            self.wavelength = wavelength.to(u.AA)
        except:
            self.wavelength = wavelength * u.AA

        try:
            self.aplanet = aplanet.to(u.au)
        except:
            self.aplanet = aplanet * u.au

        with psycopg2.connect(database=database) as con:
            gvalue = pd.read_sql(
                f'''SELECT refpt, velocity, g
                    FROM gvalues
                    WHERE species='{self.species}' and
                          wavelength='{self.wavelength.value}' ''', con)

        if len(gvalue) == 0:
            self.velocity = np.array([0., 1.])*u.km/u.s
            self.g = np.array([0., 0.])/u.s
            print(f'Warning: g-values not found for species = {sp}')
        elif len(gvalue) == 1:
            self.velocity = np.array(gvalue.velocity[0])*u.km/u.s
            self.g = (np.array(gvalue.g[0])/u.s *
                      gvalue.refpt[0]**2/self.aplanet.value**2)
        else:
            assert 0, 'Multiple rows found.'


class RadPresConst:
    r"""Class containing radial acceleration vs. velocity for a specified atom.

    **Parameters**

    sp
        atomic species

    aplanet
        Distance from the Sun. Can be given as an astropy quantity with
        distance units or as a float assumed to be in AU. Default = 1 AU

    database
        Database containing solar system information. Default =
        `thesolarsystem` which probably shouldn't be overridden.

    **Class Attributes**

    species
        The input species

    aplanet
        The input distance from the Sun

    velocity
        Radial velocity deviation relative to the Sun in km/s.
        Positive values indicate
        motion away from the Sun. Given as a numpy array of astropy quantities

    accel
        Radial acceleration vs. velocity with units km/s**2.
    """
    def __init__(self, sp, aplanet, database='thesolarsystemmb'):
        self.species = sp
        try:
            self.aplanet = aplanet.value * u.au
        except:
            self.aplanet = aplanet * u.au

        # Open database connection
        with psycopg2.connect(database=database) as con:
            waves = pd.read_sql(f'''SELECT DISTINCT wavelength
                                    FROM gvalues
                                    WHERE species='{sp}' ''', con)

        if len(waves) == 0:
            self.v = np.array([0., 1.])*u.km/u.s
            self.accel = np.array([0., 0.])*u.km/u.s**2
            print(f'Warning: g-values not found for species = {sp}')
        else:
            self.wavelength = [w*u.AA for w in waves.wavelength]

            gvals = [gValue(sp, w, aplanet, database=database)
                     for w in self.wavelength]

            # Complete velocity set
            allv = []
            for g in gvals:
                allv.extend(g.velocity.value)
            allv = np.unique(allv) * u.km/u.s

            # Interpolate gvalues to full velocity set and compute rad pres
            rr = np.zeros_like(allv)/u.s
            for g in gvals:
                g2 = mathMB.interpu(allv, g.velocity, g.g)
                q = const.h/atomicmass(sp)/g.wavelength * g2
                rr += q.to(u.km/u.s**2)
            self.velocity = allv
            self.accel = rr
