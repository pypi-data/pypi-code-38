"""Pandas series / dataframe manipulation."""

import pandas as pd
import transforms3d.quaternions as quat
import transforms3d.taitbryan as tf
import numpy as np
import utm


def combine_names(msg_name, new_name):
    """combine msg-name with a new name."""
    if msg_name:
        return "{0}_{1}".format(msg_name, new_name)
    else:
        return new_name


def get_series_quat2euler(q0, q1, q2, q3, msg_name=""):
    """Given pandas series q0-q4, compute series roll, pitch, yaw.

    Arguments:
    q0-q4 -- quaternion entries

    Keyword arguments:
    msg_name -- name of the message for which the euler angles should be computed (default "")

    """
    yaw, pitch, roll = np.array(
        [
            tf.quat2euler([q0i, q1i, q2i, q3i])
            for q0i, q1i, q2i, q3i in zip(q0, q1, q2, q3)
        ]
    ).T

    yaw = pd.Series(
        name=combine_names(msg_name, "yaw"), data=yaw, index=q0.index
    )
    pitch = pd.Series(
        name=combine_names(msg_name, "pitch"), data=pitch, index=q0.index
    )
    roll = pd.Series(
        name=combine_names(msg_name, "roll"), data=roll, index=q0.index
    )
    return roll, pitch, yaw


def angle_wrap_pi(x):
    """wrap angle to [-pi, pi).

    Arguments:
    x -- angle to be wrapped

    """
    return (x - np.pi) % (2 * np.pi) - np.pi


def get_series_quatrot(x, y, z, q0, q1, q2, q3, msg_name=""):
    """Given pandas series x-z and quaternion q0-q4, compute rotated vector x_r, y_r, z_r.

    Arguments:
    x,y,z -- vector to be rotated
    q0-q4 -- quaternion entries. The vector is being rotated with this quaternion

    Keyword arguments:
    rot_name -- name of the rotation

    """
    vec = np.array(
        [
            quat.rotate_vector([xi, yi, zi], [q0i, q1i, q2i, q3i])
            for xi, yi, zi, q0i, q1i, q2i, q3i in zip(x, y, z, q0, q1, q2, q3)
        ]
    )
    x_r = pd.Series(
        name=combine_names(msg_name, "x"), data=vec[:, 0], index=x.index
    )
    y_r = pd.Series(
        name=combine_names(msg_name, "y"), data=vec[:, 1], index=y.index
    )
    z_r = pd.Series(
        name=combine_names(msg_name, "z"), data=vec[:, 2], index=z.index
    )
    return x_r, y_r, z_r


def get_series_quatrot_inverse(x, y, z, q0, q1, q2, q3, msg_name=""):
    """Given pandas series x-z and quaternion q0-q4, compute reversed rotated vector x_r, y_r, z_r.

    Arguments:
    x,y,z -- vector to be rotated
    q0-q4 -- quaternion entries. The vector is being rotated with the inverse of that quaternion

    Keyword arguments:
    rot_name -- name of the rotation

    """
    return get_series_quatrot(x, y, z, q0, -q1, -q2, -q3, msg_name)


def get_series_dot(x0, y0, z0, x1, y1, z1, msg_name=""):
    """Given pandas series x0-z0 and x1-z1, compute dot product.

    Arguments:
    x0, y0, z0 -- first vector
    x1, y1, z1 -- second vector

    Keyword Arguments:
    dotname -- name of the newly created data (default "")

    """
    dot = np.array(
        [
            np.dot([x0i, y0i, z0i], [x1i, y1i, z1i])
            for x0i, y0i, z0i, x1i, y1i, z1i in zip(x0, y0, z0, x1, y1, z1)
        ]
    )
    return pd.Series(
        name=combine_names(msg_name, "dot"), data=dot, index=x0.index
    )


def get_series_norm_2d(x0, y0, msg_name=""):
    """Given pandas series x0-y0, compute norm.

    Arguments:
    x0 -- first pandas series
    y0 -- second pandas series

    Keyword Arguments:
    dotname -- name of the newly created data (default "")
    """
    norm = np.array(
        [np.linalg.norm([x0i, y0i], axis=0) for x0i, y0i in zip(x0, y0)]
    )
    return pd.Series(
        name=combine_names(msg_name, "norm"), data=norm, index=x0.index
    )


