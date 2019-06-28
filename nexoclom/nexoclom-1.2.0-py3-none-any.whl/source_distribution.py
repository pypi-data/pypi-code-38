import os, os.path
import numpy as np
import pickle
import astropy.units as u
import astropy.constants as const
import mathMB
from atomicdataMB import atomicmass


def gaussiandist(velocity, vprob, sigma):
    f_v = np.exp(-(velocity-vprob)**2/2./sigma**2)
    f_v /= np.max(f_v)
    return f_v


def sputdist(velocity, U, alpha, beta, atom):
    matom = atomicmass(atom)
    v_b = np.sqrt(2*U/matom)
    v_b = v_b.to(u.km/u.s)
    f_v = velocity**(2*beta+1) / (velocity**2 + v_b**2)**alpha
    f_v /= np.max(f_v)
    return f_v


def MaxwellianDist(velocity, temperature, atom):
    vth2 = 2*temperature*const.k_B/atomicmass(atom)
    vth2 = vth2.to(u.km**2/u.s**2)
    f_v = velocity**3 * np.exp(-velocity**2/vth2)
    f_v /= np.max(f_v)
    return f_v


def xyz_from_lonlat(lon, lat, isplan, unit, exobase):
    if isplan:
        # Starting at a planet
        # 0 deg longitude = subsolar pt. = (0, -1, 0)
        # 90 deg longitude = dusk pt. = (1, 0, 0)
        # 270 deg longitude = dawn pt. = (-1, 0, 0)
        x0 = exobase * np.sin(lon) * np.cos(lat)
        y0 = -exobase * np.cos(lon) * np.cos(lat)
        z0 = exobase * np.sin(lat)
    else:
        # Starting at a satellite
        # 0 deg longitude = sub-planet pt. = (0, -1, 0)
        # 90 deg longitude = leading pt. = (-1, 0, 0)
        # 270 deg longitude = trailing pt. = (1, 0, 0)
        x0 = -exobase * np.sin(lon) * np.cos(lat)
        y0 = -exobase * np.cos(lon) * np.cos(lat)
        z0 = exobase * np.sin(lat)

    X0 = np.array([x0, y0, z0])*unit

    # Error checking
    assert np.all(np.isfinite(X0)), 'Non-Finite values of X0'
    return X0


def surface_distribution(inputs, npack, unit):
    '''
    Distribution packets on a sphere with radius r = SpatialDist.exobase

    Returns (x0, y0, z0, lon0, lat0)
    for satellites, assumes satellite is at phi=0

    Testing notes:
    1) Basic function with lon = [0,360], lat = [-90,90]
    2) Spatial map given
    3) Longitude, latitude range
    3) Longitude, latitude range, lon1 > lon0
    '''

    SpatialDist = inputs.spatialdist
    if SpatialDist.use_map:
        # Choose lon, lat based on predetermined map
        if SpatialDist.mapfile.endswith('.pkl'):
            with open(SpatialDist.mapfile, 'rb') as mapfile:
                sourcemap = pickle.load(mapfile)
        elif SpatialDist.mapfile.endswith('.sav'):
            from scipy.io import readsav
            sourcemap_ = readsav(SpatialDist.mapfile)['sourcemap']
            sourcemap = {'longitude':sourcemap_['longitude'][0]*u.rad,
                         'latitude':sourcemap_['latitude'][0]*u.rad,
                         'map':sourcemap_['map'][0].transpose()}
        else:
            assert 0, 'Mapfile is the wrong format.'

        lon, lat = mathMB.random_deviates_2d(sourcemap['map'],
                                           sourcemap['longitude'],
                                           np.sin(sourcemap['latitude']),
                                           npack)
        lat = np.arcsin(lat)
    else:
        # Choose the latitude: f(lat) = cos(lat)
        lat0 = SpatialDist.latitude
        if lat0[0] == lat0[1]:
            lat = np.zeros(npack)+lat0[0]
        else:
            ll = (np.sin(lat0[0]), np.sin(lat0[1]))
            sinlat = ll[0] + (ll[1]-ll[0]) * np.random.rand(npack)
            lat = np.arcsin(sinlat)

        # Choose the longitude: f(lon) = 1/(lonmax-lonmin)
        lon0 = SpatialDist.longitude
        if lon0[0] > lon0[1]:
            lon0 = [lon0[0], lon0[1]+2*np.pi*u.rad]
        lon = ((lon0[0] + (lon0[1]-lon0[0]) * np.random.rand(npack)) %
                (2*np.pi*u.rad))

    X0 = xyz_from_lonlat(lon, lat, inputs.geometry.planet.type == 'Planet',
                         unit, SpatialDist.exobase)
    return X0, lon, lat

