import numpy as np
from mgpro import expand
from mgpro.proj import *
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from scipy.fftpack import fft2, fftshift, ifft2, ifftshift
from scipy.interpolate import griddata
import argparse


def msg():
    return '''
    Usage: mgpro.py -c<conti>/<diff> -d <dx>/<dy> -o <out_path> [-R <xmin/<xmax>/<ymix>/<ymax>]
    '''


def cal_pos(max_len, len_x, len_y):
    if max_len > 1 or max_len < 0:
        raise ValueError('Input arg of max_len must be in the range of 0 to 1')
    if len_x > len_y:
        width = max_len
        hight = max_len * (len_y / len_x)
    else:
        hight = max_len
        width = max_len * (len_x / len_y)
    return width, hight


def xyz2grd(raw_data, dx, dy, xy_limit=None):
    data = raw_data.copy()
    data[:, [0, 1]] = data[:, [1, 0]]
    if xy_limit is None:
        xmin = np.min(raw_data[:, 0])
        xmax = np.max(raw_data[:, 0])
        ymin = np.min(raw_data[:, 1])
        ymax = np.max(raw_data[:, 1])
    else:
        xmin, xmax, ymin, ymax = xy_limit
    xrange = np.arange(xmin, xmax, dx)
    yrange = np.arange(ymin, ymax, dy)
    ymesh, xmesh = np.meshgrid(yrange, xrange, indexing='ij')
    grid_data = griddata(data[:, 0:2], data[:, 2], (ymesh, xmesh))
    return xrange, yrange, grid_data


def norm_uv(data, dx, dy):
    (len_row, len_col) = data.shape
    dom_row = 2 * np.pi / len_row / dy
    dom_col = 2 * np.pi / len_col / dx
    row = np.arange(1, len_row+1)
    col = np.arange(1, len_col+1)
    row0 = int(len_row / 2) + 1
    col0 = int(len_col / 2) + 1
    (col_mesh, row_mesh) = np.meshgrid(col, row)
    u = (col_mesh - col0)*dom_col
    v = (row_mesh - row0)*dom_row
    return u, v


class JetNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        if midpoint is None:
            self.midpoint = [0.2, 0.4, 0.6, 0.8]
        else:
            try:
                self.midpoint = list(midpoint)
            except Exception as e:
                raise ValueError(e)
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin] + self.midpoint + [self.vmax], np.linspace(0, 1, len(self.midpoint)+2)
        return np.ma.masked_array(np.interp(value, x, y))


class mgmat(object):
    def __init__(self, file, dx, dy, xy_limit=None, to_geo=False):
        self.dx = dx
        self.dy = dy
        in_data = np.loadtxt(file)
        if to_geo:
            in_data = latlon2geo(in_data)
        self.x, self.y, self.data = xyz2grd(in_data, dx, dy, xy_limit=xy_limit)
        self.data_expand, self.row_begin, self.row_end, self.col_begin, self.col_end = expand.expand(self.data)
        self.data_sf = fftshift(fft2(self.data_expand))
        self.h = None
        self.order = None
        self.result = np.array([])

    def continuation(self, h, order):
        self.h = h
        self.order = order
        u, v = norm_uv(self.data_sf, self.dx, self.dy)
        H = np.sqrt(u**2+v**2) ** order * np.exp(h * np.sqrt(u**2+v**2))
        result = np.real(ifft2(ifftshift(H * self.data_sf)))[self.row_begin: self.row_end + 1, self.col_begin: self.col_end + 1]
        return result

    def gradient(self, degree):
        data_expand = np.flipud(self.data_expand)
        if degree == '0':
            grad = -np.diff(data_expand, axis=0)[self.row_begin: self.row_end + 1, self.col_begin: self.col_end + 1]
            grad /= self.dy
        elif degree == '90':
            grad = np.diff(data_expand, axis=1)[self.row_begin: self.row_end + 1, self.col_begin: self.col_end + 1]
            grad /= self.dx
        elif degree == 'mod':
            ns = -np.diff(data_expand, axis=0)[self.row_begin: self.row_end + 1, self.col_begin: self.col_end + 1]
            we = np.diff(data_expand, axis=1)[self.row_begin: self.row_end + 1, self.col_begin: self.col_end + 1]
            grad = np.sqrt(ns**2 + we**2)
        elif degree == '45':
            grad = np.zeros_like(data_expand)
            for _i in range(self.row_begin, self.row_end + 1):
                for _j in range(self.col_begin, self.col_end + 1):
                    grad[_i, _j] = data_expand[_i, _j] - data_expand[_i-1, _j+1]
            grad = grad[self.row_begin: self.row_end + 1, self.col_begin: self.col_end + 1] / np.sqrt(self.dx**2 + self.dy**2)
        elif degree == '135':
            grad = np.zeros_like(data_expand)
            for _i in range(self.row_begin, self.row_end + 1):
                for _j in range(self.col_begin, self.col_end + 1):
                    grad[_i, _j] = data_expand[_i, _j] - data_expand[_i-1, _j-1]
            grad = grad[self.row_begin: self.row_end + 1, self.col_begin: self.col_end + 1] / np.sqrt(self.dx**2 + self.dy**2)
        grad = np.flipud(grad)*1000
        return grad

    def dt2za(self, i0, d0):
        P0 = np.cos(np.deg2rad(i0)) * np.cos(np.deg2rad(d0))
        Q0 = np.cos(np.deg2rad(i0)) * np.sin(np.deg2rad(d0))
        R0 = np.sin(np.deg2rad(i0))
        u, v = norm_uv(self.data_sf, self.dx, self.dy)
        phi = np.sqrt(u**2 + v**2) / ((P0*u + Q0*v)*1j + R0*np.sqrt(u**2 + v**2))
        result = np.real(ifft2(ifftshift(phi * self.data_sf)))[self.row_begin: self.row_end + 1, self.col_begin: self.col_end + 1]
        return result

    def pltmap(self, fig, data, breakpoint=None):
        f_width = fig.get_figwidth()
        f_height = fig.get_figheight()
        frac_w = min([f_height, f_width])/max([f_height, f_width])
        real_width, real_height = cal_pos(0.7, data.shape[1], data.shape[0])
        real_width *= frac_w
        fig.clf()
        ax_raw = fig.gca()
        pcm = ax_raw.pcolor(data, cmap='jet')
        # ax_raw.figure.canvas.draw()
        cb = fig.colorbar(pcm, extend='both')
        # ax_raw.set_position([.1, .125, real_width, real_height], which='original')
        # cb.ax.set_position([.8, .1, real_height/6.27, real_height])
        fig.canvas.draw()

    def savetxt(self, filename, result, to_latlon=False):
        points = np.zeros([result.size, 3])
        m = 0
        for i, x in enumerate(self.x):
            for j, y in enumerate(self.y):
                points[m, 0] = x
                points[m, 1] = y
                points[m, 2] = result[j, i]
                m += 1
        if to_latlon:
            points = geo2latlon(points)
        np.savetxt(filename, points, fmt='%.4f %.4f %.6f')


if __name__ == '__main__':
    mg = mgmat('/Users/xumj/Codes/MGPro/example/mag_proj.dat', 2000, 2000)
    mg.dt2za(46, -1)

    # exec()
