#!/usr/bin/env python
from pathlib import Path
import logging
from numpy import sqrt, atleast_1d
from matplotlib.pyplot import figure
# from matplotlib.colors import LogNorm
from datetime import datetime
#
from astropy.visualization.mpl_normalize import ImageNormalize
import astropy.visualization as vis
#
import skimage.restoration as skres
from scipy.signal import wiener, medfilt2d
#
from .nans import nans
import dascutils.io as dio
from gridaurora.plots import writeplots
from themisasi.plots import overlayrowcol

DPI = 100


def plotPlainImg(sim, cam, rawdata, t, odir):
    """
    No subplots, just a plan

    http://stackoverflow.com/questions/22408237/named-colors-in-matplotlib
    """
    for R, C in zip(rawdata, cam):
        fg = figure()
        ax = fg.gca()
        ax.set_axis_off()  # no ticks
        ax.imshow(R[t, :, :],
                  origin='lower',
                  vmin=max(C.clim[0], 1), vmax=C.clim[1],
                  cmap='gray')
        ax.text(0.05, 0.075, datetime.utcfromtimestamp(C.tKeo[t]).isoformat()[:-3],
                ha='left',
                va='top',
                transform=ax.transAxes,
                color='limegreen',
                # weight='bold',
                size=24
                )

        writeplots(fg, 'cam{}rawFrame'.format(C.name), t, odir)
# %%


def plotRealImg(sim, cam, rawdata, t: int, odir: Path = None, fg=None):
    """
    sim: histfeas/simclass.py
    cam: camclass.py
    rawdata: nframe x ny x nx ndarray
    t: integer index to read
    odir: output directory (where to write results)

    plots both cameras together,
    and magnetic zenith 1-D cut line
    and 1 degree radar beam red circle centered on magnetic zenith
    """
    ncols = len(cam)
    #  print('using {} cameras'.format(ncols))
    T = nans(ncols, dtype=datetime)

#    if asi is not None:
#        ncols=3
#        if isinstance(asi,(tuple,list)):
#            pass
#        elif isinstance(asi,(str,Path)):
#            asi = Path(asi).expanduser()
#            if asi.is_dir():
#                asi=list(asi.glob('*.FITS'))
    if fg is None:
        doclose = True
        fg = figure(figsize=(15, 12), dpi=DPI, facecolor='black')
        axs = fg.subplots(nrows=1, ncols=ncols)
        axs = atleast_1d(axs)  # in case only 1
        # fg.set_size_inches(15,5) #clips off
    else:  # maintain original figure handle for anim.writer
        doclose = False
        fg.clf()
        axs = [fg.add_subplot(1, ncols, i + 1) for i in range(ncols)]

    for i, C in enumerate(cam):
        if C.usecam:  # HiST cameras
            # print('frame {}'.format(t))
            # hold times for all cameras at this time step
            T[i] = updateframe(t, rawdata[i], None, cam[i], axs[i], fg)
        elif C.name == 'asi':  # ASI
            dasc = dio.load(C.fn, treq=T[sim.useCamBool][0])
            C.tKeo = dasc.time

            updateframe(0, dasc.values, dasc.wavelength, C,
                        axs[i], fg)  # FIXME may need API update
            try:
                overlayrowcol(axs[i], C.hlrows, C.hlcols)
            except AttributeError:
                pass  # az/el were not registered
        else:
            logging.error(f'unknown camera {C.name} index {i}')

        if i == 0:
            axs[0].set_ylabel(datetime.strftime(T[0], '%x')).set_color('limegreen')

            # NOTE: commented out due to Matplotlib 1.x bugs
            # fg.suptitle(datetime.strftime(T[0],'%x')) #makes giant margins that tight_layout doesn't help, bug
            # fg.text(0.5,0.15,datetime.strftime(T[0],'%x'))#, va='top',ha='center') #bug too
            # fg.tight_layout()
            # fg.subplots_adjust(top=0.95)

    # TODO: T[0] is fastest cam now, but needs generalization
    writeplots(fg, 'rawFrame', T[0], odir=odir,
               dpi=sim.dpi, facecolor='k', doclose=doclose)