def surface_spot(inputs, npackets, unit):
    '''Create a spot that drops off exponentially from (lon0, lat0)'''

    lon0, sigma = inputs.spatialdist.longitude
    lat0, _ = inputs.spatialdist.latitude

    spot0 = (np.sin(lon0)*np.cos(lat0),
             -np.cos(lon0)*np.cos(lat0),
             np.sin(lat0))
    longitude = np.linspace(0, 2*np.pi, 361)*u.rad
    latitude = np.linspace(-np.pi/2, np.pi/2, 181)*u.rad

    ptsx = np.outer(np.sin(longitude), np.cos(latitude))
    ptsy = -np.outer(np.cos(longitude), np.cos(latitude))
    ptsz = -np.outer(np.ones_like(longitude), np.sin(latitude))

    cosphi = ptsx*spot0[0] + ptsy*spot0[1] + ptsz*spot0[2]
    cosphi[cosphi > 1] = 1
    cosphi[cosphi < -1] = -1
    phi = np.arccos(cosphi)
    sourcemap = np.exp(-phi/sigma)

    lon, lat = mathMB.random_deviates_2d(sourcemap, longitude,
                                         np.sin(latitude), npackets)
    lat = np.arcsin(lat)

    X0 = xyz_from_lonlat(lon, lat, inputs.geometry.planet.type == 'Planet',
                         unit, inputs.spatialdist.exobase)

    return X0, lon, lat


def idlversion(inputs, unit):
    from scipy.io import readsav

    # Determine IDL files
    path, _ = os.path.split(__file__)
    rfile = os.path.join(path, 'data', 'modeloutput_search_routines.sav')
    vfile = os.path.join(path, 'data', 'modeloutput_search_variables.sav')

    with open('make_file_list.pro', 'w') as f:
        #profname = f.name
        #tempdir, _ = os.path.split(f.name)
        #filelistfile = os.path.join(tempdir, 'filelist.dat')
        filelistfile = 'filelist.dat'
        f.write(f'''
pro make_file_list

restore, '{vfile}'
defsysv, '!model', modelvar
filelist = modeloutput_search('{inputs.spatialdist.mapfile}')
openw, 1, '{filelistfile}'
for i=0,n_elements(filelist)-1 do printf, 1, filelist[i]
close, 1

end''')

    # Search for the IDL files
    cmd = (f'/Applications/exelis/idl/bin/idl '
           f'''-e "restore, '{rfile}' & make_file_list" ''')
    os.system(cmd)

    # Load the initial values
    x0 = None
    idloutputfiles = open('filelist.dat', 'r').readlines()
    print(f'{len(idloutputfiles)} IDL sav files found')
    for savfile in idloutputfiles:
        idl = readsav(savfile.strip())
        idlout = idl['output']

        index = sorted(list(set(idlout['index'][0])))
        x_ = [idlout['x0'][0][idlout['index'][0] == i][0] for i in index]
        y_ = [idlout['y0'][0][idlout['index'][0] == i][0] for i in index]
        z_ = [idlout['z0'][0][idlout['index'][0] == i][0] for i in index]
        vx_ = [idlout['vx0'][0][idlout['index'][0] == i][0] for i in index]
        vy_ = [idlout['vy0'][0][idlout['index'][0] == i][0] for i in index]
        vz_ = [idlout['vz0'][0][idlout['index'][0] == i][0] for i in index]
