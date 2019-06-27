'''
A simple and generic control interface for MD simulation jobs under IMD control.

An instance of a simulation job is created from a string of the sort that
might have been a command line, e.g.:

    sim = from_command('gmx mdrun -deffnm test')

An exception will be raised if the job is not a valid IMD job.

The simulation is started only when the start method is called:

    sim.start()

The status of the simulation can be checked using the is_running method:

    is_running = (sim.is_running() == True)

The simulation is advanced to the next IMD timestep by the step method:

    sim.step()

The IMD sample interval can be changed during a simulation:

    sim.set_trate(trate)

The simulation can be stopped using the stop method:

    sim.stop()

Once stopped, the standard output and standard error from the job are
available:

    print sim.stdout
    print sim.stderr

A pdb file corresponding to the system is available as a string object:

    pdbfile = sim.pdb

The current coordinates and box parameters are available:

    coordinates = sim.xyz
    box = sim.box

The current energy components, etc. are available in the energies attribute 
(a dictionary). The contents of this are defined by the IMD protocol, the
keys are: 'tstep', 'T', 'Etot', 'Epot', 'Evdw', 'Eelec', 'Ebond', 'Eangle', 
'Edihe', 'Eimpr'.

Note that sim.energies['tstep'] returns the current timestep number; the
'age' of the simulation, in picoseconds, is available in the 'timepoint' attribute:

    age = sim.timepoint

The underlying MD code may feature checkpointing. If so, then the attribute
new_checkpoint will be True if an updated checkpoint is available. It is
returned by the get_checkpoint() method, which then resets new_checkpoint to
False. Exactly what is returned by get_checkpoint() is MD-code dependent, but 
the contents can be passed back to a new instatiation of the run as an
optional argument:

    if sim.has_checkpoint:
        new_chk = sim.get_checkpoint()
    sim.stop()
    ...
    restarted_sim = from_command('gmx mdrun -deffnm test', checkpoint=new_chk)

'''
from tios import utilities, gromacs_utilities, namd_utilities, imd

import os
import subprocess
import time
import glob
import socket
import zlib
import numpy as np

def from_command(command_line, checkpoint=None, trate=1.0):
    """
    Create an instance of an IMDJob from a command line.

    Optional extra (code-specific) checkpoint data can be provided. The IMD 
    sampling rate can also be set.

    Args:
        command_line (str): A command line that would run the job interactively.
        checkpoint: optional checkpoint data of code-specific type.
        trate (float, optional): IMD sampling inteval (in picoseconds).

    Returns:
        IMDJob: An instance of an IMD-controlled MD job.

    Raises:
        NotImplementedError: If the MD code is not supported.

    """
    md_code = utilities.md_code_from_string(command_line)
    version = utilities.installed_version(md_code)
    if version is not None:
        if md_code == 'GROMACS':
            return GromacsIMDJob(command_line, checkpoint=checkpoint, trate=trate)
        elif md_code == 'NAMD':
            return NAMDIMDJob(command_line, checkpoint=checkpoint, trate=trate)
        else:
            raise NotImplementedError('Error - this is a {} job but this code is currently not supported by tios.'.format(md_code))
    else:
        raise NotImplementedError('Error - this is a {} job but this code is not available on this resource'.format(md_code))

