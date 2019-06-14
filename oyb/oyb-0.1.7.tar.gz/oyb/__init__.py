"""The heart of the *oyb* package. Contains orbital models and conversions.
"""

import datetime
import numpy
from math import pi, cos, sin, acos, asin
from oyb import anomaly, rot, earth

class Orbit(object):
    """Restricted two-body propagation model
    """
    
    def __init__(self, a_m=None, e=0.0, i_rad=0.0, O_rad=0.0, w_rad=0.0, M_rad=0.0, tEpoch_dt=None):
        """Initializes a restricted two-body propagation model for a spherical
           earth. Defaults to a circular GEO orbit with all angles set to 0.
           (Epoch is set to the UTC time when the object is created.)
        """
        self.tEpoch_dt = tEpoch_dt if tEpoch_dt is not None else datetime.datetime.utcnow()
        self.a_m = a_m if a_m is not None else ((earth.tSidDay_s / (2 * pi))**2 * earth.mu_m3ps2)**(1/3)
        self.e = e
        self.i_rad = i_rad
        self.O_rad = O_rad
        self.w_rad = w_rad
        self.M_rad = M_rad
        
    def __str__(self):
        """Converts an Orbit object into a string representation (invoked by the
           *str* and *print* functions) that references the shape (altitude at
           perigee and apogee) and object location in memory.
        """
        hPer_m, hApo_m = self.getShape()
        return '<%g x %g [km] %s at 0x%08x>' % (hPer_m * 1e-3, hApo_m * 1e-3, self.__class__.__name__, id(self))
        
    def getPeriod(self):
        """Returns the period of the current orbit, in seconds.
        """
        T_s = 2 * pi * (self.a_m**3 / earth.mu_m3ps2)**0.5
        return T_s
        
    def getTrue(self, t_dt=None):
        """Returns the true anomaly of the object when propagated to a given
           datetime.
        """
        if t_dt is None:
            t_dt = self.tEpoch_dt
        dt_s = (t_dt - self.tEpoch_dt).total_seconds()
        dM_rad = dt_s * 2 * pi / self.getPeriod()
        M_rad = (self.M_rad + dM_rad) % (2 * pi)
        return anomaly.mean2true(M_rad, self.e)
        
    def getRpqw(self, t_dt=None):
        """Returns the 3-component position vector of the object at the given
           datetime, as evaluted in the PQW (co-planar) frame.
        """
        tht_rad = self.getTrue(t_dt)
        d = 1 + self.e * cos(tht_rad)
        p_m = self.a_m * (1 - self.e**2) * cos(tht_rad) / d
        q_m = self.a_m * (1 - self.e**2) * sin(tht_rad) / d
        return numpy.array([p_m, q_m, 0])
    
    def getQpqw2eci(self):
        """Returns the frame transformation matrix from the PQW (co-planar)
           frame to the earth-centered inertial (ECI) frame, w.r.t. J2000.
        """
        w = rot.Z(self.w_rad)
        i = rot.X(self.i_rad)
        O = rot.Z(self.O_rad)
        return (w.dot(i).dot(O)).transpose()
        
    def getReci(self, t_dt=None):
        """Returns the position of the object at the given point in time, as
           evaluated within the earth-centered inertial (ECI) frame, in meters.
        """
        rPqw = self.getRpqw(t_dt)
        Qpqw2eci = self.getQpqw2eci()
        return Qpqw2eci.dot(rPqw)
        
    def getRlla(self, t_dt=None):
        """Computes and returns the position at the given datetime, in latitude,
           longitude, and altitude (radians, radians, and meters, respectively).
        """
        if t_dt is None:
            t_dt = self.tEpoch_dt
        rEci_m = self.getReci(t_dt)
        rEcf_m = earth.getQeci2ecf(t_dt).dot(rEci_m)
        rLla_radm = rot.xyz2sph(rEcf_m)
        return numpy.array([rLla_radm[1], rLla_radm[0], rLla_radm[2] - earth.eqRad_m])
        
    def getAngMom(self):
        """Returns the scalar angular momentum of the orbit, in m/s^2.
        """
        return (earth.mu_m3ps2 * self.a_m * (1 - self.e**2))**0.5
        
    def getShape(self):
        """Returns a two-element tuple containing the altitude of the object at
           perigee and apogee, in meters above spherical sea level.
        """
        hPer_m = self.a_m * (1 - self.e) - earth.eqRad_m
        hApo_m = self.a_m * (1 + self.e) - earth.eqRad_m
        return (hPer_m, hApo_m)
        
    def getShapeVel(self):
        """Returns a two-element tuple containing the scalar velocity of the
           object at perigee and apogee, in meters per second.
        """
        rPer_m = self.a_m * (1 - self.e)
        rApo_m = self.a_m * (1 + self.e)
        h_m2ps = self.getAngMom()
        return h_m2ps / rPer_m, h_m2ps / rApo_m
        
    def getTaaRad(self):
        """Returns the true-anomaly averaged radius (geometric mean of radius at
           perigee and apogee), in meters.
        """
        rPer_m = self.a_m * (1 - self.e)
        rApo_m = self.a_m * (1 + self.e)
        return (rPer_m * rApo_m)**0.5
    
    def setShape(self, hPer_m, hApo_m):
        """Sets the a_m (semi-major axis) and e (eccentricity) values of an
           orbit based on the given altitude (meters above spherical sea level)
           at perigee and apogee.
        """
        rPer_m = hPer_m + earth.eqRad_m
        rApo_m = hApo_m + earth.eqRad_m
        self.a_m = 0.5 * (rPer_m + rApo_m)
        self.e = (rApo_m - rPer_m) / (rApo_m + rPer_m)
        
    def propagate(self, tEpoch_dt=None, T_s=None, nSamples=1000):
        """Computes inertial position over the course of one orbit, beginning
           with the given datetime (or, if not provided, the element epoch).
           This defaults to 1,000 samples within that time range.
        """
        if tEpoch_dt is None:
            tEpoch_dt = self.tEpoch_dt
        if T_s is None:
            T_s = self.getPeriod()
        ti_s = numpy.linspace(0, T_s, nSamples)
        rEci_m = numpy.zeros((0,3))
        for t_s in ti_s:
            r = self.getReci(tEpoch_dt + datetime.timedelta(t_s/86400))
            rEci_m = numpy.append(rEci_m, r.reshape(1,-1), axis=0)
        return rEci_m
        
    def track(self, tEpoch_dt=None, T_s=None, nSamples=1000):
        """Computes lat/lon/alt position over the course of one orbit, beginning
           with the given datetime (or, if not provided, the element epoch).
           This defaults to 1,000 samples within that time range.
        """
        if tEpoch_dt is None:
            tEpoch_dt = self.tEpoch_dt
        if T_s is None:
            T_s = self.getPeriod()
        ti_s = numpy.linspace(0, T_s, nSamples)
        rLla_radm = numpy.zeros((0,3))
        for t_s in ti_s:
            r = self.getRlla(tEpoch_dt + datetime.timedelta(t_s/86400))
            rLla_radm = numpy.append(rLla_radm, r.reshape(1,-1), axis=0)
        return rLla_radm
        
    def getApogee(self):
        """Returns the 3-component position vector of the object at apogee, in
           meters and evaluated within the earth-centered inertial (ECI) frame.
        """
        ra_m = self.a_m * (1 + self.e)
        return self.getQpqw2eci().dot(numpy.array([-ra_m,0,0]))
        
    def getPerigee(self):
        """Returns the 3-component position vector of the object at perigee, in
           meters and evaluated within the earth-centered inertial (ECI) frame.
        """
        rp_m = self.a_m * (1 - self.e)
        return self.getQpqw2eci().dot(numpy.array([rp_m,0,0]))
        
    def getAscNode(self):
        """Returns the 3-component position vector of the object at the
           ascending node, in meters and evaluated within the earth-centered
           inertial (ECI) frame.
        """
        tht_rad = 2 * pi - anomaly.mean2true(self.M_rad, self.e) - self.w_rad
        d = 1 + self.e * cos(tht_rad)
        p_m = self.a_m * (1 - self.e**2) * cos(tht_rad) / d
        q_m = self.a_m * (1 - self.e**2) * sin(tht_rad) / d
        rPqw_m = numpy.array([p_m, q_m, 0])
        return self.getQpqw2eci().dot(rPqw_m)
        
    def getDescNode(self):
        """Returns the 3-component position vector of the object at the
           descending node, in meters and evaluated within the earth-centered
           inertial (ECI) frame.
        """
        tht_rad = pi - anomaly.mean2true(self.M_rad, self.e) - self.w_rad
        d = 1 + self.e * cos(tht_rad)
        p_m = self.a_m * (1 - self.e**2) * cos(tht_rad) / d
        q_m = self.a_m * (1 - self.e**2) * sin(tht_rad) / d
        rPqw_m = numpy.array([p_m, q_m, 0])
        return self.getQpqw2eci().dot(rPqw_m)
        
    @classmethod
    def fromRV(cls, rEci_m, vEci_mps):
        """Constructs an Orbit object from the given position (meters) and
           velocity (meters-per-second) state vectors, as evaluated in the
           earth-centered inertial (ECI) frame.
        """
        r_m = rEci_m.dot(rEci_m)**0.5
        v_mps = vEci_mps.dot(vEci_mps)**0.5
        vr_mps = rEci_m.dot(vEci_mps) / r_m
        hEci_m2ps = numpy.cross(rEci_m, vEci_mps)
        h_m2ps = hEci_m2ps.dot(hEci_m2ps)**0.5
        i_rad = acos(hEci_m2ps[2] / h_m2ps)
        Neci = numpy.cross(numpy.array([0,0,1]), hEci_m2ps)
        N = Neci.dot(Neci)**0.5
        O_rad = acos(Neci[0] / N)
        if Neci[1] < 0:
            O_rad = 2 * pi - O_rad
        eEci = (numpy.cross(vEci_mps, hEci_m2ps) - earth.mu_m3ps2 * rEci_m / r_m) / earth.mu_m3ps2
        e = eEci.dot(eEci)**0.5
        w_rad = acos(Neci.dot(eEci) / N / e)
        if eEci[2] < 0:
            w_rad = 2 * pi - w_rad
        tht_rad = acos(eEci.dot(rEci_m) / e / r_m)
        if vr_mps < 0:
            tht_rad = 2 * pi - tht_rad
        M_rad = anomaly.true2mean(tht_rad, e)
        a_m = h_m2ps**2 / (earth.mu_m3ps2 * (1 - e**2))
        return cls(a_m=a_m, e=e, i_rad=i_rad, O_rad=O_rad, w_rad=w_rad, M_rad=M_rad)
        
    @classmethod
    def fromHTht(cls, h1_m, tht1_rad, h2_m, tht2_rad):
        """Constructs an Orbit object based on the given altitude (meters above
           spherical sea level) and true anomaly values (in radians).
        """
        r1_m = h1_m + earth.eqRad_m
        r2_m = h2_m + earth.eqRad_m
        e = (r1_m - r2_m) / (r2_m * cos(tht2_rad) - r1_m * cos(tht1_rad))
        h_m2ps = (r1_m * earth.mu_m3ps2 * (1 + e * cos(tht1_rad)))**0.5
        a_m = h_m2ps**2 / (earth.mu_m3ps2 * (1 - e**2))
        return cls(a_m=a_m, e=e)
        
    @classmethod
    def fromTle(cls, line1, line2):
        """Constructs an Orbit object from the given two strings, as formatted
           by the TLE (two-line element) specification (one string per line).
        """
        ey = line1[18:20]
        ed = line1[20:32]
        inc = line2[8:16]
        raan = line2[17:25]
        ecc = line2[26:33]
        aop = line2[34:42]
        ma = line2[43:51]
        mm = line2[52:63]
        a_m = (earth.mu_m3ps2 * (86400 / (2 * pi * float(mm)))**2)**(1/3)
        e = float('.' + ecc)
        i_rad = float(inc) * pi / 180
        O_rad = float(raan) * pi / 180
        w_rad = float(aop) * pi / 180
        M_rad = float(ma) * pi / 180
        tEpoch_y = 2000 + int(ey) if int(ey) < 50 else 1900 + int(ey)
        tEpoch_d = float(ed) - 1
        tEpoch_dt = datetime.datetime(tEpoch_y, 1, 1, 0, 0, 0) + datetime.timedelta(tEpoch_d)
        return cls(a_m=a_m, e=e, i_rad=i_rad, O_rad=O_rad, w_rad=w_rad, M_rad=M_rad, tEpoch_dt=tEpoch_dt)

