#!/usr/bin/env python
from pathlib import Path
from numpy import uint16, diff, gradient
from datetime import datetime
try:
    import simplekml as skml
except ImportError:
    skml = None
#
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.pyplot import figure, hist, draw, pause, show
from matplotlib.colors import LogNorm
# from matplotlib.ticker import ScalarFormatter
# import matplotlib.animation as anim
#
from pymap3d import ecef2geodetic


def doPlayMovie(data, playMovie, ut1_unix=None, rawFrameInd=None, clim=None):
    if not playMovie or data is None:
        return
# %%
    # sfmt = ScalarFormatter(useMathText=True)
    hf1 = figure(1)
    hAx = hf1.gca()

    try:
        hIm = hAx.imshow(data[0, ...],
                         vmin=clim[0], vmax=clim[1],
                         cmap='gray', origin='lower', norm=LogNorm())
    except TypeError:  # clim wasn't specified properly
        print('setting image viewing limits based on first frame')
        hIm = hAx.imshow(data[0, ...], cmap='gray',
                         origin='lower', norm=LogNorm())

    hT = hAx.text(0.5, 1.005, '', ha='center', transform=hAx.transAxes)
    # hc = hf1.colorbar(hIm,format=sfmt)
    # hc.set_label('data numbers ' + str(data.dtype))
    hAx.set_xlabel('x-pixels')
    hAx.set_ylabel('y-pixels')

    if ut1_unix is not None:
        titleut = True
    else:
        titleut = False

    for i, d in enumerate(data):
        hIm.set_data(d)
        try:
            if titleut:
                hT.set_text(f'UT1 estimate: {datetime.utcfromtimestamp(ut1_unix[i])}  RelFrame#: {i}')
            else:
                hT.set_text(f'RawFrame#: {rawFrameInd[i]} RelFrame# {i}')
        except TypeError:
            hT.set_text(f'RelFrame# {i}')

        draw()
        pause(playMovie)

# def doanimate(data,nFrameExtract,playMovie):
#    # on some systems, just freezes at first frame
#    print('attempting animation')
#    fg = figure()
#    ax = fg.gca()
#    himg = ax.imshow(data[:,:,0],cmap='gray')
#    ht = ax.set_title('')
#    fg.colorbar(himg)
#    ax.set_xlabel('x')
#    ax.set_ylabel('y')
#
#    #blit=False so that Title updates!
#    anim.FuncAnimation(fg,animate,range(nFrameExtract),fargs=(data,himg,ht),
#                       interval=playMovie, blit=False, repeat_delay=1000)


def doplotsave(bigfn, data, rawind, clim, dohist, meanImg):
    if bigfn is None or data is None:
        return

    bigfn = Path(bigfn)

    if dohist:
        ax = figure().gca()
        hist(data.ravel(), bins=256, log=True)
        ax.set_title('histogram of {}'.format(bigfn))
        ax.set_ylabel('frequency of occurence')
        ax.set_xlabel('data value')

    if meanImg:
        # DO NOT use dtype= here, it messes up internal calculation!
        meanStack = data.mean(axis=0).astype(uint16)
        fg = figure(32)
        ax = fg.gca()
        if clim:
            hi = ax.imshow(meanStack, cmap='gray', origin='lower',
                           vmin=clim[0], vmax=clim[1], norm=LogNorm())
        else:
            hi = ax.imshow(meanStack, cmap='gray',
                           origin='lower', norm=LogNorm())

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('mean of image frames')
        fg.colorbar(hi)

        pngfn = bigfn.with_suffix('_mean.png')
        print(f'writing mean PNG {pngfn}')
        fg.savefig(pngfn, dpi=150, bbox_inches='tight')


def animate(i, data, himg, ht):
    # himg = plt.imshow(data[:,:,i]) #slow, use set_data instead
    himg.set_data(data[i, :, :])
    ht.set_text('RelFrame#' + str(i))
    # 'RawFrame#: ' + str(rawFrameInd[jFrm]) +

    draw()  # plot won't update without plt.draw()!
    # plt.pause(0.01)
    # plt.show(False) #breaks (won't play)
    return himg, ht


