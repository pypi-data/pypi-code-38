'''Classes used by the Inputs class'''
import numpy as np
import pandas as pd
import psycopg2
from astropy.time import Time
import astropy.units as u
from solarsystemMB import SSObject


def isNone(x):
    try:
        q = x.value
    except:
        q = x

    if type(q) == str:
        return f'is NULL' if q is None else f"= '{q}'"
    else:
        return f'is NULL' if q is None else f"= {q}"


def inRange(field, x, delta):
    return f'ABS({field} - {x}) <= {delta/2}'

dtor = np.pi/180.


class Geometry():
    def __init__(self, gparam):
        '''Geometry object: object to model
           Fields:
               planet
               StartPoint
               objects
               starttime
               phi
               subsolarpt = (subsolarlong, subsolarlat)
               TAA'''

        # Choose the planet
        if 'planet' in gparam:
            planet = gparam['planet'].title()
            self.planet = SSObject(planet)
        else:
            assert 0, 'Planet not defined.'

        objlist = [self.planet.object]
        if self.planet.moons is not None:
            objlist.extend([m.object for m in self.planet.moons])

        # Choose the starting point
        self.startpoint = (gparam['startpoint'].title()
                           if 'startpoint' in gparam
                           else self.planet.object)
        assert self.startpoint in objlist, 'Not a valid starting point'

        # Choose which objects to include
        # This is given as a list of names
        # Default = geometry.planet and geometry.startpoint
        if 'objects' in gparam:
            inc = set(i.strip().title()
                      for i in gparam['objects'].split(','))
        else:
            inc = set((self.planet.object, self.startpoint))

        for i in inc:
            assert i in objlist, 'Invalid object included: {}'.format(i)
        self.objects = set(SSObject(o) for o in inc)

        # Check to see if a starting time is given
        if 'time' in gparam:
            try:
                self.time = Time(gparam['time'].upper())
            except:
                assert 0, 'Time is not given in a valid format'

            assert 0, 'Need to figure out how to calculate orbital positions'
        else:
            # Initial positions are given
            self.time = None
            if 'phi' in gparam:
                phi = tuple(float(p)*u.rad for p in gparam['phi'].split(','))
                assert 0, 'Need to figure out best way to do this'
            elif len(self.objects) == 1:
                # No moons, so this isn't needed
                self.phi = [0.*u.rad]
            else:
                assert 0, ('Need to give either an observation time'
                           'or orbital position.')

        # Subsolar longitude and latitude
        subslong = (float(gparam['subsolarlong'])*u.rad if
                    'subsolarlong' in gparam else 0.*u.rad)
        subslat= (float(gparam['subsolarlat'])*u.rad if
                  'subsolarlat' in gparam else 0.*u.rad)
        self.subsolarpoint = (subslong, subslat)

        # True Anomaly Angle
        self.taa = float(gparam['taa']) if 'taa' in gparam else 0.
        self.taa *= u.rad

    def __str__(self):
        print('geometry.planet = {}'.format(self.planet.object))
        print('geometry.StartPoint = {}'.format(self.startpoint))
        oo = [o.object for o in self.objects]
        obs = ', '.join(oo)
        print('geometry.objects = {}'.format(obs))
        if self.time is not None:
            print('geometry.starttime = {}'.format(self.time.iso))
        else:
            print('geometry.startime not specified')
        if len(self.phi) != 0:
            print('geometry.phi XXX')
        print('geometry.subsolarpoint = ({}, {})'.format(*self.subsolarpoint))
        print('geometry.TAA = {}'.format(self.taa))
        return ''

    def search(self, database='thesolarsystemmb', startlist=None):
        # Make list of objects in planet system
        objs = [obj.object for obj in self.objects]
        objs.sort()
        objs2 = ','.join(objs)

        if startlist is None:
            startstr = ''
        else:
            start_ = [str(s) for s in startlist]
            startstr = f"and geo_idnum in ({', '.join(start_)})"

        if self.time is None:
            # Fields to query:
            #   planet, startpoint, objects, phi, subsolarpoint, TAA
            dtaa = (5.*u.deg).to(u.rad)
            taa = [self.taa-dtaa/2., self.taa+dtaa/2.]
            taa = [taa[0].value, taa[1].value]
            if taa[0] < 0.:
                taabit = '(taa>={} or taa<{})'.format(2*np.pi+taa[0], taa[1])
            elif taa[1] > 2*np.pi:
                taabit = '(taa>={} or taa<{})'.format(taa[0],
                                                      taa[1] % (2*np.pi))
            else:
                taabit = inRange('taa', self.taa.value, dtaa.value)

            phi = [p.value for p in self.phi]
            assert phi[0] == 0., 'phi for planet should be zero.'
            ptxt = [inRange('phi[{}]'.format(i+1), p, 5.*dtor) for
                    i,p in enumerate(phi)]
            ptxt2 = ' and '.join(ptxt)

            sspt0 = inRange('subsolarpt[0]', self.subsolarpoint[0].value,
                            5*dtor)
            sspt1 = inRange('subsolarpt[1]', self.subsolarpoint[1].value,
                            5*dtor)

            query = f'''SELECT geo_idnum FROM geometry
                        WHERE planet = '{self.planet.object}' and
                              startpoint = '{self.startpoint}' and
                              objects = ARRAY['{objs2}']::SSObject[] and
                              {ptxt2} and
                              {sspt0} and
                              {sspt1} and
                              {taabit} {startstr}'''
        else:
            # Fields to query
            # planet, StartPoint, objects, time
            # query =
            assert 0, 'Not working yet.'

        with psycopg2.connect(database=database) as con:
            result = pd.read_sql(query, con)
        if len(result) == 0:
            return None
        else:
            return result.geo_idnum.to_list()
