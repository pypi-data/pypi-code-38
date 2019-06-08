"""Isotel IDM Support for Monodaq U Series
   http://isotel.eu/idm/device/monodaq/monodaq-u-x.html
"""

from isotel.idm import gateway, signal, _version
import socket
import struct
import time
import requests
import logging
import argparse
try:
    if get_ipython:
        from IPython.core.display import display, HTML
except:
    pass

class MonoDAQError(Exception):
    def __init__(self, message):
        super().__init__(message)

class MonoDAQ_U(gateway.Device):
    USER_HEADER_LEN = 2
    DIGITAL_MASK = 0x80080000   # digital stream enabled with additional bit in digital only mode
    ANALOG_MASK = 0x47FFFF      # all analog channels present in a stream
    ANUSED_MASK = 0x7FFFF       # used (selected) channels
    PCKTCNT_MASK = 0x3FFF       # counter mask to detect lost packets

    """
    MonoDAQ_U Class adds triggering, streaming data retrieval methods and plots
    """

    def __init__(self, group = None, name = None, exclude = None, accuracy=True, prefix=''):
        """
        :param group: an gateway.Group reference
        :param str name: name of the device returned by the get_device_list(),
                        such as 'device0' root designation or a full name
        """
        super().__init__(group, name, exclude, unit=True, accuracy=accuracy, advanced=True, development=True, hidden=True, brand_filter='MonoDAQ-U')
        self.analog_channels_map = None
        self.digital_channels_map = None
        self.ad_mux_copy = None
        self.analog_socket = None
        self.digital_socket = None
        self.ad_mux = None
        self.channel_muxes = None
        self.units = None
        self.pins = None
        self.ch_gains = None
        self.ain_sa_pckt = None
        self.din_sa_pckt = None
        self.din2ain_rate = None
        self.dt_ain = None
        self.dt_din = None
        self.fetched_Ain = None
        self.fetched_Din = None
        self.pckt_cnt_Ain = 0
        self.pckt_cnt_Din = 0
        self.ain = b''
        self.din = b''
        self.ain_last_T = 0
        self.din_last_T = 0
        self.prefix = prefix.upper()        
        self.settime(False)
        self.logger = logging.getLogger(__name__)

    def reset(self):
        self['daq.trigger.timed'] = 'Off'  # Stop A/D
        self['daq.trigger.N']     = '0'
        if self['ch.config.state'] != 'Cleared':
            self['ch.config.state']   = '~Clear' # Reset channel setup configuration
        self.get('ch', after='now') # Update entire table
    
    def settime(self, finetune=False):
        if self.get_value('id.b1') == 'Uninitialized' or not self.active:
            return None

        t = self.get('clock', after='now')
        t_diff = float(t['time'])*1000 - float(t['clock']['time']['value'])

        # Sync time to UTC, always when not initialized otherwise on request
        if finetune or abs(t_diff) > 321408000000:
            t['clock']['time']['value']  = '~' + str((round(t_diff)))
            t['clock']['uticks']['value']  = '~0'
            t.pop('status')
            t.pop('time')
            self.set('clock', t)

        return -t_diff # [ms]

    def isready(self):
        sys_state = self.get_value('sys.state', after='now')
        return sys_state == 'Ready' or sys_state == 'Uncalibrated'

    def wait4ready(self, mintime=0, timeout=15):
        mintime = timeout - mintime
        while not self.isready() or timeout > mintime:
            time.sleep(0.25)
            timeout -= 0.25
            if timeout <= 0:
                raise MonoDAQError('Device is not ready because it is: ' + self.get_value('sys.state'))

    def wait4value(self, ch_num):
        while not (self['ch.value.value' + str(ch_num)] != '---'):
            pass

    def get_streaming_channels(self):
        return [int(''.join(list(filter(str.isdigit, ch[0])))) for ch in self.get('ch.mux')['mux'].items() if int(ch[1]['value'],16)]

    def is_digital(self, channel):
        return int(self['ch.mux.mux' + str(channel)],16) & self.DIGITAL_MASK

    def get_channel_bypin(self, pin_name):
        return [int(''.join(list(filter(str.isdigit, x[0])))) for x in self.get('ch.pin')['pin'].items() if x[1]['value'] == pin_name][0]
    
    def get_setup(self, HTML=None):
        """
        :returns: html description of the channel setup
        """
        if HTML:
            resp = self.request.get(self.get_url() + '/ch.html', self.group.timeout)
        else:
            resp = self.request.get(self.get_url() + '/ch.txt', self.group.timeout)
            
        return resp

    def set_channel_value(self, pin_name, value, after=None):
        channel = self.get_channel_bypin(pin_name)
        return self.set_value('ch.set.set'+str(channel), value, after=after)

    def get_channel_value(self, pin_name, after=None):
        channel = self.get_channel_bypin(pin_name)
        return self.get_value('ch.set.set'+str(channel), after=after)

    def print_setup(self):
        try:
            get_ipython
            display(HTML(self.get_setup(HTML=True)))
        except:
            print(self.get_setup(HTML=False))

    def stop(self):
        self['daq.trigger.timed'] = 'Off'
        self.ain = b''
        self.din = b''

    def _fetch_init(self, N=0, timed=None):

        def get_gains(ad_mux, ch_muxes, ch_value_config):
            gain = [[]] * bin(ad_mux & self.ANALOG_MASK).count('1')
            for ch_num in range(len(ch_muxes)):
                ch_mux = int(ch_muxes['mux' + str(ch_num)]['value'], 16)
                if ch_mux & self.ANALOG_MASK:
                    ch_idx = bin(ad_mux & int(ch_mux * 2 - 1)).count('1') - 1
                    gain[ch_idx] = 1/float(ch_value_config['value']['value'+str(ch_num)]['args'][-1])
            return gain

        def port_tcp(port):
            return int(self.get_protocols()['LongTransport'][str(port)]['SFrame']
                       ['Stream' + str(port)]['status']['port'])

        # Fetch channel configuration
        self.wait4ready()
        daqconf = self.get('daq')
        self.ad_mux = int(daqconf['daq']['ad']['mux']['value'], 16)
        self.channel_muxes = self.get('ch.mux')['mux']
        self.units = self.get('ch.unit')['unit']
        self.pins  = self.get('ch.pin')['pin']
        self.ch_gains = get_gains(self.ad_mux, self.channel_muxes, self.get('ch.value', args=True))

        # Close possibly open streams if mux has changed
        if self.ad_mux_copy:
            #if self.ad_mux != self.ad_mux_copy:
            if self.analog_socket:
                self.analog_socket.close()
                self.analog_socket = None
            if self.digital_socket:
                self.digital_socket.close()
                self.digital_socket = None

        self.ad_mux_copy = self.ad_mux

        # Open TCP/IP Streams
        # digital input only case
        if (self.ad_mux & self.DIGITAL_MASK) == self.ad_mux:
            if self.analog_socket:
                self.analog_socket.close()
                self.analog_socket = None
        else:
            if self.ad_mux & self.ANALOG_MASK and not self.analog_socket:
                self.analog_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.analog_socket.connect((self.group.get_gatewayname(), port_tcp(1)))
                self.analog_socket.settimeout(0.1)

        if self.ad_mux & self.DIGITAL_MASK and not self.digital_socket:
            self.digital_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.digital_socket.connect((self.group.get_gatewayname(), port_tcp(2)))
            self.digital_socket.settimeout(0.1)

        if self.analog_socket == None and self.digital_socket == None:
            raise MonoDAQError('No streaming channels selected')

        # Metrics used in decoding and validation
        self.ain_sa_pckt = int(daqconf['daq']['ad']['AI']['value']) if self.analog_socket else 0
        self.din_sa_pckt = int(daqconf['daq']['ad']['DI']['value'])
        self.din2ain_rate = int(daqconf['daq']['ad']['DI_AI']['value'])
        self.dt_ain      = 1 / float(daqconf['daq']['ad']['rate']['value'])
        self.dt_din      = self.dt_ain / self.din2ain_rate if self.din2ain_rate > 0 else 0
        self.fetched_Ain = 0
        self.fetched_Din = 0
        self.pckt_cnt_Ain= 0
        self.pckt_cnt_Din= 0
        self.ain_last_T  = 0
        self.din_last_T  = 0
        self.ain = b''
        self.din = b''
        self.set('daq.trigger',
            dict({'trigger': {'timed': {'value': timed if timed else '~Immediate'}, 'N': {'value': N}}}))

    def fetch(self, N=10, timed=None):

        def idm_get_rxcnts(ref):
            stats = self.get_protocols()
            return (stats['LongTransport']['1']['SFrame']['Stream1']['status']['rx'] - ref[0],
                    stats['LongTransport']['2']['SFrame']['Stream2']['status']['rx'] - ref[1])

        # Read data via tcp/ip channels and return when minimum required amount is obtained
        def readdata():
            RETRY_COUNT = 50
            BUF_LEN = 65536*8
            nonlocal ain_recv, din_recv, idm_cnts
            retry = RETRY_COUNT
            while retry > 0:
                try:
                    if ain_recv > ain_len or din_recv > din_len:
                        raise MonoDAQError("Received excess data: analog %d/%d B in buf %d, digital %d/%d B in buf %d" % 
                                           (ain_recv, ain_len, len(self.ain), din_recv, din_len, len(self.din) ))

                    if ((ain_recv >= ain_len and din_recv >= din_len) or
                        (ain_recv >= ain_len and len(self.din) >= din_lenmin) or
                        (din_recv >= din_len and len(self.ain) >= ain_lenmin) or                        
                        (len(self.din) >= din_lenmin and len(self.ain) >= ain_lenmin)):     # Local condition
                        break

                    if self.analog_socket and ain_recv < ain_len:
                        d = self.analog_socket.recv(BUF_LEN)
                        self.ain += d
                        ain_recv += len(d)
                    if self.digital_socket and din_recv < din_len:
                        d = self.digital_socket.recv(BUF_LEN)
                        self.din += d
                        din_recv += len(d)
                    
                    retry = RETRY_COUNT
                except socket.timeout:
                    self.logger.debug("sample_ad: socket.timeout, din { req:%d, len:%d }, ain: { req:%d, len:%d }",
                                      din_len, din_recv, ain_len, ain_recv)
                    retry -= 1
                    if retry == 0:
                        idm_resent = idm_get_rxcnts(idm_cnts)
                        raise MonoDAQError("Did not receive enough data: analog %d/%d B in buf %d, digital %d/%d B in buf %d, idm resent analog: %d B, digital: %d B" % 
                                           (ain_recv, ain_len, len(self.ain), din_recv, din_len, len(self.din), idm_resent[0], idm_resent[1] ))
                    pass

        def decode_analog(samples_ppck, dt, demuxchs, gains, ain, t_offset):
            T = 0
            x = []
            y = [[]]*anused_chs
            if anused_chs == 0:
                return x,y

            packet_size = 2*samples_ppck            
            assert( int(samples_ppck/demuxchs) == float(samples_ppck/demuxchs) )
            for frame in range(self.USER_HEADER_LEN, len(ain), int(packet_size)+self.USER_HEADER_LEN):
                if frame+packet_size <= len(ain):

                    # Detect possible losses on the way
                    if self.pckt_cnt_Ain != (((ain[frame-self.USER_HEADER_LEN+1]<<8) + ain[frame-self.USER_HEADER_LEN]) & self.PCKTCNT_MASK):
                        raise MonoDAQError('Detected lost analog streaming packets')
                    
                    self.pckt_cnt_Ain = (self.pckt_cnt_Ain + 1) & self.PCKTCNT_MASK

                    decoded = struct.unpack(str(samples_ppck) + "h", ain[frame:frame+packet_size])
                    for ch in range(anused_chs):
                        if not y[ch]:
                            y[ch] = []
                            
                        y[ch] += [ int(y*gains[ch]*1000000+0.5)/1000000 for y in decoded[ch::demuxchs] ]
                    x += [int(((t_offset + t*dt)*1000000)+0.5)/1000000 for t in range(T,T+int(samples_ppck/demuxchs))]
                    T += int(samples_ppck/demuxchs)
                else:
                    print("Analog Stream has received inconsistent data", len(ain), 'required', frame+packet_size+self.USER_HEADER_LEN)
            return x,y
            
        def getanalog():
            Ax,Ay = decode_analog(self.ain_sa_pckt, self.dt_ain, ain_chs, self.ch_gains, self.ain[:ain_lenmin], self.fetched_Ain * self.dt_ain)
            self.fetched_Ain += len(Ax)
            self.ain = self.ain[ain_lenmin:]
            return Ax,Ay

        def getanalog_labels(demuxchs, pinname=True):
            labels = [None]*demuxchs
            for ch_num in range(len(self.channel_muxes)):
                ch_mux = int(self.channel_muxes['mux' + str(ch_num)]['value'], 16)
                if ch_mux & self.ANALOG_MASK:
                    ch_idx = bin(self.ad_mux & int(ch_mux * 2 - 1)).count('1') - 1
                    if pinname:
                        labels[ch_idx] = self.prefix + self.pins['pin'+str(ch_num)]['value'] + " [" + self.units['unit'+str(ch_num)]['value'] + "]"
                    else:
                        labels[ch_idx] = "stream" + str(ch_num)
                    
            return labels

        def decode_digital(samples_ppck, dt, din, t_offset, dmux, expand=True):
            T = 0
            x = []
            y = []
            for frame in range(self.USER_HEADER_LEN, len(din), int(samples_ppck)+self.USER_HEADER_LEN):
                if frame+samples_ppck <= len(din):

                    # Detect possible losses on the way
                    if self.pckt_cnt_Din != (((din[frame-self.USER_HEADER_LEN+1]<<8) + din[frame-self.USER_HEADER_LEN]) & self.PCKTCNT_MASK):
                        raise MonoDAQError('Detected lost digital streaming packets')
                    
                    self.pckt_cnt_Din = (self.pckt_cnt_Din + 1) & self.PCKTCNT_MASK

                    decoded = struct.unpack(str(samples_ppck) + "B", din[frame:frame+samples_ppck])
                    if expand:                        
                        for z in decoded:
                            Y = [(z>>v) & 1 for i,v in enumerate(dmux)]
                            y += [tuple(Y)]
                    else:
                        y += decoded

                    x += [int(((t_offset + t*dt)*1000000)+0.5)/1000000 for t in range(T,T+samples_ppck)]
                    T += samples_ppck
                else:
                    self.logger.error("Digital Stream has received inconsistent data len:%d, required:%d"
                                      % (len(din), frame + samples_ppck + self.USER_HEADER_LEN))
            return x,y

        def getdigital(dmux):
            Dx,Dy = decode_digital(self.din_sa_pckt, self.dt_din, self.din[:din_lenmin], self.fetched_Din * self.dt_din, dmux)
            self.fetched_Din += len(Dx)
            self.din = self.din[din_lenmin:]
            return Dx,Dy

        def getdigital_labels(pinname=True):
            labels = []
            dmux   = []
            for ch_num in range(len(self.channel_muxes)):
                if int(self.channel_muxes['mux' + str(ch_num)]['value'], 16) & self.DIGITAL_MASK:
                    assert(ch_num >= 0 and ch_num <= 7)
                    dmux += [ch_num]
                    if pinname:
                        labels += [ self.prefix + self.pins['pin'+str(ch_num)]['value'] + " [" + self.units['unit'+str(ch_num)]['value'] + "]" ]
                    else:
                        labels += [ "din" + str(ch_num) ]
            return labels, dmux

        # Prepare HW for fetch
        self._fetch_init(N, timed)

        # Calculate total number of packets to be expected and minimal lengths to be
        # able to decode a frame
        ain_len   = 0
        ain_pckts = 0
        anused_chs= bin(self.ad_mux & self.ANUSED_MASK).count('1')
        ain_chs   = bin(self.ad_mux & self.ANALOG_MASK).count('1')
        ain_recv  = 0
        ain_lenmin= 0
        if self.ain_sa_pckt > 0:
            ain_pckts = int( (N*ain_chs + self.ain_sa_pckt-1) / self.ain_sa_pckt )
            ain_len   = ain_pckts * (2*self.ain_sa_pckt + self.USER_HEADER_LEN)
            ain_lenmin= 2*self.ain_sa_pckt + self.USER_HEADER_LEN

        din_len   = 0
        din_pckts = 0
        din_recv  = 0
        N_digital = 0
        din_lenmin= 0
        if self.din_sa_pckt:
            N_digital = self.din2ain_rate * N
            din_pckts = int( (N_digital + self.din_sa_pckt-1) / self.din_sa_pckt )
            din_len   = din_pckts * (self.din_sa_pckt + self.USER_HEADER_LEN)
            din_lenmin= self.din_sa_pckt + self.USER_HEADER_LEN

        #print('total requirements:', N, ain_pckts, ain_len, len(self.ain), ':', N_digital, din_pckts, din_len, len(self.din))
        idm_cnts = idm_get_rxcnts( (0,0) )
        dlabels, dmux = getdigital_labels()
        analog_nans  = tuple( [float('nan')]*anused_chs )
        digital_nans = tuple( [float('nan')]*len(dmux) )
        try:
            yield ("t [s]", tuple(getanalog_labels(anused_chs))) , ("t [s]", tuple(dlabels))
            readdata()
            Ax,Ay = getanalog()
            Dx,Dy = getdigital(dmux)
            Axi = iter(Ax)
            Ayi = iter(zip(*Ay))
            Dxi = iter(Dx)
            Dyi = iter(Dy)
            ax = next(Axi, None)
            ay = next(Ayi, None)
            dx = next(Dxi, None)
            dy = next(Dyi, None)
            i  = 0
            while ax != None or dx != None:
                if ax != None and ax == dx:
                    yield (ax,ay),(dx,dy)
                    ax = next(Axi, None)
                    ay = next(Ayi, None)
                    dx = next(Dxi, None)
                    dy = next(Dyi, None)
                    i += 1
                elif dx == None or (ax != None and ax < dx):
                    yield (ax,ay),(None, digital_nans)
                    ax = next(Axi, None)
                    ay = next(Ayi, None)
                    i += 1
                elif ax == None or (dx != None and ax > dx):
                    yield (None, analog_nans),(dx,dy)
                    dx = next(Dxi, None)
                    dy = next(Dyi, None)
                    if Ax == []:
                        i += 1

                if i >= N:
                    break

                if (Ax != None and ax == None) or (Dx != None and dx == None):
                    assert(i < N)
                    readdata()

                if Ax != [] and ax == None:
                    Ax,Ay = getanalog()
                    Axi = iter(Ax)
                    Ayi = iter(zip(*Ay))
                    ax = next(Axi, None)
                    ay = next(Ayi, None)

                if Dx != [] and dx == None:
                    Dx,Dy = getdigital(dmux)
                    Dxi = iter(Dx)
                    Dyi = iter(Dy)
                    dx = next(Dxi, None)
                    dy = next(Dyi, None)

        except KeyboardInterrupt:
            self.stop()

        except (GeneratorExit, MonoDAQError):
            self.stop()
            raise

        self.stop()


