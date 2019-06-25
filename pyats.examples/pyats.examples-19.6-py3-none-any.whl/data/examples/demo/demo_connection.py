'''Simple Connection Code

The intention of the the code below is to demonstrate, using raw code, how to
load a device from topology YAML file, establish connection to it, and use
Tcl code to collect parser results.

You can run this script directly, but it's better to copy paste each command
into a python interpreter shell and observe/interact with the code.
'''

from pyats import tcl
from pyats.topology import loader

# create the testbed object by loading YAML
testbed = loader.load('demo_tb.yaml')

# pick a device as uut
uut = testbed.devices['ott-tb1-n7k3']

# establish connection. 
# this defaults to using Csccon class
uut.connect()

version_str = uut.execute('show version')

uut.configure('''
interface Ethernet4/1
    ip address 1.1.1.1/24
    no shutdown

interface Ethernet4/2
    ip address 1.1.1.2/24
    no shutdown
''')

# to use this device connection in tcl
tcl.q.package('require', 'router_show')
tcl.q.router_show(device = uut.handle, cmd = 'show version')
# KeyedList({'bootflash': 'unknown', 'disk0': 'unknown', 'nv_ram': 'unknown', 
#            'eboot_version': 'unknown', 'fe_intf': '0', 
#            'chassis_type': 'Nexus7000', 'ge_intf': '0', 'cpu_type': 'unknown',
#            'te_intf': '0', 'cable_intf': '0', 'pxf_status_l': KeyedList({}), 
#            'pos_intf': '0', 'phy_mem': 'unknown', 'io_mem': 'unknown', 
#            'uptime': '6 day(s), 17 hour(s), 27 minutes', 
#            'main_mem': 'unknown', 'cfgreg': 'unknown', 
#            'pxf_l': KeyedList({}), 'ios_version_num': 'unknown', 
#            'spa_card': '0', 'rommon_version': 'unknown', 'serial_intf': '0',
#            'ios_version': 'IOS compile time:       02/20/10\n', 
#            'system_image': 'unknown', 'dtcc': '0', 'tcc': '0', 
#            'jacket_card': '0'})

uut.disconnect()