###############################################################


class StickingInfo():
    '''
    stickcoef
    tsurf
    stickfn
    stick_mapfile
    epsilon
    n
    tmin
    emitfn
    accom_mapfile
    accom_factor
    '''

    def __init__(self, sparam):
        self.stickcoef = (float(sparam['stickcoef'])
                          if 'stickcoef' in sparam
                          else 1.)
        if self.stickcoef > 1.:
            self.stickcoef = 1.

        # Defaults
        self.tsurf = None
        self.stickfn = sparam['stickfn'] if 'stickfn' in sparam else None
        self.stick_mapfile = None
        self.epsilon = None
        self.n = None
        self.tmin = None
        self.emitfn = sparam['emitfn'] if 'emitfn' in sparam else None
        self.accom_mapfile = None
        self.accom_factor = None

        # Set the stick function parameters
        if self.stickcoef == 1:
            # Complete sticking
            self.stickfn = 'complete'
        elif self.stickcoef > 0.:
            # Cosnstant stick function
            self.stickfn = 'constant'
        elif (self.stickcoef == -1) and (self.stickfn == 'use_map'):
            self.stick_mapfile = sparam['stick_mapfile']
        elif (self.stickcoef == -1) and (self.stickfn == 'linear'):
            self.epsilon = float(sparam['epsilon'])
            self.n = float(sparam['n']) if 'n' in sparam else 1.
            self.tmin = float(sparam['tmin'])*u.K
        elif (self.stickcoef == -1) and (self.stickfn == 'cossza'):
            self.n = float(sparam['n']) if 'n' in sparam else 1.
            self.tmin = float(sparam['tmin'])*u.K
        else:
            assert 0, 'sticking_info.stickfn not given or invalid.'

        # set the re-emission function parameters
        if self.emitfn == 'use_map':
            self.accom_mapfile = sparam['accom_mapfile']
        elif self.emitfn == 'maxwellian':
            ac = float(sparam['accom_factor'])
            if ac < 0:
                ac = 0.
            elif ac > 1:
                ac = 1.
            else:
                pass
            self.accom_factor = ac
        elif self.emitfn == 'elastic scattering':
            pass
        else:
            pass

    def __str__(self):
        print('sticking_info.stickcoef = {}'.format(self.stickcoef))
        if self.stickfn is not None:
            print('sticking_info.stickfn = {}'.format(self.stickfn))
        if self.tsurf is not None:
            print('sticking_info.tsurf = {}'.format(self.tsurf))
        if self.stick_mapfile is not None:
            print('sticking_info.stick_mapfile = {}'.
                  format(self.stick_mapfile))
        if self.epsilon is not None:
            print('sticking_info.epsilon = {}'.format(self.epsilon))
        if self.n is not None:
            print('sticking_info.n = {}'.format(self.n))
        if self.tmin is not None:
            print('sticking_info.tmin = {}'.format(self.tmin))
        if self.emitfn is not None:
            print('sticking_info.emitfn = {}'.format(self.emitfn))
        if self.accom_mapfile is not None:
            print('sticking_info.accom_mapfile = {}'.
                  format(self.accom_mapfile))
        if self.accom_factor is not None:
            print('sticking_info.accom_factor = {}'.format(self.accom_factor))

        return ''

    def search(self, database='thesolarsystemmb', startlist=None):
        if startlist is None:
            startstr = ''
        else:
            start_ = [str(s) for s in startlist]
            startstr = f"and st_idnum in ({', '.join(start_)})"

        if self.stickcoef == 1:
            query = f'''SELECT st_idnum FROM sticking_info
                        WHERE stickcoef=1 {startstr}'''
        else:
            query = f'''SELECT st_idnum FROM sticking_info
                        WHERE stickcoef={self.stickcoef}
                             tsurf {self.tsurf} and
                             stickfn {self.stickfn} and
                             stick_mapfile {self.stick_mapfile} and
                             epsilon {self.epsilon} and
                             n {self.n} and
                             tmin {self.tmin} and
                             emitfn {self.emitfn} and
                             accom_mapfile {self.accom_mapfile}
                             {startstr}'''

        with psycopg2.connect(database=database) as con:
            result = pd.read_sql(query, con)
        if len(result) == 0:
            return None
        else:
            return result.st_idnum.to_list()


