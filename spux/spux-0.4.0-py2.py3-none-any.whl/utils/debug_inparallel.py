# from: https://wiki.canterbury.ac.nz/display/UCHPC/Debugging+mpi4py+code
#
# Running the command just below will open 4 xterm windows, displaying a Process each for script.py.
# mpiexec --mca pmix_server_max_wait 9000 --mca pmix_base_exchange_timeout 9000 -n 4 xterm -fa 'Monospace' -fs 13 -e "python3 debug_inparallel.py"
# then attach xterms to log with cntrl key + right mouse

import pdb

if __name__ == '__main__':
    """See https://wiki.canterbury.ac.nz/display/UCHPC/Debugging+mpi4py+code"""

    import script_split # noqa: F401
    pdb.run('script_split')
