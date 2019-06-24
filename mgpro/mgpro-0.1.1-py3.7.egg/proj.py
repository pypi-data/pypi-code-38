import pyproj
import numpy as np
import argparse


def latlon2geo(raw_data, init='epsg:3857'):
    # raw_data = np.loadtxt(xyz_file)
    gcs = pyproj.Proj(proj='latlong', datum='WGS84')
    pcs = pyproj.Proj(init=init)
    px, py = pyproj.transform(gcs, pcs, raw_data[:, 0], raw_data[:, 1])
    proj_data = np.vstack((px, py, raw_data[:, 2])).T
    return proj_data


def geo2latlon(proj_data, init='epsg:3857'):
    pcs = pyproj.Proj(init=init)
    lons, lats = pcs(proj_data[:, 0], proj_data[:, 1], inverse=True)
    geo_data = np.vstack((lons, lats, proj_data[:, 2])).T
    return geo_data


def exec():
    parser = argparse.ArgumentParser(description="Convertor for lat & long coordinates and projected systems")
    parser.add_argument('-o', help='Path to output file ', required=True, dest='path', type=str)
    parser.add_argument('-I', help='If \'-I\' is specified, projected systems convert to lat & long coordinates',
                        action='store_true', default=False)
    parser.add_argument('-c', help='Coordinates code for projected system. (default = epsg:3857)',
                        type=str, default='epsg:3857', dest='init')
    parser.add_argument('in_file', help='Path to input table file', type=str)
    arg = parser.parse_args()
    try:
        data = np.loadtxt(arg.in_file)
    except Exception as e:
        raise IOError('{}\n{} not found or in error format'.format(e, arg.in_file))
    if arg.I:
        out_data = geo2latlon(data, init=arg.init)
    else:
        out_data = latlon2geo(data, init=arg.init)
    np.savetxt(arg.path, out_data)


if __name__ == '__main__':
    exec()
