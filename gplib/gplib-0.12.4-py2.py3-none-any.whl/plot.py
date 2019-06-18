# -*- coding: utf-8 -*-
#
#    Copyright 2019 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D

plt.style.use('ggplot')


class Plot(object):

    @staticmethod
    def kernel(kernel, data=None, file_name=None):
        """
        Plot a kernel implementation

        :param kernel:
        :type kernel:
        :param data:
        :type data:
        :param file_name:
        :type file_name:
        :return:
        :rtype:
        """

        if data is None:
            data = np.linspace(-3.0, 3.0, 201)[:, None]
            index_mode = False
        else:
            index_mode = True

        middle_index = int(data.shape[0] * 0.5)
        middle_data = data[middle_index, :][None, :]

        plt.figure(figsize=(11, 4))
        plt.clf()
        plt.suptitle(kernel.__class__.__name__)
        plt.subplot(121)
        covar = kernel.marginalize_covariance(data, middle_data)
        covar = covar.reshape(-1)
        if index_mode:
            half_label = np.arange(0, data.shape[0])
            middle_label = middle_index
        else:
            half_label = data
            middle_label = middle_data[0, 0]
        plt.plot(half_label, covar, linestyle='-', color='#1f77b4', ms=40)
        plt.xlabel("input, x")
        plt.ylabel("covariance, k(x, {})".format(middle_label))

        plt.subplot(122)
        covar = kernel.marginalize_covariance(data, data)
        covar = np.flip(covar, 0)
        if index_mode:
            extent = [0, data.shape[0], 0, data.shape[0]]
        else:
            min_data = np.min(data)
            max_data = np.max(data)
            extent = [min_data, max_data, min_data, max_data]
        plt.imshow(
            covar,
            cmap='Blues',
            interpolation='none',
            extent=extent
        )
        cb = plt.colorbar()
        cb.set_label("covariance, k(x, x')")
        plt.xlabel("input, x")
        plt.ylabel("input, x'")
        if file_name is None:
            plt.show()
        else:
            plt.savefig(file_name, bbox_inches='tight')
            plt.close()

    @staticmethod
    def gp_1d(gp, data=None, test_data=None, file_name=None, n_samples=0):
        """
        Plot gp in 1D

        :param gp:
        :type gp:
        :param data:
        :type data:
        :param test_data:
        :type test_data:
        :param file_name:
        :type file_name:
        :param n_samples:
        :type n_samples:
        :return:
        :rtype:
        """
        plt.figure(figsize=(5, 4))

        show_data, min_values, max_values, diff_values = \
            Plot._get_plot_bounds(data, test_data)

        plot_points = np.arange(
            min_values[0],
            max_values[0],
            diff_values[0] / 500.0
        )[:, None]

        mean = gp.mean_function.marginalize_mean(
            plot_points)

        var = gp.covariance_function.marginalize_covariance(
            plot_points, only_diagonal=True)

        sdev = 3.0 * np.sqrt(var)

        plt.clf()
        if 0 < n_samples:
            posterior_samples = gp.sample(plot_points, n_samples=n_samples)
            plt.plot(
                plot_points.flatten().tolist(),
                posterior_samples, color='#1f77b4', linewidth=0.5
            )
        plt.plot(
            plot_points.flatten().tolist(),
            mean.flatten().tolist(), color='#1f77b4', linewidth=2
        )
        ax = plt.gca()
        ax.fill_between(
            plot_points.flatten().tolist(),
            (mean - sdev).flatten().tolist(),
            (mean + sdev).flatten().tolist(),
            color='#aec7e8'
        )
        if show_data is not None:
            plt.plot(
                show_data['X'].flatten().tolist(),
                show_data['Y'].flatten().tolist(), color='#444444',
                linestyle='None', marker='o', markersize=4
            )
        if test_data is not None:
            plt.plot(
                test_data['X'].flatten().tolist(),
                test_data['Y'].flatten().tolist(), color='#d62728',
                linestyle='None', marker='^', markersize=4
            )

        if file_name is None:
            plt.show()
        else:
            plt.savefig(file_name, bbox_inches='tight')
            plt.close()

    @staticmethod
    def gp_2d(gp, data=None, test_data=None, resolution=40, file_name=None):
        """
        Plot gp in 2D

        :param resolution:
        :type resolution:
        :param test_data:
        :type test_data:
        :param file_name:
        :type file_name:
        :param data:
        :type data:
        :param gp:
        :type gp:
        :return:
        :rtype:
        """
        show_data, min_values, max_values, _ = \
            Plot._get_plot_bounds(data, test_data)

        # Init grid
        x_grid = np.linspace(min_values[0], max_values[0], resolution)
        y_grid = np.linspace(min_values[1], max_values[1], resolution)
        x_grid, y_grid = np.meshgrid(x_grid, y_grid)
        plot_points = np.vstack((x_grid.flatten(), y_grid.flatten())).T

        mean = gp.mean_function.marginalize_mean(
            plot_points)

        # Init plot
        fig = plt.figure()
        axis = fig.gca(projection='3d')

        # plot data
        if show_data is not None:
            axis.scatter(
                show_data['X'][:, 0].tolist(),
                show_data['X'][:, 1].tolist(),
                show_data['Y'].tolist(), s=20, color='#444444', marker='o'
            )

        # plot test data
        if test_data is not None:
            axis.scatter(
                test_data['X'][:, 0].tolist(),
                test_data['X'][:, 1].tolist(),
                test_data['Y'].tolist(), s=20, color='#d62728', marker='^'
            )

        # plot GP
        z_points = mean
        z_points = z_points.reshape(resolution, resolution)
        axis.plot_surface(
            x_grid, y_grid,
            z_points, rstride=1,
            cstride=1, cmap='Blues', linewidth=0,
            antialiased=False, alpha=0.3
        )

        axis.zaxis.set_major_locator(LinearLocator(10))
        axis.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

        if file_name is None:
            plt.show()
        else:
            plt.savefig(file_name, bbox_inches='tight')
            plt.close()

    @staticmethod
    def _get_plot_bounds(data=None, test_data=None, tail=0.5):
        if test_data is not None:
            focus_data = test_data
        elif data is not None:
            focus_data = data
        else:
            focus_data = {
                'X': np.array([[1.0], [-1.0]])
            }

        points = focus_data['X']
        min_values = np.min(points, axis=0)
        max_values = np.max(points, axis=0)
        diff_values = max_values - min_values
        min_values -= diff_values * tail
        max_values += diff_values * tail
        diff_values = max_values - min_values

        show_data = None
        if data is not None:
            show_i = np.logical_and(
                np.all(min_values < data['X'], axis=1),
                np.all(data['X'] < max_values, axis=1)
            )
            show_data = {
                'X': data['X'][show_i],
                'Y': data['Y'][show_i]
            }

        return show_data, min_values, max_values, diff_values
