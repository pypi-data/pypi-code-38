import unittest
from tios import receiver, transmitter, producer
import shutil
import tempfile
import numpy as np
import os

class TestTiosReceiverMethods(unittest.TestCase):

    def setUp(self):
        self.protocol = 'Mongo'
        self.testdir = 'xxxxxx'
        os.mkdir(self.testdir)
        shutil.copy('test/examples/bpti.tpr', self.testdir)
        shutil.copy('test/examples/bpti.cpt', self.testdir)

    def tearDown(self):
        shutil.rmtree(self.testdir)

    def test_initialize_new_tios_receiver_from_database(self):
        tp = producer.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   splitpoint=100,
                                   protocol=self.protocol)
        id = tp.id

        tj = transmitter.from_entry(id, protocol=self.protocol)
        tj2 = receiver.TiosReceiver(id, protocol=self.protocol)
        self.assertIsInstance(tj2, receiver.TiosReceiver)
        self.assertEqual(tj2.status, 'Ready')
        self.assertIsInstance(tj2.xyz, np.ndarray)
        self.assertEqual(len(tj2.xyz), 20521)

        tj3 = receiver.TiosReceiver(id, protocol=self.protocol, firstn=892)
        self.assertEqual(len(tj3.xyz), 892)

    def test_tios_receiver_collection(self):
        tp = producer.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   splitpoint=100,
                                   protocol=self.protocol)
        id = tp.id

        tj = transmitter.from_entry(id, protocol=self.protocol)
        tj2 = receiver.TiosReceiver(id, protocol=self.protocol)
        self.assertEqual(tj2.status, 'Ready')
        tj.start()
        self.assertEqual(tj.status, 'Running')
        tj.step()
        self.assertEqual(tj.status, 'Running')
        tj2.step()
        self.assertEqual(tj2.status, 'Running')
        tj.step()
        tj2.step()
        tj.stop()
        self.assertEqual(tj2.status, 'Stopped')
        self.assertEqual(tj.status, 'Stopped')
      
