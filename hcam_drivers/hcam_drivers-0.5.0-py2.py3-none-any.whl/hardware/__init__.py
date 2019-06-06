# Licensed under a 3-clause BSD style license - see LICENSE.rst

# This sub-module is destined for common non-package specific utility
# functions that will ultimately be merged into `astropy.utils`

# As far as possible, utils contains classes of generic use, such as
# PosInt for positive integer input. See e.g. 'hcam' for more instrument
# dependent components.

from __future__ import print_function, unicode_literals, absolute_import, division
import six
import numpy as np
import threading
import time

from hcam_widgets import widgets as w
from hcam_widgets.tkutils import get_root, addStyle
from . import honeywell, meerstetter, unichiller, vacuum, rack
from ..utils.alarms import AlarmDialog

if not six.PY3:
    import Tkinter as tk
    from Queue import Queue, Empty
else:
    import tkinter as tk
    from queue import Queue, Empty


class NoAlarmState(object):
    """
    State representing no alarm
    """
    @staticmethod
    def raise_alarm(widget):
        widget.alarmdialog = AlarmDialog(
            widget,
            'Critical {} fault on {}'.format(
                widget.kind,
                widget.name
            )
        )
        widget.set_state(ActiveAlarmState)
        widget.alarm_raised_time = time.time()

    @staticmethod
    def cancel_alarm(widget):
        # no alarm, so do nothing
        return

    @staticmethod
    def acknowledge_alarm(widget):
        # no alarm, so do nothing
        return


