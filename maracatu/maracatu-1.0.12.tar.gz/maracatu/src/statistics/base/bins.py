"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""
import numpy as np
from maracatu.src.base.parameters import Parameter


class BinsFactory(object):

    def __init__(self):
        pass

    @staticmethod
    def get(binning):
        if binning == 'quantile':
            return BinsQuantile()
        elif binning == 'step':
            return BinsStep()
        elif binning == 'equally':
            return BinsEquallySpaced()


class BinsDataFrame(object):

    def __init__(self):
        pass

    def get(self, df, par):
        par_binnings = Parameter.get_par(par, 'binning')
        bins = []
        if par_binnings:
            for par_binning in par_binnings:
                binning_type = Parameter.get_par(par_binning, 'binning_type')
                var = Parameter.get_par(par_binning, 'var')
                if par.__contains__(var):
                    var = par[var]
                binning = BinsFactory.get(binning_type)
                bins.append(binning.get(df[var], par_binning))
        else:
            bins.append(df.iloc[:, 0])
        return tuple(bins)


class Bins(object):

    def __init__(self):
        pass

    def get_params(self, par):
        pass

    def get(self, values, par):
        pass


class BinsStep(Bins):

    def __init__(self):
        super().__init__()

    def get(self, values, par):
        bin_min = Parameter.get_par(par, 'bin_min')
        bin_min_quantile = Parameter.get_par(par, 'bin_min_quantile', False)
        bin_max = Parameter.get_par(par, 'bin_max')
        bin_max_quantile = Parameter.get_par(par, 'bin_max_quantile', False)
        step = Parameter.get_par(par, 'step', 1)

        xmin = bin_min
        if bin_min_quantile:
            xmin = values.quantile(bin_min)

        xmax = bin_max
        if bin_max_quantile:
            xmax = values.quantile(bin_max)

        bins = np.arange(xmin, xmax, step)

        return bins


class BinsEquallySpaced(Bins):

    def __init__(self):
        super().__init__()

    def get(self, values, par):
        bin_min = Parameter.get_par(par, 'bin_min')
        bin_min_quantile = Parameter.get_par(par, 'bin_min_quantile', False)
        bin_max = Parameter.get_par(par, 'bin_max')
        bin_max_quantile = Parameter.get_par(par, 'bin_max_quantile', False)
        bin_sample = Parameter.get_par(par, 'bin_sample', 10)

        xmin = bin_min
        if bin_min_quantile:
            xmin = values.quantile(bin_min)
        #
        xmax = bin_max
        if bin_max_quantile:
            xmax = values.quantile(bin_max)

        bins = np.linspace(xmin, xmax, bin_sample)

        return bins


class BinsQuantile(Bins):

    def __init__(self):
        super().__init__()

    def get(self, values, par):
        bin_min = Parameter.get_par(par, 'bin_min')
        # bin_min_quantile = Parameter.get_par(par, 'bin_min_quantile', False)
        bin_max = Parameter.get_par(par, 'bin_max')
        # bin_max_quantile = Parameter.get_par(par, 'bin_max_quantile', False)
        bin_sample = Parameter.get_par(par, 'bin_sample', 10)

        quantiles = np.linspace(bin_min, bin_max, bin_sample)
        # print(quantiles)
        bins = values.quantile(quantiles).values
        # print(bins)
        return bins

# class Bins(object):
#
#     def __init__(self):
#         pass
#
#     # def get(self, df, par):
#     #     pass
#
#     def get_par_binning(self, par):
#         binning_x = Parameter.get_par(par, 'binning.x', 'quantile')
#         binning_xmin = Parameter.get_par(par, 'binning.xmin', .0)
#         binning_xmax = Parameter.get_par(par, 'binning.xmax', .95)
#         binning_xsample = Parameter.get_par(par, 'binning.xsample', 20)
#         binning_y = Parameter.get_par(par, 'binning.y', 'quantile')
#         binning_ymin = Parameter.get_par(par, 'binning.ymin', .0)
#         binning_ymax = Parameter.get_par(par, 'binning.ymax', 0.3)
#         binning_ysample = Parameter.get_par(par, 'binning.ysample', 20)
#         return binning_x, binning_xmin, binning_xmax, binning_xsample, binning_y, binning_ymin, binning_ymax, \
#                binning_ysample
#
#     def get_binning(self, name):
#         if name == 'quantile':
#             return BinsQuantile()
#         elif name == 'step':
#             return BinsStep()
#
#     def get(self, df, par):
#         binning_x, binning_xmin, binning_xmax, binning_xsample, binning_y, binning_ymin, binning_ymax, \
#         binning_ysample = self.get_par_binning(par)
#
#         xvar = Parameter.get_par(par, 'xvar')
#         yvar = Parameter.get_par(par, 'yvar')
#
#         xbinnig = self.get_binning(binning_x)
#
#         xbins = xbinnig.get(df[xvar], binning_xmin, binning_xmax, binning_xsample)
#         ybinning = self.get_binning(binning_y)
#         ybins = ybinning.get(binning_ymin, binning_ymax, binning_ysample)
#         return xbins, ybins

