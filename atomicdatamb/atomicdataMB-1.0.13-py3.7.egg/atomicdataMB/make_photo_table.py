"""Create photoionization database table."""
import os, os.path
import glob


def make_photo_table(con):
    """Create photoionization database table.

    Searches for *.dat in Data/AtomicData/Loss/Photo/
    If multiple reaction rates are found for a reaction, user is prompted
        to choose the best one.
    Saves the table as an HTML table for easy viewing. [Not implemented yet
        because I don't know where to save it]
    """
    cur = con.cursor()

    # drop the old table if necessary
    try:
        cur.execute('''DROP table photorates''')
    except:
        con.rollback()

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
