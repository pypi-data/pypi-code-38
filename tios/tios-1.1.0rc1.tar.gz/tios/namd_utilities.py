"""
Utilities to extract required information from NAMD files
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

def config_file_valid_for_imd(configfile):
    """
    Checks that the config file contains all required parameters for an IMD run.

    Args:
        configfile (str): Name of NAMD config file.

    Returns:
        bool: True if the file is valid, else False.

    """
    if not os.path.exists(configfile):
        print('Error: cannot find {}'.format(configfile))
        return False

    pcoupl = None
    imd = None
    port = None

    env = environments.load_mongo_env()
    imd_port = env['IMD_PORT']
    
    with open(configfile, 'r') as f:
        for line in f:
            w = line.split()
            if len(w) > 0:
                if w[0] == 'langevinPiston':
                    pcoupl = w[1]
                if w[0] == 'IMDon':
                    imd = w[1]
                if w[0] == 'IMDport':
                    port = int(w[1])
    if pcoupl == 'on':
        print('Error: Tios does not support constant pressure simulations')
        print('Please set \"langevinPiston off\" in your .conf file.')
        return False

    if imd != 'yes':
        print("Error: IMD has not been enabled for this simulation.")
        print("Please add \"IMDon   yes\" to your .conf file.")
        return False

    if imd == 'yes' and  port != int(imd_port):
        if port is None:
            print('Error: the port for IMD is not set.')
        else:
            print('Error: the port for IMD is set to  {}.'.format(port))
        print('Please add \"IMDport {}\" to your .conf file.'.format(imd_port))
        return False

    return True

def dt_from_config_file(configfile):
    """
    Extracts the MD timestep from the config file.

    Args:
        configfile (str): Name of the NAMD config file.

    Returns:
        float: The basic MD timestep unit (in picoseconds).

    Raises:
        RuntimeError: if the value of `dt` cannot be determined.

    """
    dt = None
    
    with open(configfile, 'r') as f:
        for line in f:
            w = line.split()
            if len(w) > 0:
                if w[0] == 'timestep':
                    dt = float(w[1])
    if dt is None:
        raise RuntimeError('Error: cannot find MD timestep info in .conf file')
    return dt / 1000 # convert from fs to ps.

def trate_from_config_file(configfile):
    """
    Extracts the IMD sample frequency from the config file.

    Args:
        configfile (str): Name of the NAMD config file.

    Returns:
        float: The IMD sampling frequence (in timesteps).

    Raises:
        RuntimeError: if the value of `trate` cannot be determined.

    """
    trate = None
    
    with open(configfile, 'r') as f:
        for line in f:
            w = line.split()
            if len(w) > 0:
                if w[0] == 'IMDfreq':
                    trate = float(w[1])
    if trate is None:
        raise RuntimeError('Error: cannot find IMD sample rate info in .conf file')
    return trate

def step_from_config_file(configfile):
    """
    Extracts the step number from the config file.

    Args:
        configfile (str): Name of the NAMD config file.

    Returns:
        float: The current time step

    """
    step = None
    
    with open(configfile, 'r') as f:
        for line in f:
            w = line.split()
            if len(w) > 0:
                if w[0] == 'step':
                    dt = int(w[1])
    if step is None:
        raise RuntimeError('Error: cannot find timestep info in .conf file')
    return step

def pdb_from_config_file(configfile):
    """
    Create a string representation of a pdb file from the configfile.

    Args:
        configfile (str): Name of the NAMD config file.

    Returns:
        string: PDB file contents. 

    """
    topfile = None
    
    dir = os.path.dirname(configfile)
    with open(configfile, 'r') as f:
        for line in f:
            w = line.split()
            if len(w) > 0:
                if w[0] == 'coordinates':
                    topfile = w[1]
    if topfile is None:
        raise RuntimeError('Error: cannot find coordinates file info in .conf file')
    with open(os.path.join(dir, topfile)) as f:
        pdb = f.read()
    return pdb

def coordinates_from_config_file(configfile):
    """
    Extract coordinates from the configfile.

    Args:
        configfile (str): Name of the NAMD config file.

    Returns:
        numpy.ndarray: The cordinates [natoms, 3]. 

    """
    topfile = None
    
    dir = os.path.dirname(configfile)
    with open(configfile, 'r') as f:
        for line in f:
            w = line.split()
            if len(w) > 0:
                if w[0] == 'coordinates':
                    topfile = w[1]
    if topfile is None:
        raise RuntimeError('Error: cannot find coordinates file info in .conf file')
    topfile = os.path.join(dir, topfile)
    result = subprocess.check_output(['grep','ATOM',topfile],
                                     universal_newlines=True,
                                     stderr=subprocess.STDOUT)
    d = StringIO(result)
    xyz = np.loadtxt(d, usecols=[5,6,7], dtype='float32')
    xyz = xyz * 0.1 # convert to nanometers
    return xyz

def box_from_config_file(configfile):
    """
    Extract box data from the configfile.

    Args:
        configfile (str): Name of the NAMD config file.

    Returns:
        numpy.ndarray: The box info as a six-element array. 

    """
    topfile = None
    
    dir = os.path.dirname(configfile)
    with open(configfile, 'r') as f:
        for line in f:
            w = line.split()
            if len(w) > 0:
                if w[0] == 'coordinates':
                    topfile = w[1]
    if topfile is None:
        raise RuntimeError('Error: cannot find coordinates file info in .conf file')
    topfile = os.path.join(dir, topfile)
    result = subprocess.check_output(['grep','CRYST1',topfile],
                                     universal_newlines=True,
                                     stderr=subprocess.STDOUT)
    d = StringIO(result)
    box = np.loadtxt(d, usecols=[1,2,3,4,5,6], dtype='float32')
    box[:3] = box[:3] * 0.1 # convert to nanometers
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
    raise NotImplementedError('Not supported for NAMD')

def namd_check_version():
    '''
    Return the version of NAMD available on this resource.

    Returns:
        The NAMD version as a string, or None if it cannot be determined.

    '''
    namd = None
    try:
        output = subprocess.check_output(['which', 'namd2'], stderr=subprocess.STDOUT)
        namd = 'namd2'
    except:
        raise RuntimeError('Cannot find namd2 - is it in your path?')
    try:
        output2 = subprocess.check_output([namd, '-h'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
            output2 = e.output
    version = 'unknown'
    for line in output2.split(b'\n'):
        words = line.split()
        if len(words) > 0:
            if words[0] == b'Info:' and words[1] == b'NAMD':
                version = words[2].decode()
                break

    return version

def filenames_from_config_file(configfile):
    """
    Parse a NAMD config file and return a list of names of input files.

    Args:
        configfile (str): Name of the configuration file.

    Returns:
        list: List of file names

    """
    result = [configfile]
    dir = os.path.dirname(configfile)
    with open(configfile, 'r') as f:
        for line in f:
            if len(line) > 0:
                words = line.split()
                if len(words) > 1:
                    if words[0] in ['structure', 'coordinates', 'parameters',
                                    'bincoordinates', 'extendedSystem']:
                        result.append(os.path.join(dir, words[1]))
    return result

def apply_checkpoint(inputs, checkpoint):
    """
    Modify the inputs for a NAMD run according to checkpoint data.

    Args:
        inputs (dict): Dictionary of inputs
        checkpoint (dict): NAMD-format checkpoint data

    Returns:
        dict: Modified dictionary of inputs

    """
    configfile = config_file_name(inputs)
    restartfilebase = restart_file_basename(configfile)
    dir = os.path.dirname(restartfilebase)
    for key in checkpoint:        
        with open(os.path.join(dir, key), 'wb') as f:
            f.write(zlib.decompress(checkpoint[key]))

    with open(restartfilebase + '.xsc', 'r') as f:
        for line in f:
            step = line.split()[0]

    with open(configfile, 'r') as f:
        oldconf = f.readlines()
    os.rename(configfile, configfile + '.bak')
    with open(configfile, 'w') as f:
        f.write('bincoordinates     '+ restartfilebase + '.coor\n')
        f.write('binvelocities      '+ restartfilebase + '.vel\n')
        f.write('extendedSystem     '+ restartfilebase + '.xsc\n')
        f.write('firsttimestep      '+ step + '\n')
        for line in oldconf:
            words = line.split()
            if len(words) > 0:
                skip = False
                for keyword in ['binvelocities', 'bincoordinates', 
                                'extendedSystem', 'temperature', 
                                'firsttimestep']:
                    if words[0] == keyword:
                        skip = True
                if not skip:
                    f.write(line)
    return inputs

def config_file_name(inputs):
    """
    Extracts the name of the config file from the inputs dictionary.

    Args:
        inputs (dict): dictionary of inputs

    Returns:
        string: name of config file

    """
    result = None
    for key in inputs:
        if isinstance(inputs[key], str):
            if not inputs[key][0] in '<>+':
                result = inputs[key]
    return result

def restart_file_basename(configfile):
    """
    Returns the basename of the restart files.

    Args:
        configfile (str): configuration file

    Returns:
        str: basename of restart files

    """
    result = None
    dir = os.path.dirname(configfile)
    vars = {}
    with open(configfile, 'r') as f:
        for line in f:
            words = line.split()
            if len(words) > 0:
                if words[0] == 'set':
                    vars['$' + words[1]] = words[2]
                elif words[0] == 'outputName':
                    result = words[1]
                    break
    if result[0] == '$':
        result = vars[result]
    return os.path.join(dir, result) + '.restart'

def step_from_config_file(configfile):
    """
    Returns the start step number set in the config file

    Args:
        configfile (str): config file name

    Returns:
        int: step number

    """
    result = None
    with open(configfile, 'r') as f:
        for line in f:
            if 'step' in line:
                words = line.split()
                if words[0] == 'step':
                    result = int(words[1])
    return result

def inputs_dict_to_filepack(inputs, infiles):
    """
    Convert an inputs dictionary to a filepack - namd style.

    Args:
        inputs (dict): a dictionary of inputs.
        infiles (list): a list of required input files

    Returns:
        list

    """
    for key in inputs:
        if inputs[key] in infiles:
            inputs[key] = os.path.basename(inputs[key])
    filepack = {}
    for file in infiles:
        with open(file, 'rb') as f:
            filepack[os.path.basename(file)] = zlib.compress(f.read())
    return [inputs, filepack]

def filepack_to_inputs_dict(filepack, targetdir='.'):
    """
    Unpack a filepack.

    Args:
        filepack (list): a two element list, first is the inputs dict,
            second is the dictionary of compressed files.
        targetdir (str): optional: directory to uncompress files into.

    Returns:
        dict: The inputs dict.

    """
    inputs = filepack[0]
    filedict = filepack[1]
    for file in filedict:
        with open(os.path.join(targetdir, file), 'wb') as f:
            f.write(zlib.decompress(filedict[file]))

    infiles = [key for key in filedict]
    for key in inputs:
        if inputs[key] in infiles:
            inputs[key] = os.path.join(targetdir, inputs[key]) 
    return inputs
    
