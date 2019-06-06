# Specific widgets, widget groups and parameters for hipercam instrument
from __future__ import print_function, unicode_literals, absolute_import, division
import math
import json
import six
from os.path import expanduser

# non-standard imports
import numpy as np

# internal imports
from . import widgets as w
from . import DriverError
from .tkutils import get_root
from .misc import (createJSON, saveJSON, postJSON, startNodding, forceNod,
                   execCommand, isRunActive, jsonFromFits)

if not six.PY3:
    import Tkinter as tk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import filedialog, messagebox


# Timing, Gain, Noise parameters
# Times in seconds
VCLOCK_FRAME_SLOW = 15e-6  # vertical clocking time in image area
VCLOCK_STORAGE_SLOW = 20e-6  # vertical clocking time in storage area
HCLOCK_SLOW = 0.24e-6  # horizontal clocking time
VCLOCK_FAST = 13e-6  # faster mode with poorer CTE
HCLOCK_FAST = 0.12e-6  # faster mode with poorer CTE
SETUP_READ = 9.0e-7  # time required for Naidu's setup_read SR
DUMP_TIME_SLOW = 18e-6  # time to dump extra pixels, slow clocking
DUMP_TIME_FAST = 3.6e-6  # time to dump extra pixels, fast clocking
VIDEO_SLOW_SE = 8.72e-6  # ~113 kHz, Naidu's clock speed for single output mode
VIDEO_SLOW = 5.2e-6  # ~192 kHz, same clock speed as fast, but 4 samples
VIDEO_FAST = 1.9e-6  # ~520 kHz
GAIN_FAST = 1.1  # electrons/ADU
GAIN_SLOW = 1.1
RNO_FAST = 5.0  # e- / pixel
RNO_SLOW = 4.5
DARK_E = 0.02  # e/pix/s


FFX = 1024  # X pixels per output
FFY = 520   # Y pixels per output
PRSCX = 50  # number of pre-scan pixels


class ExposureMultiplier(tk.LabelFrame):
    """
    Top to bottom group of RangedInt entry items to specify Nblue etc. Has a max
    number of rows after which it will jump to the left of next column and start over.
    """
    def __init__(self, master, labels, ivals, imins, imaxs,
                 nrmax, checker, blank, **kw):
        """
        Parameters
        ----------
        master : tk.widget
            enclosing widget
        labels : iterable
            labels for entry items
        ivals : list of int
            initial values
        imins : list of int
            minimum values
        imaxs : list of int
            maximum values
        nrmax : int
            maximum number of rows before wrapping
        checker : callable
            command that is run on any change to the entry
        blank : bool
            controls whether the field is allowed to be blank
            In some cases it makes things easier if blank fields are
            allowed, even if it is technically invalid
        kw : dict
            keyword arguments

        """
        tk.LabelFrame.__init__(self, master, bd=0)
        nitems = len(labels)
        if (len(ivals) != nitems or len(imins) != nitems or
                len(imaxs) != nitems):
            raise DriverError('ExposureMultiplier.__init__ values and options ' +
                              'must have same length')
        self.nitems = nitems
        self.labels = labels
        self.widgets = [w.RangedInt(self, ival, imin, imax, checker, blank, **kw) for
                        ival, imin, imax in zip(ivals, imins, imaxs)]
        row = 0
        col = 0
        for nw, widget in enumerate(self.widgets):
            tk.Label(self, text=labels[nw]).grid(row=row, column=col, sticky=tk.W)
            widget.grid(row=row, column=col+1, sticky=tk.W)
            row += 1
            if row == nrmax:
                col += 1
                row = 0

    def value(self, index):
        return self.widgets[index].value()

    def set(self, index, num):
        self.widgets[index].set(num)

    def getall(self):
        return [widget.value() for widget in self.widgets]

    def setall(self, nums):
        for index, val in enumerate(nums):
            self.set(index, val)

    def disable(self):
        for widget in self.widgets:
            widget.configure(state='disable')
            widget.set_unbind()

    def enable(self):
        for widget in self.widgets:
            widget.configure(state='normal')
            widget.set_bind()