def get_series_utm(lat, lon, msg_name=""):
    """Given pandas series lat/lon in degrees, compute UTM easting/northing/zone.

    Arguments:
    lat -- latitude
    lon -- longitude

    Keyword Arguments:
    msg_name -- name of the newly created data (default "")

    """
    easting, northing, zone, letter = np.array(
        [utm.from_latlon(lati, loni) for lati, loni in zip(lat, lon)]
    ).T

    easting = pd.Series(
        name=combine_names(msg_name, "easting"),
        data=easting.astype(np.float),
        index=lat.index,
    )
    northing = pd.Series(
        name=combine_names(msg_name, "northing"),
        data=northing.astype(np.float),
        index=lat.index,
    )
    zone = pd.Series(
        name=combine_names(msg_name, "zone"),
        data=zone.astype(np.float),
        index=lat.index,
    )
    return easting, northing, zone


def get_z_axis_from_attitude(q0, q1, q2, q3, msg_name=""):
    """Compute the desired body z axis in world coordinate system.

    Arguments:
    q0 -- pandas time series quaternion element 0
    q1 -- pandas time series queternion element 1
    q2 -- pandas time series quaternion element 2
    q3 -- pandas time series quaternion element 3

    Keyword Arguments:
    msg_name -- name of the newly created data (default "")

    """
    x = pd.Series(
        np.zeros(q0.shape[0]),
        index=q0.index,
        name=combine_names(msg_name, "z_axis_x"),
    )
    y = pd.Series(
        np.zeros(q0.shape[0]),
        index=q0.index,
        name=combine_names(msg_name, "z_axis_y"),
    )
    z = pd.Series(
        np.ones(q0.shape[0]),
        index=q0.index,
        name=combine_names(msg_name, "z_axis_z"),
    )

    x, y, z = get_series_quatrot(x, y, z, q0, q1, q2, q3)
    return x, y, z


def get_tilt_from_attitude(q0, q1, q2, q3, msg_name=""):
    """Compute desired tilt angle and add it to the dataframe.

    Arguments:
    q0 -- pandas time series quaternion element 0
    q1 -- pandas time series queternion element 1
    q2 -- pandas time series quaternion element 2
    q3 -- pandas time series quaternion element 3

    Keyword Arguments:
    msg_name -- name of the newly created data (default "")

    """
    z_x, z_y, z_z = get_z_axis_from_attitude(q0, q1, q2, q3)

    x = pd.Series(np.zeros(q0.shape[0]), index=q0.index, name="x")
    y = pd.Series(np.zeros(q0.shape[0]), index=q0.index, name="y")
    z = pd.Series(np.ones(q0.shape[0]), index=q0.index, name="z")

    tilt = get_series_dot(x, y, z, z_x, z_y, z_z, msg_name)
    tilt.where(
        tilt < 1, 1, inplace=True
    )  # ensure that angle 1 is never exceeded
    return tilt.apply(np.arccos)


def get_normalize_2d_vector(x, y, msg_name=""):
    """Normalize 2D vector.

    Arguments:
    x -- pandas time series x component of vector
    y -- pandas time series y component of vector

    Keyworkd Arguments:
    msg_name -- name of the newly created data (default "")

    """
    norm = get_series_norm_2d(x, y, msg_name=msg_name)
    norm[norm <= np.finfo(np.float64).eps] = np.finfo(np.float64).eps

    x_n = x / norm
    y_n = y / norm
    return x_n, y_n


def get_heading_from_2d_vector(north, east, msg_name=""):
    """Compute the heading (0 heading = North) from a 2D vector.

    0 Heading = north is only true if north/east is aligned with GPS coordinate system.

    Arguments:
    x -- pandas time series x component of vector
    y -- pandas time series y component of vector

    Keyworkd Arguments:
    msg_name -- name of the newly created data (default "")

    """
    x_n, y_n = get_normalize_2d_vector(north, east, msg_name)
    return np.sign(y_n) * angle_wrap_pi(np.arccos(x_n))