class IMDJob(object):
    '''
    Base class for IMD-controlled MD jobs.
    MD-code specific subclasses are based on this.
    '''
    def __init__(self, command_line, checkpoint=None, trate=1.0):
        """
        Initialises a new IMD controlled simulation job. 

    Args:
        command_line (str): A command line that would run the job interactively.
        checkpoint: optional checkpoint data of code-specific type.
        trate (float, optional): IMD sampling inteval (in picoseconds).

    Attributes:
        status (str): Status of the simulation.
        timepoint (float): Age of the simulation.
        pdb (str): PDB format version of the system
        xyz (numpy array): Current coordinates (nanometers)
        box (numpy array): Periodic box parameters.
        energies (dict): IMD energy components.
        stdout (str): Contents of STDOUT from running job.
        stderr (str): Contents of STDERR from running job.
        new_checkpoint (bool): True if a new checkpoint file is available.

        """

        self.status = "Unknown" 
        self.pdb = None
        self.xyz = None
        self.box = None
        self.energies = None 
        self.timepoint = 0.0 
        self._timechecked = False
        self.trate = trate
        self._stdout = open('STDOUT', 'wb')
        self.stdout = ""
        self.stderr = ""
        self.new_checkpoint = False
        self._subprocess = None # subprocess running MD code
        self._socket = None # socket being used by IMD protocol
        self._dt = 0.001 # simulation timestep

    def __del__(self):
        try:
            self._stdout.flush()
            self._stdout.close()
            imd.imd_kill(self._socket)
            self._socket.close()
            self._subprocess.kill()
        except:
            pass

    def start(self):
        """
        Launch the job.
        """
        raise NotImplementedError

    def is_running(self):
        """
        Returns True if the simulation appears to be running.
        """
        try:
            self._stdout.flush()
        except:
            pass
        self._subprocess.poll()
        if self._subprocess.returncode is None:
            self.status = 'Running'
            return True
        else:
            self.status = 'Stopped'
            stdout, stderr = self._subprocess.communicate()
            if stdout is not None:
                self.stdout += stdout.decode()
            if stderr is not None:
                self.stderr += stderr.decode()
        return False

    def stop(self):
        """
        Stops the IMD simulation.
        """
        if not self._stdout.closed:
            self._stdout.flush()
            self._stdout.close()
        imd.imd_kill(self._socket)
        self._socket.close()
        try:
            self._subprocess.wait(timeout=10)
        except subprocess.TimeoutExpired:
            try:
                self._subprocess.terminate()
            except OSError:
                pass
        self.status = 'Stopped'
        time.sleep(2)
        self._update_checkpoint()

    def step(self):
        """
        Move the IMD simulation forward to the next data collection timepoint.

        Also updates the current data attributes.
        """
        self._stdout.flush()
        new_data = False
        while not new_data:
            typ, length = imd.imd_recv_header(self._socket)
        
            if typ == imd.IMD_ENERGIES:
                self.energies = imd.imd_recv_energies(self._socket)
                self._timechecked = True
                self.timepoint = self.energies['tstep'] * self._dt
            elif typ == imd.IMD_FCOORDS:
                n_coords = length
                coords = imd.imd_recv_fcoords(self._socket, n_coords) 
                self.xyz = np.array(coords).reshape((-1, 3)) * 0.1
                if not self._timechecked:
                    self.timepoint += self._trate
                else:
                    self._timechecked = False
                new_data = True
        self._update_checkpoint()

    def _update_checkpoint(self):
        """
        Ensure the latest checkpoint data is available for get_checkpoint()

        if successful, sets the new_checkpoint attribute to True
        """
        raise NotImplementedError

    def get_checkpoint(self):
        """
        Return the latest checkpoint data.

        This can be in what ever format suits the _apply_checkpoint() method.
        Once called, sets the new_checkpoint attribute to False.
        """
        raise NotImplementedError
 
