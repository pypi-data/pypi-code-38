'''
Tios_receiver complements tios_transmitter.

A tios receiver is initialised with a tios job ID:

    tr = tios.receiver('abc123')

It collects a new frame of data every time the step() method is called:

    tr.step()

To see if the simulation is still running, use the is_running method:

    alive = tr.is_running()

NOTE: tr.step() does not return with an error if the simulation is stopped - it
just waits until it starts again.

The recent history of certain simulation metrics - e.g. temperature, 
potential energy, are available via the monitors dictionary attribute. Each 
key is associated with a list that grows as frames are read. The available 
keys are: 'Timepoint', 'T', 'Etot', 'Epot', 'Evdw', 'Eelec', 'Ebond', 'Eangle',
'Edihe', 'Eimpr', 'RMSD'.

    rmsd_history = tr.monitors['RMSD']

'''
from tios import communication

import numpy as np
import time
import tempfile
import os

class TiosReceiver(object):
    def __init__(self, id, protocol='Mongo', firstn=None):
        """
        Create a new receiver.

        Args:
            id (str): ID of the Tios job.
            protocol (str, optional): Communication protocol to use.
            firstn (int, optional): only include the first *firstn* atoms.

        Attributes:
            pdbfile(str): A pdb file for the selected atoms.
            xyz ([natoms, 3] np.array): current coordinates.
            box ([3,3] np.array): box vectors.
            monitors (dict): Dictionary of simulation metrics (energies, etc.).
            timepoint (float): Age of the simulation, in picoseconds.

        """
        self._te = communication.TiosAgent(id, protocol=protocol)
        self._te_const = communication.TiosAgent(id + '_const', protocol=protocol)
        pdb = self._te_const.pdb
        xyz = self._te.xyzsel
        self._splitpoint = len(xyz)
        if firstn is None:
            self._use_unsel = True
        else:
            firstn = int(firstn)
            self._use_unsel =  firstn > self._splitpoint
        if self._use_unsel:
            xyz = np.vstack((xyz, self._te.xyzunsel))
        if firstn is None:
            firstn = len(xyz)
        npl = 0
        if firstn == len(xyz):
            self.pdb = pdb
        else:
            self.pdb = ''
            plines = pdb.split('\n')
            ip1 = 0
            np1 = 0
            while np1 < firstn:
                if 'ATOM' in plines[ip1][:4] or 'HETATM' in plines[ip1][:6]:
                    np1 +=1
                    if np1 <= firstn:
                        self.pdb += plines[ip1]
                        self.pdb += '\n'
                        np1 += 1
                ip1 += 1
        self.xyz = xyz[:firstn]
        self.box = self._te.box
        self.monitors = self._te.monitors
        self.timepoint = self._te.timepoint
        self._firstn = firstn

    @property
    def status(self):
        """
        str: Current status of simulation.

        """
        return self._te.status

    def step(self, wait=True, killer=None):
        """
        Collect the next timestep of data from the simulation.

        Args:
            wait (bool, optional): If True, if the simulation is Stopped, wait
                for it to update. Otherwise return immediately.e
            killer (GracefulKiller, optional): hook to trap ctrl-C, etc.

        """
        newtimepoint = self.timepoint
        while newtimepoint == self.timepoint:
            if killer is not None:
                if killer.kill_now:
                    return
            if self.status != 'Running':
                if wait:
                    interval = 30
                else:
                    return
            else:
                if self._te.frame_rate == 0:
                    interval = 2.0
                else:
                    interval = max(2.0, 30.0 / self._te.frame_rate)
            time.sleep(interval)
            newtimepoint = self._te.timepoint
        self.timepoint = newtimepoint
        xyz = self._te.xyzsel
        if self._use_unsel:
            xyz = np.vstack((xyz, self._te.xyzunsel))
        self.xyz = xyz[:self._firstn]
        self.monitors = self._te.monitors

    def is_running(self):
        """
        Return True if the simulation appears to be running.

        """
        return self.status == 'Running'
