from pathlib import Path
import logging
import numpy as np
from numpy.testing import assert_allclose
from dateutil.parser import parse
from datetime import datetime
from scipy.signal import savgol_filter
from numpy.random import poisson
import h5py
import xarray
from typing import List, Union

from . import splitconf
from .timedmc import datetime2unix
from pymap3d import azel2radec, aer2ecef
from pymap3d.haversine import anglesep
import dascutils.io as dio
from themisasi.fov import mergefov
import themisasi
from .plots import plotnear_rc, plotlsq_rc


class Cam:  # use this like an advanced version of Matlab struct
    """
    simple mode via try except attributeerror
    """

    def __init__(self, sim, cp, name: str,
                 zmax=None, xreq=None, makeplot: List[str] = [],
                 calfn: Path = None, verbose: int = 0) -> None:

        self.verbose = verbose

        try:
            ci = cp['name'].split(',').index(name)
            self.usecam = sim.useCamBool[ci]
        except KeyError:
            ci = name
            self.usecam = True

        self.cp = cp  # in case you want custom options w/o clogging up camclass.py

        self.x_km = None
        self.alt_m = None

        self.az2pts: float
        self.el2pts: float
        self.r2pts: float
        self.xpix: int

        self.name: Union[int, str]
        try:  # integer name
            self.name = int(name)
        except ValueError:  # non-integer name
            self.name = name

        if sim.realdata and isinstance(self.name, str):  # ASI
            self.clim = [None] * 2
            if splitconf(cp, 'plotMinVal', ci) is not None:
                self.clim[0] = splitconf(cp, 'plotMinVal', ci)
            if splitconf(cp, 'plotMaxVal', ci) is not None:
                self.clim[1] = splitconf(cp, 'plotMaxVal', ci)
# %% store az,el calibration data
            if self.name.startswith('dasc'):
                dasc = dio.loadcal(cp['azcalfn'].split(',')[ci],
                                   cp['elcalfn'].split(',')[ci])
            elif self.name.startswith('themis'):
                themis = themisasi.loadcal(cp['azcalfn'].split(',')[ci])
            else:
                raise ValueError(f'I do not know how to load az/el data for {self.name}')

            if 'realvid' in makeplot:
                if 'h5' in makeplot and sim.fovfn:
                    print(f'fov: writing {sim.fovfn}')
                    dasc, themis = mergefov(dasc, themis, method='mzslice')

                    self.hlrows = dasc.rows
                    self.hlcols = dasc.cols

                    with h5py.File(sim.fovfn, 'w') as H:
                        # TODO: Ncam x 4 x Nx  (list,list,ndarray)
                        H['/rows'] = np.array(self.hlrows)
                        H['/cols'] = np.array(self.hlcols)
                elif sim.fovfn and sim.fovfn.is_file():
                    with h5py.File(sim.fovfn, 'r') as H:
                        self.hlrows = H['/rows'][:]
                        self.hlcols = H['/cols'][:]
# %% 1-D cuts
        if isinstance(cp['nCutPix'], str):
            self.ncutpix = int(cp['nCutPix'].split(',')[ci])
        else:  # int
            self.ncutpix = cp['nCutPix']

        self.Bincl = splitconf(cp, 'Bincl', ci)
        self.Bdecl = splitconf(cp, 'Bdecl', ci)
        self.Bepoch = splitconf(cp, 'Bepoch', ci, parse)

        try:
            self.Baz = 180. + self.Bdecl
            self.Bel = self.Bincl
        except TypeError:  # magnetic field was not specified
            pass

        self.timeShiftSec = splitconf(cp, 'timeShiftSec', ci, fallback=None)
# %% image contrast set
        self.clim = [None] * 2
        self.clim[0] = splitconf(cp, 'plotMinVal', ci)
        self.clim[1] = splitconf(cp, 'plotMaxVal', ci)

        self.intensityScaleFactor = splitconf(
            cp, 'intensityScaleFactor', ci, fallback=1.)
        self.lowerthres = splitconf(cp, 'lowerthres', ci)
