"""
Author: Diego Pinheiro
github: https://github.com/diegompin

"""


class Parameter(object):

    def __init__(self):
        pass

    @staticmethod
    def set_par(par, name, func, default=None, transform=None):
        par = Parameter.get_par(par, name, default, transform)
        if par:
            func(par)

    # @staticmethod
    # def set_par(par_plot, names, func, default=None, transform=None):
    #     if not isinstance(names, list):
    #         names = [names]
    #
    #     pars = []
    #     for n in names:
    #         par = PlotBase.get_par(par_plot, n, default, transform)
    #         pars.append(par)
    #     if pars:
    #         func(tuple(pars))

    @staticmethod
    def get_par(par, name, default=None, transform=None):
        param = None
        if par.keys().__contains__(name):
            param = par[name]
        elif not par.keys().__contains__(name) and default is not None:
            param = default
        if (param is not None) and (transform is not None):
            param = transform(param)
        return param
