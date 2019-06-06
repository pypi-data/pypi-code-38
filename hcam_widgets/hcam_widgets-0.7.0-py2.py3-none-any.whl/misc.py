# miscellaneous useful tools
from __future__ import print_function, unicode_literals, absolute_import, division
import json
from six.moves import urllib
import six
import threading
import sys
import traceback
import os
import re

from astropy.io import fits
from astropy.io import ascii
import requests


from . import DriverError
if not six.PY3:
    import tkFileDialog as filedialog
    from StringIO import StringIO
else:
    from tkinter import filedialog
    from io import StringIO

try:
    # should not be a required module since can run on WHT fine without it
    from .gtc.corba import get_telescope_server
    from .gtc.headers import create_header_from_telpars
    has_corba = True
except Exception as err:
    has_corba = False


class ReadServer(object):
    """
    Class to field the json responses sent back from the ULTRACAM servers

    Set the following attributes:

     root    : the decoded json response
     ok      : whether response is OK or not (True/False)
     err     : message if ok == False
     state   : state of the camera. Possibilties are:
               'IDLE', 'BUSY', 'ERROR', 'ABORT', 'UNKNOWN'
     clocks  : whether the clock voltages are enabled. Possible values:
               'enabled', 'disabled'
     run     : current or last run number
    """
    def __init__(self, resp, status_msg=False):
        """
        Parameters
        ----------
        resp : bytes
            response from server
        status_msg : bool (default True)
            Set True if the response should contain status info
        """
        # Store the entire response
        try:
            self.root = json.loads(resp.decode())
            self.ok = True
        except Exception:
            self.ok = False
            self.err = 'Could not parse JSON response'
            self.state = None
            self.clocks = None
            self.root = dict()
            return

        # Work out whether it was happy
        if 'RETCODE' not in self.root:
            self.ok = False
            self.err = 'Could not identify status'
            self.state = None
            self.clocks = None
            return
        else:
            self.ok = True if self.root['RETCODE'] == "OK" else False

        if not status_msg:
            self.state = None
            self.run = 0
            self.err = ''
            self.clocks = None
            self.msg = self.root['MESSAGEBUFFER']
            return

        # Determine state of the camera
        sfind = self.root['system.subStateName']
        if sfind is 'ERR':
            self.ok = False
            self.err = 'Could not identify state'
            self.state = None
            self.clocks = None
            self.root = dict()
            return
        else:
            self.ok = True
            self.err = ''
            self.state = self.root['system.subStateName']

        # determine state of clocks
        sfind = self.root['cldc_0.statusName']
        if sfind is 'ERR':
            self.ok = False
            self.err = 'Could not identify clock status'
            self.state = None
            self.clocks = None
            self.root = dict()
            return
        else:
            self.ok = True
            self.err = ''
            self.clocks = self.root['cldc_0.statusName']

        # Find current run number (set it to 0 if we fail)
        newDataFileName = self.root["exposure.newDataFileName"]
        exposure_state = self.root["exposure.expStatusName"]
        pattern = '\D*(\d*).*.fits'
        try:
            run_number = int(re.match(pattern, newDataFileName).group(1))
            if exposure_state == "success":
                self.run = run_number
            elif exposure_state == "aborted":
                # We use abort instead of end. Don't know why
                self.run = run_number
            elif exposure_state == "integrating":
                self.run = run_number + 1
            else:
                raise ValueError("unknown exposure state {}".format(
                    exposure_state
                ))
        except (ValueError, IndexError, AttributeError):
            self.run = 0

    def resp(self):
        return json.dumps(self.root)


def overlap(xl1, yl1, nx1, ny1, xl2, yl2, nx2, ny2):
    """
    Determines whether two windows overlap
    """
    return (xl2 < xl1+nx1 and xl2+nx2 > xl1 and
            yl2 < yl1+ny1 and yl2+ny2 > yl1)