#
# class BinsQuantile:
#
#     def __init__(self):
#         pass
#         # super().__init__()
#
#     def get(self, df, par):
#         xvar = Parameter.get_par(par, 'xvar')
#         yvar = Parameter.get_par(par, 'yvar')
#
#         binning_x = Parameter.get_par(par, 'binning.x', 'quantile')
#         binning_xmin = Parameter.get_par(par, 'binning.xmin', .0)
#         binning_xmax = Parameter.get_par(par, 'binning.xmax', .95)
#         binning_xsample = Parameter.get_par(par, 'binning.xsample', 20)
#         binning_y = Parameter.get_par(par, 'binning.y', 'quantile')
#         binning_ymin = Parameter.get_par(par, 'binning.ymin', .0)
#         binning_ymax = Parameter.get_par(par, 'binning.ymax', 0.3)
#         binning_ysample = Parameter.get_par(par, 'binning.ysample', 20)
#
#         xmin = values.quantile(binning_min)
#         xmax = values.quantile(binning_max)
#         bins = np.linspace(xmin, xmax, binning_sample)
#         return bins
#
#
#
#         # # # TODO flexible to n dimentions
#         # # quantiles = np.linspace(0.1, .9, 10)
#         # # xbins = self.df.iloc[:, 0].quantile(quantiles).values
#         # # ybins = self.df.iloc[:, 1].quantile(quantiles).values
#         # # #     xbins = np.linspace(xslice)
#         # # #     ybins = np.linspace(ymin, ymax, 50)
#         # #
#         # # # xbins = np.logspace(1, int(np.log(xmax)), 50)
#         # # # ybins = np.logspace(1, int(np.log(ymax)), 50)
#         #
#         # xvar = Parameter.get_par(par, 'xvar')
#         # yvar = Parameter.get_par(par, 'yvar')
#         #
#         # def get(self, values, binning_min, binning_max, binning_sample):
#         # binning_xmin, binning_xmax, binning_xsample, binning_ymin, binning_ymax, binning_ysample = self.get_binning(par)
#         #
#         # xmin = df[xvar].quantile(binning_xmin)
#         # xmax = df[xvar].quantile(binning_xmax)
#         # ymin = df[yvar].quantile(binning_ymin)
#         # ymax = df[yvar].quantile(binning_ymax)
#         #
#         # xbins = np.linspace(xmin, xmax, binning_xsample)
#         # ybins = np.linspace(ymin, ymax, binning_ysample)
#         #
#         # return xbins, ybins
#
#
# class BinsStep:
#
#     def get(self, df, par):
#     # def get(self, values, binning_min, binning_max, binning_sample):
#         xvar = Parameter.get_par(par, 'xvar')
#         yvar = Parameter.get_par(par, 'yvar')
#
#         # binning_x = Parameter.get_par(par, 'binning.x', 'quantile')
#         binning_xmin = Parameter.get_par(par, 'binning.xmin', .0)
#         binning_xmax = Parameter.get_par(par, 'binning.xmax', .95)
#         # binning_xsample = Parameter.get_par(par, 'binning.xsample', 20)
#         # binning_y = Parameter.get_par(par, 'binning.y', 'quantile')
#         binning_ymin = Parameter.get_par(par, 'binning.ymin', .0)
#         binning_ymax = Parameter.get_par(par, 'binning.ymax', 0.3)
#         # binning_ysample = Parameter.get_par(par, 'binning.ysample', 20)
#         xstep = Parameter.get_par(par, 'binning.xstep', 1)
#         ystep = Parameter.get_par(par, 'binning.xstep', 1)
#
#         # binning_xmin, binning_xmax, binning_xsample, binning_ymin, binning_ymax, binning_ysample = self.get_par_binning(par)
#
#         xbins = np.arange(binning_xmin, binning_xmax, xstep)
#         ybins = np.arange(binning_ymin, binning_ymax, ystep)
#
#         return xbins, ybins
#
#
# class BinsEquallySpaced(Bins):
#
#     def __init__(self):
#         super().__init__()
#
#     def get(self, df, par):
#         pass
#
# # class BinsLinear(Bins):
# #
# #     def __init__(self):
# #         super().__init__()
# #
# #     def get(self, num = 50):
# #         # TODO flexible to n dimentions
# #         # xmin = df[xvar].min()
# #         # xmax = df[xvar].max()
# #
# #         xmin = self.df.iloc[:, 0].min()
# #         xmax = self.df.iloc[:, 0].max()
# #         # xmax = df[xvar].quantile(.99)
# #         ymin = self.df.iloc[:, 1].min()
# #         ymax = self.df.iloc[:, 1].max()
# #
# #         xbins = np.linspace(xmin, xmax, num)
# #         ybins = np.linspace(ymin, ymax, num)
# #
# #         return xbins, ybins
#


        # binning_x = Parameter.get_par(par, 'binning.x', 'quantile')
        # binning_y = Parameter.get_par(par, 'binning.y', 'quantile')
        #
        # xbinnig = self.get_binning(binning_x)
        # ybinning = self.get_binning(binning_y)

        # xbins = xbinnig.get(df[xvar], binning_xmin, binning_xmax, binning_xsample)
        # ybins = ybinning.get(binning_ymin, binning_ymax, binning_ysample)
        # xvar = Parameter.get_par(par, 'xvar')
        # yvar = Parameter.get_par(par, 'yvar')


# def get_binning(self, name):
#     if name == 'quantile':
#         return BinsQuantile()
#     elif name == 'step':
#         return BinsStep()
