'''Demonstrate AEtest Parameters Feature

This is an AEtest script intended to demonstrate the usage of parameters
feature. It can be run either in standalone, or using the "demo_job.py" jobfile.

For running as part of a jobfile, see demo_job.py.

Run this jobfile in standalone:
    
    # straightforward run (require testbed)
    bash$ python demo_params.py --testbed demo_tb.yaml --cli "show clock"

'''
from pyats import aetest, topology

# common setup, connects to testbed devices
class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connects(self, testbed):
        for device in testbed:
            device.connect()

            assert device.connected, 'device %s failed to connect' % device.name

# testcase, executes a provided cli on each device
class Testcase(aetest.Testcase):

    @aetest.test
    def run_cli(self, testbed, cli):
        for device in testbed:
            try:
                device.execute(cli)
            except:
                self.failed("failed to execute '%s' on %s" % (cli, device.name))

# common cleanup, disconnects from testbed devices
class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def disconnects(self, testbed):
        for device in testbed:
            try:
                device.disconnect()
            except:
                pass

# standalone execution
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', type = topology.loader.load)
    parser.add_argument('--cli', dest = 'cli', type = str)
    aetest.main(**vars(parser.parse_known_args()[0]))