# %% check FOV and 1D cut sizes for sanity
        self.fovmaxlen = splitconf(cp, 'FOVmaxLengthKM', ci, fallback=np.nan)

        if self.fovmaxlen is not None and self.fovmaxlen > 10e3:
            logging.warning(
                'sanityCheck: Your FOV length seems excessive > 10000 km')
        if self.ncutpix > 4096:
            logging.warning(
                'sanityCheck: Program execution time may be excessive due to large number of camera pixels')

        try:
            if self.fovmaxlen < (1.5 * zmax):
                logging.warning(
                    'sanityCheck: To avoid unexpected pixel/sky voxel intersection problems,'
                    ' make your candidate camera FOV at least 1.5 times longer than your maximum Z altitude.')
        except TypeError:  # just plotting raw data
            pass

        self.boresightEl = splitconf(cp, 'boresightElevDeg', ci)
        self.arbfov = splitconf(cp, 'FOVdeg', ci)
# %% sky mapping
        if calfn:
            self.cal1Dfn: Union[None, Path] = calfn
        else:
            try:
                cal1Ddir = sim.rootdir / sim.cal1dpath
                cal1Dname = cp['cal1Dname'].split(',')[ci].strip()
                self.cal1Dfn = (cal1Ddir / cal1Dname).expanduser()
            except (AttributeError, IndexError):
                self.cal1Dfn = None

        self.raymap = sim.raymap
        # don't use realdata with arbitrary, doesn't make sense and causes flipped brightness data when loading--you've been warned!
        if not sim.realdata and self.raymap == 'arbitrary':
            self.angle_deg = self.arbanglemap()
#        elif self.raymap == 'astrometry': #not OOPable at this time
#            self.angle_deg = self.astrometrymap()
#        else:
#            exit('*** unknown ray mapping method ' + self.raymap)
# %% pixel noise/bias
        self.noiselam = splitconf(cp, 'noiseLam', ci)
        self.ccdbias = splitconf(cp, 'CCDBias', ci)

        self.debiasData = splitconf(cp, 'debiasData', ci)
        self.smoothspan = splitconf(cp, 'smoothspan', ci, dtype=int)
        self.savgolOrder = splitconf(cp, 'savgolOrder', ci, dtype=int)

        # data file name
        if sim.realdata and self.usecam and isinstance(self.name, str):
            if isinstance(cp['fn'], str):
                # .strip() needed in case of multi-line ini
                self.fn = (sim.realdatapath /
                           cp['fn'].split(',')[ci].strip()).expanduser()
            elif isinstance(cp['fn'], Path):
                self.fn = sim.realdatapath / cp['fn']
            else:
                raise ValueError(f'your camera filename {cp["fn"]} not found')
# %% metadata
            self.lat: float
            self.lon: float
            data: xarray.Dataset

            if self.name.startswith('dasc'):
                data = dio.load(self.fn)
                self.lat = data.lat
                self.lon = data.lon
                self.alt_m = data.alt_m
                self.ut1unix = datetime2unix(data.time.values.astype(datetime))
            elif self.name.startswith('themis'):
                data = themisasi.load(self.fn)
                self.lat = data.lat
                self.lon = data.lon
                self.alt_m = data.alt_m
                self.ut1unix = datetime2unix(data.time.values.astype(datetime))
            # legacy data including HiST  (should use xarray to convert instead)
            elif self.fn.suffix == '.h5':

                assert self.fn.is_file(), f'{self.fn} does not exist'
                """timing, parameter wrangling  FIXME someday use xarray.Dataset. convert/save data with xarray instead of h5py"""
                with h5py.File(self.fn, 'r') as f:
                    # time of each frame in entire video
                    self.ut1unix = f['/ut1_unix'][:]
                    try:
                        self.ut1unix += self.timeShiftSec
                    except TypeError:
                        pass

                    self.supery, self.superx = f['/rawimg'].shape[1:]

                    p = f['/params']
                    self.kineticsec = p['kineticsec']
                    self.rotccw = p['rotccw']
                    self.transpose = p['transpose'] == 1
                    self.fliplr = p['fliplr'] == 1
                    self.flipud = p['flipud'] == 1

                    c = f['/sensorloc']
                    self.lat = c['lat'].item()
                    self.lon = c['lon'].item()
                    self.alt_m = c['alt_m'].item()
            else:
                raise OSError(
                    f'I am not sure how to work with the data for {self.name}')

        elif not sim.realdata:  # sim ONLY
            self.kineticsec = splitconf(cp, 'kineticsec', ci)  # simulation
            # no fallback, must specify z-location of each cam
            self.alt_m = splitconf(cp, 'zkm', ci) * 1000

            if xreq is not None:  # override
                self.x_km = xreq
            else:  # normal
                # no fallback, must specify x-location of each cam
                self.x_km = splitconf(cp, 'xkm', ci)

            self.lat = splitconf(cp, 'latitude', ci)
            self.lon = splitconf(cp, 'longitude', ci)

            self.superx = self.supery = self.ncutpix

            self.transpose = splitconf(cp, 'transpose', ci)
            self.fliplr = splitconf(cp, 'fliplr', ci)
            self.flipud = splitconf(cp, 'flipud', ci)
            self.rotccw = splitconf(cp, 'rotccw', ci, fallback=0.)
