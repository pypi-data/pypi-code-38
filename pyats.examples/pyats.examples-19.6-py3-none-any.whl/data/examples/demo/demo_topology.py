'''Simple Topology Code

The intention of the the code below is to demonstrate, using raw code, how to
use the topology functionality of pyATS, how to interact with topology device
objects & etc.

You can run this script directly, but it's better to copy paste each command
into a python interpreter shell and observe/interact with the code.
'''

from pyats.topology import loader

testbed = loader.load('demo_tb_topology.yaml')

import pdb; pdb.set_trace()

# hostname + alias support
'ott-tb1-n7k3' in testbed and 'ott-tb1-n7k4' in testbed
'uut-1' in testbed and 'uut-2' in testbed
# True

testbed.devices
# AttrDict({'ott-tb1-n7k4': <Device ott-tb1-n7k3 at 0xf77190cc>,
#           'ott-tb1-n7k3': <Device ott-tb1-n7k4 at 0xf744e16c>})

# grab both device (by name or alias)
uut1 = testbed.devices['uut-1']
uut2 = testbed.devices['uut-2']

# check testbed links
testbed.links
# {<Link link-2 at 0xf76a6dcc>,
#  <Link link-1 at 0xf7683b6c>}

# grab an interface
intf = uut1.interfaces['Ethernet4/1']

# the entire topology is chained by attributes
intf.link.interfaces
# WeakList([<Interface Ethernet4/1 at 0xf744eeac>,
#           <Interface Ethernet3/1 at 0xf744d74c>])
intf.link.interfaces[1].device
# <Device ott-tb1-n7k5 at 0xf744e16c>
intf.link.interfaces[1].device.testbed
# <pyats.topology.testbed.Testbed object at 0xf76b5f0c>
intf.link.interfaces[1].device is uut1
# True

# and all properties are computed on the fly
uut1.find_links(uut2)
# {<Link link-1 at 0xf744ee8c>,
#  <Link link-2 at 0xf744efac>}
