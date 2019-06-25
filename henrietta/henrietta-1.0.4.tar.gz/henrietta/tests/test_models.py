from .. import *

def test_batman():
    '''
    This function tests the batman transit light curve model.
    '''
    example_transit_model()

def test_plot(N=1e6, duration=10, cadence=1.0/60.0/24.0, period=3.14, t0=0.5, **kw):
    '''
    This function tests the plot_with_transit_model function.
    '''
    for e in [True, False]:
        lc = simulate_transit_data(N=N, duration=duration, cadence=cadence, period=period, t0=t0)
        plot_with_transit_model(lc, period=period, t0=t0, show_errors=e, **kw)

        folded = lc.fold(period=period, transit_midpoint=t0)
        plot_with_transit_model(folded, period=period, t0=t0, show_errors=e, **kw)
    return lc, folded


def test_plot_with_kepler():
    '''
    This function tests the plot_with_transit_model, using with Kepler data.
    '''

    # download a light curve
    lc = download_kepler_lc('Kepler-7')

    # phase fold it
    period = 4.8854892
    t0 = 2454967.27687
    transitparams = dict(b=0.5599, a=6.637, radius=0.08294)
    folded = lc.fold(period=period, transit_midpoint=bjd2bkjd(t0))

    # plot it
    plot_with_transit_model(folded, period=period, t0=t0, **transitparams)


def test_goodness(N=1e6, duration=10, cadence=1.0/60.0/24.0, period=3.14, t0=0.5, **kw):

    lc = simulate_transit_data(N=N, duration=duration, cadence=cadence, period=period, t0=t0,  **kw)
    folded = lc.fold(period=period, transit_midpoint=t0)
    return plot_with_transit_model(folded, period=period, t0=t0, goodness=chisq, **kw)
