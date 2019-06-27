import unittest
import shutil
import tempfile
from tios import imd_sim
import glob
import os
import time
import numpy as np
import mdtraj as mdt
import sys
import warnings

class NAMDWorkflowTest(unittest.TestCase):

    def setUp(self):
        #self.testdir = tempfile.mkdtemp()
        self.testdir = 'scratchdir'
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)
        os.mkdir(self.testdir)
        shutil.copy('test/examples/ubq_wb.conf', self.testdir)
        shutil.copy('test/examples/ubq_wb_eq.coor', self.testdir)
        shutil.copy('test/examples/ubq_wb_eq.xsc', self.testdir)
        shutil.copy('test/examples/ubq_wb.psf', self.testdir)
        shutil.copy('test/examples/ubq_wb.pdb', self.testdir)
        shutil.copy('test/examples/par_all27_prot_lipid.inp', self.testdir)
        if sys.version_info[0] > 2:
            warnings.simplefilter("ignore", ResourceWarning)

    def tearDown(self):
        #shutil.rmtree(self.testdir)
        pass

    def test_simulation_startup(self):
        command_line = 'namd2 +p4 {}/ubq_wb.conf'.format(self.testdir)
        # Attempt to start the job:
        imd_job = imd_sim.from_command(command_line)
        # Have we created an instance of an imd_sim.imd_job?
        self.assertIsInstance(imd_job, imd_sim.IMDJob)
        # Is the status 'Ready'?
        self.assertEqual(imd_job.status, 'Ready')
        self.assertEqual(imd_job.timepoint, 0.0)
        self.assertIsInstance(imd_job.xyz, np.ndarray)

    def test_simulation_start(self):
        command_line = 'namd2 +p4 {}/ubq_wb.conf'.format(self.testdir)
        imd_job = imd_sim.from_command(command_line)
        imd_job.start()
        # Check we are at timepoint 0.0:
        self.assertEqual(imd_job.timepoint, 0.0)
        # Move the simulation forward by one step. First time
        # it should only be advanced by dt:
        imd_job.step()
        self.assertEqual(imd_job.timepoint, imd_job._trate)
        # Move the simulation forward again. This time it should be trate
        # further forward:
        imd_job.step()
        self.assertEqual(imd_job.timepoint, 2 * imd_job._trate)
        # Stop the job and confirm that it appears to be so:
        imd_job.stop()
        time.sleep(3)
        self.assertFalse(imd_job.is_running())
        # A checkpoint file should have been written - has it?
        self.assertTrue(imd_job._has_checkpoint)
        self.assertTrue(imd_job.new_checkpoint)
        # Retrieve the checkpoint and test new_checkpoint again:
        cpt = imd_job.get_checkpoint()
        self.assertFalse(imd_job.new_checkpoint)
      