class Forces():
    def __init__(self, fparam):
        '''
        gravity
        radpres
        '''
        self.gravity = (bool(int(float(fparam['gravity'])))
                        if 'gravity' in fparam
                        else False)
        self.radpres = (bool(int(float(fparam['radpres'])))
                        if 'radpres' in fparam
                        else False)

    def __str__(self):
        print('forces.gravity = {}'.format(self.gravity))
        print('forces.radpres = {}'.format(self.radpres))
        return ''

    def search(self, database='thesolarsystemmb', startlist=None):
        if startlist is None:
            startstr = ''
        else:
            start_ = [str(s) for s in startlist]
            startstr = f"and f_idnum in ({', '.join(start_)})"

        query = f'''SELECT f_idnum FROM forces
                    WHERE gravity={self.gravity} and
                          radpres={self.radpres} {startstr}'''
        with psycopg2.connect(database=database) as con:
            result = pd.read_sql(query, con)

        if len(result) == 0:
            return None
        else:
            return result.f_idnum.to_list()

###############################################################


class SpatialDist():
    def __init__(self, sparam):
        '''
        type
        exobase
        use_map
        mapfile
        lonrange
        latrange
        '''

        # Set defaults
        self.type = sparam['type']
        self.exobase = 0.
        self.use_map = False
        self.mapfile = None
        self.longitude = None
        self.latitude = None

        if self.type == 'surface':
            self.exobase = (float(sparam['exobase'])
                            if 'exobase' in sparam
                            else 1.)  # Unit gets set later
            self.use_map = (bool(int(sparam['use_map']))
                            if 'use_map' in sparam
                            else False)
            if self.use_map:
                self.mapfile = sparam['mapfile']

            long0 = (float(sparam['longitude0'])*u.rad
                if 'longitude0' in sparam else 0.*u.rad)
            long1 = (float(sparam['longitude1'])*u.rad
                if 'longitude1' in sparam else 2*np.pi*u.rad)
            lat0 = (float(sparam['latitude0'])*u.rad
                if 'latitude0' in sparam else -np.pi/2.*u.rad)
            lat1 = (float(sparam['latitude1'])*u.rad
                if 'latitude1' in sparam else np.pi/2.*u.rad)
            self.longitude = (long0, long1)
            self.latitude = (lat0, lat1)
        elif self.type == 'surfacespot':
            self.exobase = (float(sparam['exobase'])
                            if 'exobase' in sparam
                            else 1.)  # Unit gets set later
            lon = (float(sparam['longitude'])*u.rad
                   if 'longitude' in sparam else 0.*u.rad)
            lat = (float(sparam['latitude'])*u.rad
                   if 'latitude' in sparam else 0*u.rad)
            sigma = (float(sparam['sigma'])*u.rad
                     if 'sigma' in sparam else 25*u.deg)
            if sigma < 0*u.deg:
                sigma = 0*u.deg
            elif sigma > 90*u.deg:
                sigma - 90*u.deg
            else:
                pass

            self.longitude = (lon, sigma.to(u.rad))
            self.latitude = (lat, sigma.to(u.rad))
        elif self.type== 'idlversion':
            if 'idlinputfile' in sparam:
                self.mapfile = sparam['idlinputfile']
            else:
                assert 0, 'Must specify idlinputfile'

        else:
            assert 0, f'{self.type} distribution not defined yet.'

    def __str__(self):
        print('spatialdist.type = {}'.format(self.type))
        print('spatialdist.exobase = {}'.format(self.exobase))
        print('spatialdist.use_map = {}'.format(self.use_map))
        print('spatialdist.mapfile = {}'.format(self.mapfile))
        if self.longitude is None:
            print('spatialdist.longitude is None')
        else:
            print('spatialdist.longitude = ({:0.2f}, {:0.2f})'.
                  format(*self.longitude))
        if self.latitude is None:
            print('spatialdist.latitude is None')
        else:
            print('spatialdist.latitude = ({:0.2f}, {:0.2f})'.
                  format(*self.latitude))
        return ''

    def search(self, database='thesolarsystemmb', startlist=None):
        if startlist is None:
            startstr = ''
        else:
            start_ = [str(s) for s in startlist]
            startstr = f"and spat_idnum in ({', '.join(start_)})"

        if self.longitude is None:
            long0 = 'longitude[1] = 0.'
            long1 = 'longitude[2] = 0.'
        else:
            long0 = inRange('longitude[1]', self.longitude[0].value, 5*dtor)
            long1 = inRange('longitude[2]', self.longitude[1].value, 5*dtor)

        if self.latitude is None:
            lat0 = 'latitude[1] = 0.'
            lat1 = 'latitude[2] = 0.'
        else:
            lat0 = inRange('latitude[1]', self.latitude[0].value, 5*dtor)
            lat1 = inRange('latitude[2]', self.latitude[1].value, 5*dtor)

        query = f'''SELECT spat_idnum FROM spatialdist
                    WHERE type = '{self.type}' and
                         {inRange('exobase', self.exobase, 0.05)} and
                         use_map {isNone(self.use_map)} and
                         mapfile {isNone(self.mapfile)} and
                         {long0} and
                         {long1} and
                         {lat0} and
                         {lat1} {startstr}'''

        with psycopg2.connect(database=database) as con:
            result = pd.read_sql(query, con)
        if len(result) == 0:
            return None
        else:
            return result.spat_idnum.to_list()
