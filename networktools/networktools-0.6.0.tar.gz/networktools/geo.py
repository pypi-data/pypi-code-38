import math as mt
import math
from math import sin, cos
from numpy import matrix
import numpy as np
from networktools.colorprint import gprint, bprint, rprint


"""
Some special functions for geometric and geodesic use

"""
r2d = 180/math.pi


def excentricity(a0, b0):
    assert a0 >= b0, "a must be a superior value over b"
    aux = b0/a0
    return math.sqrt(1. - aux*aux)


ecuatorial = 6378.137e3
polar = 6356.75231424e3
a = ecuatorial
b = polar
e = excentricity(a, b)
f = (a-b)/a
e_2 = e*e
dg2rd = math.pi/180
rd2dg = 180/math.pi


def rad2deg(rlat, rlon):
    dlat = math.degrees(rlat)
    dlon = math.degrees(rlon)
    return (dlat, dlon)


def deg2rad(dlat, dlon):
    rlat = math.radians(dlat)
    rlon = math.radians(dlon)
    return (rlat, rlon)


def radius(latitude):  # latitude in radians
    sin_lat = math.sin(latitude)
    dex = math.pow(e, 2)
    N = ecuatorial/math.sqrt(1-dex*math.pow(sin_lat, 2))
    M = ecuatorial*(1-dex)/math.sqrt(math.pow(1-dex*math.pow(sin_lat, 2), 3))
    RADIUS = math.sqrt(M*N)
    return [RADIUS, N, M]


def sph_rotation_matrix(lat, lon):
    phi = lat  # rads
    lamb = lon  # rads
    rho_ = [cos(phi)*cos(lamb), cos(phi)*sin(lamb), sin(phi)]
    phi_ = [-sin(phi)*cos(lamb), -sin(phi)*cos(phi), cos(phi)]
    lamb_ = [-sin(lamb), cos(lamb), 0]
    R = matrix([lamb_, phi_, rho_])
    return R


def llh2ecef(LAT, LON, elev):
    # Source: https://www.mathworks.com/help/aeroblks/llatoecefposition.html
    lambda_s = math.atan(math.pow(1-f, 2)*math.tan(LAT))
    rs = a/math.sqrt(1+((1/math.pow(1-f, 2))-1) *
                     math.pow(math.sin(lambda_s), 2))
    x = (rs+elev)*math.cos(lambda_s)*math.cos(LON)
    y = (rs*math.cos(lambda_s)+elev*math.cos(LAT)) * math.sin(LON)
    z = rs*math.sin(lambda_s)+elev*math.sin(LON)
    return [x, y, z]


def ecef2llh(x, y, z):
    # ECEF coordinates to (longitude, latitude, ellipsoidal_height)
    aux = mt.sqrt(x*x + y*y)
    alpha = aux/a
    beta = z/aux
    # mu = tan(phi)
    mu = beta
    aux1 = beta - mu*(1 - e_2/(alpha*mt.sqrt(1 + mu*mu*(1.0 - e_2))))
    while abs(aux1) > 1.0e-12:
        mu2 = mu*mu
        aux2 = mt.sqrt(1 + mu2*(1.0 - e_2))
        aux1 = beta - mu*(1 - e_2/(alpha*aux2))
        mu += aux1/(1 - e_2/(alpha*aux2*aux2*aux2))
    mu2 = mu*mu
    lon, lat = rd2dg*mt.atan2(y, x) % 360, rd2dg*mt.atan(mu)
    if lon > 180:
        lon -= 360
    return lon, lat, mt.sqrt(1 + mu2)*(aux - a/mt.sqrt(1 + mu2*(1 - e_2)))


def ecef2neu(P0, dx, dy, dz):
    lat0 = P0[0]
    lon0 = P0[1]
    h0 = P0[2]
    pi = math.pi
    sin_lat0 = math.sin(lat0)
    sin_lon0 = math.sin(lon0)
    cos_lat0 = math.cos(lat0)
    cos_lon0 = math.cos(lon0)
    nt = -sin_lat0*cos_lon0*dx-sin_lat0 * \
        sin_lon0*dy+cos_lat0*dz  # [m]
    et = -sin_lon0*dx+cos_lon0*dy  # [m]
    ut = cos_lat0*cos_lon0*dx+cos_lat0 * \
        sin_lon0*dy+sin_lat0*dz  # [m]
    return dict(N=nt, E=et, U=ut)


