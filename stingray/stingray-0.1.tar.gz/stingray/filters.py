import numpy as np

__all__ = ['Window1D', 'Optimal1D']


class Window1D(object):
    """
    Make a top hat filter (window function) for power spectrum or cross
    spectrum. It assumes that the first model is the QPO component
    Lorentzian model.

    Parameters
    ----------
    model: astropy.modeling.models class instance
        The compound model fit to the spectrum.

    Attributes
    ----------
    model:  astropy.modeling.models class instance
        The compound model fit to the spectrum.

    x_o: Parameter class instance
        Centroid of Lorentzian model.

    fwhm: Parameter class instance
        Full width at half maximum of Lorentzian model.
    """

    def __init__(self, model):
        self.model = model
        self.x_0 = model[0].x_0
        self.fwhm = model[0].fwhm

    def __call__(self, x):
        y = np.zeros((len(x),), dtype=np.float64)
        for i in range(len(x)):
            if np.abs(x[i] - self.x_0[0]) <= self.fwhm[0] / 2:
                y[i] = 1.
        return y


class Optimal1D(object):
    """
    Make a optimal filter for power spectrum or cross spectrum.
    It assumes that the first model is the QPO component.

    Parameters
    ----------
    model: astropy.modeling.models class instance
        The compound model fit to the spectrum.

    Attributes
    ----------
    model:  astropy.modeling.models class instance
        The compound model fit to the spectrum.

    filter: astropy.modeling.models class instance
        It s the ratio of QPO component to the model fit to the spectrum.
    """

    def __init__(self, model):
        self.model = model
        qpo_component_model = self.model[0]
        all_components_model = self.model
        self.filter = qpo_component_model / all_components_model

    def __call__(self, x):
        return self.filter(x)