#        f_ = [idlout['f0'][0][idlout['index'][0] == i][0] for i in index]
        f_ = np.ones_like(x_)

        if x0 is None:
            x0 = np.array(x_)
            y0 = np.array(y_)
            z0 = np.array(z_)
            vx0 = np.array(vx_)
            vy0 = np.array(vy_)
            vz0 = np.array(vz_)
            f = np.array(f_)
        else:
            x0 = np.append(x0, np.array(x_))
            y0 = np.append(y0, np.array(y_))
            z0 = np.append(z0, np.array(z_))
            vx0 = np.append(vx0, np.array(vx_))
            vy0 = np.append(vy0, np.array(vy_))
            vz0 = np.append(vz0, np.array(vz_))
            f = np.append(f, np.array(f_))

    X = [x0, y0, z0]*unit
    V = [vx0, vy0, vz0]*unit/u.s
    F = f

    return X, V, F

def speed_distribution(inputs, npackets):
    SpeedDist = inputs.speeddist

    if inputs.spatialdist.type == 'idlversion':
        return None
    else:
        pass

    if SpeedDist.type.lower() == 'gaussian':
        if SpeedDist.sigma == 0.:
            v0 = np.zeros(npackets)*u.km/u.s + SpeedDist.vprob
        else:
            v0 = np.random.normal(SpeedDist.vprob.value,
                                  SpeedDist.sigma.value,
                                  npackets)
            v0 *= SpeedDist.vprob.unit
    elif SpeedDist.type == 'sputtering':
        velocity = np.linspace(.1, 50, 5000)*u.km/u.s
        f_v = sputdist(velocity, SpeedDist.U, SpeedDist.alpha,
                       SpeedDist.beta, inputs.options.atom)

        v0 = (mathMB.random_deviates_1d(velocity.value, f_v.value, npackets) *
              velocity.unit)
    elif SpeedDist.type == 'maxwellian':
        if SpeedDist.temperature != 0:
            # Use a constant temperature
            amass = atomicmass(inputs.options.atom)
            v_th = np.sqrt(2*SpeedDist.temperature*const.k_B/amass)
            v_th = v_th.to(u.km/u.s)
            velocity = np.linspace(0.1*u.km/u.s, v_th*5, 5000)
            f_v = MaxwellianDist(velocity, SpeedDist.temperature,
                                 inputs.options.atom)
            v0 = (mathMB.random_deviates_1d(velocity.value, f_v.value, npackets) *
                  velocity.unit)
        else:
            # Use a surface temperature map
            # Need to write this
            assert 0, 'Not implemented yet'
    elif SpeedDist.type == 'flat':
        v0 = (np.random.rand(npackets)*2*SpeedDist.delv +
               SpeedDist.vprob - SpeedDist.delv)
    else:
        # Need to add more distributions
        assert 0, 'Distribtuion does not exist'

    assert np.all(np.isfinite(v0)), 'Infinite values for v0'

    return v0


