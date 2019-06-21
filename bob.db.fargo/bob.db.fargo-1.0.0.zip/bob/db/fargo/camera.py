#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import json
import numpy as np

def points_to_color(points, intrinsics):
    x = points[0] / points[2]
    y = points[1] / points[2]
    r2 = x * x + y * y
    f = 1 + intrinsics.k[0] * r2 + intrinsics.k[1] * r2 * r2 +\
        intrinsics.k[4] * r2 * r2 * r2
    x *= f
    y *= f
    dx = x + 2 * intrinsics.k[2] * x * y + intrinsics.k[3] * (r2 + 2 * x * x)
    dy = y + 2 * intrinsics.k[3] * x * y + intrinsics.k[2] * (r2 + 2 * y * y)
    x = dx
    y = dy
    return (x * intrinsics.f_c + intrinsics.c_0,
            y * intrinsics.f_r + intrinsics.r_0)


def point_to_color(point, intrinsics):
    x = point[0] / point[2]
    y = point[1] / point[2]
    r2 = x * x + y * y
    f = 1 + intrinsics.k[0] * r2 + intrinsics.k[1] * r2 * r2 +\
        intrinsics.k[4] * r2 * r2 * r2
    x *= f
    y *= f
    dx = x + 2 * intrinsics.k[2] * x * y + intrinsics.k[3] * (r2 + 2 * x * x)
    dy = y + 2 * intrinsics.k[3] * x * y + intrinsics.k[2] * (r2 + 2 * y * y)
    x = dx
    y = dy
    return np.float32([x * intrinsics.f_c + intrinsics.c_0,
                       y * intrinsics.f_r + intrinsics.r_0])


def depth_to_points(depth_map, scale, intrinsics):
    c, r = np.meshgrid(range(depth_map.shape[1]), range(depth_map.shape[0]))
    x = (c - intrinsics.c_0) / intrinsics.f_c
    y = (r - intrinsics.r_0) / intrinsics.f_r
    r2 = x * x + y * y
    f = 1 + intrinsics.k[0] * r2 +\
        intrinsics.k[1] * r2 * r2 + intrinsics.k[4] * r2 * r2 * r2
    ux = x * f + 2 * intrinsics.k[2] * x * y +\
        intrinsics.k[3] * (r2 + 2 * x * x)
    uy = y * f + 2 * intrinsics.k[3] * x * y +\
        intrinsics.k[2] * (r2 + 2 * y * y)
    x = ux * scale * depth_map
    y = uy * scale * depth_map
    z = scale * depth_map
    return x, y, z


def depth_to_point(r, c, depth, scale, intrinsics):
    x = (c - intrinsics.c_0) / intrinsics.f_c
    y = (r - intrinsics.r_0) / intrinsics.f_r
    r2 = x * x + y * y
    f = 1 + intrinsics.k[0] * r2 +\
        intrinsics.k[1] * r2 * r2 + intrinsics.k[4] * r2 * r2 * r2
    ux = x * f + 2 * intrinsics.k[2] * x * y +\
        intrinsics.k[3] * (r2 + 2 * x * x)
    uy = y * f + 2 * intrinsics.k[3] * x * y +\
        intrinsics.k[2] * (r2 + 2 * y * y)
    x = ux
    y = uy
    return np.float32([depth * scale * x, depth * scale * y, depth * scale])


def transform_points(points, extrinsics):
    return (extrinsics.rotation[0] * points[0] +
            extrinsics.rotation[3] * points[1] +
            extrinsics.rotation[6] * points[2] +
            extrinsics.translation[0],
            extrinsics.rotation[1] * points[0] +
            extrinsics.rotation[4] * points[1] +
            extrinsics.rotation[7] * points[2] +
            extrinsics.translation[1],
            extrinsics.rotation[2] * points[0] +
            extrinsics.rotation[5] * points[1] +
            extrinsics.rotation[8] * points[2] +
            extrinsics.translation[2])


def transform_point(point, extrinsics):
    return np.float32([extrinsics.rotation[0] * point[0] +
                       extrinsics.rotation[3] * point[1] +
                       extrinsics.rotation[6] * point[2] +
                       extrinsics.translation[0],
                       extrinsics.rotation[1] * point[0] +
                       extrinsics.rotation[4] * point[1] +
                       extrinsics.rotation[7] * point[2] +
                       extrinsics.translation[1],
                       extrinsics.rotation[2] * point[0] +
                       extrinsics.rotation[5] * point[1] +
                       extrinsics.rotation[8] * point[2] +
                       extrinsics.translation[2]])


def get_UV_map(depth_image, min_depth, depth_intrinsics, depth_scale,
               color_intrinsics, depth2color):
    depth_points = depth_to_points(depth_image, depth_scale, depth_intrinsics)
    depth_points = np.where(depth_image >= min_depth, depth_points, np.nan)
    color_points = transform_points(depth_points, depth2color)
    color_pixels = points_to_color(color_points, color_intrinsics)
    return (np.clip(color_pixels[0] / color_intrinsics.width, 0, 1),
            np.clip(color_pixels[1] / color_intrinsics.height, 0, 1))


def get_correspondences(points, UV_map, color_width, color_height, depth_width, depth_height):

    x = points[:, 0].reshape((1, -1)) - np.array(UV_map[0] * color_width).ravel().reshape((-1, 1))
    y = points[:, 1].reshape((1, -1)) - np.array(UV_map[1] * color_height).ravel().reshape((-1, 1))
    dist2 = x * x + y * y
    return np.nanmin(dist2, 0), np.nanargmin(dist2, 0)


class IntrinsicParameters:
    def __init__(self, width=None, height=None, c_0=None, r_0=None, f_c=None,
                 f_r=None, k=None, model=None, fov_h=None, fov_v=None):
        self.width = width
        self.height = height
        self.c_0 = c_0
        self.r_0 = r_0
        self.f_c = f_c
        self.f_r = f_r
        self.k = k
        self.model = model
        self.fov_h = fov_h
        self.fov_v = fov_v

    def read_json(self, filepath, key):
        with open(filepath) as json_file:
            device_info = json.load(json_file)
        device_info = device_info['device']
        if key not in device_info:
            raise ValueError('{} not in {}'.format(key, filepath))
        device_info = device_info[key]
        resolution = device_info['resolution']
        principal_point = device_info['principal_point']
        focal = device_info['focal']
        if 'distortion' in device_info:
            dist_coeffs = np.array(device_info['distortion']['coeffs'])
            if 'type' in device_info['distortion']:
                dist_model = device_info['distortion']['type']
            else:
                dist_model = 'unknown'
        else:
            dist_coeffs = np.zeros((5, 1), dtype=np.float32)
            dist_model = None
        fov = device_info['field_of_view']
        self.width = resolution[0]
        self.height = resolution[1]
        self.c_0 = principal_point[0]
        self.r_0 = principal_point[1]
        self.f_c = focal[0]
        self.f_r = focal[1]
        self.k = dist_coeffs
        self.model = dist_model
        self.fov_h = fov[0]
        self.fov_v = fov[1]


class ExtrinsicParameters:
    def __init(self, translation=None, rotation=None):
        self.translation = translation
        self.rotation = rotation

    def read_json(self, filepath, key):
        with open(filepath) as json_file:
            device_info = json.load(json_file)
        device_info = device_info['device']
        if key not in device_info:
            raise ValueError('{} not in {}'.format(key, filepath))
        device_info = device_info[key]
        self.translation = np.float32(device_info['translation']) * 1e-3
        self.rotation = np.float32(device_info['rotation'])
