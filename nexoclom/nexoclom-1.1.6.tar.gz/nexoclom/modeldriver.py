import os
import numpy as np
from astropy.time import Time
import astropy.units as u
from .Output import Output


def delete_files(filelist, database):
    ''' Delete output files and remove them from the database '''
    import psycopg2

    with psycopg2.connect(host='localhost', database=database) as con:
        con.autocommit = True
        cur = con.cursor()

        for f in filelist:
            # Delete the file
            print(f)
            if os.path.exists(f):
                os.remove(f)

            # Remove from database
            cur.execute('''SELECT idnum FROM outputfile
                           WHERE filename = %s''', (f, ))
            idnum = cur.fetchone()[0]

            cur.execute('''DELETE FROM outputfile
                           WHERE idnum = %s''', (idnum, ))
            cur.execute('''DELETE FROM geometry
                           WHERE geo_idnum = %s''', (idnum, ))
            cur.execute('''DELETE FROM sticking_info
                           WHERE st_idnum = %s''', (idnum, ))
            cur.execute('''DELETE FROM forces
                           WHERE f_idnum = %s''', (idnum, ))
            cur.execute('''DELETE FROM spatialdist
                           WHERE spat_idnum = %s''', (idnum, ))
            cur.execute('''DELETE FROM speeddist
                           WHERE spd_idnum = %s''', (idnum, ))
            cur.execute('''DELETE FROM angulardist
                           WHERE ang_idnum = %s''', (idnum, ))
            cur.execute('''DELETE FROM options
                       WHERE opt_idnum = %s''', (idnum, ))
            print(f'Removed {idnum}: {os.path.basename(f)} from database')

            cur.execute('''SELECT idnum, filename FROM modelimages
                           WHERE out_idnum = %s''', (idnum, ))
            for mid, mfile in cur.fetchall():
                cur.execute('''DELETE from modelimages
                               WHERE idnum = %s''', (mid, ))
                if os.path.exists(mfile):
                    os.remove(mfile)

            cur.execute('''SELECT idnum, filename FROM uvvsmodels
                           WHERE out_idnum = %s''', (idnum, ))
            for mid, mfile in cur.fetchall():
                cur.execute('''DELETE from uvvsmodels
                               WHERE idnum = %s''', (mid, ))
                if os.path.exists(mfile):
                    os.remove(mfile)


def modeldriver(inputs, npackets, overwrite=False, compress=True):
    '''
    Starting point for running the model
    INPUTS:
        inputs: Input object
        npackets: Total number of packets to run for this simulation
        overwrite: If True, delete existing files for this set of inputs
    '''

    t0_ = Time.now()
    print(f'Starting at {t0_}')

    if len(inputs.geometry.planet) != 1:
        print('Gravity and impact check not working for planets with moons.')
        sys.exit(1)

    # Determine how many packets have already been run
    outputfiles, totalpackets, _ = inputs.findpackets()
    print(f'Found {len(outputfiles)} files with {totalpackets} packets')

    if overwrite and (totalpackets > 0):
        # delete files and remove from database
        delete_files(outputfiles, inputs._database)
        totalpackets = 0
    else:
        pass

    npackets = int(npackets)
    ntodo = npackets - totalpackets
    packs_per_it = 100000 if inputs.options.streamlines else int(1e6)
    packs_per_it = min(ntodo, packs_per_it)

    if ntodo > 0:
        # Check to make sure at_once is set properly
        if inputs.options.streamlines and (inputs.options.at_once is False):
            raise RuntimeError

        # Determine how many iterations are needed
        nits = int(np.ceil(ntodo/packs_per_it))

        print('Running Model')
        print(f'Will compute {nits} iterations of {packs_per_it} packets.')

        # Do the iterations
        for _ in range(nits):
            tit0_ = Time.now()
            print(f'** Starting iteration #{_+1} of {nits} **')

            # Create an output object
            output = Output(inputs, packs_per_it, compress=compress)

            # Run the packets
            if inputs.options.streamlines:
                output.stream_driver()
            else:
                output.driver()

            # Save
            output.save()
            del output
            tit1_ = Time.now()
            print(f'** Completed iteration #{_+1} in {(tit1_-tit0_).sec} '
                  f'seconds.')
    else:
        pass

    t2_ = Time.now()
    dt_ = (t2_-t0_).sec
    if dt_ < 60:
        dt_ = f'{dt_} sec'
    elif dt_ < 3600:
        dt_ = f'{dt_/60} min'
    else:
        dt_ = f'{dt_/3600} hr'
    print(f'Model run completed in {dt_}')