def forceNod(g, data):
    nodPattern = data.get('appdata', {}).get('nodpattern', {})
    if g.cpars['telins_name'] == 'GTC' and nodPattern:
        try:
            url = urllib.parse.urljoin(g.cpars['gtc_offset_server'], 'force')
            opener = urllib.request.build_opener()
            req = urllib.request.Request(url)
            response = opener.open(req, timeout=5).read().decode()
            g.rlog.info('Dither Server Response: ' + response)
        except Exception as err:
            g.clog.warn('Failed to send dither offset')
            g.clog.warn(str(err))
            return False
    return True


def startNodding(g, data):
    nodPattern = data.get('appdata', {}).get('nodpattern', {})
    if g.cpars['telins_name'] == 'GTC' and nodPattern:
        try:
            url = urllib.parse.urljoin(g.cpars['gtc_offset_server'], 'start')
            opener = urllib.request.build_opener()
            req = urllib.request.Request(url)
            response = opener.open(req, timeout=5).read().decode()
            g.rlog.info('Dither Server Response: ' + response)
        except Exception as err:
            g.clog.warn('Failed to stop dither server')
            g.clog.warn(str(err))
            return False
    return True


def stopNodding(g):
    if g.cpars['telins_name'] == 'GTC':
        try:
            url = urllib.parse.urljoin(g.cpars['gtc_offset_server'], 'stop')
            opener = urllib.request.build_opener()
            req = urllib.request.Request(url)
            response = opener.open(req, timeout=5).read().decode()
            g.rlog.info('Dither Server Response: ' + response)
        except Exception as err:
            g.clog.warn('Failed to stop dither server')
            g.clog.warn(str(err))
            return False
    return True


def saveJSON(g, data, backup=False):
    """
    Saves the current setup to disk.

    g : hcam_drivers.globals.Container
    Container with globals

    data : dict
    The current setup in JSON compatible dictionary format.

    backup : bool
    If we are saving a backup on close, don't prompt for filename
    """
    if not backup:
        fname = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('json files', '.json'), ],
            initialdir=g.cpars['app_directory']
            )
    else:
        fname = os.path.join(os.path.expanduser('~/.hdriver'), 'app.json')

    if not fname:
        g.clog.warn('Aborted save to disk')
        return False

    with open(fname, 'w') as of:
        of.write(
            json.dumps(data, sort_keys=True, indent=4,
                       separators=(',', ': '))
        )
    g.clog.info('Saved setup to' + fname)
    return True


def postJSON(g, data):
    """
    Posts the current setup to the camera and data servers.

    g : hcam_drivers.globals.Container
    Container with globals

    data : dict
    The current setup in JSON compatible dictionary format.
    """
    g.clog.debug('Entering postJSON')

    # encode data as json
    json_data = json.dumps(data).encode('utf-8')

    # Send the xml to the server
    url = urllib.parse.urljoin(g.cpars['hipercam_server'], g.SERVER_POST_PATH)
    g.clog.debug('Server URL = ' + url)

    opener = urllib.request.build_opener()
    g.clog.debug('content length = ' + str(len(json_data)))
    req = urllib.request.Request(url, data=json_data, headers={'Content-type': 'application/json'})
    response = opener.open(req, timeout=15).read()
    g.rlog.debug('Server response: ' + response.decode())
    csr = ReadServer(response, status_msg=False)
    if not csr.ok:
        g.clog.warn('Server response was not OK')
        g.rlog.warn('postJSON response: ' + response.decode())
        g.clog.warn('Server error = ' + csr.err)
        return False

    # now try to setup nodding server if appropriate
    if g.cpars['telins_name'] == 'GTC':
        url = urllib.parse.urljoin(g.cpars['gtc_offset_server'], 'setup')
        g.clog.debug('Offset Server URL = ' + url)
        opener = urllib.request.build_opener()
        try:
            req = urllib.request.Request(url, data=json_data, headers={'Content-type': 'application/json'})
            response = opener.open(req, timeout=5).read().decode()
        except Exception as err:
            g.clog.warn('Could not communicate with GTC offsetter')
            g.clog.warn(str(err))
            return False

        g.rlog.info('Offset Server Response: ' + response)
        if not json.loads(response)['status'] == 'OK':
            g.clog.warn('Offset Server response was not OK')
            return False

    g.clog.debug('Leaving postJSON')
    return True