class MeanJ2(Orbit):
    """Implements propagation to evolve elements with mean J2 perturbations
    """
        
    def getRaanRate(self):
        """Computes and returns the rate at which the right-ascension of the
           ascending node precesses, in radians per second, as a result of the
           non-spherical Earth's J2 harmonic.
        """
        return -1.5 * earth.mu_m3ps2**0.5 * earth.j2 * earth.eqRad_m**2 * cos(self.i_rad) / ((1 - self.e**2)**2 * self.a_m**3.5)
        
    def getAopRate(self):
        """Computes and returns the rate at which the argument of perigee
           processes, in radians per second, as a result of the non-spherical
           Earth's J2 harmonic.
        """
        return -1.5 * earth.mu_m3ps2**0.5 * earth.j2 * earth.eqRad_m**2 * (2.5 * sin(self.i_rad)**2 - 2) / ((1 - self.e**2)**2 * self.a_m**3.5)
        
    def getRaan(self, t_dt=None):
        """Computes the RAAN value of the object (in radians) at the given point
           in time, as propagated by the orbit-averaged mean precession computed
           in the *getRaanRate* method.
        """
        if t_dt is None:
            return self.O_rad
        dt_s = (t_dt - self.tEpoch_dt).total_seconds()
        dRaan_radps = self.getRaanRate()
        return (self.O_rad + dRaan_radps * dt_s) % (2 * pi)
        
    def getAop(self, t_dt=None):
        """Computes the AoP value of the object (in radians) at the given point
           in time, as propagated by the orbit-averaged mean precession computed
           in the *getAopRate* method.
        """
        if t_dt is None:
            return self.w_rad
        dt_s = (t_dt - self.tEpoch_dt).total_seconds()
        dAop_radps = self.getAopRate()
        return (self.w_rad + dAop_radps * dt_s) % (2 * pi)
    
    def getQpqw2eci(self, t_dt=None):
        """Returns a time-varying tranformation matrix that converts vectors
           from the PQW (co-orbital) frame to the earth-centered inertial (ECI)
           frame (w.r.t. the J2000 epochal orientation). This includes the RAAN
           precession and AoP procession rates induced by the J2 harmonic.
        """
        w = rot.Z(self.getAop(t_dt))
        i = rot.X(self.i_rad)
        O = rot.Z(self.getRaan(t_dt))
        return (w.dot(i).dot(O)).transpose()
        
    def getReci(self, t_dt=None):
        """Computes and returns the position of the object, in meters, as
           evaluted in the earth-centered inertial (ECI) frame. This includes
           the RAAN precession and ApP procession rates induced by J2 harmonic.
        """
        rPqw = self.getRpqw(t_dt)
        Qpqw2eci = self.getQpqw2eci(t_dt)
        return Qpqw2eci.dot(rPqw)
        
    @classmethod
    def fromSunSync(cls, T_s):
        """Returns a new MeanJ2 orbit object scaled to a specific inclination
           and altitude to achieve the given period, but with fixed RAAN
           (inclined such that the orbital plane orientation w.r.t. the sun
           remains constant).
        """
        a_m = (T_s * earth.mu_m3ps2**0.5 / (2 * pi))**(2/3)
        dRaan_radps = 2 * pi / earth.tSidYear_s
        d = -1.5 * earth.mu_m3ps2**0.5 * earth.j2 * earth.eqRad_m**2 / a_m**3.5
        i_rad = acos(dRaan_radps / d)
        return cls(a_m=a_m, i_rad=i_rad)
        
    @classmethod
    def fromConstAop(cls, T_s):
        """Determines an eccentric sun-synch orbit from the given period
        """
        a_m = (T_s * earth.mu_m3ps2**0.5 / (2 * pi))**(2/3)
        i_rad = pi - asin(0.8**0.5)
        dRaan_radps = 2 * pi / earth.tSidYear_s
        n = -3 * cos(i_rad) * earth.mu_m3ps2**0.5 * earth.j2 * earth.eqRad_m**2
        d = 2 * dRaan_radps * a_m**3.5
        e = (1 - (n / d)**0.5)**0.5
        return cls(a_m=a_m, e=e, i_rad=i_rad)
    
    @classmethod
    def fromMolniya(cls, lon_rad):
        """Returns a Molniya-style orbit designed to peak at the given longitude
           (in radians). Inclined to match RAAN recession to solar orientation.
        """
        i_rad = 63.4 * pi/180
        w_rad = 270 * pi/180
        T_s = 0.5 * earth.tSidDay_s
        a_m = ((T_s / (2 * pi))**2 * earth.mu_m3ps2)**(1/3)
        o = cls(a_m=a_m, e=0.74105, i_rad=i_rad, w_rad=w_rad)
        o.O_rad = (earth.getGmst(o.tEpoch_dt) + lon_rad) % (2 * pi)
        return o
        
    @classmethod
    def fromTundra(cls, lon_rad):
        """According to some definitions, tundra orbits do not necessarily match
           inclination to eliminate RAAN recession. QZSS, for example, targets
           apogee dwell at a specific latitude. While technically not requiring
           a J2 model, it is implemented here to support cases where the
           inclination (at 63.4 degrees) is choosen to ensure a fixed track.
        """
        i_rad = 63.4 * pi/180
        o = cls(e=0.25, i_rad=i_rad, w_rad=1.5*pi)
        gmst0_rad = earth.getGmst(o.tEpoch_dt)
        o.O_rad = (gmst0_rad + lon_rad - acos(cos(o.i_rad) * cos(o.w_rad)) + pi) % (2 * pi)
        return o