class GromacsIMDJob(IMDJob):
    def __init__(self, command_line, checkpoint=None, trate=1.0):

        inputs = utilities.string_to_inputs_dict(command_line)
        inputs = gromacs_utilities.complete_inputs(inputs)
        inputs = gromacs_utilities.complete_inputs_for_imd(inputs)

        self._has_checkpoint = False
        self.new_checkpoint = False
        self._last_checkpoint_time = time.time()
        self.stdout = ''
        self.stderr = ''
        self.logfile = 'STDOUT'
        self._stdout = open(self.logfile, 'wb')
        self.timepoint = 0.0

        if checkpoint is not None:
            inputs = gromacs_utilities.apply_checkpoint(inputs, checkpoint)
        if '-s' in inputs:
            tpr_file = inputs['-s']
        else:
            self.stderr += 'Error: cannot identify the GROMACS tpr file for this job\n'
            self.status='Failed'
            raise RuntimeError('Error: cannot identify the GROMACS tpr file for this job')
        if not gromacs_utilities.tpr_file_valid_for_imd(tpr_file):
            self.stderr += 'Error: {} does not define a valid IMD job\n'.format(tpr_file)
            self.status='Failed'
            raise RuntimeError('Error: {} does not define a valid IMD job\n'.format(tpr_file))

        self._dt = gromacs_utilities.dt_from_tpr_file(tpr_file)
        self._trate = trate
        if '-cpi' in inputs:
            step = gromacs_utilities.step_from_checkpoint_file(inputs['-cpi'])
            if step is not None:
                self.timepoint = step * self._dt

        self.pdb = gromacs_utilities.pdb_from_tpr_file(tpr_file)
        self.xyz = gromacs_utilities.coordinates_from_tpr_file(tpr_file)
        self.box = gromacs_utilities.box_from_tpr_file(tpr_file)
        self._inputs = inputs
        self.status = 'Ready'

    def _update_checkpoint(self):
        try:
            self._stdout.flush()
        except:
            pass
        if os.path.exists(self._inputs['-cpo']):
            self._has_checkpoint = True
            self._checkpoint_mtime = os.path.getmtime(self._inputs['-cpo'])
            if self._last_checkpoint_time < self._checkpoint_mtime:
                self.new_checkpoint = True
                self._last_checkpoint_time = self._checkpoint_mtime

    def get_checkpoint(self):
        try:
            self._stdout.flush()
        except:
            pass
        if self._has_checkpoint:
            with open(self._inputs['-cpo'], 'rb') as f:
                result = zlib.compress(f.read())
            self.new_checkpoint = False
            return result

    def start(self):
        try:
            command = utilities.inputs_dict_to_string(self._inputs)
            self._subprocess = subprocess.Popen(command.split(),
                                        stderr=subprocess.STDOUT,
                                        stdout=self._stdout)
        except OSError as e:
            self.status = 'Failed'
            self.stderr += e.strerror
            raise
        time.sleep(5)

        if not self.is_running():
            self.stdout += "Job terminated prematurely\n"
            self.status = 'Failed'
            raise RuntimeError(self.stdout)

        self._port = int(self._inputs['-imdport'])
        time.sleep(5)
        self._stdout.flush()
        '''
        f = open(self.logfile, 'rb')
        output = f.readline()
        while not b'Listening' in output or b'Fatal' in output:
            self._stdout.flush()
            if self.is_running():
                output = f.readline()
                self.stdout += output.decode()
            else:
                raise RuntimeError('Error - job failed - check log file {}\n'.format(logfile))
        if b'Fatal' in output:
            self.stop()
            raise RuntimeError('Error - job failed - check log file {}.log\n'.format(logfile))
        f.close()
        words = output.split()
        indx = words.index(b'Listening')
        self._port = int(words[indx + 6][:-1])
        '''
        logfile = self._inputs['-g']
        logroot = os.path.splitext(logfile)[0]
        real_logfiles = glob.glob(logroot + '*.log')
        if len(real_logfiles) == 0:
            raise RuntimeError('Cannot find a logfile like {}*.log'.format(logroot))
        self._inputs['-g'] = real_logfiles[-1]
        logfile = real_logfiles[-1]

        with open(logfile, 'r') as f:
            output = f.readline()
            while not 'Host:' in output:
                output = f.readline()
        words = output.split()
        indx = words.index('Host:')
        self._hostname = words[indx + 1]
        #self._hostname = 'localhost'
        try:
            self._socket = imd.imd_connect(self._hostname, self._port)
        except socket.gaierror:
            self._hostname = 'localhost'
        except socket.error:
            self._hostname = 'localhost'
        self._socket = imd.imd_connect(self._hostname, self._port)
        imdcheck = imd.imd_recv_handshake(self._socket)
        if imdcheck == -1:
            self.stop()
            raise RuntimeError('Error: IMD handshake failed')
        elif imdcheck == 1:
            self.stop()
            raise RuntimeError('Error: IMD handshake detects endianness problem')
            return
            
        imd.imd_trate(self._socket, self._trate/self._dt)
        self.status = 'Running'