def createJSON(g, full=True):
    """
    Create JSON compatible dictionary from current settings

    Parameters
    ----------
    g :  hcam_drivers.globals.Container
    Container with globals
    """
    data = dict()
    if 'gps_attached' not in g.cpars:
        data['gps_attached'] = 1
    else:
        data['gps_attached'] = 1 if g.cpars['gps_attached'] else 0
    data['appdata'] = g.ipars.dumpJSON()
    data['user'] = g.rpars.dumpJSON()
    if full:
        data['hardware'] = g.ccd_hw.dumpJSON()
        data['tcs'] = g.info.dumpJSON()

        if g.cpars['telins_name'].lower() == 'gtc' and has_corba:
            try:
                s = get_telescope_server()
                data['gtc_headers'] = dict(
                    create_header_from_telpars(s.getTelescopeParams())
                )
            except:
                g.clog.warn('cannot get GTC headers from telescope server')
    return data


def jsonFromFits(fname):
    hdr = fits.getheader(fname)

    def full_key(key):
        return 'HIERARCH ESO {}'.format(key)

    def get(name, default=None):
        return hdr.get(full_key(name), default)

    app_data = dict(
        multipliers=[1 + get('DET NSKIPS{}'.format(i+1), 0) for i in range(5)],
        dummy_out=get('DET DUMMY', 0),
        fastclk=get('DET FASTCLK', 0),
        oscan=int(get('DET INCPRSCX', False)),
        oscany=int(get('DET INCOVSCY', False)),
        readout='Slow' if get('DET SPEED', 0) == 0 else 'Fast',
        xbin=get('DET BINX1', 1),
        ybin=get('DET BINY1', 1),
        clear=int(get('DET CLRCCD', True)),
        led_flsh=int(get('DET EXPLED', False)),
        dwell=get('DET TEXPOSE', 0.1)/1000
        # TODO: numexp
    )

    user = dict(
        Observers=hdr.get('OBSERVER', ''),
        target=hdr.get('OBJECT', ''),
        comment=hdr.get('RUNCOM', ''),
        flags=hdr.get('IMAGETYP', 'data'),
        filters=hdr.get('FILTERS', 'us,gs,rs,is,zs'),
        ID=hdr.get('PROGRM', ''),
        PI=hdr.get('PI', '')

    )

    mode = get('DET READ CURID')
    if mode == 2:
        # one window
        app_data['app'] = 'Windows'
        app_data['x1size'] = get('DET WIN1 NX')
        app_data['y1size'] = get('DET WIN1 NY')
        app_data['x1start_lowerleft'] = get('DET WIN1 XSLL')
        app_data['x1start_lowerright'] = get('DET WIN1 XSLR')
        app_data['x1start_upperleft'] = get('DET WIN1 XSUL')
        app_data['x1start_upperright'] = get('DET WIN1 XSUR')
        app_data['y1start'] = get('DET WIN1 YS') + 1
    elif mode == 3:
        # two window
        app_data['app'] = 'Windows'
        app_data['x1size'] = get('DET WIN1 NX')
        app_data['y1size'] = get('DET WIN1 NY')
        app_data['x1start_lowerleft'] = get('DET WIN1 XSLL')
        app_data['x1start_lowerright'] = get('DET WIN1 XSLR')
        app_data['x1start_upperleft'] = get('DET WIN1 XSUL')
        app_data['x1start_upperright'] = get('DET WIN1 XSUR')
        app_data['y1start'] = get('DET WIN1 YS') + 1
        app_data['x2size'] = get('DET WIN2 NX')
        app_data['y2size'] = get('DET WIN2 NY')
        app_data['x2start_lowerleft'] = get('DET WIN2 XSLL')
        app_data['x2start_lowerright'] = get('DET WIN2 XSLR')
        app_data['x2start_upperleft'] = get('DET WIN2 XSUL')
        app_data['x2start_upperright'] = get('DET WIN2 XSUR')
        app_data['y2start'] = get('DET WIN2 YS') + 1
    elif mode == 4:
        # drift mode
        app_data['app'] = 'Drift'
        app_data['x1size'] = get('DET DRWIN NX')
        app_data['y1size'] = get('DET DRWIN NY')
        app_data['x1start_left'] = get('DET DRWIN XSL')
        app_data['x1start_right'] = get('DET DRWIN XSR')
        app_data['y1start'] = 1 + get('DET DRWIN YS')
    else:
        app_data['app'] = 'FullFrame'

    setup_data = dict(
        appdata=app_data,
        user=user
    )
    return json.dumps(setup_data)