def plotLOSecef(cam, odir):
    fg = figure()

    if odir and skml is not None:
        kml1d = skml.Kml()

    for C in cam:
        if not C.usecam:
            continue

        ax = fg.gca(projection='3d')
        ax.plot(xs=C.x2mz, ys=C.y2mz, zs=C.z2mz, zdir='z', label=str(C.name))
        ax.set_title('LOS to magnetic zenith in ECEF')
        ax.set_xlabel('x [m]')
        ax.set_ylabel('y [m]')
        ax.set_zlabel('z [m]')

        if odir and skml is not None:  # Write KML
            # convert LOS ECEF -> LLA
            loslat, loslon, losalt = ecef2geodetic(C.x2mz, C.y2mz, C.z2mz)
            kclr = ['ff5c5ccd', 'ffff0000']
            # camera location points
            bpnt = kml1d.newpoint(name='HST {}'.format(C.name),
                                  description='camera {} location'.format(
                                      C.name),
                                  coords=[(C.lon, C.lat)])
            bpnt.altitudemode = skml.AltitudeMode.clamptoground
            bpnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/pink-blank.png'
            bpnt.style.iconstyle.scale = 2.0
            # show cam to mag zenith los
            linestr = kml1d.newlinestring(name='')
            # TODO this is only first and last point without middle!
            linestr.coords = [(loslon[0], loslat[0], losalt[0]),
                              (loslon[-1], loslat[-1], losalt[-1])]
            linestr.altitudemode = skml.AltitudeMode.relativetoground
            linestr.style.linestyle.color = kclr[C.name]

    ax.legend()
    if C.verbose:
        show()

    if odir and skml is not None:
        kmlfn = odir / 'debug1dcut.kmz'
        print(f'saving {kmlfn}')
        kml1d.savekmz(str(kmlfn))

    if odir:
        ofn = odir / 'ecef_cameras.eps'
        print(f'saving {ofn}')
        fg.savefig(ofn, bbox_inches='tight')


def plotnear_rc(R, C, name, shape, odir):
    fg = figure()
    ax = fg.gca()
    ax.plot(C, R,
            linestyle='None', marker='.')

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    # ax.set_title('pixel indices (pre-least squares)')
    ax.set_xlim([0, shape[1]])
    ax.set_ylim([0, shape[0]])
    ax.set_title('camera {} pre-LSQ fit indices to extract'.format(name))

    if odir:
        ofn = odir / 'prelsq_cam{}.eps'.format(name)
        print(f'saving {ofn}')
        fg.savefig(ofn, bbox_inches='tight')


def plotlsq_rc(nR, nC, R, C, ra, dec, angle, name, odir):
    # %% indices
    fg = figure()
    ax = fg.gca()
    # NOTE do NOT use twinax() here, leads to incorrect conclusion based on different axes limits
    ax.plot(nC, nR,
            label='cam{} data'.format(name),
            color='r', linestyle='none', marker='.')
    ax.plot(C, R,
            label='cam{} fit'.format(name),
            linestyle='-')

    ax.legend()
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    ax.set_title('polyfit with computed ray points')
    ax.autoscale(True, 'x', True)

    if odir:
        ofn = odir / 'lsq_cam{}.eps'.format(name)
        print(f'saving {ofn}')
        fg.savefig(ofn, bbox_inches='tight')
# %% ra/dec
    fg = figure
    axs = fg.subplots(2, 1, sharex=True)
    fg.suptitle('camera {} ra/dec extracted'.format(name))

    ax = axs[0]
    ax.plot(ra)
    ax.set_ylabel('right asc.')
    ax.autoscale(True, 'x', True)

    ax2 = ax.twinx()
    ax2.plot(diff(ra), color='r')
    ax2.set_ylabel('diff(ra)', color='r')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')

    ax = axs[1]
    ax.plot(dec)
    ax.set_ylabel('decl.')

    ax2 = ax.twinx()
    ax2.plot(diff(dec), color='r')
    ax2.set_ylabel('diff(dec)', color='r')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')

    ax2.autoscale(True, 'x', True)

    if odir:
        ofn = odir / 'radec_cam{}.eps'.format(name)
        print(f'saving {ofn}')
        fg.savefig(ofn, bbox_inches='tight')
# %% angles
    fg = figure()
    axs = fg.subplots(3, 1, sharex=True)

    ax = axs[0]
    ax.plot(angle)
    ax.set_ylabel(r'$\theta$ [deg.]')
    ax.set_title(r'angle from magnetic zenith $\theta$')

    ax = axs[1]
    dAngle = gradient(angle)
    ax.plot(dAngle, color='r', label=r'$\frac{d^1}{d\theta^1}$')
    ax.set_ylabel(r'$\frac{d^n}{d\theta^n}$ [deg.]')

    ax = axs[2]
    d2Angle = gradient(dAngle)
    ax.plot(d2Angle, color='m', label=r'$\frac{d^2}{d\theta^2}$')

    ax.autoscale(True, 'x', True)
    ax.legend()
    ax.set_xlabel('x-pixel')

    if odir:
        ofn = odir / 'angles_cam{}.eps'.format(name)
        print(f'saving {ofn}')
        fg.savefig(ofn, bbox_inches='tight')
# %% zoom angles
    for a in (ax, ax2):
        a.set_xlim((150, 200))
        # a.set_xlim((200,300))
#    for p in (p0,p1,p2):
#        p.set_linestyle('')
#        p.set_marker('.')

    if odir:
        ofn = odir / 'angles_zoom_cam{}.eps'.format(name)
        print(f'saving {ofn}')
        fg.savefig(ofn, bbox_inches='tight')