# %% camera performance parameters
        self.pixarea_sqcm = splitconf(cp, 'pixarea_sqcm', ci)
        self.pedn = splitconf(cp, 'pedn', ci)
        self.ampgain = splitconf(cp, 'ampgain', ci)
# %% camera model
        """
        A model for sensor gain
        pedn is photoelectrons per data number
        This is used in fwd model and data inversion
        """
        try:
            if self.pedn is not None:
                self.dn2intens = self.pedn / \
                    (self.kineticsec * self.pixarea_sqcm * self.ampgain)
                if sim.realdata:
                    self.intens2dn = 1.
                else:
                    self.intens2dn = 1. / self.dn2intens
            else:
                self.intens2dn = self.dn2intens = 1.  # avoid VisibleDeprecationWarning
        except TypeError:  # this will give tiny ver and flux
            self.intens2dn = self.dn2intens = 1.
# %% summary
        if sim.realdata and self.usecam:
            logging.info(
                f'cam{self.name} timeshift: {self.timeShiftSec} seconds')

            logging.info(f'Camera {self.name} start/stop UTC:'
                         f'{datetime.utcfromtimestamp(self.ut1unix[0])} / '
                         f'{datetime.utcfromtimestamp(self.ut1unix[-1])}  '
                         f'{self.ut1unix.size} frames.')

    def arbanglemap(self):
        '''
        here's the center angle of each pixel ( + then - to go from biggest to
        smallest angle)  (e.g. 94.5 deg to 85.5 deg. -- sweeping left to right)
        '''
        # raySpacingDeg = self.arbfov / self.nCutPix
        maxAng = self.boresightEl + self.arbfov / 2
        minAng = self.boresightEl - self.arbfov / 2
        angles = np.linspace(maxAng, minAng, num=self.ncutpix, endpoint=True)
        assert np.isclose(angles[0], maxAng) & np.isclose(angles[-1], minAng)
        return angles

    def astrometrymap(self):
        pass
        # not sure if get1Dcut.py can be OOP'd
        # FOVangWidthDeg =pixAngleDeg[-1,iCam] - pixAngleDeg[0,iCam]
        # ModelRaySpacingDeg = np.mean( np.diff(pixAngleDeg[:,iCam],n=1) ) # for reference purposes

    def toecef(self, ranges):
        assert isinstance(
            self.Baz, float), 'please specify [cam]Bincl, [cam]Bdecl for each camera in .ini file'
        assert isinstance(
            self.lat, float), 'please specify [cam]latitude, [cam]longitude'
        self.x2mz, self.y2mz, self.z2mz = aer2ecef(self.Baz, self.Bel, ranges,
                                                   self.lat, self.lon, self.alt_m)

    # TODO put doorientimage and doorient in one function for safety
    def doorientimage(self, frame):
        if self.transpose:
            if frame.ndim == 3:
                frame = frame.transpose(0, 2, 1)
            elif frame.ndim == 2:
                frame = frame.T
            else:
                raise ValueError('ndim==2 or 3')
        # rotate -- note if you use origin='lower', rotCCW -> rotCW !
        # rotate works with first two axes
        if self.rotccw:  # NOT isinstance integer_types!
            if frame.ndim == 3:
                frame = np.rot90(frame, self.rotccw, (1, 2))
            elif frame.ndim == 2:
                frame = np.rot90(frame, self.rotccw)
            else:
                raise ValueError('ndim==2 or 3')
        # flip
        if self.fliplr:
            if frame.ndim == 3:
                frame = np.fliplr(frame.transpose(1, 2, 0)).transpose(2, 0, 1)
            elif frame.ndim == 2:
                frame = np.fliplr(frame)
            else:
                raise ValueError('ndim==2 or 3')
        if self.flipud:
            if frame.ndim == 3:
                frame = np.flipud(frame.transpose(1, 2, 0)).transpose(2, 0, 1)
            elif frame.ndim == 2:
                frame = np.flipud(frame)
            else:
                raise ValueError('ndim==2 or 3')
        return frame

    def doorient(self):
        """
        NOTE: we need to retrieve values in case no modifications are done.
        (since we'd get a closed h5py handle)
        """
        assert self.cal1Dfn.is_file(
        ), 'please specify filename for each camera under [cam]/cal1Dname: in .ini file  {}'.format(self.cal1Dfn)

        with h5py.File(self.cal1Dfn, 'r') as f:
            az = f['az'][:]
            el = f['el'][:]
            ra = f['ra'][:]
            dec = f['dec'][:]

        assert az.ndim == el.ndim == 2
        assert az.shape == el.shape

        if self.transpose:
            logging.debug('tranposing cam #{} az/el/ra/dec data. '.format(self.name))
            az = az.T
            el = el.T
            ra = ra.T
            dec = dec.T
        if self.fliplr:
            logging.debug('flipping horizontally cam #{} az/el/ra/dec data.'.format(self.name))
            az = np.fliplr(az)
            el = np.fliplr(el)
            ra = np.fliplr(ra)
            dec = np.fliplr(dec)
        if self.flipud:
            logging.debug('flipping vertically cam #{} az/el/ra/dec data.'.format(self.name))
            az = np.flipud(az)
            el = np.flipud(el)
            ra = np.flipud(ra)
            dec = np.flipud(dec)
        if self.rotccw != 0:
            logging.debug('rotating cam #{} az/el/ra/dec data.'.format(self.name))
            az = np.rot90(az, self.rotccw)
            el = np.rot90(el, self.rotccw)
            ra = np.rot90(ra, self.rotccw)
            dec = np.rot90(dec, self.rotccw)

        self.az = az
        self.el = el
        self.ra = ra
        self.dec = dec

    def debias(self, data):
        if hasattr(self, 'debiasData') and self.debiasData is not None and np.isfinite(self.debiasData):
            logging.debug('Debiasing Data for Camera #{} by -{}'.format(self.name, self.debiasData))
            data -= self.debiasData
        return data

    def donoise(self, data):
        noisy = data.copy()

        if self.noiselam:
            logging.info('adding Poisson noise with ' + r'$\lambda=' +
                         f'{self.noiselam} to camera #{self.name}')
            dnoise = poisson(lam=self.noiselam, size=self.ncutpix)
            noisy += dnoise
            self.dnoise = dnoise  # diagnostic

        if self.ccdbias:
            logging.info('adding bias {:.1f} to camera #{}'.format(
                self.ccdbias, self.name))
            noisy += self.ccdbias