def insertFITSHDU(g):
    """
    Uploads a table of TCS data to the servers, which is appended onto a run.

    Arguments
    ---------
    g : hcam_drivers.globals.Container
        the Container object of application globals
    """
    if not g.cpars['hcam_server_on']:
        g.clog.warn('insertFITSHDU: servers are not active')
        return False

    run_number = getRunNumber(g)
    tcs_table = g.info.tcs_table

    g.clog.info('Adding TCS table data to run{:04d}.fits'.format(run_number))
    url = g.cpars['hipercam_server'] + 'addhdu'
    try:
        fd = StringIO()
        ascii.write(tcs_table, format='ecsv', output=fd)
        files = {'file': fd.getvalue()}
        r = requests.post(url, data={'run': 'run{:04d}.fits'.format(run_number)},
                          files=files)
        fd.close()
        rs = ReadServer(r.content, status_msg=False)
        if rs.ok:
            g.clog.info('Response from server was OK')
            return True
        else:
            g.clog.warn('Response from server was not OK')
            g.clog.warn('Reason: ' + rs.err)
            return False
    except Exception as err:
        g.clog.warn('insertFITSHDU failed')
        g.clog.warn(str(err))


def execCommand(g, command, timeout=10):
    """
    Executes a command by sending it to the rack server

    Arguments:
      g : hcam_drivers.globals.Container
        the Container object of application globals
      command : (string)
           the command (see below)

    Possible commands are:

      start   : starts a run
      stop    : stops a run
      abort   : aborts a run
      online  : bring ESO control server online and power up hardware
      off     : put ESO control server in idle state and power down
      standby : server can communicate, but child processes disabled
      reset   : resets the NGC controller front end

    Returns True/False according to whether the command
    succeeded or not.
    """
    if not g.cpars['hcam_server_on']:
        g.clog.warn('execCommand: servers are not active')
        return False

    try:
        url = g.cpars['hipercam_server'] + command
        g.clog.info('execCommand, command = "' + command + '"')
        response = urllib.request.urlopen(url, timeout=timeout)
        rs = ReadServer(response.read(), status_msg=False)

        g.rlog.info('Server response =\n' + rs.resp())
        if rs.ok:
            g.clog.info('Response from server was OK')
            return True
        else:
            g.clog.warn('Response from server was not OK')
            g.clog.warn('Reason: ' + rs.err)
            return False
    except urllib.error.URLError as err:
        g.clog.warn('execCommand failed')
        g.clog.warn(str(err))

    return False


def isRunActive(g):
    """
    Polls the data server to see if a run is active
    """
    if g.cpars['hcam_server_on']:
        url = g.cpars['hipercam_server'] + 'summary'
        response = urllib.request.urlopen(url, timeout=2)
        rs = ReadServer(response.read(), status_msg=True)
        if not rs.ok:
            raise DriverError('isRunActive error: ' + str(rs.err))
        if rs.state == 'idle':
            return False
        elif rs.state == 'active':
            return True
        else:
            raise DriverError('isRunActive error, state = ' + rs.state)
    else:
        raise DriverError('isRunActive error: servers are not active')


