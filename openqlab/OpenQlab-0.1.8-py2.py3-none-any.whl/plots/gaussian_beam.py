import numpy as np
import matplotlib.pyplot as plt


def beam_profile(beams, data=None, title='Beam Profile'):
    """
    Create a plot of the (longitudinal) beam profiles for a set
    of Gaussian beams.

    The plotting range is adjusted such that it covers 
    the Rayleigh range of all Gaussian beams, and includes all
    measurement points.

    Parameters
    ----------
    beams: :obj:`dict`
        A :obj:`dict` of :obj:`GaussianBeam` objects, with
        descriptive labels as keys.
    data: :obj:`DataFrame`, optional
        Optional measurement data that should be plotted
        together with the Gaussian beams.
    title: :obj:`str`, optional
        The figure title.

    Returns
    -------
    :obj:`matplotlib.figure.Figure`
        A handle to the created matplotlib figure.
    """

    zmax = max([b.z0 + b.zR for b in beams.values()])
    zmin = min([b.z0 - b.zR for b in beams.values()])
    if data is not None:
        zmax = max(zmax, data.index[-1])
        zmin = min(zmin, data.index[0])

    z = np.linspace(zmin, zmax, 400)

    fig, ax = plt.subplots()
    for label, beam in beams.items():
        ax.plot(z * 1e2, beam.get_profile(z) * 1e6,
                label=label + ', ' + str(beam))

    if data is not None:
        scaled_data = data * 1e6
        scaled_data.index *= 1e2
        scaled_data.plot(ax=ax, style='x', legend=True)

    ax.legend()
    ax.grid()
    ax.set_ylabel(u'Radius (µm)')
    ax.set_xlabel('Position (cm)')

    return fig
