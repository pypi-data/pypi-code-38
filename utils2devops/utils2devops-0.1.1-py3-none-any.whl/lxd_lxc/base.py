import argparse
from utils2devops.lxd_lxc import __version__

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--version', action='version', version=__version__)
group1 = parser.add_argument_group()
group1.add_argument('-e', '--endpoint', help='the endpoint if not local')
group1.add_argument('-c', '--cert', help='''
tuple of (cert, key) like ('/path/to/client.crt', '/path/to/client.key')''')
group1.add_argument('-sure', default='NO_I_AM_NOT_SURE', help='''
Required for all deleteAll* with value YES_I_AM_SURE''')