class MonoDAQs_U(object):
    def __init__(self, *monodaqs):
        self.group = None
        self.monodaqs = monodaqs
        # TODO 1-wire config and auto config prefixes

    def fetch(self, N):
        for d in self.monodaqs:
            d.wait4ready()

        # TODO detect false starts
        t_start = float(self.monodaqs[0].get('clock', after='now')['clock']['time']['value']) + 2000 # ms
        streams = [[]]*len(self.monodaqs)
        for i,d in enumerate(self.monodaqs):
            streams[i] = d.fetch(N, t_start)
        return signal.mergeNsync( *streams )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='MonoDAQ-U-X Utility %s' % (_version.__version__))

    parser.add_argument("--gateway", help="gateway address, defaults to http://localhost:33000", required=False,
                        default='http://localhost:33000')
    parser.add_argument("--user", help="user name", required=False, default=None)
    parser.add_argument("--pass", dest='password', help="password", required=False, default=None)
    parser.add_argument("-d",
                        help="Device to fetch from, like: 'MonoDAQ-U-X v1.55.0.17 0x4' or just: device0",
                        required=False)
    parser.add_argument("-N", help="Fetch N samples and print results in TSV format", 
                        required=False, type=int)
    parser.add_argument("--from", dest='start', help="Fetch samples from records, given by time in UTC, or bounded in interval --to", required=False, default=None)
    parser.add_argument("--to", dest='end', help="Fetch samples from records until time in UTC, or bounded in interval --from", required=False, default='last')
    parser.add_argument("--scale", help="Down-sample samples from records to given number", required=False, default=None)
    parser.add_argument("-s", help="Set or query a parameter, like: ch.function.function0 'Digital Input'", required=False, nargs='+')

    args = parser.parse_args()

    try:
        gw = gateway.Group(gateway=args.gateway, username=args.user, password=args.password)
    except:
        print('Cannot connect to a gateway %s, use --gateway http://yourgw:33000 [--user USERNAME] [--pass PASSWORD]' % ( args.gateway ) )
        exit(-1)
    
    if args.d:
        mdu = MonoDAQ_U(gw, name = args.d)
        if args.start or args.end:
            if args.s:
                records = mdu.get_records(args.s[0], time_from=args.start, time_to=args.end, limit=args.N, scale=args.scale)
                for item in records:
                    try:
                        print(item['time'], end='\t')
                        if item['value']:
                            for k,v in item['value'].items():
                                try:
                                    print(v['value'], end='\t')
                                except:
                                    pass
                    except:
                        print(item['time'], end='\t')
                        for k,v in item.items():
                            try:
                                print(v['value'], end='\t')
                            except:
                                pass                                
                    print('')
            else:
                print('Specify a parameter to dump')
        elif args.s:
            if len(args.s) == 2:
                mdu[args.s[0]] = args.s[1]
            if len(args.s) >= 1:
                print(mdu.get_value(args.s[0], after='now'))
        elif args.N:
            for line in signal.to_tsv( mdu.fetch(args.N) ):
                print(line)
        else:
            mdu.print_setup()
    else:
        for d in gw.get_device_list(brand_filter='MonoDAQ-U'):
            print(d['root'], '\t', d['name'])