def get_from_ecef(ECEF_DATA):
    x = None
    y = None
    z = None
    try:
        #rprint("PRE ECEF: %s" %ECEF_DATA, flush =True)
        ecef = ECEF_DATA['ECEF']
        #gprint("ECEF: %s" %ecef)
        if 'X' in ecef:
            x = ecef['X']
            y = ecef['Y']
            z = ecef['Z']
        elif 'X_POS' in ecef:
            x = ecef['X_POS']
            y = ecef['Y_POS']
            z = ecef['Z_POS']
    except Exception as ex:
        print("get from ecef execption %s" % ex)
        raise ex
    return [x, y, z]


def get_vcv_matrix(VCV):
    xx = VCV['VCV_XX']
    yy = VCV['VCV_YY']
    zz = VCV['VCV_ZZ']
    xy = VCV['VCV_XY']
    xz = VCV['VCV_XZ']
    yz = VCV['VCV_YZ']
    cov_xyz = np.array([[xx, xy, xz],
                        [xy, yy, yz],
                        [xz, yz, zz]])
    return cov_xyz


def rotate_vcv(R, VCV):
    return R.dot(VCV.dot(R.T))


def vcv2dict(C):
    return {'EE': C[0][0],
            'EN': C[0][1],
            'EU': C[0][2],
            'NN': C[1][1],
            'NU': C[1][2],
            'UU': C[2][2], }


def all_in_one_vcv(R, POSITION_VCV):
    vcv = get_vcv_matrix(POSITION_VCV)
    C = rotate_vcv(R, vcv)
    vcv_dict = vcv2dict(C)
    return vcv_dict

# @Poncho: Fco del campo::::>


def trig(alpha):
    r"""Cosine and sine of an angle.

    :param alpha: angle :math:`\alpha` in radians.
    :return: :math:`\cos\alpha, \, \sin\alpha`
    """
    if isinstance(alpha, float):
        return mt.cos(alpha), mt.sin(alpha)
    else:
        return np.cos(alpha), np.sin(alpha)


def ecef2enu_rot(lon, lat):
    r"""
    Rotation matrix from ECEF to local coordinates.

    Rotation matrix from Earth-centered earth-fixed Coordinates to
    (east, north, up). As input, uses longitude and latitude of the point
    where the transformation wants to be applied.

    .. math::
        R_{ecef2enu}(\lambda, \varphi) = \begin{bmatrix}
        -\sin\lambda & \cos\lambda & 0 \\
        -\sin\varphi\cos\lambda & -\sin\varphi\sin\lambda & \cos\varphi \\
        \cos\varphi\cos\lambda & \cos\varphi\sin\lambda & \sin\varphi
        \end{bmatrix}

        \vec{r}_{enu} = R_{ecef2enu}(\lambda, \varphi) \vec{r}_{ecef}

    :param lon: longitude in degrees :math:`\lambda`.
    :param lat: latitude in degrees :math:`\varphi`
    :type lon: float
    :type lat: float
    :return: rotation matrix :math:`R_{ecef2enu}(\varphi, \lambda)`.
    :rtype: numpy.ndarray [3][3]
    """
    cos_lon, sin_lon = trig(lon*dg2rd)
    cos_lat, sin_lat = trig(lat*dg2rd)
    return ecef2enu_rot_tr(cos_lon, sin_lon, cos_lat, sin_lat)


def ecef2enu_rot_tr(cos_lon, sin_lon, cos_lat, sin_lat):
    r"""
    Rotation matrix from ECEF to local coordinates.

    Rotation matrix from Earth-centered earth-fixed Coordinates to
    (east, north, up). As input, uses trigonometric functions of longitude and
    latitude of the point where the transformation wants to be applied.

    .. math::
        R_{ecef2enu}(\lambda, \varphi) = \begin{bmatrix}
        -\sin\lambda & \cos\lambda & 0 \\
        -\sin\varphi\cos\lambda & -\sin\varphi\sin\lambda & \cos\varphi \\
        \cos\varphi\cos\lambda & \cos\varphi\sin\lambda & \sin\varphi
        \end{bmatrix}

        \vec{r}_{enu} = R_{ecef2enu}(\lambda, \varphi) \vec{r}_{ecef}

    :param cos_lon: cosine of longitude :math:`\cos\lambda`.
    :param sin_lon: sine of longitude :math:`\sin\lambda`.
    :param cos_lat: cosine of latitude :math:`\cos\varphi`.
    :param sin_lat: sine of latitude :math:`\sin\varphi`.
    :type cos_lon: float
    :type sin_lon: float
    :type cos_lat: float
    :type sin_lat: float
    :return: rotation matrix :math:`R_{ecef2enu}(\varphi, \lambda)`.
    :rtype: numpy.ndarray [3][3]
    """
    e_, n_, v_ = enu_tr(cos_lon, sin_lon, cos_lat, sin_lat)
    return np.append([e_, n_], [v_], axis=0)