###############################################################


class SpeedDist():
    '''
    type
    vprob
    sigma
    U
    alpha
    beta
    temperature
    delv
    '''


    def __init__(self, sparam):
        self.type = sparam['type']

        # Defaults
        self.vprob = None
        self.sigma = None
        self.U = None
        self.alpha = None
        self.beta = None
        self.temperature = None
        self.delv = None

        if self.type == 'gaussian':
            self.vprob = float(sparam['vprob'])*u.km/u.s
            self.sigma = float(sparam['sigma'])*u.km/u.s
        elif self.type == 'sputtering':
            self.U = float(sparam['u'])*u.eV
            self.alpha = float(sparam['alpha'])
            self.beta = float(sparam['beta'])
        elif self.type == 'maxwellian':
            self.temperature = float(sparam['temperature'])*u.K
        elif self.type == 'flat':
            self.vprob = float(sparam['vprob'])*u.km/u.s
            self.delv = float(sparam['delv'])*u.km/u.s
        else:
            assert 0, f'SpeedDist.type = {self.type} not available'

    def __str__(self):
        print('SpeedDist.type = {}'.format(self.type))
        if self.vprob is not None:
            print('SpeedDist.vprob = {}'.format(self.vprob))
        if self.sigma is not None:
            print('SpeedDist.sigma = {}'.format(self.sigma))
        if self.U is not None:
            print('SpeedDist.U = {}'.format(self.U))
        if self.alpha is not None:
            print('SpeedDist.alpha = {}'.format(self.alpha))
        if self.beta is not None:
            print('SpeedDist.beta = {}'.format(self.beta))
        if self.temperature is not None:
            print('SpeedDist.temperature = {}'.format(self.temperature))
        if self.delv is not None:
            print('SpeedDist.delv = {}'.format(self.delv))

        return ''

    def search(self, database='thesolarsystemmb', startlist=None):
        if startlist is None:
            startstr = ''
        else:
            start_ = [str(s) for s in startlist]
            startstr = f"and spd_idnum in ({', '.join(start_)})"

        if self.vprob is None:
            vstr = 'vprob is NULL'
        else:
            vstr = inRange('vprob', self.vprob.value,
                           self.vprob.value*0.05)

        if self.temperature is None:
            Tstr = 'temperature is NULL'
        else:
            Tstr = inRange('temperature', self.temperature.value,
                           self.temperature.value*0.05)

        query = f'''SELECT spd_idnum FROM speeddist
                    WHERE type = '{self.type}' and
                          {vstr} and
                          sigma {isNone(self.sigma)} and
                          U  {isNone(self.U)} and
                          alpha  {isNone(self.alpha)} and
                          beta  {isNone(self.beta)} and
                          {Tstr} and
                          delv  {isNone(self.delv)} {startstr}'''

        with psycopg2.connect(database=database) as con:
            result = pd.read_sql(query, con)
        if len(result) == 0:
            return None
        else:
            return result.spd_idnum.to_list()


