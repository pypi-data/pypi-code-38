''' Computes acceleration and ionization on a packet due to specified forces

Gravitational acceleration

Equations of motion:
    dvxdt = sum_objects (GM * (x-x_obj))/(r_obj)^3
    dvydt = sum_objects (GM * (y-y_obj))/(r_obj)^3
    dvzdt = sum_objects (GM * (z-z_obj))/(r_obj)^3
        -- r_obj = sqrt( (x-x_obj)^2 + (y-y_obj)^2 + (z-z_obj)^2 )
    dndt = instantaneous change in density

Current version: Assumes there is only a planet -- does not do moons yet
'''

import numpy as np
from astropy.time import Time
#from .xyz_to_magcoord import xyz_to_magcoord

def State(t, x, v, output):
    # compute gravitational acceleration
    if output.inputs.forces.gravity:
        r3 = (x[0,:]**2 + x[1,:]**2 + x[2,:]**2)**1.5
        agrav = output.GM * x/r3
    else:
        agrav = np.zeros_like(x)

    # compute radiation acceleration
    arad = np.zeros_like(x)
    if output.inputs.forces.radpres:
        rho = x[0,:]**2 + x[2,:]**2
        out_of_shadow = (rho > 1) | (x[1,:] < 0)

        # radial velocity of each packet realtive to the Sun
        vv = v[1,:] + output.vrplanet

        # Compute radiation acceleration
        arad[1,:] = (np.interp(vv, output.radpres.velocity,
                               output.radpres.accel) * out_of_shadow)
    else:
        pass

    # Compute total acceleration
    accel = agrav + arad
    assert np.all(np.isfinite(accel))

    # Compute ionization rate
    if output.inputs.options.lifetime > 0:
        # Explicitly set lifetime
        ionizerate = np.ones_like(t)/output.inputs.options.lifetime.value
    else:
        if output.loss_info.photo is not None:
            # Compute photoionization rate
            rho = x[0,:]**2 + x[2,:]**2
            out_of_shadow = (rho > 1) | (x[1,:] < 0)
            photorate = output.loss_info.photo * out_of_shadow
        else:
            photorate = 0.

        '''
        magcoord = xyz_to_magcoord(t, x, output.inputs, output.planet)

        if output.loss_info.eimp:
            # Compute electron impact rate
            assert 0, 'Electron impacts not set up yet'
        else:
            eimprate = 0.

        if output.loss_info.chX:
            # Compute charge exchange rate
            assert 0, 'Charge exchange not set up yet'
        else:
            chxrate = 0.
        '''

    ionizerate = photorate  #+ eimprate + chxrate

    return accel, ionizerate