# %% diagnostic quantities
#         self.raw = data #these are untouched pixel intensities
        self.noisy = noisy

        return noisy

    def dosmooth(self, data):
        assert np.isfinite(data).all(
        ), 'NaN leaked into brightness data, savgol cannot handle NaN'
        try:
            if self.smoothspan > 0 and self.savgolOrder > 0:
                logging.debug(
                    'Smoothing Data for Camera #{}'.format(self.name))
                data = savgol_filter(data, self.smoothspan, self.savgolOrder)
        except TypeError:
            pass

        return data

    def fixnegval(self, data):
        mask = data < 0
        if mask.sum() > 0.2 * self.ncutpix:
            logging.info('Setting {} negative Data values to 0 for Camera #{}'.format(
                mask.sum(), self.name))

        data[mask] = 0

#        self.nonneg = data
        return data

    def scaleintens(self, data):
        try:
            logging.info('Scaling data to Cam #{} by factor of {}'.format(
                self.name, self.intensityScaleFactor))
            data *= self.intensityScaleFactor
            # assert isnan(data).any() == False
        except TypeError:
            pass

        return data

    def dolowerthres(self, data):
        try:
            print('Thresholding Data to 0 when DN < {:.1f} for Camera {}'.format(
                self.lowerthres, self.name))
            data[data < self.lowerthres] = 0
        except TypeError:
            pass

        return data

    def findLSQ(self, nearrow, nearcol, odir):
        polycoeff = np.polyfit(nearcol, nearrow, deg=1, full=False)