class AngularDist():
    '''
    type
    azimuth
    altitude
    n
    '''

    def __init__(self, aparam, spatialdist):
        self.type = aparam['type'] if 'type' in aparam else None
        self.azimuth = None
        self.altitude = None
        self.n = None

        if self.type is None:
            pass
        elif self.type == 'radial':
            pass
        elif self.type == 'isotropic':
            if 'azimuth' in aparam:
                self.azimuth = tuple(float(a)*u.rad
                    for a in aparam['azimuth'].split(','))
                assert len(self.azimuth) == 2, (
                    'AngularDist.azimuth must have two values.')
            else:
                self.azimuth = (0*u.rad, 2*np.pi*u.rad)

            if 'altitude' in aparam:
                self.altitude = tuple(float(a)*u.rad
                    for a in aparam['altitude'].split(','))
                assert len(self.altitude) ==2, (
                    'AngularDist.altitude must have two values.')
            else:
                altmin = (0.*u.rad if 'surface' in spatialdist.type
                          else -np.pi/2.*u.rad)
                self.altitude = (altmin, np.pi/2.*u.rad)
        elif self.type == 'costheta':
            if 'azimuth' in aparam:
                self.azimuth = tuple(float(a)*u.rad
                    for a in aparam['azimuth'].split(','))
                assert len(self.azimuth) == 2, (
                    'AngularDist.azimuth must have two values.')
            else:
                self.azimuth = (0*u.rad, 2*np.pi*u.rad)

            if 'altitude' in aparam:
                self.altitude = tuple(float(a)*u.rad
                    for a in aparam['altitude'].split(','))
                assert len(self.altitude) ==2, (
                    'AngularDist.altitude must have two values.')
            else:
                altmin = (0.*u.rad if 'surface' in spatialdist.type
                          else -np.pi/2.*u.rad)
                self.altitude = (altmin, np.pi/2.*u.rad)

            self.n = float(aparam['n']) if 'n' in aparam else 1.

    def __str__(self):
        print('AngularDist.type = {}'.format(self.type))
        if self.altitude is not None:
            print('AngularDist.altitude = ({:0.2f}, {:0.2f})'.
                  format(*self.altitude))
        if self.azimuth is not None:
            print('AngularDist.azimuth = ({:0.2f}, {:0.2f})'.
                  format(*self.azimuth))
        if self.n is not None:
            print('AngularDist.n = {}'.format(self.n))

        return ''

    def search(self, database='thesolarsystemmb', startlist=None):
        if startlist is None:
            startstr = ''
        else:
            start_ = [str(s) for s in startlist]
            startstr = f"and ang_idnum in ({', '.join(start_)})"

        if self.azimuth is None:
            az0 = 'azimuth[1] is NULL'
            az1 = 'azimuth[2] is NULL'
        else:
            az0 = inRange('azimuth[1]', self.azimuth[0].value, 5*dtor)
            az1 = inRange('azimuth[2]', self.azimuth[1].value, 5*dtor)

        if self.altitude is None:
            alt0 = 'altitude[1] is NULL'
            alt1 = 'altitude[2] is NULL'
        else:
            alt0 = inRange('altitude[1]', self.altitude[0].value, 5*dtor)
            alt1 = inRange('altitude[2]', self.altitude[1].value, 5*dtor)
        n = isNone(self.n)

        query = f'''SELECT ang_idnum from angulardist
                    WHERE type = '{self.type}' and
                          {az0} and {az1} and
                          {alt0} and {alt1} and
                          n {n} {startstr}'''
        with psycopg2.connect(database=database) as con:
            result = pd.read_sql(query, con)

        if len(result) == 0:
            return None
        else:
            return result.ang_idnum.to_list()
