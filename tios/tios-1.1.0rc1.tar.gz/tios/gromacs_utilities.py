"""
Utilities to extract required information from GROMACS files
"""
from __future__ import print_function
import sys
import os
import subprocess
import tempfile
import zlib
from io import StringIO
import numpy as np
from tios import environments

def complete_inputs(inputs):
    """
    Complete entries in an inputs dictionary for a Gromacs simulation.

    Used when the invocation has used the "-deffnm" shorthand.

    Args:
        inputs (dict): Dictionary of ``{inputflag : inputvalue}`` pairs.

    Returns:
        dict: Completed dictionary of `inputs`.
    """
    if '-deffnm' in inputs:
        deffnm = inputs['-deffnm']
        if not '-s' in inputs:
            inputs['-s'] = deffnm + '.tpr'
        if not '-o' in inputs:
            inputs['-o'] = deffnm + '.trr'
        if not '-x' in inputs:
            inputs['-x'] = deffnm + '.xtc'
        if not '-cpo' in inputs:
            inputs['-cpo'] = deffnm + '.cpt'
        if not '-e' in inputs:
            inputs['-e'] = deffnm + '.edr'
        if not '-g' in inputs:
            inputs['-g'] = deffnm + '.log'
        del inputs['-deffnm']
    return inputs

def complete_inputs_for_imd(inputs):
    """
    Checks and amends the inputs dictionary for a valid gromacs IMD run.

    Args:
        inputs (dict): Dictionary of ``{inputflag : inputvalue}`` pairs.

    Returns:
        dict: Completed dictionary of `inputs`.
    """
    new_inputs = inputs.copy()
    env = environments.load_mongo_env()
    if not '-imdwait' in new_inputs:
        new_inputs['-imdwait'] = None
    if not '-imdterm' in new_inputs:
        new_inputs['-imdterm'] = None
    if not '-imdport' in new_inputs:
        new_inputs['-imdport'] = str(env['IMD_PORT'])
    return new_inputs

def apply_checkpoint(inputs, checkpoint):
    """
    Unpack checkpoint data and update the inputs dictionary accordingly.

    Args:
        inputs (dict): Dictionary of ``{inputflag : inputvalue}`` pairs.
        checkpoint (str): ``zlib`` compressed checkpoint file contents.

    Returns:
        dict: Completed dictionary of `inputs`
    """
    new_inputs = inputs.copy()
    if '-cpo' in inputs:
        checkpointfile = inputs['-cpo']
    elif '-deffnm' in inputs:
        checkpointfile = inputs['-deffnm'] + '.cpt'
    elif '-s' in inputs:
        checkpointfile = os.path.splitext(inputs['-s'])[0] +'.cpt'
    else:
        checkpointfile = 'system.cpt'

    new_inputs['-cpi'] = checkpointfile
    with open(checkpointfile, 'wb') as f:
        f.write(zlib.decompress(checkpoint))

    new_inputs['-noappend'] = None
    return new_inputs
       
def tpr_file_valid_for_imd(tprfile):
    """
    Checks that the tpr file contains all required parameters for an IMD run.

    Args:
        tprfile (str): Name of GROMACS tpr file.

    Returns:
        bool: True if the file is valid, else False.

    """
    if not os.path.exists(tprfile):
        print('Error: cannot find {}'.format(tprfile))
        return False
    try:
        result = subprocess.check_output(["gmx", "dump", "-s",
                                          tprfile],
                                          stderr=subprocess.STDOUT)
    except:
        message = sys.exc_info()[1]
        print('Error:', message)
        if isinstance(message, tuple):
            errno = sys.exc_info()[1][0]
            if errno == 2:
                print('Is the gmx command in your path?')
        return False

    pcoupl = None
    for line in result.split(b'\n'):
        w = line.split()
        if len(w) > 0:
            if w[0] == b'pcoupl':
                pcoupl = w[2]
    if pcoupl != b'No' and pcoupl != b'no':
        print('Error: Tios does not support constant pressure simulations')
        print('Please set pcoupl = no in your .mdp file and re-run grompp')
        return False

    if not b'IMD-atoms' in result:
        print("Error: IMD has not been enabled for this simulation.")
        print("Please add \"imd-group = System\" to your .mdp file and")
        print("re-run grompp.")
        return False

    return True

def dt_from_tpr_file(tprfile):
    """
    Extracts the MD timestep from the tpr file.

    Args:
        tprfile (str): Name of the Gromacs tpr file.

    Returns:
        float: The basic MD timestep unit (in picoseconds).

    Raises:
        RuntimeError: if the value of `dt` cannot be determined.

    """
    dt = None
    try:
        result = subprocess.check_output(["gmx", "dump", "-s",
                                          tprfile],
                                          stderr=subprocess.STDOUT)
    except:
        print('Error:', sys.exc_info()[1])
        errno = sys.exc_info()[1][0]
        if errno == 2:
            print('Is the gmx command in your path?')
        exit(1)

    for line in result.split(b'\n'):
        w = line.split()
        if len(w) > 0:
            if w[0] == b'dt':
                dt = float(w[2])
    if dt is None:
        raise RuntimeError('Error: cannot find MD timestep info in .tpr file')
    return dt