def east_north_up(lon, lat):
    r"""East, north and vertical directions in ECEF coordinates.

    :param lon: longitude :math:`\lambda` in degrees.
    :param lat: latitude :math:`\varphi` in degrees.
    :type lon: float
    :type lat: float
    :return: unit east :math:`\hat{e}`, north :math:`\hat{n}` and up
        :math:`\hat{z}` directions. See :py:mod:`east_st`, :py:mod:`north_st`
        and :py:mod:`up_st` functions.
    :rtype: numpy.ndarray [3]
    """
    return enu_tr(*(trig(dg2rd*lon) + trig(dg2rd*lat)))


def enu_tr(cos_lon, sin_lon, cos_lat, sin_lat):
    r"""East, north and up directions in ECEF coordinates.

    :param cos_lon: cosine of longitude :math:`\cos\lambda`.
    :param sin_lon: sine of longitude :math:`\sin\lambda`.
    :param cos_lat: cosine of latitude :math:`\cos\varphi`.
    :param sin_lat: sine of latitude :math:`\sin\varphi`.
    :type cos_lon: float
    :type sin_lon: float
    :type cos_lat: float
    :type sin_lat: float
    :return: unit east :math:`\hat{e}`, north :math:`\hat{n}` and up
        :math:`\hat{z}` directions. See :py:mod:`east_`, :py:mod:`north_` and
        :py:mod:`up_` functions.
    :rtype: numpy.ndarray [3]
    """
    return (east_tr(cos_lon, sin_lon),
            north_tr(cos_lon, sin_lon, cos_lat, sin_lat),
            up_tr(cos_lon, sin_lon, cos_lat, sin_lat))


def east_tr(cos_lon, sin_lon):
    r"""East direction in ECEF coordinates.

    .. math::
        \hat{e} = \begin{bmatrix} -\sin\lambda \\ \cos\lambda \\ 0
        \end{bmatrix}

    :param cos_lon: cosine of longitude :math:`\cos\lambda`.
    :param sin_lon: sine of longitude :math:`\sin\lambda`.
    :type cos_lon: float
    :type sin_lon: float
    :return: unit east direction :math:`\hat{e}`.
    :rtype: numpy.ndarray [3]
    """
    return np.array([-sin_lon, cos_lon, 0.0])


def north_tr(cos_lon, sin_lon, cos_lat, sin_lat):
    r"""North direction in ECEF coordinates.

    .. math::
        \hat{n} = \begin{bmatrix}
        -\sin\varphi\cos\lambda \\ -\sin\varphi\sin\lambda \\ \cos\varphi
        \end{bmatrix}

    :param cos_lon: cosine of longitude :math:`\cos\lambda`.
    :param sin_lon: sine of longitude :math:`\sin\lambda`.
    :param cos_lat: cosine of latitude :math:`\cos\varphi`.
    :param sin_lat: sine of latitude :math:`\sin\varphi`.
    :type cos_lon: float
    :type sin_lon: float
    :type cos_lat: float
    :type sin_lat: float
    :return: unit north direction :math:`\hat{n}`.
    :rtype: numpy.ndarray [3]
    """
    return np.array([-sin_lat*cos_lon, -sin_lat*sin_lon, cos_lat])


def up_tr(cos_lon, sin_lon, cos_lat, sin_lat):
    r"""Upwards vertical direction in ECEF coordinates.

    .. math::
        \hat{z} = \begin{bmatrix}
        \cos\varphi\cos\lambda \\ \cos\varphi\sin\lambda \\ \sin\varphi
        \end{bmatrix}

    :param cos_lon: cosine of longitude :math:`\cos\lambda`.
    :param sin_lon: sine of longitude :math:`\sin\lambda`.
    :param cos_lat: cosine of latitude :math:`\cos\varphi`.
    :param sin_lat: sine of latitude :math:`\sin\varphi`.
    :type cos_lon: float
    :type sin_lon: float
    :type cos_lat: float
    :type sin_lat: float
    :return: unit up direction :math:`\hat{z}`.
    :rtype: numpy.ndarray [3]
    """
    return np.array([cos_lat*cos_lon, cos_lat*sin_lon, sin_lat])
