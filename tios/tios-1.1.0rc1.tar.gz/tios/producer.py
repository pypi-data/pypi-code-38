'''
Tios_producer: Creates a tios job from a command line style  string.

    tp = from_command('gmx mdrun -deffnm test')

'''
from tios import utilities, communication, imd_sim

import socket
import os
import numpy as np
import time
from collections import deque
import tempfile

def from_command(command, title='', splitpoint=None, trate=1.0, 
                 deque_length=50, protocol='Mongo'):
    """
    Create a Tios producer from a command line string.

    Args:
        command (str): command-line like string.
        title (str, optional): Descriptive title for the job.
        splitpoint (int, optional): Atoms up to the last defined here 
            are stored separately in the database
            from the rest, potentially reducing data transfer to the receiver.
        trate (float, optional): The IMD sampling interval in picoseconds.
            Defaults to 1ps.
        deque_length (int, optional): Length of data timeseries to retain.
            Defaults to 50.
        protocol (str, optional): Communication protocol to use. Defaults to
            "Mongo".

    Returns:
        An instance of a `TiosProducer`
    """
    imd_job = imd_sim.from_command(command)
    id = utilities.id_generator()
    is_duplicate = True
    while is_duplicate:
        try:
            te = communication.TiosAgent(id, protocol=protocol, new=True)
            is_duplicate = False
        except ValueError:
            id = utilities.id_generator()
    id_const = id + '_const'
    id_check = id + "_check"
    te_const = communication.TiosAgent(id_const, protocol=protocol, new=True)
    te_check = communication.TiosAgent(id_check, protocol=protocol, new=True)
    te.title = title
    te.trate = trate
    te.message = {'header' : None}
    te.md_code = utilities.md_code_from_string(command)
    inputs = utilities.string_to_inputs_dict(command)
    te_const.filepack = utilities.inputs_dict_to_filepack(inputs)
    te_const.pdb = imd_job.pdb
    te_const.sync()
    te_check.checkpoint = None
    te_check.sync()
    xyz = imd_job.xyz

    if splitpoint is None:
        splitpoint = len(xyz) // 2
    te.xyzsel = xyz[:splitpoint]
    te.xyzunsel = xyz[splitpoint:]
    monitors = {}
    for key in ['Timepoint', 'T', 'Etot', 'Epot', 'Evdw', 'Eelec', 'Ebond', 
                'Eangle', 'Edihe', 'Eimpr', 'RMSD']:
        monitors[key] = None
    te.splitpoint = splitpoint
    te.monitors = monitors
    #te.inspect()
    te.sync()
    tes = [te, te_const, te_check]
    return TiosProducer(imd_job, tes)

class TiosProducer(object):
    def __init__(self, imd_sim, tios_agents):
        """
        Producer for an MD simulation job, as created by Tios

        Args:
            imd_sim (IMDJob): An instance of an `IMDJob`.
            tios_agents (list): A list of `TiosAgents`

        Attributes:
            id (str): Tios ID for the job.
            status (str): Status of the job.
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