class ActiveAlarmState(object):
    """
    State representing a currently active alarm
    """
    @staticmethod
    def raise_alarm(widget):
        # no sense raising an alarm that is already active
        return

    @staticmethod
    def cancel_alarm(widget):
        # called when cancel button in alarmwidget clicked
        widget.set_state(NoAlarmState)

    @staticmethod
    def acknowledge_alarm(widget):
        # called when acknowledge button in alarmwidget clicked
        g = get_root(widget.parent).globals
        acknowledged_time_limit = g.cpars['alarm_sleep_time']
        istr = 'Alarm on {} acknowledged, will re-raise in {} mins if not fixed'
        g.clog.info(istr.format(widget.name, acknowledged_time_limit // 60))
        widget.set_state(AcknowledgedAlarmState)


class AcknowledgedAlarmState(object):
    """
    An acknowledged alarm. Quiet, but won't raise again
    for 10 minutes.
    """
    @staticmethod
    def raise_alarm(widget):
        g = get_root(widget).globals
        acknowledged_time_limit = g.cpars['alarm_sleep_time']
        if time.time() - widget.alarm_raised_time > acknowledged_time_limit:
            widget.set_state(NoAlarmState)
            widget.raise_alarm()

    @staticmethod
    def cancel_alarm(widget):
        widget.set_state(NoAlarmState)

    @staticmethod
    def acknowledge_alarm(widget):
        return


class BoolFormatter(object):
    """
    A simple class to convert integer values to True/False strings.

    This class is a bit of a Kludge to make boolean values work nicely with the
    HardwareDisplayWidget, which was originally written with floating point numbers
    in mind. It provides one function, format, which converts 0 to 'ERROR' and 1 to
    'OK'.
    """
    def format(self, val):
        if val == 1:
            return 'OK'
        else:
            return 'ERROR'


class HardwareDisplayWidget(tk.Frame):
    """
    A widget that displays and checks the status of a piece of hardware.

    Consists of a label naming the piece of hardware, and an Ilabel to display the results of
    the hardware check. Checks itself repeatedly in the background using a thread so as
    not to hang the GUI main thread.

    Each HardwareDisplayWidget has its own status (ok/nok) and an alarm state which can
    be NoAlarm, ActiveAlarm, AcknowledgedAlarm.

    Arguments
    ----------
    parent : tk.Widget
        parent widget
    kind : string
        type of hardware item, e.g. 'pressure'
    name : string
        name to display on label
    fmt : string
        format string for displaying results
    update_interval : float
        time in seconds between updates
    lower_limit : float, `~astropy.units.Quantity`
        lower limit for hardware check
    upper_limit : float, `~astropy.units.Quantity`
        upper limit for hardware check
    """
    def __init__(self, parent, kind, name, update_interval, lower_limit, upper_limit):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.name = name
        self.kind = kind
        self.update_interval = int(update_interval*1000)
        self.ok = True
        self.queue = Queue()
        self.fmt = '{:.1f}'
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        self.set_state(NoAlarmState)
        tk.Label(self, text=self.name + ':', width=9, anchor=tk.E).pack(side=tk.LEFT, anchor=tk.N, padx=5)
        self.label = w.Ilabel(self, text='nan', width=9)
        self.label.pack(side=tk.LEFT, anchor=tk.N, padx=5)

        self.after(self.update_interval, self.start_update)

    def process_update(self):
        """
        Try and get the result of hardware update from the queue. If it's not ready yet,
        reschedule this check for 200ms later.
        """
        try:
            val, errmsg = self.queue.get(block=False)
            g = get_root(self.parent).globals
            if errmsg is not None:
                g.clog.warn('Could not update {} for {}: {}'.format(self.kind, self.name, errmsg))

            self.label.configure(text=self.fmt.format(val), bg=g.COL['main'])

            if errmsg is None and val <= self.upper_limit and val >= self.lower_limit:
                self.ok = True
            elif np.isnan(val) and errmsg is None:
                # no error and nan returned means checking disabled
                self.ok = True
            else:
                self.ok = False

            if not self.ok:
                self.label.configure(bg=g.COL['warn'])

            self.after(self.update_interval, self.start_update)
        except Empty:
            self.after(200, self.process_update)

    def start_update(self):
        """
        Start a thread to check hardware, and schedule a later check to see if it's done.
        """
        t = threading.Thread(target=self.update)
        t.start()
        self.after(200, self.process_update)

    def update(self):
        """
        Simple wrapper to call update function and put the return value and any error message into queue.
        """
        errmsg = None
        try:
            val = self.update_function()
        except Exception as err:
            errmsg = str(err)
            val = np.nan
        self.queue.put((val, errmsg))

    def update_function(self):
        raise NotImplementedError('concrete class must implement update_function')

    def acknowledge_alarm(self):
        self._state.acknowledge_alarm(self)

    def raise_alarm(self):
        self._state.raise_alarm(self)

    def cancel_alarm(self):
        self._state.cancel_alarm(self)

    def set_state(self, state):
        self._state = state


class MeerstetterWidget(HardwareDisplayWidget):
    """
    Get CCD info from Meerstetters
    """
    def __init__(self, parent, ms, address, name, kind, update_interval, lower_limit, upper_limit):
        HardwareDisplayWidget.__init__(self, parent, kind, name, update_interval, lower_limit, upper_limit)
        self.ms = ms
        self.address = address
        if kind == 'peltier power':
            self.fmt = '{:.0f}'
        elif kind == 'status':
            self.fmt = BoolFormatter()

    def update_function(self):
        g = get_root(self.parent).globals
        if g.cpars['ccd_temp_monitoring_on']:
            if self.kind == 'status':
                ok, code = self.ms.get_status(self.address)
                return int(ok)
            if self.kind == 'temperature':
                return self.ms.get_ccd_temp(self.address).value
            elif self.kind == 'heatsink temperature':
                return self.ms.get_heatsink_temp(self.address).value
            elif self.kind == 'peltier power':
                return 100 * self.ms.get_current(self.address) / self.ms.tec_current_limit
            else:
                raise ValueError('unknown kind: {}'.format(self.kind))
        else:
            return np.nan


class ChillerWidget(HardwareDisplayWidget):
    """
    Get Temperature from Chiller
    """
    def __init__(self, parent, chiller, update_interval, lower_limit, upper_limit):
        HardwareDisplayWidget.__init__(self, parent, 'temperature', 'CHILLER',
                                       update_interval, lower_limit, upper_limit)
        self.chiller = chiller

    def update_function(self):
        g = get_root(self.parent).globals
        if g.cpars['chiller_temp_monitoring_on']:
            return self.chiller.temperature
        else:
            return np.nan


class RackSensorWidget(HardwareDisplayWidget):
    """
    Get Temperature and Humidity from Rack Sensor
    """
    def __init__(self, parent, rack_sensor, update_interval, lower_limit, upper_limit):
        HardwareDisplayWidget.__init__(self, parent, 'temperature', 'RACK',
                                       update_interval, lower_limit, upper_limit)
        self.rack_sensor = rack_sensor

    def update_function(self):
        g = get_root(self.parent).globals
        if g.cpars['chiller_temp_monitoring_on']:
            return self.rack_sensor.temperature
        else:
            return np.nan


class FlowRateWidget(HardwareDisplayWidget):
    """
    Flow rates from honeywell
    """
    def __init__(self, parent, honey_ip, pen_address, name, update_interval, lower_limit, upper_limit):
        HardwareDisplayWidget.__init__(self, parent, 'flow rate', name, update_interval,
                                       lower_limit, upper_limit)
        self.honey = honeywell.Honeywell(honey_ip, 502)
        self.pen_address = pen_address
        self.fmt = '{:.2f}'

    def update_function(self):
        g = get_root(self.parent).globals
        if g.cpars['flow_monitoring_on']:
            return self.honey.read_pen(self.pen_address)
        else:
            return np.nan


class VacuumWidget(HardwareDisplayWidget):
    """
    Vacuum pressure from gauge
    """
    def __init__(self, parent, gauge, name, update_interval, lower_limit, upper_limit):
        HardwareDisplayWidget.__init__(self, parent, 'pressure', name, update_interval,
                                       lower_limit, upper_limit)
        self.gauge = gauge
        self.fmt = '{:.2E}'

    def update_function(self):
        g = get_root(self.parent).globals
        if g.cpars['ccd_vac_monitoring_on']:
            return 1000*self.gauge.pressure.value
        else:
            return np.nan


class CCDInfoWidget(tk.Toplevel):
    """
    A child window to monitor and show the status of the CCD heads.

    Keeps track of vacuum levels, CCD temperatures, flow rates etc. Normally this
    window is hidden, but can be revealed from the main GUIs menu. It will also
    appear automatically if there any issues, and should play a sound to notify
    users.
    """
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.parent = parent

        addStyle(self)
        self.title("CCD Head Status")

        # do not display on creation
        self.withdraw()

        # dont destroy when we click the close button
        self.protocol('WM_DELETE_WINDOW', self.withdraw)

        # create hardware references
        g = get_root(self.parent).globals
        honey_ip = g.cpars['honeywell_ip']
        self.meerstetters = [
            meerstetter.MeerstetterTEC1090(ip_addr, 50000) for ip_addr in
            g.cpars['meerstetter_ip']]
        self.vacuum_gauges = [
            vacuum.PDR900(g.cpars['termserver_ip'], port) for port in
            g.cpars['vacuum_ports']
        ]
        if g.cpars['telins_name'].lower() == 'wht':
            self.chiller = unichiller.UnichillerMPC(g.cpars['termserver_ip'],
                                                    g.cpars['chiller_port'])
        else:
            self.chiller = rack.GTCRackSensor(g.cpars['rack_sensor_ip'])

        # create label frames
        self.status_frm = tk.LabelFrame(self, text='Meerstetter status', padx=4, pady=4)
        self.temp_frm = tk.LabelFrame(self, text='Temperatures (C)', padx=4, pady=4)
        self.heatsink_frm = tk.LabelFrame(self, text='Heatsink Temps (C)', padx=4, pady=4)
        self.peltier_frm = tk.LabelFrame(self, text='Peltier Powers (%)', padx=4, pady=4)
        self.flow_frm = tk.LabelFrame(self, text='Flow Rates (l/min)', padx=4, pady=4)
        self.vac_frm = tk.LabelFrame(self, text='Vacuums (mbar)', padx=4, pady=4)

        # variables to store hardware widgets
        update_interval = 20
        self.ms_status = []
        self.ccd_temps = []
        self.heatsink_temps = []
        self.peltier_powers = []
        self.ccd_flow_rates = []
        self.vacuums = []
        if g.cpars['telins_name'].lower() == 'wht':
            self.chiller_temp = ChillerWidget(self.temp_frm, self.chiller,
                                              update_interval, g.cpars['chiller_temp_lower'],
                                              g.cpars['chiller_temp_upper'])
        else:
            self.chiller_temp = RackSensorWidget(self.temp_frm, self.chiller, update_interval,
                                                 g.cpars['rack_temp_lower'],
                                                 g.cpars['rack_temp_upper'])

        self.ngc_flow_rate = FlowRateWidget(self.flow_frm, honey_ip, 'ngc', 'NGC', update_interval,
                                            g.cpars['ngc_flow_lower'], g.cpars['ngc_flow_upper'])

        ms1 = self.meerstetters[0]
        ms2 = self.meerstetters[1]
        mapping = {1: (ms1, 1), 2: (ms1, 2), 3: (ms1, 3),
                   4: (ms2, 1), 5: (ms2, 2)}
        # populate CCD frames
        for iccd in range(5):
            ms, address = mapping[iccd+1]
            name = 'CCD {}'.format(iccd+1)
            # meerstetter widgets
            self.ms_status.append(
                MeerstetterWidget(self.status_frm, ms, address, name,
                                  'status', update_interval, 0.5, 1.5)  # ok is 1, which is between 0.5 and 1.5
            )
            self.ccd_temps.append(
                MeerstetterWidget(self.temp_frm, ms, address, name,
                                  'temperature', update_interval,
                                  g.cpars['ccd_temp_lower'],
                                  g.cpars['ccd_temp_upper'])
            )
            self.heatsink_temps.append(
                MeerstetterWidget(self.heatsink_frm, ms, address, name,
                                  'heatsink temperature', update_interval,
                                  g.cpars['ccd_sink_temp_lower'],
                                  g.cpars['ccd_sink_temp_upper'])
            )
            self.peltier_powers.append(
                MeerstetterWidget(self.peltier_frm, ms, address, name,
                                  'peltier power', update_interval,
                                  g.cpars['ccd_peltier_lower'],
                                  g.cpars['ccd_peltier_upper'])
            )

            # grid
            self.ms_status[-1].grid(
                    row=int(iccd/3), column=iccd % 3, padx=5, sticky=tk.W
                )
            self.ccd_temps[-1].grid(
                    row=int(iccd/3), column=iccd % 3, padx=5, sticky=tk.W
                )
            self.heatsink_temps[-1].grid(
                row=int(iccd/3), column=iccd % 3, padx=5, sticky=tk.W
            )
            self.peltier_powers[-1].grid(
                row=int(iccd/3), column=iccd % 3, padx=5, sticky=tk.W
            )

            # flow rates
            pen_address = 'ccd{}'.format(iccd+1)

            self.ccd_flow_rates.append(
                FlowRateWidget(self.flow_frm, honey_ip, pen_address, name, update_interval,
                               g.cpars['ccd_flow_lower'], g.cpars['ccd_flow_upper'])
            )
            self.ccd_flow_rates[-1].grid(
                    row=int(iccd/3), column=iccd % 3, padx=5, sticky=tk.W
            )

        # vacuum gauges
        for iccd, gauge in enumerate(self.vacuum_gauges):
            name = 'CCD {}'.format(iccd+1)
            self.vacuums.append(
                VacuumWidget(self.vac_frm, gauge, name, update_interval, -1e6, 5e-3)
            )
            self.vacuums[-1].grid(
                    row=int(iccd/3), column=iccd % 3, padx=5, sticky=tk.W
            )

        # now for one-off items
        self.chiller_temp.grid(row=1, column=2, padx=5, sticky=tk.W)
        self.ngc_flow_rate.grid(row=1, column=2, padx=5, sticky=tk.W)

        # grid frames
        self.status_frm.grid(row=0, column=0, padx=4, pady=4, sticky=tk.W)
        self.temp_frm.grid(row=1, column=0, padx=4, pady=4, sticky=tk.W)
        self.heatsink_frm.grid(row=2, column=0, padx=4, pady=4, sticky=tk.W)
        self.peltier_frm.grid(row=3, column=0, padx=4, pady=4, sticky=tk.W)
        self.flow_frm.grid(row=4, column=0, padx=4, pady=4, sticky=tk.W)
        self.vac_frm.grid(row=5, column=0, padx=4, pady=4, sticky=tk.W)

        self.after(10000, self.raise_if_nok)

    def _getVal(self, widg):
        """
        Return value from widget if set, else return -99.
        """
        return -99 if widg.label['text'].lower() == 'nan' else float(widg.label['text'])

    def dumpJSON(self):
        """
        Encodes current hw data to JSON compatible dictionary
        """
        data = dict()
        g = get_root(self.parent).globals
        for i in range(5):
            ccd = i+1
            data['ccd{}temp'.format(ccd)] = self._getVal(self.ccd_temps[i])
            data['ccd{}vac'.format(ccd)] = self._getVal(self.vacuums[i])
            data['ccd{}flow'.format(ccd)] = self._getVal(self.ccd_flow_rates[i])
        if g.cpars['focal_plane_slide_on']:
            try:
                (pos_ms, pos_mm, pos_px), msg = g.fpslide.slide.return_position()
                data['fpslide'] = pos_px
            except Exception as err:
                g.clog.warn('Slide error: ' + str(err))
        return data

    @property
    def ok(self):
        okl = [self.chiller_temp.ok, self.ngc_flow_rate.ok]
        okl += [ms_state.ok for ms_state in self.ms_status]
        okl += [ccd_temp.ok for ccd_temp in self.ccd_temps]
        okl += [vac.ok for vac in self.vacuums]
        okl += [flow.ok for flow in self.ccd_flow_rates]
        okl += [power.ok for power in self.peltier_powers]
        return all(okl)

    def raise_if_nok(self):
        widgets = [self.chiller_temp, self.ngc_flow_rate]
        widgets.extend(self.ccd_temps)
        widgets.extend(self.ms_status)
        widgets.extend(self.ccd_flow_rates)
        widgets.extend(self.peltier_powers)
        for widget in widgets:
            if not widget.ok:
                self.deiconify()
                widget.raise_alarm()

        self.after(10000, self.raise_if_nok)