def isPoweredOn(g):
    if g.cpars['hcam_server_on']:
        url = g.cpars['hipercam_server'] + 'summary'
        response = urllib.request.urlopen(url, timeout=2)
        rs = ReadServer(response.read(), status_msg=True)
        if not rs.ok:
            raise DriverError('isPoweredOn error: ' + str(rs.err))
        if rs.clocks == 'enabled':
            return True
        else:
            return False
    else:
        raise DriverError('isPoweredOn error: servers are not active')


def isOnline(g):
    # checks if ESO Server is in ONLINE state
    if g.cpars['hcam_server_on']:
        url = g.cpars['hipercam_server'] + 'status'
        try:
            response = urllib.request.urlopen(url, timeout=2)
        except urllib.error.URLError:
            return False
        rs = ReadServer(response.read(), status_msg=False)
        if not rs.ok:
            raise DriverError('isOnline error: ' + str(rs.err))
        if rs.msg.lower() == 'online':
            return True
        else:
            return False
    else:
        raise DriverError('isOnline error: hserver is not active')


def getFrameNumber(g):
    """
    Polls the data server to find the current frame number.

    Throws an exceotion if it cannot determine it.
    """
    if not g.cpars['hcam_server_on']:
        raise DriverError('getRunNumber error: servers are not active')
    url = g.cpars['hipercam_server'] + 'status/DET.FRAM2.NO'
    response = urllib.request.urlopen(url, timeout=2)
    rs = ReadServer(response.read(), status_msg=False)
    try:
        msg = rs.msg
    except:
        raise DriverError('getFrameNumber error: no message found')
    try:
        frame_no = int(msg.split()[1])
    except:
        raise DriverError('getFrameNumber error: invalid msg ' + msg)
    return frame_no


def getRunNumber(g):
    """
    Polls the data server to find the current run number. Throws
    exceptions if it can't determine it.
    """
    if not g.cpars['hcam_server_on']:
        raise DriverError('getRunNumber error: servers are not active')
    url = g.cpars['hipercam_server'] + 'summary'
    response = urllib.request.urlopen(url, timeout=2)
    rs = ReadServer(response.read(), status_msg=True)
    if rs.ok:
        return rs.run
    else:
        raise DriverError('getRunNumber error: ' + str(rs.err))


def checkSimbad(g, target, maxobj=5, timeout=5):
    """
    Sends off a request to Simbad to check whether a target is recognised.
    Returns with a list of results, or raises an exception if it times out
    """
    url = 'http://simbad.u-strasbg.fr/simbad/sim-script'
    q = 'set limit ' + str(maxobj) + \
        '\nformat object form1 "Target: %IDLIST(1) | %COO(A D;ICRS)"\nquery ' \
        + target
    query = urllib.parse.urlencode({'submit': 'submit script', 'script': q})
    resp = urllib.request.urlopen(url, query.encode(), timeout)
    data = False
    error = False
    results = []
    for line in resp:
        line = line.decode()
        if line.startswith('::data::'):
            data = True
        if line.startswith('::error::'):
            error = True
        if data and line.startswith('Target:'):
            name, coords = line[7:].split(' | ')
            results.append(
                {'Name': name.strip(), 'Position': coords.strip(),
                 'Frame': 'ICRS'})
    resp.close()

    if error and len(results):
        g.clog.warn('drivers.check: Simbad: there appear to be some ' +
                    'results but an error was unexpectedly raised.')
    return results


class FifoThread(threading.Thread):
    """
    Adds a fifo Queue to a thread in order to store up disasters which are
    added to the fifo for later retrieval. This is to get around the problem
    that otherwise exceptions thrown from withins threaded operations are
    lost.
    """
    def __init__(self, name, target, fifo, args=()):
        threading.Thread.__init__(self, target=target, args=args)
        self.fifo = fifo
        self.name = name

    def run(self):
        """
        Version of run that traps Exceptions and stores
        them in the fifo
        """
        try:
            threading.Thread.run(self)
        except Exception:
            t, v, tb = sys.exc_info()
            error = traceback.format_exception_only(t, v)[0][:-1]
            tback = (self.name + ' Traceback (most recent call last):\n' +
                     ''.join(traceback.format_tb(tb)))
            self.fifo.put((self.name, error, tback))
