import numpy as np
from .input_classes import AngularDist
from .source_distribution import angular_distribution

def bouncepackets(self, t1, x1, v1, f1, hhh):
    # This will need to be rewritten for satellite impacts

    # Determine where packets hit surface
    #srad = satrad[hhh]
    #r0 = tempR[hhh]
    x0 = x1[0,hhh]
    y0 = x1[1,hhh]
    z0 = x1[2,hhh]
    r0 = np.sqrt(x0**2 + y0**2 + z0**2)
    vx0 = v1[0,hhh]
    vy0 = v1[1,hhh]
    vz0 = v1[2,hhh]

    a = vx0**2 + vy0**2 + vz0**2  # = vv02
    b = 2*(x0*vx0 + y0*vy0 + z0*vz0)
    c = x0**2 + y0**2 + z0**2 - 1.
    dd = b**2 - 4*a*c
    assert np.all(dd >= 0)

    t0 = (-b - np.sqrt(b**2-4*a*c))/(2*a)
    t1 = (-b + np.sqrt(b**2-4*a*c))/(2*a)
    t = (t0 <= 0)*t0 + (t1 < 0)*t1

    # point where packet hit the surface
    x2 = x0 + vx0*t
    y2 = y0 + vy0*t
    z2 = z0 + vz0*t
    assert np.all(np.isfinite(x2))
    assert np.all(np.isfinite(y2))
    assert np.all(np.isfinite(z2))

    lonhit = (np.arctan2(x2, -y2) + 2*np.pi) % (2*np.pi)
    lathit = np.arcsin(z2)

    # put new coordinates into array
    x1[0,hhh] = x2
    x1[1,hhh] = y2
    x1[2,hhh] = z2

    # Determine rebound velocity
    #vv02 = vx0**2 + vy0**2 + vz0**2  # rplan/s
    PE = 2*self.GM*(1./r0 - 1)
    vv02 = a + PE
    vv02[vv02 < 0] = 0.
    assert np.all(np.isfinite(vv02))

    if self.inputs.sticking_info.emitfn.lower() == 'maxwellian':
        assert 0, 'Not set up yet'
        if self.inputs.sticking_info.Tsurf == 0:
            surftemp = SurfaceTemperatue(self.inputs.geometry,
                                         lonhit, lathit)
        else:
            pass # Need to set this up to
    elif self.inputs.sticking_info.emitfn.lower() == 'elastic scattering':
        vv2 = np.sqrt(vv02)
    else:
        assert 0, 'Emit function not set up yet'

    # Determine rebound angle

    angdist = AngularDist({'type':'costheta',
                           'altitude':f'0,{np.pi/2}',
                           'azimuth':f'0,{2*np.pi}'}, None)
#    angdist = AngularDist({'type':'radial'}, None)
    VV = angular_distribution(angdist, x1[:,hhh], vv2)

    # Rotate to proper position
    # to do

    # Put back into the arrays
    v1[:,hhh] = VV

    # Adjust the fractional values
    if self.inputs.sticking_info.stickcoef > 0:
        f1[hhh] *= 1 - self.inputs.sticking_info.stickcoef
    else:
        assert 0
