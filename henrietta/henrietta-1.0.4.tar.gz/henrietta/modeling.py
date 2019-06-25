import numpy as np
import matplotlib.pyplot as plt
from .goodnesses import *
from .tools import *

try:
    import batman
except:
    print("""
    `batman-package` is not installed on this computer.

    You can use most of the henrietta tools with no problem,
    but you will not be able to generate transit models :-(

    You can try installing it with the command
        `pip install batman-package`
    """)
import lightkurve
from lightkurve import LightCurve
from .statistics import *

def BATMAN(t,
           period = 1.0, #days
           t0 = 0, #time of inferior conjunction
           radius = 0.1, #Rp/R*
           a = 10.0, #semi-major axis in a/R*
           b = 0.0, #impact parameter in stellar radii
           baseline = 1.0, #units are whatever your flux units come in
           ld1 = 0.1,#using a basic limb darkening
           ld2 = 0.3,
           ):
    '''
    This function returns a model transit light curve
    for a given array of times and set of parameters.
    It currently assumes a circular orbit.

    Parameters
    ----------
    t : array
        An array of times, in units of days.

    period : float
        The orbital period of the planet, in units of days.

    t0 : float
        One mid-transit time, in units of days.

    radius : float
        The radius of the planet, in units of stellar radii.
        (This is sometimes also called Rp/R*).

    a : float
        The orbital distance (semimajor axis) of the planet, in stellar radii.
        (This is sometimes also called a/R*).

    b : float
        The transit impact parameter of the planet, in stellar radii.
        (This is closely related to the inclination.)

    baseline : float
        The out-of-transit flux level, in whatever units you want.

    ld : list or array of floats
        The limb-darkening coefficients, for a quadratic limb-darkening.
    '''

    # create a batman transit parameter object
    params = batman.TransitParams()

    params.t0 = t0                      #time of inferior conjunction ()
    params.per = period             #period in days
    params.rp = radius         #planet radius (in units of stellar radii)
    params.a = a                      #semi-major axis (in units of stellar radii)
    params.inc = np.arccos(b/a)*180/np.pi                   #orbital inclination (in degrees)
    params.ecc = 0.                      #eccentricity
    params.w = 90.                       #longitude of periastron (in degrees)
    params.u = [ld1, ld2]        #limb darkening coefficients [u1, u2]
    params.limb_dark = "quadratic"       #limb darkening model

    # initialize a batman model for the given times
    m = batman.TransitModel(params, t)

    # calculate a light curve (at the pre-set times)
    flux = m.light_curve(params)*baseline

    # return those light curve values
    return flux

def example_transit_model( period = 0.5, #days
                           t0 = 0, #time of inferior conjunction
                           radius = 0.1, #Rp/R*
                           a = 10.0, #semi-major axis in a/R*
                           b = 0.0, #impact parameter in stellar radii,
                           tmin=-0.5, tmax=0.5, cadence=1.0/60.0/24.0,
                           ylim=[0.985, 1.005],
                           ax=None,
                           **plotkw):
    '''
    This function makes an example plot of a model transit light curve.

    Parameters
    ----------

    period : float
        The orbital period of the planet, in units of days.

    t0 : float
        One mid-transit time, in units of days.

    radius : float
        The radius of the planet, in units of stellar radii.
        (This is sometimes also called Rp/R*).

    a : float
        The orbital distance (semimajor axis) of the planet, in stellar radii.
        (This is sometimes also called a/R*).

    b : float
        The transit impact parameter of the planet, in stellar radii.
        (This is closely related to the inclination.)

    tmin : float
        The minimum time to plot, in days.

    tmax : float
        The maximum time to plot, in days.

    cadence : float
        The cadence (time-step) to use, in days.

    ylim : list
        The ylimits for the plot.

    ax : matplotlib.axes object
        If an ax is fed in as a keyword argument, the plot
        will be added to that existing plot axes. To include
        multiple different models on the same plot, say:

        ax = example_transit_model()
        ax = example_transit_model(rp=0.042, ax=ax)
        ax = example_transit_model(rp=0.042, b=0.9, ax=ax)
        ...

    plotkw : dict
        Any extra keywords will be passed along to `matplotlib.pyplot.plot`

    Returns
    -------

    plotted_ax : matplotlib.axes object
        The axes into which the model was was plotted.
    '''

    # create an array of times and flux values
    t = np.arange(tmin, tmax, cadence)
    f = BATMAN(t=t, period=period, t0=t0, radius=radius, a=a, b=b)

    # make a lightkurve LightCurve object
    # model_lc = LightCurve(time=t, flux=f)

    # figure out with ax to plot in
    if ax is None:
        ax = plt.gca()
    else:
        plt.sca(ax)

    # update the label, if it doesn't already exist
    if 'label' != plotkw:
        plotkw['label'] = 'period={period},t0={t0},radius={radius},a={a},b={b}'.format(**locals())

    # make the plot, set the y limits
    plt.plot(t, f, **plotkw)
    plt.ylim(*ylim)

    # set some ylimits
    plt.xlabel('Time (days)')
    plt.ylabel('Relative Flux')

    # return the current axes, in case someone wants to plot into them again
    return ax

