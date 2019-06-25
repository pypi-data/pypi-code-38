from .. import *

def test_trapezoid():
    '''
    This tests a few different astropy trapezoid transit models.
    '''
    t = np.linspace(-1.5, 1.5, 10000)

    for tau in np.arange(3)*0.12:
        for T in np.arange(3)*0.1:
            model = TrapezoidTransit(T=T, tau=tau)
            plt.plot(t, model(t), label=repr(model))
    plt.legend(fontsize=4)
    plt.show()


def test_batman(N=1e6, duration=10, cadence=1.0/60.0/24.0, period=3.14, t0=0.3, **kw):
    '''
    This tests if the batman astropy model works.
    '''
    lc = simulate_transit_data(N=N, duration=duration, cadence=cadence, period=period, t0=t0, **kw)
    ba = BatmanTransit(period=period, t0=t0, **kw)
    lc.scatter()
    plt.plot(lc.time, ba(lc.time), label=repr(ba), color='mediumseagreen')
    plt.legend(fontsize=6)


def test_batman(N=1e6, duration=10, cadence=1.0/60.0/24.0, period=3.14, t0=0.3, **kw):
    '''
    This tests if the batman astropy model works.
    '''
    lc = simulate_transit_data(N=N, duration=duration, cadence=cadence, period=period, t0=t0, **kw)
    ba = BatmanTransit(period=period, t0=t0, **kw)
    lc.scatter()
    plt.plot(lc.time, ba(lc.time), label=repr(ba), color='mediumseagreen')
    plt.legend(fontsize=6)
