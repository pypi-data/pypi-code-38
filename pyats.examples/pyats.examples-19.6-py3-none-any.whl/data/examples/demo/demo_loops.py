'''Demo Looping Feature

This is an AEtest script file intended to demonstrate how looping feature works.

The following sections within this script is looped:

    - Testcase: looped once per device input, dynamically marked for looping
                within common_setup.connects subsection
    - Testcase.run_cli: looped once per cli defined as part of loop decorator.

Run this testscript in standalone:
    
    # single device
    bash$ python demo_loops.py --testbed demo_tb.yaml

    # multiple devices
    bash$ python demo_loops.py --testbed demo_tb_topology.yaml

'''

from pyats import aetest, topology

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connects(self, testbed):
        for device in testbed:
            device.connect()

        # mark testcase for looping
        aetest.loop.mark(Testcase, 
                         uids=['Testcase(uut=%s)' % i for i in testbed.devices],
                         device = testbed.devices.values())

# dynamically looped testcase
class Testcase(aetest.Testcase):

    # static looped test
    @aetest.test.loop(cli = ['show routing', 'show vdc', 'show module'])
    def run_cli(self, device, cli):
        try:
            device.execute(cli)
        except:
            self.failed("failed to execute '%s' on %s" % (cli, device.name))

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
    aetest.main(**vars(parser.parse_known_args()[0]))

