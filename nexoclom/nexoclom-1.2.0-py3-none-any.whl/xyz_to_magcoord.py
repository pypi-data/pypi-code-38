'''
Computes the magnetic coordinates of each packet

Also determines whether the packet is in shadow
'''

import numpy as np

def xyz_to_magcoord(t, x, inputs, planet):
    if planet.object == 'Mercury':
        magcoord = None
    else:
        # Need to add magnetic coordinates for Jupiter and Saturn
        assert 0, '{} not impletmented'.format(planet)

    return magcoord
