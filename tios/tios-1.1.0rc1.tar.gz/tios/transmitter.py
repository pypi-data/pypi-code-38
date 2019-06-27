'''
Tios_transmitter: runs an MD code and streams the data using the tios
protocol.

A tios transmitter can be created from a command-line style string:

    tt = from_command('gmx mdrun -deffnm test')

or from an existing entry in the tios database:

    tt = from_entry('abc123')

The simulation is launched via the start method:

    tt.start()

Being under IMD control, it is advanced to the next sampling interval
using the step method:

    tt.step()

And stopped using the stop method:

    tt.stop()

To check the simulation is still running, use the is_running method:

    alive = tt.is_running()

Once started, the standard output and standard error from the job are
available:

    print tt.stdout
    print tt.stderr

'''
from tios import utilities, communication, imd_sim

import socket
import os
import numpy as np
import time
from collections import deque

def from_entry(id, protocol='Mongo', force=False,
               targetdir='', preamble=None, extra_args=None, trate=None):
    """
    Create a Tios transmitter from an entry in the Tios database.

    Args:
        id (str): The Tios ID.
        protocol (str, optional): The connection protocol. Defaults to "Mongo".
        force (bool, optional): If True, a transmitter will be created even if
            the job appears to still be running somewhere.
        targetdir (str, optional): The directory into which files should be
            unpacked and from which the job will be launched. Defaults to the
            current directory.
        preamble (str, optional): Preamble required for the command line, e.g.
            "mpirun -n 16".
        extra_args (str, optional): Extra arguments to be appended to the
            command line, e.g. from Gromacs, "-maxh 23".
        trate (float, optional): IMD sampling interval. Defaults to whatever
            is defined in the database entry.

    Returns:
        An instance of a `TiosTransmitter`

    """
    te = communication.TiosAgent(id, protocol=protocol)
    te_const = communication.TiosAgent(id + '_const', protocol=protocol)
    te_check = communication.TiosAgent(id + '_check', protocol=protocol)
    if te.status == 'Running':
        if force:
            print('Warning: Tios job {} appears to be running already'.format(id))
        else:
            raise RuntimeError('Tios job {} is already running'.format(id))
    #if te.filepack is not None:
    #    inputs = utilities.filepack_to_inputs_dict(te.filepack, targetdir=targetdir)
    #elif te_const.filepack is not None:
    #    inputs = utilities.filepack_to_inputs_dict(te_const.filepack, targetdir=targetdir)
    #else:
    #    raise RuntimeError('Error - cannot find the files for this simulation')
    inputs = utilities.filepack_to_inputs_dict(te_const.filepack, targetdir=targetdir)
    if preamble is not None:
        inputs[-1] = preamble.split()
    if trate is None:
       trate = te.trate
    else:
       te.trate = trate
    run_command = utilities.inputs_dict_to_string(inputs)
    if extra_args is not None:
        run_command = run_command + " " + extra_args
    checkpoint = te_check.checkpoint
    imd_job = imd_sim.from_command(run_command, checkpoint=checkpoint, trate=trate)
    te.message = {'header' : None}
    te.sync()
    tes = [te, te_const, te_check]
    return TiosTransmitter(imd_job, tes)
        
class TiosTransmitter(object):
    def __init__(self, imd_sim, tios_agents):
        """
        Transmitter for an MD simulation job, as created by Tios

        Args:
            imd_sim (IMDJob): An instance of an `IMDJob`.
            tios_agents (list): A list of `TiosAgents`

        Attributes:
            id (str): Tios ID for the running job.
            status (str): Status of the running job.
            xyz (numpy array): Current coordinates [natoms, 3], in nm.
            box (numpy array): Current box dimensions, in nm/degrees.
            monitors (dict): Dictionary of energy components.
            stdout (str): Contents of STDOUT from the running job.
            stderr (str): Contents of STDERR from the running job.

        """
        self._imd_sim = imd_sim
        self._te = tios_agents[0]
        self._te_const = tios_agents[1]
        self._te_check = tios_agents[2]
        self.id = self._te.id
        self.status = imd_sim.status
        self._splitpoint = self._te.splitpoint
        self.monitors = self._te.monitors
        self.xyz = imd_sim.xyz
        self.box = imd_sim.box
        self._te.framerate = 0.0
        self._te.md_version = utilities.installed_version(self._te.md_code)
        self._te.host = socket.gethostname()
        try:
            self._te.username = os.getlogin()
        except OSError:
            self._te.username = '(unknown)'
        self._te.frame_rate = 0.0
        self._te.timepoint = imd_sim.timepoint
        self._te.status = imd_sim.status
        self._te.sync()

    def start(self):
        """
        Launch the simulation.

        """
        self._imd_sim.start()
        self.stdout = self._imd_sim.stdout
        self.stderr = self._imd_sim.stderr
        if self._imd_sim.status != 'Running':
            print(self.stdout)
            print(self.stderr)
            raise RuntimeError('Job failed prematurely')
        self._te.status = self._imd_sim.status
        self.status = self._imd_sim.status
        self._te.sync()
        self._last_step_time = time.time()

    def stop(self):
        """
        Stop the simulation.

        """
        self._imd_sim.stop()
        self._te.status = self._imd_sim.status
        self.status = self._imd_sim.status
        if self._imd_sim.new_checkpoint:
            cpt = self._imd_sim.get_checkpoint()
            self._te_check.checkpoint = cpt
            self._te_check.checkpoint_time = self._te.timepoint
        self._te.sync()
        self._te_check.sync()
        
    def step(self):
        """
        Move the simulation along to the next IMD sample point.

        """
        message = self._te.message
        if message['header'] == 'STOP':
            self.stop()
        else:
            self._imd_sim.step()
            crds = self._imd_sim.xyz
            self._te.xyzsel = crds[:self._splitpoint]
            self._te.xyzunsel = crds[self._splitpoint:]
            energies = self._imd_sim.energies
            energies['Timepoint'] = self._imd_sim.timepoint
            if 'tstep' in energies:
                del energies['tstep']
            for key in energies:
                self.monitors[key] = energies[key]
            self._te.monitors = self.monitors
            now = time.time()
            self._te.frame_rate = 60.0 / (now - self._last_step_time)
            self._last_step_time = now
            self._te.timepoint = self._imd_sim.timepoint
            self._te.status = self._imd_sim.status
            self.status = self._imd_sim.status
            if self._imd_sim.new_checkpoint:
                cpt = self._imd_sim.get_checkpoint()
                self._te_check.checkpoint = cpt
                self._te_check.checkpoint_time = self._te.timepoint
            self._te.sync()
            self._te_check.sync()

    def is_running(self):
         """
         Return True if the simulation appears to be running.

         """
         return self._imd_sim.is_running()