def angular_distribution(inputs, X0, vv):
    if inputs.spatialdist.type == 'idlversion':
        return None
    else:
        pass

    npackets = len(vv)

    AngularDist = inputs.angulardist

    if AngularDist.type == 'none':
        pass
    elif AngularDist.type == 'radial':
        alt = np.zeros(npackets) + np.pi/2. # All packets going directly up
        az = np.zeros(npackets)
    elif AngularDist.type == 'isotropic':
        # Choose the altitude -- f(alt) = cos(alt)
        alt0 = AngularDist.altitude
        aa = (np.sin(alt0[0]), np.sin(alt0[1]))
        sinalt = np.random.rand(npackets) * (aa[1] - aa[0]) + aa[0]
        alt = np.arcsin(sinalt)

        # Choose the azimuth -- f(az) = 1/(azmax-azmin)
        az0, az1 = AngularDist.azimuth
        m = (az0, az1) if az0 < az1 else (az1, az0+2*np.pi)
        az = (m[0] + (m[1]-m[0])*np.random.rand(npackets)) % (2*np.pi*u.rad)
    elif AngularDist.type == 'costheta':
        # Choose the altitude -- f(alt) = cos(alt)
        alt0 = AngularDist.altitude
        aa = (np.sin(alt0[0]), np.sin(alt0[1]))
        sinalt = np.random.rand(npackets) * (aa[1] - aa[0]) + aa[0]
        alt = np.arcsin(sinalt)

        # Choose the azimuth -- f(az) = 1/(azmax-azmin)
        az0, az1 = AngularDist.azimuth
        m = (az0, az1) if az0 < az1 else (az1, az0+2*np.pi)
        az = (m[0] + (m[1]-m[0])*np.random.rand(npackets)) % (2*np.pi*u.rad)

        # alt0 = AngularDist.altitude
        # aa = (np.sin(alt0[0]).value, np.sin(alt0[1]).value)
        # sinalt = np.linspace(aa[0], aa[1], 1001)
        # f_sinalt = sinalt**AngularDist.n
        # salt = mathMB.random_deviates_1d(sinalt, f_sinalt, npackets)
        # alt = np.arcsin(salt)
        #
        # # Choose the azimuth -- f(az) = 1/(azmax-azmin)
        # az0, az1 = AngularDist.azimuth
        # m = (az0, az1) if az0 < az1 else (az1, az0+2*np.pi)
        # az = (m[0] + (m[1]-m[0])*np.random.rand(npackets)) % (2*np.pi*u.rad)
    else:
        assert 0, 'Angular Distribution not defined.'

    # Find the velocity components in coordinate system centered on packet
    v_rad = np.sin(alt)                 # Radial component of velocity
    v_tan0 = np.cos(alt) * np.cos(az)   # Component along latitude (points E)
    v_tan1 = np.cos(alt) * np.sin(az)   # Component along longitude (points N)

    #######
    # Now rotate to proper surface point
    # v_ren = M # v_xyz => v_xyz = invert(M) # v_ren
    rr = np.sqrt(X0[0,:]**2 + X0[1,:]**2 + X0[2,:]**2)
    x0, y0, z0 = X0[0,:]/rr, X0[1,:]/rr, X0[2,:]/rr

    rad = np.array([x0, y0, z0])
    east = np.array([y0, -x0, np.zeros_like(z0)])
    north = np.array([-z0*x0, -z0*y0, x0**2+y0**2])

    east /= np.linalg.norm(east, axis=0)
    north /= np.linalg.norm(north, axis=0)

    v0 = v_tan0*north + v_tan1*east + v_rad*rad
    vx0 = v0[0,:] * vv
    vy0 = v0[1,:] * vv
    vz0 = v0[2,:] * vv
    V0 = np.array([vx0, vy0, vz0])

    return V0


if __name__ == '__main__':
    velocity = np.linspace(.1, 50, 5000) * u.km/u.s

    f_v = gaussiandist(velocity, 2*u.km/u.s, 0.5*u.km/u.s)
#    f_v = sputdist(velocity, 2.*u.eV, 2., 1., 'Na')
#    f_v = MaxwellianDist(velocity, 1000.*u.K, 'Na')
    plt.plot(velocity, f_v)
    plt.minorticks_on()
    plt.ylim((1e-10,10))
    plt.xlim((0,20))
    plt.yscale('log')
    plt.xlabel('Velocity (km s$^{-1}$)')
    plt.ylabel('Relative f$_v$')
    plt.title('Speed Distribution Function')
    plt.show()