class InstPars(tk.LabelFrame):
    """
    Instrument parameters block.

    This widget block contains the meat of hdriver. Window settings, readout speed
    etc.
    """
    def __init__(self, master):
        """
        master : enclosing widget
        """
        tk.LabelFrame.__init__(self, master)

        # left hand side
        lhs = tk.Frame(self)
        rhs = tk.Frame(self)

        # Application (mode)
        tk.Label(lhs, text='Mode').grid(row=0, column=0, sticky=tk.W)
        self.app = w.Radio(lhs, ('Full', 'Wins', 'Drift'), 3, self.check,
                           ('FullFrame', 'Windows', 'Drift'))
        self.app.grid(row=0, column=1, columnspan=2, sticky=tk.W)

        # Clear enabled
        self.clearLab = tk.Label(lhs, text='Clear')
        self.clearLab.grid(row=1, column=0, sticky=tk.W)
        self.clear = w.OnOff(lhs, False, self.check)
        self.clear.grid(row=1, column=1, columnspan=2, sticky=tk.W)

        # nod telescope
        self.nodLab = tk.Label(lhs, text='Dithering')
        self.nodLab.grid(row=2, column=0, sticky=tk.W)
        self.nod = w.OnOff(lhs, False, self.setupNodding)
        self.nod.grid(row=2, column=1, columnspan=2, sticky=tk.W)
        self.nodPattern = {}

        # Overscan in x enabled
        self.oscanLab = tk.Label(lhs, text='Overscan')
        self.oscanLab.grid(row=3, column=0, sticky=tk.W)
        self.oscan = w.OnOff(lhs, False, self.check)
        self.oscany = w.OnOff(lhs, False, self.check)
        self.oscan.grid(row=3, column=1, sticky=tk.W)
        self.oscany.grid(row=3, column=2, sticky=tk.W)

        # led on (expert mode only)
        self.ledLab = tk.Label(lhs, text='LED setting')
        self.ledLab.grid(row=4, column=0, sticky=tk.W)
        self.led = w.OnOff(lhs, False, None)
        self.led.grid(row=4, column=1, columnspan=2, pady=2, sticky=tk.W)

        # dummy mode enabled (expert mode only)
        self.dummyLab = tk.Label(lhs, text='Dummy Output')
        self.dummyLab.grid(row=5, column=0, sticky=tk.W)
        self.dummy = w.OnOff(lhs, True, self.check)
        self.dummy.grid(row=5, column=1, columnspan=2, pady=2, sticky=tk.W)

        # Faster Clock speed enabled
        self.fastClkLab = tk.Label(lhs, text='Fast Clocks')
        self.fastClkLab.grid(row=6, column=0, sticky=tk.W)
        self.fastClk = w.OnOff(lhs, False, self.check)
        self.fastClk.grid(row=6, column=1, columnspan=2, pady=2, sticky=tk.W)

        # Readout speed
        tk.Label(lhs, text='Readout speed').grid(row=7, column=0, sticky=tk.W)
        self.readSpeed = w.Select(lhs, 1, ('Fast', 'Slow'), self.check)
        self.readSpeed.grid(row=7, column=1, columnspan=2, pady=2, sticky=tk.W)

        # Exp delay
        tk.Label(lhs, text='Exposure delay (s)').grid(row=8, column=0,
                                                      sticky=tk.W)
        self.expose = w.Expose(lhs, 0.1, 0.00001, 1677.7207,
                               self.check, width=7)
        self.expose.grid(row=8, column=1, columnspan=2, pady=2, sticky=tk.W)

        # num exp
        tk.Label(lhs, text='Num. exposures  ').grid(row=9, column=0,  sticky=tk.W)
        self.number = w.PosInt(lhs, 0, None, False, width=7)
        self.number.grid(row=9, column=1, columnspan=2, pady=2, sticky=tk.W)

        # nb, ng, nr etc
        labels = ('nu', 'ng', 'nr', 'ni', 'nz')
        ivals = (1, 1, 1, 1, 1)
        imins = (1, 1, 1, 1, 1)
        imaxs = (500, 500, 500, 500, 500)
        self.nmult = ExposureMultiplier(rhs, labels, ivals, imins, imaxs,
                                        5, self.check, False, width=4)
        # grid (on RHS)
        self.nmult.grid(row=0, column=0, pady=2, sticky=tk.W + tk.S)

        # We have two possible window frames. A single pair for
        # drift mode, or a 2-quad frame for window mode.

        # drift frame
        # xstart - LH window of pair
        xsls = (1,)
        xslmins = (1,)
        xslmaxs = (1024,)
        # xstart - RH window of pair
        xsrs = (1025,)
        xsrmins = (1025,)
        xsrmaxs = (2048,)
        # ystart values
        yss = (1,)
        ysmins = (1,)
        ysmaxs = (512,)
        # sizes of windows (start at FF)
        nxs = (100,)
        nys = (100,)
        # allowed binning factors
        xbfac = tuple(range(1, 21))
        ybfac = tuple(range(1, 21))
        self.drift_frame = w.WinPairs(lhs, xsls, xslmins, xslmaxs,
                                      xsrs, xsrmins, xsrmaxs,
                                      yss, ysmins, ysmaxs,
                                      nxs, nys, xbfac, ybfac,
                                      self.check)

        # window frame for quads
        # xstart on LHS
        xsll = xsul = (1, 1)
        xsllmin = xsulmin = (1, 1)
        xsllmax = xsulmax = (1024, 1024)
        # xstart on RHS
        xslr = xsur = (1025, 1025)
        xslrmin = xsurmin = (1025, 1025)
        xslrmax = xsurmax = (2048, 2048)
        # ystart
        ys = (1, 1)
        ysmin = (1, 1)
        ysmax = (512, 512)
        # sizes (start at FF)
        nx = (1024, 1024)
        ny = (512, 512)
        self.quad_frame = w.WinQuads(lhs, xsll, xsllmin, xsllmax,
                                     xsul, xsulmin, xsulmax,
                                     xslr, xslrmin, xslrmax,
                                     xsur, xsurmin, xsurmax,
                                     ys, ysmin, ysmax, nx, ny,
                                     xbfac, ybfac, self.check)

        self.quad_frame.grid(row=10, column=0, columnspan=3,
                             sticky=tk.W+tk.N)

        # Pack two halfs
        lhs.pack(side=tk.LEFT, anchor=tk.N, padx=5)
        rhs.pack(side=tk.LEFT, anchor=tk.N, padx=5)

        # Store freeze state
        self.frozen = False

        self.setExpertLevel()

    @property
    def wframe(self):
        if self.isDrift():
            return self.drift_frame
        return self.quad_frame

    def setupNodding(self):
        """
        Setup Nodding for GTC
        """
        g = get_root(self).globals

        if not self.nod():
            # re-enable clear mode box if not drift
            if not self.isDrift():
                self.clear.enable()

            # clear existing nod pattern
            self.nodPattern = {}
            self.check()
            return

        # Do nothing if we're not at the GTC
        if g.cpars['telins_name'] != 'GTC':
            messagebox.showerror('Error', 'Cannot dither WHT')
            self.nod.set(False)
            self.nodPattern = {}
            return

        # check for drift mode and bomb out
        if self.isDrift():
            messagebox.showerror('Error', 'Cannot dither telescope in drift mode')
            self.nod.set(False)
            self.nodPattern = {}
            return

        # check for clear not enabled and warn
        if not self.clear():
            if not messagebox.askokcancel('Warning',
                                          'Dithering telescope will enable clear mode. Continue?'):
                self.nod.set(False)
                self.nodPattern = {}
                return

        # Ask for nod pattern
        try:
            home = expanduser('~')
            fname = filedialog.askopenfilename(
                title='Open offsets text file',
                defaultextension='.txt',
                filetypes=[('text files', '.txt')],
                initialdir=home)

            if not fname:
                g.clog.warn('Aborted load from disk')
                raise ValueError

            ra, dec = np.loadtxt(fname).T
            if len(ra) != len(dec):
                g.clog.warn('Mismatched lengths of RA and Dec offsets')
                raise ValueError

            data = dict(
                ra=ra.tolist(),
                dec=dec.tolist()
            )
        except:
            g.clog.warn('Setting dither pattern failed. Disabling dithering')
            self.nod.set(False)
            self.nodPattern = {}
            return

        # store nodding on ipars object
        self.nodPattern = data
        # enable clear mode
        self.clear.set(True)
        # update
        self.check()

    def setExpertLevel(self):
        g = get_root(self).globals
        level = g.cpars['expert_level']
        if level == 0:
            self.ledLab.grid_forget()
            self.led.grid_forget()
            self.led.set(0)

            self.oscanLab.config(text='Overscan')
            self.oscany.grid_forget()
            self.remember_oscany = self.oscany()
            self.oscany.set(0)

            self.dummyLab.grid_forget()
            self.dummy.grid_forget()
        else:
            self.ledLab.grid(row=4, column=0, sticky=tk.W)
            self.led.grid(row=4, column=1, columnspan=2, pady=2, sticky=tk.W)

            self.oscanLab.config(text='Overscan (x, y)')
            self.oscany.grid(row=3, column=2, sticky=tk.W)
            if hasattr(self, 'remember_oscany'):
                self.oscany.set(self.remember_oscany)

            self.dummyLab.grid(row=5, column=0, sticky=tk.W)
            self.dummy.grid(row=5, column=1, columnspan=2, pady=2, sticky=tk.W)

    def isDrift(self):
        if self.app.value() == 'Drift':
            return True
        elif self.app.value() in ['FullFrame', 'Windows']:
            return False
        else:
            raise DriverError('InstPars.isDrift: application ' +
                              self.app.value() + ' not recognised')

    def isFF(self):
        if self.app.value() == 'FullFrame':
            return True
        elif self.app.value() in ['Drift', 'Windows']:
            return False
        else:
            raise DriverError('InstPars.isDrift: application ' +
                              self.app.value() + ' not recognised')

    def dumpJSON(self):
        """
        Encodes current parameters to JSON compatible dictionary
        """
        numexp = self.number.get()
        expTime, _, _, _, _ = self.timing()
        if numexp == 0:
            numexp = -1

        data = dict(
            numexp=self.number.value(),
            app=self.app.value(),
            led_flsh=self.led(),
            dummy_out=self.dummy(),
            fast_clks=self.fastClk(),
            readout=self.readSpeed(),
            dwell=self.expose.value(),
            exptime=expTime,
            oscan=self.oscan(),
            oscany=self.oscany(),
            xbin=self.wframe.xbin.value(),
            ybin=self.wframe.ybin.value(),
            multipliers=self.nmult.getall(),
            clear=self.clear()
        )

        # only allow nodding in clear mode, even if GUI has got confused
        if data['clear'] and self.nodPattern:
            data['nodpattern'] = self.nodPattern

        # no mixing clear and multipliers, no matter what GUI says
        if data['clear']:
            data['multipliers'] = [1 for i in self.nmult.getall()]

        # add window mode
        if not self.isFF():
            if self.isDrift():
                # no clear, multipliers or oscan in drift
                for setting in ('clear', 'oscan', 'oscany'):
                    data[setting] = 0
                data['multipliers'] = [1 for i in self.nmult.getall()]

                for iw, (xsl, xsr, ys, nx, ny) in enumerate(self.wframe):
                    data['x{}start_left'.format(iw+1)] = xsl
                    data['x{}start_right'.format(iw+1)] = xsr
                    data['y{}start'.format(iw+1)] = ys
                    data['y{}size'.format(iw+1)] = ny
                    data['x{}size'.format(iw+1)] = nx
            else:
                # no oscany in window mode
                data['oscany'] = 0

                for iw, (xsll, xsul, xslr, xsur, ys, nx, ny) in enumerate(self.wframe):
                    data['x{}start_upperleft'.format(iw+1)] = xsul
                    data['x{}start_lowerleft'.format(iw+1)] = xsll
                    data['x{}start_upperright'.format(iw+1)] = xsur
                    data['x{}start_lowerright'.format(iw+1)] = xslr
                    data['y{}start'.format(iw+1)] = ys
                    data['x{}size'.format(iw+1)] = nx
                    data['y{}size'.format(iw+1)] = ny
        return data

    def loadJSON(self, json_string):
        """
        Loads in an application saved in JSON format.
        """
        g = get_root(self).globals
        data = json.loads(json_string)['appdata']
        # first set the parameters which change regardless of mode
        # number of exposures
        numexp = data.get('numexp', 0)
        if numexp == -1:
            numexp = 0
        self.number.set(numexp)
        # Overscan (x, y)
        if 'oscan' in data:
            self.oscan.set(data['oscan'])
        if 'oscany' in data:
            self.oscan.set(data['oscany'])
        # LED setting
        self.led.set(data.get('led_flsh', 0))
        # Dummy output enabled
        self.dummy.set(data.get('dummy_out', 0))
        # Fast clocking option?
        self.fastClk.set(data.get('fast_clks', 0))
        # readout speed
        self.readSpeed.set(data.get('readout', 'Slow'))
        # dwell
        dwell = data.get('dwell', 0)
        self.expose.set(str(float(dwell)))

        # multipliers
        mult_values = data.get('multipliers',
                               (1, 1, 1, 1, 1))
        self.nmult.setall(mult_values)

        # look for nodpattern in data
        nodPattern = data.get('nodpattern', {})
        if nodPattern and g.cpars['telins_name'] == 'GTC':
            self.nodPattern = nodPattern
            self.nod.set(True)
            self.clear.set(True)
        else:
            self.nodPattern = {}
            self.nod.set(False)

        # binning
        self.quad_frame.xbin.set(data.get('xbin', 1))
        self.quad_frame.ybin.set(data.get('ybin', 1))
        self.drift_frame.xbin.set(data.get('xbin', 1))
        self.drift_frame.ybin.set(data.get('ybin', 1))

        # now for the behaviour which depends on mode
        if 'app' in data:
            self.app.set(data['app'])
            app = data['app']

            if app == 'Drift':
                # disable clear mode in drift
                self.clear.set(0)
                # only one pair allowed
                self.wframe.npair.set(1)

                # set the window pair values
                labels = ('x1start_left', 'y1start',
                          'x1start_right', 'x1size',
                          'y1size')
                if not all(label in data for label in labels):
                    raise DriverError('Drift mode application missing window params')
                # now actually set them
                self.wframe.xsl[0].set(data['x1start_left'])
                self.wframe.xsr[0].set(data['x1start_right'])
                self.wframe.ys[0].set(data['y1start'])
                self.wframe.nx[0].set(data['x1size'])
                self.wframe.ny[0].set(data['y1size'])
                self.wframe.check()

            elif app == 'FullFrame':
                # enable clear mode if set
                self.clear.set(data.get('clear', 0))

            elif app == 'Windows':
                # enable clear mode if set
                self.clear.set(data.get('clear', 0))
                nquad = 0
                for nw in range(2):
                    labels = ('x{0}start_lowerleft y{0}start x{0}start_upperleft x{0}start_upperright ' +
                              'x{0}start_lowerright x{0}size y{0}size').format(nw+1).split()
                    if all(label in data for label in labels):
                        xsll = data[labels[0]]
                        xslr = data[labels[4]]
                        xsul = data[labels[2]]
                        xsur = data[labels[3]]
                        ys = data[labels[1]]
                        nx = data[labels[5]]
                        ny = data[labels[6]]
                        self.wframe.xsll[nw].set(xsll)
                        self.wframe.xslr[nw].set(xslr)
                        self.wframe.xsul[nw].set(xsul)
                        self.wframe.xsur[nw].set(xsur)
                        self.wframe.ys[nw].set(ys)
                        self.wframe.nx[nw].set(nx)
                        self.wframe.ny[nw].set(ny)
                        nquad += 1
                    else:
                        break
                self.wframe.nquad.set(nquad)
                self.wframe.check()

    def check(self, *args):
        """
        Callback to check validity of instrument parameters.

        Performs the following tasks:
            - spots and flags overlapping windows or null window parameters
            - flags windows with invalid dimensions given the binning parameter
            - sets the correct number of enabled windows
            - disables or enables clear and nod buttons depending on drift mode or not
            - checks for window synchronisation, enabling sync button if required
            - enables or disables start button if settings are OK

        Returns
        -------
        status : bool
            True or False according to whether the settings are OK.
        """
        status = True
        g = get_root(self).globals

        # clear errors on binning (may be set later if FF)
        xbinw, ybinw = self.wframe.xbin, self.wframe.ybin
        xbinw.config(bg=g.COL['main'])
        ybinw.config(bg=g.COL['main'])

        # keep binning factors of drift mode and windowed mode up to date
        oframe, aframe = ((self.quad_frame, self.drift_frame) if self.drift_frame.winfo_ismapped()
                          else (self.drift_frame, self.quad_frame))
        xbin, ybin = aframe.xbin.value(), aframe.ybin.value()
        oframe.xbin.set(xbin)
        oframe.ybin.set(ybin)

        if not self.frozen:
            if self.clear() or self.isDrift():
                # disable nmult in clear or drift mode
                self.nmult.disable()
            else:
                self.nmult.enable()

        if self.isDrift():
            self.clearLab.config(state='disable')
            self.nodLab.config(state='disable')
            if not self.drift_frame.winfo_ismapped():
                self.quad_frame.grid_forget()
                self.drift_frame.grid(row=10, column=0, columnspan=3,
                                      sticky=tk.W+tk.N)

            if not self.frozen:
                self.oscany.config(state='disable')
                self.oscan.config(state='disable')
                self.clear.config(state='disable')
                self.nod.config(state='disable')
                self.wframe.enable()
                status = self.wframe.check()

        elif self.isFF():
            # special case check of binning from window frame
            if 1024 % xbin != 0:
                status = False
                xbinw.config(bg=g.COL['error'])
            elif (1024 // xbin) % 4 != 0:
                status = False
                xbinw.config(bg=g.COL['error'])
            if 512 % ybin != 0:
                status = False
                ybinw.config(bg=g.COL['error'])

            if not self.quad_frame.winfo_ismapped():
                self.drift_frame.grid_forget()
                self.quad_frame.grid(row=10, column=0, columnspan=3,
                                     sticky=tk.W+tk.N)

            self.clearLab.config(state='normal')
            if g.cpars['telins_name'] == 'GTC':
                self.nodLab.config(state='normal')
            else:
                self.nodLab.config(state='disable')
            if not self.frozen:
                self.oscany.config(state='normal')
                self.oscan.config(state='normal')
                self.clear.config(state='normal')
                if g.cpars['telins_name'] == 'GTC':
                    self.nod.config(state='normal')
                else:
                    self.nod.config(state='disable')
                self.wframe.disable()

        else:
            self.clearLab.config(state='normal')
            if g.cpars['telins_name'] == 'GTC':
                self.nodLab.config(state='normal')
            else:
                self.nodLab.config(state='disable')
            if not self.quad_frame.winfo_ismapped():
                self.drift_frame.grid_forget()
                self.quad_frame.grid(row=10, column=0, columnspan=3,
                                     sticky=tk.W+tk.N)

            if not self.frozen:
                self.oscany.config(state='disable')
                self.oscan.config(state='normal')
                self.clear.config(state='normal')
                if g.cpars['telins_name'] == 'GTC':
                    self.nod.config(state='normal')
                else:
                    self.nod.config(state='disable')
                self.wframe.enable()
                status = self.wframe.check()

        # exposure delay
        if self.expose.ok():
            self.expose.config(bg=g.COL['main'])
        else:
            self.expose.config(bg=g.COL['warn'])
            status = False

        # don't allow binning other than 1, 2 in overscan or prescan mode
        if self.oscan() or self.oscany():
            if xbin not in (1, 2):
                status = False
                xbinw.config(bg=g.COL['error'])
            if ybin not in (1, 2):
                status = False
                ybinw.config(bg=g.COL['error'])

        # disable clear if nodding enabled. re-enable if not drift
        if not self.frozen:
            if self.nod() or self.nodPattern:
                self.clear.config(state='disabled')
                self.clearLab.config(state='disabled')
            elif not self.isDrift():
                self.clear.config(state='normal')
                self.clearLab.config(state='normal')

        # allow posting if parameters are OK. update count and SN estimates too
        if status:
            if (g.cpars['hcam_server_on'] and g.cpars['eso_server_online'] and
                    g.observe.start['state'] == 'disabled' and
                    not isRunActive(g)):
                g.observe.start.enable()
            g.count.update()
        else:
            g.observe.start.disable()

        return status

    def freeze(self):
        """
        Freeze all settings so they cannot be altered
        """
        self.app.disable()
        self.clear.disable()
        self.nod.disable()
        self.led.disable()
        self.dummy.disable()
        self.readSpeed.disable()
        self.expose.disable()
        self.number.disable()
        self.wframe.disable(everything=True)
        self.nmult.disable()
        self.frozen = True

    def unfreeze(self):
        """
        Reverse of freeze
        """
        self.app.enable()
        self.clear.enable()
        self.nod.enable()
        self.led.enable()
        self.dummy.enable()
        self.readSpeed.enable()
        self.expose.enable()
        self.number.enable()
        self.wframe.enable()
        self.nmult.enable()
        self.frozen = False

    def getRtplotWins(self):
        """"
        Returns a string suitable to sending off to rtplot when
        it asks for window parameters. Returns null string '' if
        the windows are not OK. This operates on the basis of
        trying to send something back, even if it might not be
        OK as a window setup. Note that we have to take care
        here not to update any GUI components because this is
        called outside of the main thread.
        """
        try:
            if self.isFF():
                return 'fullframe\r\n'
            elif self.isDrift():
                xbin = self.wframe.xbin.value()
                ybin = self.wframe.ybin.value()
                nwin = 2*self.wframe.npair.value()
                ret = str(xbin) + ' ' + str(ybin) + ' ' + str(nwin) + '\r\n'
                for xsl, xsr, ys, nx, ny in self.wframe:
                    ret += '{:d} {:d} {:d} {:d}\r\n'.format(
                        xsl, ys, nx, ny
                    )
                    ret += '{:d} {:d} {:d} {:d}'.format(
                        xsr, ys, nx, ny
                    )
                return ret
            else:
                xbin = self.wframe.xbin.value()
                ybin = self.wframe.ybin.value()
                nwin = 4*self.wframe.nquad.value()
                ret = str(xbin) + ' ' + str(ybin) + ' ' + str(nwin) + '\r\n'
                for xsll, xsul, xslr, xsur, ys, nx, ny in self.wframe:
                    ret += '{:d} {:d} {:d} {:d}\r\n'.format(
                        xsll, ys, nx, ny
                    )
                    ret += '{:d} {:d} {:d} {:d}\r\n'.format(
                        xsul, 1025 - ys - ny, nx, ny
                    )
                    ret += '{:d} {:d} {:d} {:d}\r\n'.format(
                        xslr, ys, nx, ny
                    )
                    ret += '{:d} {:d} {:d} {:d}\r\n'.format(
                        xsur, 1025 - ys - ny, nx, ny
                    )
                return ret
        except:
            return ''

    def timing(self):
        """
        Estimates timing information for the current setup. You should
        run a check on the instrument parameters before calling this.

        Returns: (expTime, deadTime, cycleTime, dutyCycle)

        expTime   : exposure time per frame (seconds)
        deadTime  : dead time per frame (seconds)
        cycleTime : sampling time (cadence), (seconds)
        dutyCycle : percentage time exposing.
        frameRate : number of frames per second
        """
        # drift mode y/n?
        isDriftMode = self.isDrift()
        # FF y/n?
        isFF = self.isFF()

        # Set the readout speed
        readSpeed = self.readSpeed()

        if readSpeed == 'Fast' and self.dummy():
            video = VIDEO_FAST
        elif readSpeed == 'Slow' and self.dummy():
            video = VIDEO_SLOW
        elif not self.dummy():
            video = VIDEO_SLOW_SE
        else:
            raise DriverError('InstPars.timing: readout speed = ' +
                              readSpeed + ' not recognised.')

        if self.fastClk():
            DUMP_TIME = DUMP_TIME_FAST
            VCLOCK_FRAME = VCLOCK_FAST
            VCLOCK_STORAGE = VCLOCK_FAST
            HCLOCK = HCLOCK_FAST
        else:
            DUMP_TIME = DUMP_TIME_SLOW
            VCLOCK_FRAME = VCLOCK_FRAME_SLOW
            VCLOCK_STORAGE = VCLOCK_STORAGE_SLOW
            HCLOCK = HCLOCK_SLOW

        # clear chip on/off?
        lclear = not isDriftMode and self.clear()

        # overscan read or not
        oscan = not isDriftMode and self.oscan()
        oscany = not isDriftMode and self.oscany()

        # get exposure delay
        expose = self.expose.value()

        # window parameters
        xbin = self.wframe.xbin.value()
        ybin = self.wframe.ybin.value()
        if isDriftMode:
            nwin = 1  # number of windows per output
            dys = self.wframe.ys[0].value() - 1
            dnx = self.wframe.nx[0].value()
            dny = self.wframe.ny[0].value()
            dxsl = self.wframe.xsl[0].value()
            dxsr = self.wframe.xsr[0].value()
            # differential shift needed to line both
            # windows up with the edge of the chip
            diffshift = abs(dxsl - 1 - (2*FFX - dxsr - dnx + 1))
        elif isFF:
            nwin = 1
            ys, nx, ny = [0], [1024], [512]
        else:
            ys, nx, ny = [], [], []
            xse, xsf, xsg, xsh = [], [], [], []
            nwin = self.wframe.nquad.value()
            for xsll, xsul, xslr, xsur, ysv, nxv, nyv in self.wframe:
                xse.append(xsll - 1)
                xsf.append(2049 - xslr - nxv)
                xsg.append(2049 - xsur - nxv)
                xsh.append(xsul - 1)
                ys.append(ysv-1)
                nx.append(nxv)
                ny.append(nyv)

        # convert timing parameters to seconds
        expose_delay = expose

        # clear chip by VCLOCK-ing the image and area and dumping storage area (x5)
        if lclear:
            clear_time = 5*(FFY*VCLOCK_FRAME + FFY*DUMP_TIME)
        else:
            clear_time = 0.0

        if isDriftMode:
            # for drift mode, we need the number of windows in the pipeline
            # and the pipeshift
            nrows = FFY  # number of rows in storage area
            pnwin = int(((nrows / dny) + 1)/2)
            pshift = nrows - (2*pnwin-1)*dny
            frame_transfer = (dny+dys)*VCLOCK_FRAME

            yshift = [dys*VCLOCK_STORAGE]

            # After placing the window adjacent to the serial register, the
            # register must be cleared by clocking out the entire register,
            # taking FFX hclocks.
            line_clear = [0.]
            if yshift[0] != 0:
                line_clear[0] = DUMP_TIME

            # to calculate number of HCLOCKS needed to read a line in
            # drift mode we have to account for the diff shifts and dumping.
            # first perform diff shifts
            # for now we need this *2 (for quadrants E, H or F, G)
            numhclocks = 2*diffshift
            # now add the amount of clocks needed to get
            # both windows to edge of chip
            if dxsl - 1 > 2*FFX - dxsr - dnx + 1:
                # it was the left window that got the diff shift,
                # so the number of hclocks increases by the amount
                # needed to get the RH window to the edge
                numhclocks += 2*FFX - dxsr - dnx + 1
            else:
                # vice versa
                numhclocks += dxsl - 1
            # now we actually clock the windows themselves
            numhclocks += dnx
            # finally, we need to hclock the additional pre-scan pixels
            numhclocks += 2*PRSCX

            # here is the total time to read the whole line
            line_read = [VCLOCK_STORAGE*ybin + numhclocks*HCLOCK +
                         video*dnx/xbin + DUMP_TIME + 2*SETUP_READ]

            readout = [(dny/ybin) * line_read[0]]
        elif isFF:
            # move entire image into storage area
            frame_transfer = FFY*VCLOCK_FRAME + DUMP_TIME

            yshift = [0]
            line_clear = [0]

            numhclocks = FFX + PRSCX
            line_read = [VCLOCK_STORAGE*ybin + numhclocks*HCLOCK +
                         video*nx[0]/xbin + SETUP_READ]
            if oscan:
                line_read[0] += video*PRSCX/xbin
            nlines = ny[0]/ybin if not oscany else (ny[0] + 8/ybin)
            readout = [nlines*line_read[0]]
        else:
            # windowed mode
            # move entire image into storage area
            frame_transfer = FFY*VCLOCK_FRAME + DUMP_TIME

            # dump rows in storage area up to start of the window without changing the
            # image area.
            yshift = nwin*[0.]
            yshift[0] = ys[0]*DUMP_TIME
            for nw in range(1, nwin):
                yshift[nw] = (ys[nw]-ys[nw-1]-ny[nw-1])*DUMP_TIME

            line_clear = nwin*[0.]
            # Naidu always dumps the serial register, in windowed mode
            # regardless of whether we need to or not
            for nw in range(nwin):
                line_clear[nw] = DUMP_TIME

            # calculate how long it takes to shift one row into the serial
            # register shift along serial register and then read out the data.
            # total number of hclocks needs to account for diff shifts of
            # windows, carried out in serial
            numhclocks = nwin*[0]
            for nw in range(nwin):
                common_shift = min(xse[nw], xsf[nw], xsg[nw], xsh[nw])
                diffshifts = sum((xs-common_shift for xs in (xse[nw], xsf[nw], xsg[nw], xsh[nw])))
                numhclocks[nw] = 2*PRSCX + common_shift + diffshifts + nx[nw]

            line_read = nwin*[0.]
            # line read includes vclocking a row, all the hclocks, digitising pixels and dumping serial register
            # when windows are read out.
            for nw in range(nwin):
                line_read[nw] = (VCLOCK_STORAGE*ybin + numhclocks[nw]*HCLOCK +
                                 video*nx[nw]/xbin + 2*SETUP_READ + DUMP_TIME)
                if oscan:
                    line_read[nw] += video*PRSCX/xbin

            # multiply time to shift one row into serial register by
            # number of rows for total readout time
            readout = nwin*[0.]
            for nw in range(nwin):
                nlines = ny[nw]/ybin if not oscany else (ny[nw] + 8/ybin)
                readout[nw] = nlines * line_read[nw]

        # now get the total time to read out one exposure.
        cycleTime = expose_delay + clear_time + frame_transfer
        if isDriftMode:
            cycleTime += pshift*VCLOCK_STORAGE + yshift[0] + line_clear[0] + readout[0]
        else:
            for nw in range(nwin):
                cycleTime += yshift[nw] + line_clear[nw] + readout[nw]

        # use 5sec estimate for nod time
        # TODO: replace with accurate estimate
        if self.nod() and lclear:
            cycleTime += 5
        elif self.nod():
            g = get_root(self).globals
            g.clog.warn('ERR: dithering enabled with clear mode off')

        frameRate = 1.0/cycleTime
        expTime = expose_delay if lclear else cycleTime - frame_transfer
        deadTime = cycleTime - expTime
        dutyCycle = 100.0*expTime/cycleTime
        return (expTime, deadTime, cycleTime, dutyCycle, frameRate)


class RunPars(tk.LabelFrame):
    """
    Run parameters
    """
    def __init__(self, master):
        tk.LabelFrame.__init__(self, master, text='Next run parameters',
                               padx=10, pady=10)

        row = 0
        column = 0
        tk.Label(self, text='Target name').grid(row=row, column=column, sticky=tk.W)

        row += 1
        tk.Label(self, text='Filters').grid(row=row, column=column, sticky=tk.W)

        row += 1
        tk.Label(self, text='Programme ID/OB').grid(row=row, column=column, sticky=tk.W)

        row += 1
        tk.Label(self, text='Principal Investigator').grid(row=row,
                                                           column=column, sticky=tk.W)

        row += 1
        tk.Label(self, text='Observer(s)').grid(row=row, column=column, sticky=tk.W)

        row += 1
        tk.Label(self, text='Pre-run comment').grid(row=row, column=column, sticky=tk.W)

        # spacer
        column += 1
        tk.Label(self, text=' ').grid(row=0, column=column)

        # target
        row = 0
        column += 1
        self.target = w.Target(self, self.check)
        self.target.grid(row=row, column=column, sticky=tk.W)

        # filter
        row += 1
        self.filter = w.TextEntry(self, 20, self.check)
        self.filter.grid(row=row, column=column, sticky=tk.W)

        # programme ID / OBID
        row += 1
        self.prog_ob = w.ProgramID(self)
        self.prog_ob.grid(row=row, column=column, sticky=tk.W)

        # principal investigator
        row += 1
        self.pi = w.TextEntry(self, 20, self.check)
        self.pi.grid(row=row, column=column, sticky=tk.W)

        # observers
        row += 1
        self.observers = w.TextEntry(self, 20, self.check)
        self.observers.grid(row=row, column=column, sticky=tk.W)

        # comment
        row += 1
        self.comment = w.TextEntry(self, 38)
        self.comment.grid(row=row, column=column, sticky=tk.W)

    def loadJSON(self, json_string):
        """
        Sets the values of the run parameters given an JSON string
        """
        g = get_root(self).globals
        user = json.loads(json_string)['user']

        def setField(widget, field):
            val = user.get(field)
            if val is not None:
                widget.set(val)

        setField(self.prog_ob.obid, 'OB')
        setField(self.target, 'target')
        setField(self.prog_ob.progid, 'ID')
        setField(self.pi, 'PI')
        setField(self.observers, 'Observers')
        setField(self.comment, 'comment')
        setField(self.filter, 'filters')
        setField(g.observe.rtype, 'flags')

    def dumpJSON(self):
        """
        Encodes current parameters to JSON compatible dictionary
        """
        g = get_root(self).globals
        dtype = g.observe.rtype()
        if dtype == 'bias':
            target = 'BIAS'
        elif dtype == 'flat':
            target = 'FLAT'
        elif dtype == 'dark':
            target = 'DARK'
        else:
            target = self.target.value()

        return dict(
            target=target,
            ID=self.prog_ob.progid.value(),
            PI=self.pi.value(),
            OB='{:04d}'.format(self.prog_ob.obid.value()),
            Observers=self.observers.value(),
            comment=self.comment.value(),
            flags=dtype,
            filters=self.filter.value()
        )

    def check(self, *args):
        """
        Checks the validity of the run parameters. Returns
        flag (True = OK), and a message which indicates the
        nature of the problem if the flag is False.
        """

        ok = True
        msg = ''
        g = get_root(self).globals
        dtype = g.observe.rtype()
        expert = g.cpars['expert_level'] > 0

        if dtype == 'bias' or dtype == 'flat' or dtype == 'dark':
            self.pi.configure(state='disable')
            self.prog_ob.configure(state='disable')
            self.target.disable()
        else:
            if expert:
                self.pi.configure(state='normal')
                self.prog_ob.configure(state='normal')
                self.prog_ob.enable()
            else:
                self.prog_ob.configure(state='disable')
                self.pi.configure(state='disable')
                self.prog_ob.disable()
            self.target.enable()

        if g.cpars['require_run_params']:
            if self.target.ok():
                self.target.entry.config(bg=g.COL['main'])
            else:
                self.target.entry.config(bg=g.COL['error'])
                ok = False
                msg += 'Target name field cannot be blank\n'

            if dtype == 'data caution' or \
               dtype == 'data' or dtype == 'technical':

                if self.prog_ob.ok():
                    self.prog_ob.config(bg=g.COL['main'])
                else:
                    self.prog_ob.config(bg=g.COL['error'])
                    ok = False
                    msg += 'Programme or OB ID field cannot be blank\n'

                if self.pi.ok():
                    self.pi.config(bg=g.COL['main'])
                else:
                    self.pi.config(bg=g.COL['error'])
                    ok = False
                    msg += 'Principal Investigator field cannot be blank\n'

            if self.observers.ok():
                self.observers.config(bg=g.COL['main'])
            else:
                self.observers.config(bg=g.COL['error'])
                ok = False
                msg += 'Observers field cannot be blank'
        return (ok, msg)

    def setExpertLevel(self):
        g = get_root(self).globals
        expert = g.cpars['expert_level'] > 0
        if expert:
            self.pi.configure(state='normal')
            self.prog_ob.configure(state='normal')
            self.prog_ob.enable()
        else:
            self.prog_ob.configure(state='disable')
            self.pi.configure(state='disable')
            self.prog_ob.disable()

    def freeze(self):
        """
        Freeze all settings so that they can't be altered
        """
        self.target.disable()
        self.filter.configure(state='disable')
        self.prog_ob.configure(state='disable')
        self.pi.configure(state='disable')
        self.observers.configure(state='disable')
        self.comment.configure(state='disable')

    def unfreeze(self):
        """
        Unfreeze all settings so that they can be altered
        """
        g = get_root(self).globals
        self.filter.configure(state='normal')
        dtype = g.observe.rtype()
        if dtype == 'data caution' or dtype == 'data' or dtype == 'technical':
            self.prog_ob.configure(state='normal')
            self.pi.configure(state='normal')
            self.target.enable()
        self.observers.configure(state='normal')
        self.comment.configure(state='normal')


class CountsFrame(tk.LabelFrame):
    """
    Frame for count rate estimates
    """
    def __init__(self, master):
        """
        master : enclosing widget
        """
        tk.LabelFrame.__init__(self, master, pady=2,
                               text='Count & S-to-N estimator')

        # divide into left and right frames
        lframe = tk.Frame(self, padx=2)
        rframe = tk.Frame(self, padx=2)

        # entries
        self.filter = w.Radio(lframe,
                              ('u', 'g', 'r', 'i', 'z'), 3,
                              self.checkUpdate, initial=1)
        self.mag = w.RangedFloat(lframe, 18., 0., 30.,
                                 self.checkUpdate, True, width=5,
                                 nplaces=2)
        self.seeing = w.RangedFloat(lframe, 1.0, 0.2, 20.,
                                    self.checkUpdate, True, True,
                                    width=5, nplaces=1)
        self.airmass = w.RangedFloat(lframe, 1.5, 1.0, 5.0,
                                     self.checkUpdate, True, width=5,
                                     nplaces=2)
        self.moon = w.Radio(lframe, ('d', 'g', 'b'),  3, self.checkUpdate)

        # results
        self.cadence = w.Ilabel(rframe, text='UNDEF', width=10, anchor=tk.W)
        self.exposure = w.Ilabel(rframe, text='UNDEF', width=10, anchor=tk.W)
        self.duty = w.Ilabel(rframe, text='UNDEF', width=10, anchor=tk.W)
        self.peak = w.Ilabel(rframe, text='UNDEF', width=10, anchor=tk.W)
        self.total = w.Ilabel(rframe, text='UNDEF', width=10, anchor=tk.W)
        self.ston = w.Ilabel(rframe, text='UNDEF', width=10, anchor=tk.W)
        self.ston3 = w.Ilabel(rframe, text='UNDEF', width=10, anchor=tk.W)

        # layout
        # left
        tk.Label(lframe, text='Filter:').grid(row=0, column=0,
                                              padx=5, pady=3, sticky=tk.W+tk.N)
        self.filter.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Label(lframe, text='Mag:').grid(row=1, column=0, padx=5,
                                           pady=3, sticky=tk.W)
        self.mag.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Label(lframe, text='Seeing:').grid(row=2, column=0, padx=5,
                                              pady=3, sticky=tk.W)
        self.seeing.grid(row=2, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Label(lframe, text='Airmass:').grid(row=3, column=0, padx=5,
                                               pady=3, sticky=tk.W)
        self.airmass.grid(row=3, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Label(lframe, text='Moon:').grid(row=4, column=0, padx=5,
                                            pady=3, sticky=tk.W)
        self.moon.grid(row=4, column=1, padx=5, pady=3, sticky=tk.W)

        # right
        tk.Label(rframe, text='Cadence:').grid(row=0, column=0, padx=5,
                                               pady=3, sticky=tk.W)
        self.cadence.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Label(rframe, text='Exposure:').grid(row=1, column=0, padx=5,
                                                pady=3, sticky=tk.W)
        self.exposure.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Label(rframe, text='Duty cycle:').grid(row=2, column=0, padx=5,
                                                  pady=3, sticky=tk.W)
        self.duty.grid(row=2, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Label(rframe, text='Peak:').grid(row=3, column=0, padx=5, pady=3,
                                            sticky=tk.W)
        self.peak.grid(row=3, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Label(rframe, text='Total:').grid(row=4, column=0, padx=5,
                                             pady=3, sticky=tk.W)
        self.total.grid(row=4, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Label(rframe, text='S/N:').grid(row=5, column=0, padx=5, pady=3, sticky=tk.W)
        self.ston.grid(row=5, column=1, padx=5, pady=3, sticky=tk.W)

        tk.Label(rframe, text='S/N (3h):').grid(row=6, column=0, padx=5,
                                                pady=3, sticky=tk.W)
        self.ston3.grid(row=6, column=1, padx=5, pady=3, sticky=tk.W)

        # slot frames in
        lframe.grid(row=0, column=0, sticky=tk.W+tk.N)
        rframe.grid(row=0, column=1, sticky=tk.W+tk.N)

    def checkUpdate(self, *args):
        """
        Updates values after first checking instrument parameters are OK.
        This is not integrated within update to prevent ifinite recursion
        since update gets called from ipars.
        """
        g = get_root(self).globals
        if not self.check():
            g.clog.warn('Current observing parameters are not valid.')
            return False

        if not g.ipars.check():
            g.clog.warn('Current instrument parameters are not valid.')
            return False

    def check(self):
        """
        Checks values
        """
        status = True
        g = get_root(self).globals
        if self.mag.ok():
            self.mag.config(bg=g.COL['main'])
        else:
            self.mag.config(bg=g.COL['warn'])
            status = False

        if self.airmass.ok():
            self.airmass.config(bg=g.COL['main'])
        else:
            self.airmass.config(bg=g.COL['warn'])
            status = False

        if self.seeing.ok():
            self.seeing.config(bg=g.COL['main'])
        else:
            self.seeing.config(bg=g.COL['warn'])
            status = False

        return status

    def update(self, *args):
        """
        Updates values. You should run a check on the instrument and
        target parameters before calling this.
        """
        g = get_root(self).globals
        expTime, deadTime, cycleTime, dutyCycle, frameRate = g.ipars.timing()

        total, peak, peakSat, peakWarn, ston, ston3 = \
            self.counts(expTime, cycleTime)

        if cycleTime < 0.01:
            self.cadence.config(text='{0:7.5f} s'.format(cycleTime))
        elif cycleTime < 0.1:
            self.cadence.config(text='{0:6.4f} s'.format(cycleTime))
        elif cycleTime < 1.:
            self.cadence.config(text='{0:5.3f} s'.format(cycleTime))
        elif cycleTime < 10.:
            self.cadence.config(text='{0:4.2f} s'.format(cycleTime))
        elif cycleTime < 100.:
            self.cadence.config(text='{0:4.1f} s'.format(cycleTime))
        elif cycleTime < 1000.:
            self.cadence.config(text='{0:4.0f} s'.format(cycleTime))
        else:
            self.cadence.config(text='{0:5.0f} s'.format(cycleTime))

        if expTime < 0.01:
            self.exposure.config(text='{0:7.5f} s'.format(expTime))
        elif expTime < 0.1:
            self.exposure.config(text='{0:6.4f} s'.format(expTime))
        elif expTime < 1.:
            self.exposure.config(text='{0:5.3f} s'.format(expTime))
        elif expTime < 10.:
            self.exposure.config(text='{0:4.2f} s'.format(expTime))
        elif expTime < 100.:
            self.exposure.config(text='{0:4.1f} s'.format(expTime))
        elif expTime < 1000.:
            self.exposure.config(text='{0:4.0f} s'.format(expTime))
        else:
            self.exposure.config(text='{0:5.0f} s'.format(expTime))

        self.duty.config(text='{0:4.1f} %'.format(dutyCycle))
        self.peak.config(text='{0:d} cts'.format(int(round(peak))))
        if peakSat:
            self.peak.config(bg=g.COL['error'])
        elif peakWarn:
            self.peak.config(bg=g.COL['warn'])
        else:
            self.peak.config(bg=g.COL['main'])

        self.total.config(text='{0:d} cts'.format(int(round(total))))
        self.ston.config(text='{0:.1f}'.format(ston))
        self.ston3.config(text='{0:.1f}'.format(ston3))

    def counts(self, expTime, cycleTime, ap_scale=1.6, ndiv=5):
        """
        Computes counts per pixel, total counts, sky counts
        etc given current magnitude, seeing etc. You should
        run a check on the instrument parameters before calling
        this.

        expTime   : exposure time per frame (seconds)
        cycleTime : sampling, cadence (seconds)
        ap_scale  : aperture radius as multiple of seeing

        Returns: (total, peak, peakSat, peakWarn, ston, ston3)

        total    -- total number of object counts in aperture
        peak     -- peak counts in a pixel
        peakSat  -- flag to indicate saturation
        peakWarn -- flag to indication level approaching saturation
        ston     -- signal-to-noise per exposure
        ston3    -- signal-to-noise after 3 hours on target
        """

        # code directly translated from Java equivalent.
        g = get_root(self).globals

        # Set the readout speed
        readSpeed = g.ipars.readSpeed()
        if readSpeed == 'Fast':
            gain = GAIN_FAST
            read = RNO_FAST
        elif readSpeed == 'Slow':
            gain = GAIN_SLOW
            read = RNO_SLOW
        else:
            raise DriverError('CountsFrame.counts: readout speed = ' +
                              readSpeed + ' not recognised.')

        xbin, ybin = g.ipars.wframe.xbin.value(), g.ipars.wframe.ybin.value()

        # calculate SN info.
        zero, sky, skyTot, darkTot = 0., 0., 0., 0.
        total, peak, correct, signal, readTot, seeing = 0., 0., 0., 0., 0., 0.
        noise, narcsec, npix, signalToNoise3 = 1., 0., 0., 0.

        tinfo = g.TINS[g.cpars['telins_name']]
        filtnam = self.filter.value()

        zero = tinfo['zerop'][filtnam]
        mag = self.mag.value()
        seeing = self.seeing.value()
        sky = g.SKY[self.moon.value()][filtnam]
        airmass = self.airmass.value()
        plateScale = tinfo['plateScale']

        # calculate expected electrons
        total = 10.**((zero-mag-airmass*g.EXTINCTION[filtnam])/2.5)*expTime

        # compute fraction that fall in central pixel
        # assuming target exactly at its centre. Do this
        # by splitting each pixel of the central (potentially
        # binned) pixel into ndiv * ndiv points at
        # which the seeing profile is added. sigma is the
        # RMS seeing in terms of pixels.
        sigma = seeing/g.EFAC/plateScale

        sum = 0.
        for iyp in range(ybin):
            yoff = -ybin/2.+iyp
            for ixp in range(xbin):
                xoff = -xbin/2.+ixp
                for iys in range(ndiv):
                    y = (yoff + (iys+0.5)/ndiv)/sigma
                    for ixs in range(ndiv):
                        x = (xoff + (ixs+0.5)/ndiv)/sigma
                        sum += math.exp(-(x*x+y*y)/2.)
        peak = total*sum/(2.*math.pi*sigma**2*ndiv**2)

        # Work out fraction of flux in aperture with radius AP_SCALE*seeing
        correct = 1. - math.exp(-(g.EFAC*ap_scale)**2/2.)

        # expected sky e- per arcsec
        skyPerArcsec = 10.**((zero-sky)/2.5)*expTime
        # skyPerPixel = skyPerArcsec*plateScale**2*xbin*ybin
        narcsec = math.pi*(ap_scale*seeing)**2
        skyTot = skyPerArcsec*narcsec
        npix = math.pi*(ap_scale*seeing/plateScale)**2/xbin/ybin

        signal = correct*total  # in electrons
        darkTot = npix*DARK_E*expTime  # in electrons
        readTot = npix*read**2  # in electrons

        # noise, in electrons
        noise = math.sqrt(readTot + darkTot + skyTot + signal)

        # Now compute signal-to-noise in 3 hour seconds run
        signalToNoise3 = signal/noise*math.sqrt(3*3600./cycleTime)

        # convert from electrons to counts
        total /= gain
        peak /= gain

        warn = 25000
        sat = 60000

        peakSat = peak > sat
        peakWarn = peak > warn

        return (total, peak, peakSat, peakWarn, signal/noise, signalToNoise3)


class RunType(w.Select):
    """
    Dropdown box to select run type.

    Start button should be disabled until an option is made from this dropdown.
    """
    DTYPES = ('', 'data', 'acquire', 'bias', 'flat', 'dark', 'tech')
    DVALS = ('', 'data', 'data caution', 'bias', 'flat', 'dark', 'technical')

    def __init__(self, master, start_button, checker=None):
        w.Select.__init__(self, master, 0, RunType.DTYPES, self.check)
        self.start_button = start_button
        self._checker = checker

    def __call__(self):
        index = self.options.index(self.val.get())
        return RunType.DVALS[index]

    def set(self, value):
        index = RunType.DVALS.index(value)
        w.Select.set(self, RunType.DTYPES[index])

    def check(self, *args):
        if self._checker is not None:
            self._checker()
        if self.val.get() == '':
            self.start_button.run_type_set = False
            self.start_button.disable()
        else:
            self.start_button.run_type_set = True
            g = get_root(self).globals
            if (g.cpars['hcam_server_on'] and g.cpars['eso_server_online'] and
                    g.observe.start['state'] == 'disabled' and not isRunActive(g)):
                self.start_button.enable()
            g.rpars.check()


class Start(w.ActButton):
    """
    Button to start a run.

    This is a complex process including the following steps:

    -- check the instrument and run parameters are OK
    -- optionally, hassle the user if the target changes
    -- post the run settings to the ESO NGC control server
    -- start the run
    -- update the button status
    -- start the exposure timer
    """
    def __init__(self, master, width):
        """
        Parameters
        ----------
        master : tk
            containing widget
        width : int
            width of button
        """
        w.ActButton.__init__(self, master, width, text='Start')
        g = get_root(self).globals
        self.config(bg=g.COL['start'])
        self.target = None
        self.run_type_set = False

    def enable(self):
        """
        Enable the button
        """
        if self.run_type_set:
            w.ActButton.enable(self)
            g = get_root(self).globals
            self.config(bg=g.COL['start'])

    def disable(self):
        """
        Disable the button, if in non-expert mode.
        """
        w.ActButton.disable(self)
        g = get_root(self).globals
        if self._expert:
            self.config(bg=g.COL['start'])
        else:
            self.config(bg=g.COL['startD'])

    def setExpert(self):
        """
        Turns on 'expert' status whereby the button is always enabled,
        regardless of its activity status.
        """
        w.ActButton.setExpert(self)
        g = get_root(self).globals
        self.config(bg=g.COL['start'])

    def setNonExpert(self):
        """
        Turns off 'expert' status whereby to allow a button to be disabled
        """
        self._expert = False
        if self._active and self.run_type_set:
            self.enable()
        else:
            self.disable()

    def act(self):
        """
        Carries out action associated with start button
        """
        g = get_root(self).globals
        # check binning against overscan
        msg = """
        HiperCAM has an o/scan of 50 pixels.
        Your binning does not fit into this
        region. Some columns will contain a
        mix of o/scan and data.

        Click OK if you wish to continue."""
        if g.ipars.oscan():
            xbin, ybin = g.ipars.wframe.xbin.value(), g.ipars.wframe.ybin.value()
            if xbin not in (1, 2, 5, 10) or ybin not in (1, 2, 5, 10):
                if not messagebox.askokcancel('Binning alert', msg):
                    return False

        # Check instrument pars are OK
        if not g.ipars.check():
            g.clog.warn('Invalid instrument parameters; save failed.')
            return False

        # create JSON to post
        data = createJSON(g)

        # POST
        try:
            success = postJSON(g, data)
            if not success:
                raise Exception('postJSON returned False')
        except Exception as err:
            g.clog.warn("Failed to post data to servers")
            g.clog.warn(str(err))
            return False

        # Is nod enabled? Should we start GTC offsetter?
        try:
            success = startNodding(g, data)
            if not success:
                raise Exception('Failed to start dither: response was false')
        except Exception as err:
            g.clog.warn("Failed to start GTC offsetter")
            g.clog.warn(str(err))
            return False

        # START
        try:
            success = execCommand(g, 'start')
            if not success:
                raise Exception("Start command failed: check server response")
        except Exception as err:
            g.clog.warn('Failed to start run')
            g.clog.warn(str(err))
            return False

        # Send first offset if nodding enabled.
        # Initial trigger is sent after first offset, otherwise we'll hang indefinitely
        try:
            success = forceNod(g, data)
            if not success:
                raise Exception('Failed to send intitial offset and trigger - exposure will be paused indefinitely')
        except Exception as err:
            g.clog.warn('Run is paused indefinitely')
            g.clog.warn('use "ngcbCmd seq start" to fix')
            g.clog.warn(str(err))

        # Run successfully started.
        # enable stop button, disable Start
        # also make inactive until RunType select box makes active again
        # start run timer
        # finally, clear table which stores TCS info during this run
        self.disable()
        self.run_type_set = False
        g.observe.stop.enable()
        g.info.timer.start()
        g.info.clear_tcs_table()
        return True


class Load(w.ActButton):
    """
    Class defining the 'Load' button's operation. This loads a previously
    saved configuration from disk.
    """

    def __init__(self, master, width):
        """
        master  : containing widget
        width   : width of button
        """
        w.ActButton.__init__(self, master, width, text='Load')

    def act(self):
        """
        Carries out the action associated with the Load button
        """
        g = get_root(self).globals
        fname = filedialog.askopenfilename(
            defaultextension='.json',
            filetypes=[('json files', '.json'), ('fits files', '.fits')],
            initialdir=g.cpars['app_directory'])
        if not fname:
            g.clog.warn('Aborted load from disk')
            return False

        # load json
        if fname.endswith('.json'):
            with open(fname) as ifname:
                json_string = ifname.read()
        else:
            json_string = jsonFromFits(fname)

        # load up the instrument settings
        g.ipars.loadJSON(json_string)

        # load up the run parameters
        g.rpars.loadJSON(json_string)

        return True


class Save(w.ActButton):
    """
    Class defining the 'Save' button's operation. This saves the
    current configuration to disk.
    """
    def __init__(self, master, width):
        """
        master  : containing widget
        width   : width of button
        """
        w.ActButton.__init__(self, master, width, text='Save')

    def act(self):
        """
        Carries out the action associated with the Save button
        """
        g = get_root(self).globals
        g.clog.info('\nSaving current application to disk')

        # check instrument parameters
        if not g.ipars.check():
            g.clog.warn('Invalid instrument parameters; save failed.')
            return False

        # check run parameters
        rok, msg = g.rpars.check()
        if not rok:
            g.clog.warn('Invalid run parameters; save failed.')
            g.clog.warn(msg)
            return False

        # Get data to save
        data = createJSON(g, full=False)

        # Save to disk
        if saveJSON(g, data):
            # modify buttons
            g.observe.load.enable()
            g.observe.unfreeze.disable()

            # unfreeze the instrument and run params
            g.ipars.unfreeze()
            g.rpars.unfreeze()
            return True
        else:
            return False


class Unfreeze(w.ActButton):
    """
    Class defining the 'Unfreeze' button's operation.
    """
    def __init__(self, master, width):
        """
        master  : containing widget
        width   : width of button
        """
        w.ActButton.__init__(self, master, width, text='Unfreeze')

    def act(self):
        """
        Carries out the action associated with the Unfreeze button
        """
        g = get_root(self).globals
        g.ipars.unfreeze()
        g.rpars.unfreeze()
        g.observe.load.enable()
        self.disable()


class Observe(tk.LabelFrame):
    """
    Observe widget. Collects together all the buttons needed for observing.
    """
    def __init__(self, master):
        tk.LabelFrame.__init__(self, master, padx=10, pady=10)

        width = 10
        self.load = Load(self, width)
        self.save = Save(self, width)
        self.unfreeze = Unfreeze(self, width)
        self.start = Start(self, width)
        self.rtype = RunType(self, self.start)
        self.stop = w.Stop(self, width)

        # Lay them out
        self.load.grid(row=0, column=0)
        self.save.grid(row=1, column=0)
        self.unfreeze.grid(row=2, column=0)
        self.rtype.grid(row=0, column=1, sticky=tk.EW)
        self.start.grid(row=1, column=1)
        self.stop.grid(row=2, column=1)

        # Define initial status
        self.start.disable()
        self.stop.disable()
        self.unfreeze.disable()

        # Implement expert level
        self.setExpertLevel()

    def setExpertLevel(self):
        """
        Set expert level
        """
        g = get_root(self).globals
        level = g.cpars['expert_level']

        # now set whether buttons are permanently enabled or not
        if level == 0 or level == 1:
            self.load.setNonExpert()
            self.save.setNonExpert()
            self.unfreeze.setNonExpert()
            self.start.setNonExpert()
            self.stop.setNonExpert()

        elif level == 2:
            self.load.setExpert()
            self.save.setExpert()
            self.unfreeze.setExpert()
            self.start.setExpert()
            self.stop.setExpert()
