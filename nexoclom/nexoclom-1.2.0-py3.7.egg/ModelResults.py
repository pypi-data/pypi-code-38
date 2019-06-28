import numpy as np
import astropy.units as u
from atomicdataMB import gValue
import mathMB


class ModelResult:
    def __init__(self, inputs):
        # Determine model scaling
        self.inputs = inputs
        self.filenames, self.packets, self.totalsource = inputs.findpackets()
        self.mod_rate = self.totalsource/inputs.options.endtime # pack/sec
        self.atoms_per_packet = (1e26/u.s)/self.mod_rate
        print(f'Total number of packets run = {self.packets}')
        print(f'Total source = {self.totalsource} packets')
        print(f'1 packet represents {self.atoms_per_packet} atoms')
        print(f'Model rate = {self.mod_rate} packets/sec')

def read_format(formatfile):
    format_ = {}
    with open(formatfile, 'r') as f:
        for line in f:
            try:
                p, v = line.split('=')
                format_[p.strip().lower()] = v.strip()
            except:
                pass
    return format_


def results_loadfile(filename):
    ''' Load the output and do some error checking

    It may be necessary at some point to add more functionality to this'''

    from .Output import Output

    # Load output
    output = Output.restore(filename)

    # Error checking
    try:
        output.x.unit
    except:
        assert 0, 'Output does not contain units like it should.'
    assert np.all(output.frac >= 0), 'Has f < 0'
    assert np.all(np.isfinite(output.frac)), 'Has non-finite f'

    # # Transform to moon-centric frame if necessary
    # if result.origin != result.inputs.geometry.planet:
    #     assert 0, 'Need to do transformation for a moon.'
    # else:
    #     origin = np.array([0., 0., 0.])*output.x.unit
    #     sc = 1.

    # Choose which packets to use
    # touse = output.frac >= 0 if keepall else output.frac > 0

    # packet positions relative to origin -- not rotated
    # pts_sun = np.array((output.x[touse]-origin[0],
    #                     output.y[touse]-origin[1],
    #                     output.z[touse]-origin[2]))*output.x.unit
    #
    # # Velocities relative to sun
    # vels_sun = np.array((output.vx[touse],
    #                      output.vy[touse],
    #                      output.vz[touse]))*output.vx.unit

    # Fractional content
    # frac = output.frac[touse]

    return output #, pts_sun, vels_sun, frac

def results_packet_weighting(result, radvel_sun, frac, out_of_shadow, aplanet):
    if result.quantity == 'column':
        weight = frac #* result.atoms_per_packet
    elif result.quantity == 'density':
        weight = frac #* result.atoms_per_packet
    elif result.quantity == 'radiance':
        if 'resscat' in result.mechanism:
            gg = np.zeros_like(frac)/u.s
            for w in result.wavelength:
                gval = gValue(result.inputs.options.atom, w, aplanet)
                gg += mathMB.interpu(radvel_sun, gval.velocity, gval.g)

            #weight_resscat = frac*result.atoms_per_packet*out_of_shadow*gg/1e6
            weight_resscat = frac*out_of_shadow*gg/1e6
        weight = weight_resscat # + other stuff

    assert np.all(np.isfinite(weight)), 'Non-finite weights'
    return weight
