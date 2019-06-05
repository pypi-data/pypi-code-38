"""Create photoionization database table."""
import os, os.path
import glob
import pandas as pd
import psycopg2
import astropy.units as u


def make_photo_table(con=None):
    """Create photoionization database table.

    If multiple reaction rates are found for a reaction, user is prompted
    to choose the best one.

    Photoionization and photodissociation reference:
    Huebner & Mukherjee (2015), Astrophys. Space Sci., 195, 1-294.
    """
    if con is None:
        con = psycopg2.connect(host='localhost', database='thesolarsystemmb')
        con.autocommit = True

    # drop the old table if necessary
    cur = con.cursor()
    cur.execute('select table_name from information_schema.tables')
    tables = [r[0] for r in cur.fetchall()]
    if 'photorates' in tables:
        cur.execute('''DROP table photorates''')
    else:
        pass

    # Make the photorates table
    cur.execute('''CREATE TABLE photorates (
                     filename text,
                     reference text,
                     species text,
                     reaction text,
                     kappa float,
                     bestvalue boolean)''')

    photodatafiles = glob.glob(os.path.join(os.path.dirname(__file__), 'data',
                                       'Loss', 'Photo', '*.dat'))

    for f in photodatafiles:
        print(f'  {f}')
        for line in open(f).readlines():
            if 'reference' in line.lower():
                ref = line.split('//')[0].strip()
            # elif 'datatype' in line.lower():
            #     dtype = line.split('//')[0].strip()
            # elif 'reactype' in line.lower():
            #     rtype = line.split('//')[0].strip()
            # elif 'ratecoefunits' in line.lower():
            #     un = line.split('//')[0].strip()
            elif len(line.split(':')) == 4:
                parts = line.split(':')
                sp = parts[0].strip()
                reac = parts[1].strip()
                kappa = parts[2].strip()

                cur.execute('''INSERT INTO photorates values(
                                   %s, %s, %s, %s, %s, %s)''',
                            (f, ref, sp, reac, kappa, False))

    # Look for duplicates
    cur.execute('SELECT DISTINCT reaction from photorates')
    temp = cur.fetchall()
    rlist = [t[0] for t in temp]
    for r in rlist:
        print(r)
        cur.execute('SELECT reference from photorates where reaction=%s',
                    (r, ))
        if cur.rowcount > 1:
            temp = cur.fetchall()
            refs = [a[0] for a in temp]
            print('Reaction = {}'.format(r))
            for i, a in enumerate(refs):
                print('({}) {}'.format(i, a))
            q = input('Which reference do you want to use?')
            q = int(q)
            cur.execute('''UPDATE photorates
                           SET bestvalue=True
                           WHERE reaction=%s and reference=%s''',
                        (r, refs[q]))
        else:
            cur.execute('''UPDATE photorates
                           SET bestvalue=True
                           WHERE reaction=%s''',
                        (r, ))

class PhotoRate:
    r"""Determine photoreactions and photorates for a species.

    **Parameters**

    species
        Species to compute rates for.

    aplanet
        Distance from the Sun. Default is 1 AU. Given as either a numeric
        type or an astropy quantity with length units.

    **Class Attributes**

    species
        Species

    aplanet
        Distance from the Sun; astropy quanitity with units AU

    rate
        Reaction rate; astropy quantity with units s^{-1}

    reactions
        Pandas dataframe with columns for reaction and rate (in s^{-1}) for
        that reaction
    """
    def __init__(self, species, aplanet_=1.*u.AU):
        with psycopg2.connect(host='localhost',
                              database='thesolarsystemmb') as con:
            prates = pd.read_sql(
                f'''SELECT reaction, kappa
                    FROM photorates
                    WHERE species='{species}' and bestvalue=True''', con)

        try:
            aplanet_.value
            aplanet = aplanet_
        except:
            aplanet = aplanet_*u.AU

        self.species = species
        self.aplanet = aplanet
        a0 = 1*u.AU

        # Photo rate adjusted to proper heliocentric distance
        if len(prates) == 0:
            print('No photoreactions found')
            self.reactions = None
            self.rate = 1e-30/u.s
        else:
            prates['kappa'] = prates['kappa'].apply(
                lambda k: k * (a0/aplanet)**2)
            self.reactions = prates
            self.rate = prates['kappa'].sum()/u.s

    def __str__(self):
        print(f'Species = {self.species}\n'
              f'Distance = {self.aplanet}\n'
              f'Rate = {self.rate}')
        return ''