# %% columns (x)  to cut from picture
        # NOT range, NEED dtype= for arange api
        cutcol = np.arange(self.superx, dtype=int)
# %% rows (y) to cut from picture
        cutrow = np.rint(np.polyval(polycoeff, cutcol)).astype(int)
        assert (cutrow >= 0).all() and (cutrow < self.supery).all(
        ), 'impossible least squares fit for 1-D cut\n is your video orientation correct? check the params of video hdf5 file'
        # DONT DO THIS: cutrow.clip(0,self.supery,cutrow)
# %% angle from magnetic zenith corresponding to those pixels
        radecMagzen = azel2radec(
            self.Baz, self.Bel, self.lat, self.lon, self.Bepoch)
        assert len(radecMagzen) == 2
        logging.info('mag. zen. ra,dec {}'.format(radecMagzen))

        anglesep_deg = anglesep(
            radecMagzen[0], radecMagzen[1], self.ra[cutrow, cutcol], self.dec[cutrow, cutcol])

# %% assemble angular distances
        self.angle_deg, self.angleMagzenind = self.sky2beam(anglesep_deg)

        self.cutrow = cutrow
        self.cutcol = cutcol
# %% meager self-check of result
        if self.arbfov is not None:
            expect_diffang = self.arbfov / self.ncutpix
            diffang = np.diff(self.angle_deg)
            # diffoutlier = max(abs(expect_diffang-diffang.min()),
            #                   abs(expect_diffang-diffang.max()))
            assert_allclose(expect_diffang, diffang.mean(), rtol=0.01), 'large bias in camera angle vector detected'
#            assert diffoutlier < expect_diffang,'large jump in camera angle vector detected' #TODO arbitrary

        if self.verbose:
            plotlsq_rc(nearrow, nearcol, cutrow, cutcol,
                       self.ra[cutrow, cutcol],
                       self.dec[cutrow, cutcol],
                       # angledist_deg,
                       self.angle_deg,
                       self.name, odir)

    def sky2beam(self, angledist_deg):
        angle_deg = np.empty(self.superx, float)
        # whether minimum angle distance from MZ is slightly positive or slightly negative, this should be OK
        MagZenInd = angledist_deg.argmin()

        angle_deg[MagZenInd:] = 90. + angledist_deg[MagZenInd:]
        angle_deg[:MagZenInd] = 90. - angledist_deg[:MagZenInd]
# %% LSQ
        col = np.arange(self.superx, dtype=int)
        polycoeff = np.polyfit(col, angle_deg, deg=1, full=False)

        return np.polyval(polycoeff, col), MagZenInd

    def findClosestAzel(self, odir=None):
        assert self.az.shape == self.el.shape
        assert self.az2pts.shape == self.el2pts.shape
        assert self.az.ndim == 2

        npts = self.az2pts.size  # numel
        R = np.empty(npts, int)
        C = np.empty(npts, int)
        # can be FAR FAR faster than scipy.spatial.distance.cdist()
        for i in range(npts):
            # we do this point by point because we need to know the closest pixel for each point
            errdist = abs(np.hypot(self.az - self.az2pts[i],
                                   self.el - self.el2pts[i]))

            """
            THIS UNRAVEL_INDEX MUST BE ORDER = 'C'
            .argmin() has flattened output
            """
            R[i], C[i] = np.unravel_index(
                errdist.argmin(), self.az.shape, order='C')

# %% dicard edge pixels
        mask = np.logical_not(((C == 0) | (C == self.az.shape[1] - 1)) |
                              ((R == 0) | (R == self.az.shape[0] - 1)))

        R = R[mask]
        C = C[mask]
# %%
        if self.verbose:
            plotnear_rc(R, C, self.name, self.az.shape, odir)
# %% least squares fit 1-D line
        self.findLSQ(R, C, odir)

        if self.verbose > 0:
            from matplotlib.pyplot import figure
            clr = ['b', 'r', 'g', 'm']
            ax = figure().gca()
            ax.plot(C, R, color=clr[int(self.name)], label='cam{}preLSQ'.format(self.name),
                    linestyle='None', marker='.')
            ax.legend()
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            # ax.set_title('pixel indices (pre-least squares)')
            ax.set_xlim([0, self.az.shape[1]])
            ax.set_ylim([0, self.az.shape[0]])
