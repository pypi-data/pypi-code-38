
import random

"""
definitions to aid DFT (Design For Testability)
"""

account_name = 'jamesabel'
project_name = 'osnaptest'

dft_local_host = 'http://localhost'

# pick some random ephemeral ports on which to emulate the servers
if True:
    http_port_base = 55015  # statically define the port numbers so the app can use them
else:
    http_port_base = random.randrange(49152, 65535)  # execute this once to get a random base port

dft_download_http_emulation = (http_port_base, '%s/%s/raw/master' % (account_name, project_name))
dft_tags_http_emulation = (http_port_base + 1, 'repos/%s/%s/tags' % (account_name, project_name))
dft_hash_and_size_http_emulation = (http_port_base + 2, '%s/%s/master' % (account_name, project_name))