def pdb_from_tpr_file(tprfile):
    """
    Create a string copy of a pdb file  from the tprfile.

    Args:
        tprfile (str): Name of the Gromacs tpr file.

    Returns:
        string: PDB file contents. 

    """
    cwd = os.getcwd()
    try:
        topfile = os.path.basename(tempfile.NamedTemporaryFile(dir=cwd, suffix='.pdb', delete=False).name)
        result2 = None
        result2 = subprocess.check_output(["gmx", "editconf", "-f",
                                          tprfile, "-o", topfile,
                                          "-conect"],
                                          stderr=subprocess.STDOUT)
    except:
        print('Error:', sys.exc_info())
        print(result2)
        exit(1)
    with open(topfile) as f:
        pdbfile = f.read()
    os.remove(topfile)
    return pdbfile

def coordinates_from_tpr_file(tprfile):
    """
    Returns a numpy array of the coordinates from the tprfile.

    Args:
        tprfile (str): Name of the Gromacs tpr file.

    Returns:
        numpy.npdarray: an [natoms, 3] array of coordinates. 

    """
    cwd = os.getcwd()
    try:
        topfile = os.path.basename(tempfile.NamedTemporaryFile(dir=cwd, suffix='.pdb', delete=False).name)
        result = None
        result = subprocess.check_output(["gmx", "editconf", "-f",
                                          tprfile, "-o", topfile],
                                          stderr=subprocess.STDOUT)
    except:
        print('Error:', sys.exc_info())
        print(result)
        exit(1)
    try:
        result2 = None
        result2 = subprocess.check_output(["grep", "ATOM", topfile],
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
    except:
        print('Error:', sys.exc_info())
        print(result2)
        exit(1)

    d = StringIO(result2)
    xyz = np.loadtxt(d, usecols=[5,6,7], dtype='float32')
    os.remove(topfile)
    return xyz * 0.1 # convert to nanometers

def box_from_tpr_file(tprfile):
    """
    Returns a numpy array of the box vector from the tprfile.

    Args:
        tprfile (str): Name of the Gromacs tpr file.

    Returns:
        numpy.npdarray: an array of the box vectors. 

    """
    cwd = os.getcwd()
    try:
        topfile = os.path.basename(tempfile.NamedTemporaryFile(dir=cwd, suffix='.gro', delete=False).name)
        result = None
        result = subprocess.check_output(["gmx", "editconf", "-f",
                                          tprfile, "-o", topfile],
                                          stderr=subprocess.STDOUT)
    except:
        print('Error:', sys.exc_info())
        print(result)
        exit(1)
    try:
        result2 = None
        result2 = subprocess.check_output(["tail", "-1", topfile],
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True)
    except:
        print('Error:', sys.exc_info())
        print(result2)
        exit(1)

    d = StringIO(result2)
    try:
        box = np.loadtxt(d, dtype='float32')
    except:
        box = None
    os.remove(topfile)
    if box is not None:
        if len(box) == 3 or len(box) == 6:
           box[:3] = box[:3] * 0.1 # convert to nanometers
        else:
            box = None
    return box 

def step_from_checkpoint_file(cptfile):
    """
    Extracts the current time step from a checkpoint file.

    Args:
        cptfile (str): Name of the checkpoint file.

    Returns:
        int: The final timestep (in units of `dt`).

    Raises:
        RuntimeError: if `cptfile` cannot be found, or the current
            timestep cannot be identified.

    """
    step = None
    if not os.path.exists(cptfile):
        raise RuntimeError('Error: cannot find {}'.format(cptfile))
    try:
        result = subprocess.check_output(["gmx", "dump", "-cp",
                                          cptfile],
                                          stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(e.output, e.returncode)
        exit(1)
    except OSError as e:
        if e.errno == 2:
            print('Is the gmx command in your path?')
        else:
            print(e)
        exit(1)
    except:
        message = sys.exc_info()[1]
        print('Error:', message)
        exit(1)

    for line in result.split(b'\n'):
        w = line.split()
        if len(w) > 0:
            if w[0] == b'step':
                step = int(w[2])
    if step is None:
        raise RuntimeError('Error: cannot find current step info in .cpt file')
    return step

def gromacs_check_version():
    '''
    Return the version of Gromacs available on this resource.

    Returns:
        The Gromacs version as a string, or None if it cannot be determined.

    '''
    gmx = gromacs_find_gmx()
    if gmx is None:
        return None
    try:
        output = subprocess.check_output([gmx, '-version'], stderr=subprocess.STDOUT, universal_newlines=True)
    except:
        return None
    version = 'unknown'
    for line in output.split():
        words = line.split()
        if 'version:' in words:
            version = words[-1]
            break

    return version

def gromacs_find_gmx():
    '''
    Find out if the current environment has 'gmx' or 'gmx_d' commands available.

    Returns:
        "gmx", "gmx_d", or None.

    '''
    gmx = None
    try:
        output = subprocess.check_output(['which', 'gmx'], stderr=subprocess.STDOUT)
        gmx = 'gmx'
    except:
        try:
            output = subprocess.check_output(['which', 'gmx_d'], stderr=subprocess.STDOUT)
            gmx = 'gmx_d'
        except:
            try:
                output = subprocess.check_output(['which', 'gmx_mpi'], stderr=subprocess.STDOUT)
                gmx = 'gmx_mpi'
            except:
                pass
    return gmx
        
