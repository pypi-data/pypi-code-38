from tios import gromacs_utilities, namd_utilities

import subprocess
import os
import zlib
import string
import random
import sys
python3 = sys.version_info[0] == 3
#Taken with thanks from 
#https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
import signal
class GracefulKiller(object):
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.siginterrupt(signal.SIGINT, False)
        signal.siginterrupt(signal.SIGTERM, False)

    def exit_gracefully(self, signum, frame):
        print('\nkiller received signal {}\nshutting down...\n'.format(signum))
        self.kill_now = True

def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def command_line_split(command):
    '''
    Splits a command line into preamble, executable, and arguments.
    '''
    preamble = []
    executable = []
    arguments = []
    code, indx = md_code_from_string(command, index=True)
    words = command.split()
    if code == 'GROMACS':
        preamble = words[0:indx]
        executable = words[indx:indx + 2]
        arguments = words[indx + 2:]
    elif code is not None:
        preamble = words[0:indx]
        executable = [words[indx]]
        arguments = words[indx + 1:]
    return preamble, executable, arguments 
        
def string_to_inputs_dict(command):
    '''
    Given a command line string, converts it into an inputs dictionary
    according to ExTASY wrappers philosophy.
    '''
    inputs = {}
    preamble, executable, arguments = command_line_split(command)
    inputs[-1] = preamble
    inputs[0] = executable
    n_pos = 0 # number of positional arguments
    n_args = len(arguments)
    iarg = 0
    while iarg < n_args:
        if not arguments[iarg][0] in '-<>':
            n_pos += 1
            inputs[n_pos] = arguments[iarg]
            iarg += 1
        else:
            if iarg + 1 < n_args:
                if arguments[iarg + 1][0] in '-<>':
                    inputs[arguments[iarg]] = None
                    iarg += 1
                else:
                    inputs[arguments[iarg]] = arguments[iarg + 1]
                    iarg += 2
            else:
                inputs[arguments[iarg]] = None
                iarg += 1
    md_code = md_code_from_string(command)
    if md_code == 'GROMACS':
        inputs = gromacs_utilities.complete_inputs(inputs)
    return inputs
               
def inputs_dict_to_string(inputs):
    '''
    Given a dictionary of inputs, return a command line string.
    '''
    # preamble:
    command = " ".join(p for p in inputs[-1])
    if len(command) > 0:
        command += " "

    # executable:
    command += " ".join(e for e in inputs[0])

    # positional arguments:
    max_pos_arg = 0
    for key in inputs:
        if isinstance(key, int):
            if key > max_pos_arg:
                max_pos_arg = key
    for pos_arg in range(1, max_pos_arg + 1):
        command += " " + inputs[pos_arg]

    # other arguments:
    for key in inputs:
        if not isinstance(key, int):
            command += " " + key 
            if isinstance(inputs[key], tuple): # for filepacks
                command += " " + inputs[key][0]
            elif inputs[key] is not None:
                command += " " + inputs[key]
    return command
    
def inputs_dict_to_filepack(inputs):
    '''
    Given a dictionary of inputs, returns a filepack.
    A filepack is like an inputs dictionary, except that
    where the argument to a key in inputs is the name of
    an existing file, in the filepack dictionary it is a
    (filename, contents) tuple, where contents is zlib
    compressed.
    '''
    command = inputs_dict_to_string(inputs)
    code = md_code_from_string(command)
    if code == 'GROMACS':
        input_keys = ['-s', '-cpi']
    elif code == 'NAMD':
        infiles = filenames_in_inputs_dict(inputs)
        return namd_utilities.inputs_dict_to_filepack(inputs, infiles)
    else:
        raise NotImplementedError('MD code {} is not supported'.format(code))
    filepack = inputs.copy()
    for key in filepack:
        if isinstance(filepack[key], str):
            if key in input_keys and os.path.exists(filepack[key]):
                filename = filepack[key]
                with open(filename, 'rb') as f:
                    filepack[key] = (filename, zlib.compress(f.read()))
    return filepack

def filenames_in_inputs_dict(inputs):
    '''
    Parses a dictionary of inputs and returns a list of all the filenames
    '''
    command = inputs_dict_to_string(inputs)
    code = md_code_from_string(command)
    result = []
    if code == "GROMACS":
        for key in inputs:
            if key in ['-s', '-cpi', '-o', '-cpo', '-g', '-x', '-c', '-e',
                       '-dhdl', '-field', '-table', '-tabletf', '-tablep',
                       '-rerun', '-tpi', '-tpid', '-ei', '-eo', '-devout',
                       '-runav', '-px', '-pf', '-ro', '-ra', '-rs', '-rt',
                       '-mtx', '-dn', '-multidir', '-mp', '-mn', '-if',
                       '-swap']:
                result.append(inputs[key])
        return result
    elif code == 'NAMD':
        for key in inputs:
            value = inputs[key]
            if (not isinstance(value, list)) and value[0] != '+':
                result += namd_utilities.filenames_from_config_file(inputs[key])
        return result
    else:
        raise NotImplementedError('Sorry - MD code {} not supported'.format(code))
        

def filepack_to_inputs_dict(filepack, targetdir=None):
    '''
    Given a filepack, unpacks it  and returns an inputs dictionary
    '''
    if isinstance(filepack, list):
        return namd_utilities.filepack_to_inputs_dict(filepack, targetdir=targetdir)
    inputs = filepack.copy()
    filenames = filenames_in_inputs_dict(inputs)
    for key in inputs:
        if inputs[key] in filenames:
            if isinstance(inputs[key], tuple):
                filename = inputs[key][0]
                if targetdir is not None:
                    filename = os.path.join(targetdir, os.path.basename(filename))
                with open(filename, 'wb') as f:
                    if python3:
                        if isinstance(inputs[key][1], str):
                            data = zlib.decompress(inputs[key][1].encode('utf-8'))
                        else:
                            data = zlib.decompress(inputs[key][1])
                        f.write(data)
                    else:
                        f.write(zlib.decompress(inputs[key][1]))
                inputs[key] = filename
            else:
                filename = inputs[key]
                if targetdir is not None:
                    filename = os.path.join(targetdir, os.path.basename(filename))
                inputs[key] = filename
    return inputs

def md_code_from_string(command, index=False):
    '''
    Given a command line string, identify/guess the relevant MD code.
    Returns a string, or None if it cannot identify a likely code.

    If index is not none, then the index of the identificed keyword is
    also ruturned with the code name as a (codename, index) tuple.
    '''
    code = None
    words = command.split()
    # The heuristic is that the leftmost key word takes precedence. This
    # should help to overcome pathological cases such as 
    #    'gmx mdrun -deffnm sander' 
    # being misinterpreted.
    leftmost = len(words)
    codes = {'gmx' : 'GROMACS',
            'gmx_d' : 'GROMACS',
            'sander' : 'AMBER',
            'pmemd' : 'AMBER',
            'pmemd.MPI' : 'AMBER',
            'namd2' : 'NAMD',
            'namd' : 'NAMD' }
    for key in codes:
        for word in words:
            if key in word:
                if words.index(word) < leftmost:
                    leftmost = words.index(word)
                    code = codes[key]
    if not index:
        return code
    else:
        return code, leftmost
    
    
def installed_version(code):
    '''
    Check that the required MD code is available, and if so, what version it is
    '''
    if code == 'GROMACS':
        return gromacs_utilities.gromacs_check_version()
    elif code == 'NAMD':
        return namd_utilities.namd_check_version()
    else:
        raise NotImplementedError('{} is not currently supported'.format(code))