class NAMDIMDJob(IMDJob):
    def __init__(self, command_line, checkpoint=None, trate=1.0):

        inputs = utilities.string_to_inputs_dict(command_line)

        self._has_checkpoint = False
        self.new_checkpoint = False
        self._last_checkpoint_time = time.time()
        self.stdout = ''
        self.stderr = ''
        self.logfile = 'STDOUT'
        self._stdout = open(self.logfile, 'wb')
        self.timepoint = 0.0

        if checkpoint is not None:
            inputs = namd_utilities.apply_checkpoint(inputs, checkpoint)
        configfile = namd_utilities.config_file_name(inputs)
        if not namd_utilities.config_file_valid_for_imd(configfile):
            self.stderr += 'Error: {} does not define a valid IMD job\n'.format(configfile)
            self.status='Failed'
            raise RuntimeError('Error: {} does not define a valid IMD job\n'.format(configfile))

        self._dt = namd_utilities.dt_from_config_file(configfile)
        #self._trate = namd_utilities.trate_from_config_file(configfile) * self._dt
        self._trate = trate
        step = namd_utilities.step_from_config_file(configfile)
        if step is not None:
            self.timepoint = step * self._dt

        self.pdb = namd_utilities.pdb_from_config_file(configfile)
        self.xyz = namd_utilities.coordinates_from_config_file(configfile)
        self.box = namd_utilities.box_from_config_file(configfile)
        self._inputs = inputs
        self._configfile = configfile
        self.status = 'Ready'

    def _update_checkpoint(self):
        xscfile = namd_utilities.restart_file_basename(self._configfile) + '.xsc'
        try:
            self._stdout.flush()
        except:
            pass
        if os.path.exists(xscfile):
            self._has_checkpoint = True
            self._checkpoint_mtime = os.path.getmtime(xscfile)
            if self._last_checkpoint_time < self._checkpoint_mtime:
                self.new_checkpoint = True
                self._last_checkpoint_time = self._checkpoint_mtime

    def get_checkpoint(self):
        try:
            self._stdout.flush()
        except:
            pass
        result = {}
        if self._has_checkpoint:
            basename = namd_utilities.restart_file_basename(self._configfile)
            for ext in ['.coor', '.vel', '.xsc']:
                with open(basename + ext, 'rb') as f:
                    result[basename + ext] = zlib.compress(f.read())
            self.new_checkpoint = False
        return result

    def start(self):
        try:
            command = utilities.inputs_dict_to_string(self._inputs)
            self._subprocess = subprocess.Popen(command.split(),
                                        stderr=subprocess.STDOUT,
                                        stdout=self._stdout)
        except OSError as e:
            self.status = 'Failed'
            self.stderr += e.strerror
            raise
        time.sleep(5)

        if not self.is_running():
            self.stdout += "Job terminated prematurely\n"
            self.status = 'Failed'
            raise RuntimeError(self.stdout)

        f = open(self.logfile, 'r')
        output = f.readline()
        while not 'Info: 1 NAMD' in output or 'Fatal' in output:
            if self.is_running():
                output = f.readline()
                self.stdout += output
            else:
                raise RuntimeError('Error - job failed - check log file {}\n'.format(self.logfile))
        if 'Fatal' in output:
            self.stop()
            raise RuntimeError('Error - job failed')
        words = output.split()
        self._hostname = words[6]

        while not 'listening' in output or 'Fatal' in output:
            if self.is_running():
                output = f.readline()
                self.stdout += output
            else:
                raise RuntimeError('Error - job failed')
        if 'Fatal' in output:
            self.stop()
            raise RuntimeError('Error - job failed')
        words = output.split()
        indx = words.index('listening')
        self._port = int(words[indx + 3][:-1])

        try:
            self._socket = imd.imd_connect(self._hostname, self._port)
        except socket.gaierror:
            self._hostname = 'localhost'
        self._socket = imd.imd_connect(self._hostname, self._port)
        imdcheck = imd.imd_recv_handshake(self._socket)
        if imdcheck == -1:
            self.stop()
            raise RuntimeError('Error: IMD handshake failed')
        elif imdcheck == 1:
            self.stop()
            raise RuntimeError('Error: IMD handshake detects endianness problem')
            return
            
        imd.imd_trate(self._socket, self._trate/self._dt)
        self.status = 'Running'
        f.close()