def updateframe(t, raw, wavelen, cam, ax, fg):
    showcb = False

    ttxt = f'Cam {cam.name}: '

    if raw.ndim == 3:
        frame = raw[t, ...]
    elif raw.ndim == 2:
        frame = raw
    elif raw.ndim == 1:  # GeoData
        frame = raw.reshape((sqrt(raw.size), -1))
    else:
        raise ValueError('ndim==3 or 2')
# %% filtering (optional) # FIXME provide noise estimate
    """
    http://scikit-image.org/docs/dev/api/skimage.restoration.html?highlight=denoise
    """
    if 'wiener' in cam.cp:
        # psf = ones((cam.wiener, cam.wiener)) / cam.wiener**2
        frame = wiener(frame, cam.cp['wiener'])

    if 'medfilt2d' in cam.cp:
        frame = medfilt2d(frame.astype(float), cam.cp['medfilt2d'])

    if 'denoise_bilateral' in cam.cp:
        frame = skres.denoise_bilateral(((frame - cam.clim[0]) / (cam.clim[1] - cam.clim[0])).clip(0., 1.),
                                        sigma_color=0.05, sigma_spatial=15, multichannel=False)
    if 'denoise_tv_chambolle' in cam.cp:
        frame = skres.denoise_tv_chambolle(((frame - cam.clim[0]) / (cam.clim[1] - cam.clim[0])).clip(0., 1.),
                                           )
# %% plotting raw uint16 data
    if False:
        v = vis.HistEqStretch(frame)
        NORM = ImageNormalize(stretch=v)

    NORM = None
    #  NORM = LogNorm()
    # NORM = ImageNormalize(stretch=vis.LogStretch())

    hi = ax.imshow(frame,
                   origin='lower', interpolation='none',
                   # aspect='equal',
                   # extent=(0,C.superx,0,C.supery),
                   vmin=cam.clim[0], vmax=cam.clim[1],
                   cmap='gray', norm=NORM)

    # autoscale(False) for case where we put plots on top of image
    # yet still reduces blank space between subplots
    ax.autoscale(False)

    if showcb:  # showing the colorbar makes the plotting go 5-10x more slowly
        hc = fg.colorbar(hi, ax=ax)  # not cax!
        hc.set_label(f'{raw.dtype} data numbers')

    dtframe = datetime.utcfromtimestamp(cam.tKeo[t])

    if cam.name == 'asi':
        dtstr = datetime.strftime(dtframe, '%H:%M:%S')
        if int(wavelen[t]) == 428:
            tcolor = 'blue'
        elif int(wavelen[t]) == 557:
            tcolor = 'limegreen'
        elif int(wavelen[t]) == 630:
            tcolor = 'red'
        else:
            tcolor = 'limegreen'
        ttxt += f'{dtstr}' + r' $\lambda$' + f' {wavelen[t]:.1f}'
    else:
        dtstr = datetime.strftime(dtframe, '%H:%M:%S.%f')[:-3]  # millisecond
        tcolor = 'limegreen'
        ttxt += f'{dtstr}'

    ax.set_title(ttxt, color=tcolor)

    ax.set_axis_off()  # no ticks

    if False:
        ax.set_xlabel('x-pixel')
        if cam.name == 0:
            ax.set_ylabel('y-pixel')
# %% plotting 1D cut line
    try:
        ax.plot(cam.cutcol[cam.Lcind], cam.cutrow[cam.Lcind],
                marker='.', linestyle='none', color='blue', markersize=1, alpha=0.5)
        # plot magnetic zenith
        ax.scatter(x=cam.cutcol[cam.angleMagzenind],
                   y=cam.cutrow[cam.angleMagzenind],
                   marker='o', facecolors='none', color='red', s=500, linewidth=2, alpha=0.5)
    except AttributeError:  # asi
        pass
# %% plot cleanup
    ax.grid(False)  # in case Seaborn is used
    return dtframe