def simulate_transit_data(N=1e6, cadence=2.0/60.0/24.0, duration=3.0, tmin=0.0,  **kw):
    '''
    This function will generate a simulated LightCurve dataset
    with a given fractional noise (sigma) and time spacing (cadence),
    with a transit injected into it (whose parameters are set by any
    extra keyword arguments that you feed in, like `period`, `radius`, ...)

    Parameters
    ----------

    N : float
        The average number of photons expected per exposure, to
        set the standard deviation of the noise.

    cadence : float
        The integration time of the measurements, in days.

    duration : float
        The total length of time covered by the light curve.

    **kw : dict
        Any additional keywords will be passed onward to the
        batman model to set the parameters of the transit model.
        Valid additional keywords are period, t0, radius, a, b, ld.

    Returns
    -------
    lc : LightCurve
        A simulated lightkurve LightCurve, with a transit injected,
        and the specified noise.
    '''
    noise = create_photon_lightcurve(N=N, cadence=cadence, duration=duration).normalize()
    noise.time += tmin
    flux = BATMAN(noise.time, **kw)
    return LightCurve(time=noise.time, flux=flux*noise.flux, flux_err=noise.flux_err, time_format='jd')

def plot_with_transit_model(lc,
                           period = 1.0,
                           t0 = 0,
                           radius = 0.1,
                           a = 10.0,
                           b = 0.0,
                           baseline = 1.0,
                           ld1 = 0.1, ld2 = 0.3,
                           planet_name='',
                           goodness=None,
                           show_errors=False,
                           datakw={},
                           modelkw={}):
    '''
    This function will take in a lightcurve for a planet
    with a given set of transit parameters (period, t0, radius, a, b, baseline)
    and will plot a batman light curve model. Limb-darkening coefficients
    can also be specified in the form [u1,u2].

    Parameters
    ----------
    lc : LightCurve object
        Data contained in a lightkurve LightCurve object.

    period : float
        The orbital period of the planet, in units of days.

    t0 : float
        One mid-transit time, in units of days.

    radius : float
        The radius of the planet, in units of stellar radii.
        (This is sometimes also called Rp/R*).

    a : float
        The orbital distance (semimajor axis) of the planet, in stellar radii.
        (This is sometimes also called a/R*).

    b : float
        The transit impact parameter of the planet, in stellar radii.
        (This is closely related to the inclination.)

    baseline : float
        The out-of-transit flux level, in whatever units you want.

    ld : list or array of floats
        The limb-darkening coefficients, for a quadratic limb-darkening.

    planet_name : string
        The name of the planet, which will be displayed as the title

    goodness : function
        A function that takes an array of values for (data-model),
        and returns a goodness of fit metric.

    datakw : dictionary
        A dictionary with keywords that will be passed to the plt.plot()
        command that displays the actual data points.

    modelkw : dictionary
        A dictionary with keywords that will be passed to the plt.plot()
        command that displays the actual the smooth model.
    '''

    # create a high-resolution grid of times to plot
    highres_time = np.arange(lc.time[0],lc.time[-1],1.0/60.0/24.0)

    # figure out the right time format
    if isinstance(lc, lightkurve.lightcurve.FoldedLightCurve):
        epoch = 0.0
        period = 1.0
    else:
        epoch = find_appropriate_epoch(lc, t0)

    # craete a model of the flux at the light curve times
    model_flux = BATMAN(baseline = baseline,
                radius = radius,
                period = period,
                a = a,
                b = b,
                t0 = epoch,
                ld1 = ld1, ld2 = ld2,
                t = lc.time)

    # create a model of the flux at high resolution
    model_plot = BATMAN(baseline = baseline,
                radius = radius,
                period = period,
                a = a,
                b = b,
                t0 = epoch,
                ld1 = ld1, ld2 = ld2,
                t = highres_time)

    # calculation the difference between the data and the model
    residual = (lc.flux - model_flux)


    f, (a0, a1) = plt.subplots(2,1, gridspec_kw = {'height_ratios':[4,1]},figsize=(10,5),sharex=True)


    a0.set_ylabel('Flux')#,fontsize=18)
    actualdatakw = dict( alpha=0.5, color='royalblue',markersize='5', markeredgecolor='none', zorder=0)
    actualdatakw.update(**datakw)

    actualmodelkw = dict(zorder=1,color='k')
    actualmodelkw.update(**modelkw)

    summary = 'BATMAN(period={period},t0={t0},radius={radius},a={a},b={b})'.format(**locals())
    a0.plot(highres_time,model_plot,label='Model', **actualmodelkw)

    if show_errors:
        a0.errorbar(lc.time,lc.flux,yerr=lc.flux_err,fmt='o',label='Data', **actualdatakw)
    else:
        a0.plot(lc.time,lc.flux,label='Data', marker='o', linewidth=0, **actualdatakw)


    a0.legend()#loc='upper left', bbox_to_anchor=(1,1))

    if show_errors:
        a1.errorbar(lc.time,residual,yerr=lc.flux_err, **actualdatakw)
    else:
        a1.plot(lc.time,residual,marker='o',linewidth=0, **actualdatakw)
    a1.axhline(0, **actualmodelkw)
    a1.set_ylim(0-1.5*np.nanmax(np.abs(residual)),0+1.5*np.nanmax(np.abs(residual)))
    a1.set_ylabel('Residuals')
    plt.xlabel('Time (days)')

    if planet_name is '':
        title = ''
    else:
        title = '{} | '.format(planet_name)

    if goodness is None:
        title += summary
        gof = None
    else:
        plt.show()
        gof = goodness(residual/lc.flux_err)
        title += '{} | {}={:.4}'.format(summary, goodness.__name__, gof)
    a0.set_title(title, fontsize=10)

    return gof