###############################################################


class Options():
    '''
    endtime
    resolution
    at_once
    atom
    lifetime
    fullsystem
    outeredge
    motion
    streamlines
    nsteps
    '''

    def __init__(self, oparam, planet):
        self.endtime = float(oparam['endtime'])*u.s
        self.at_once = (bool(int(oparam['at_once'])) if 'at_once'
                        in oparam else False)
        self.atom = oparam['atom'].title()
        self.motion = (bool(int(oparam['motion'])) if 'motion'
                       in oparam else True)
        self.lifetime = (float(oparam['lifetime'])*u.s
                         if 'lifetime' in oparam else 0.*u.s)

        if 'fullsystem' in oparam:
            self.fullsystem = bool(int(oparam['fullsystem']))
        else:
            self.fullsystem = False if planet == 'Mercury' else True

        if not(self.fullsystem):
            self.outeredge = (float(oparam['outeredge'])
                              if 'outeredge' in oparam else 20.)
            # Units added later
        else:
            self.outeredge = None

        self.streamlines = (bool(int(oparam['streamlines']))
                            if 'streamlines' in oparam else False)
        if self.streamlines:
            self.nsteps = (int(oparam['nsteps'])
                           if 'nsteps' in oparam else 1000)
            self.resolution = None
        else:
            self.nsteps = None
            self.resolution = (float(oparam['resolution'])
                               if 'resolution' in oparam else 1e-3)

    def __str__(self):
        print('options.endtime = {}'.format(self.endtime))
        print('options.resolution = {}'.format(self.resolution))
        print('options.at_once = {}'.format(self.at_once))
        print('options.atom = {}'.format(self.atom))
        print('options.motion = {}'.format(self.motion))
        print('options.lifetime = {}'.format(self.lifetime))
        print('options.fullsystem = {}'.format(self.fullsystem))
        if self.outeredge is not None:
            print('options.outeredge = {}'.format(self.outeredge))
        print('options.streamlines = {}'.format(self.streamlines))
        if self.nsteps is not None:
            print('options.nsteps = {}'.format(self.nsteps))

        return ''

    def search(self, database='thesolarsystemmb', startlist=None):
        if startlist is None:
            startstr = ''
        else:
            start_ = [str(s) for s in startlist]
            startstr = f"and opt_idnum in ({', '.join(start_)})"

        endtime = inRange('endtime', self.endtime.value,
                          self.endtime.value*0.05)
        outeredge = isNone(self.outeredge)
        nsteps = isNone(self.nsteps)
        res = isNone(self.resolution)

        query = f'''SELECT opt_idnum from options
                    WHERE {endtime} and
                          resolution {res} and
                          at_once = {self.at_once} and
                          atom = '{self.atom}' and
                          lifetime = {self.lifetime.value} and
                          fullsystem = {self.fullsystem} and
                          outeredge {outeredge} and
                          motion = {self.motion} and
                          streamlines = {self.streamlines} and
                          nsteps {nsteps} {startstr}'''
        with psycopg2.connect(database=database) as con:
            result = pd.read_sql(query, con)

        if len(result) == 0:
            return None
        else:
            return result.opt_idnum.to_list()
