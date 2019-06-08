"""Energy Control Modules Add-ons
"""

from __future__ import print_function
from isotel.idm import gateway
import sys
import time
import argparse
import textwrap
from enum import IntFlag, IntEnum, unique

def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class ECL(gateway.Device):

    def __init__(self, group = None, name = None, exclude = None):
        super().__init__(group, name, exclude, unit=True, accuracy=False, advanced=True, development=True, hidden=True, brand_filter='ECL-')

    def set_time(self):
        return None

    def set_maxcurrents(self, I1, I2, I3):
        return None


class EC(gateway.Device):
    EC_LOG_BUF_LEN = 992
    HEADER_MASK = 0xF0
    HEADER_DATA_MASK = 15
    LOG_ID_ENERGY = 0x10
    LOG_ID_FAULT = 0x20
    LOG_ID_TIME_CHANGE = 0x30
    LOG_ID_SUBMETERING = 0x40
    LOG_ID_TRACKING = 0x50
    LOG_ID_ENERGY1 = 0x70
    LOG_REASON_SYSTEM_POWER_UP = 1
    LOG_REASON_WDT_RESET_OCCUR = 2
    LOG_REASON_TIME_CHANGE = 4

    @unique
    class ChannelStatus(IntEnum):
        OFF = 0
        ANTISMOG = 1
        ON = 2
        SHEDDED = 3
        LIMITED = 4
        CURRENT_FAULT = 5
        WAITING_PRIORITY = 6
        VOLTAGE_FAULT = 7
        UNDERVOLTAGE_FAULT = 8
        OVERVOLTAGE_FAULT = 9
        OVERUSE_FAULT   = 10

    @unique
    class CommonOpts(IntFlag):
        DETECT_CAPLOAD  = 0x02  # Enable capacitive load in load detection, as with anti-smog
        BOOST_25A       = 0x04  # Enable 25 A mode, only valid in single channel mode operation
        COMMON_OP       = 0x08  # Treat both A and B channels in a single channel mode
        AUTOLEARN       = 0x10  # Calculate average energy consumption
        CURRENT_FAULT   = 0x20  # Current Fault Enable, by default on
        FAST_OFF_EN	    = 0x40  # Enable short-circuit tripping, by default on
        SLOW_OFF        = 0x80  # Set slow reaction time on overloading, by default off

    @unique
    class ChannelOpts(IntFlag):
        OPTS_UNDER_V_FAULT	= 0x01  # Enable under voltage faults
        OPTS_ELIMIT_OVERRIDE= 0x02
        OPTS_ELIMIT_ENABLE	= 0x04
        OPTS_ASMOG_ENABLE	= 0x08  # Enable Anti-Smog
        OPTS_SINGLE_OP		= 0x10	
        OPTS_ELIMIT_CUT_OFF	= 0x20  # Enable Excessive Energy consumption Fault
        OPTS_GEN_ELIMIT_EN	= 0x40
        OPTS_EXT_INPUT		= 0x80  # Enable External Gate Input

    def __init__(self, group = None, name = None, exclude = None):
        super().__init__(group, name, exclude, unit=True, accuracy=False, advanced=True, development=True, hidden=True, brand_filter='EC-')

    def geta_status(self):
        return self.ChannelStatus(int(self.get_value('ec.ChA', after='now')))

    def getb_status(self):
        return self.ChannelStatus(int(self.get_value('ec.ChB', after='now')))

    def get_status(self):
        return [self.geta_status(), self.getb_status()]

    def seta(self, turn_on=True):
        return self.ChannelStatus(int(self.set_value('ec.ChA', int(self.ChannelStatus.ON) if turn_on else int(self.ChannelStatus.OFF))))

    def reseta(self):
        self.seta(False)
        return self.seta(True)

    def setb(self, turn_on=True):
        return self.ChannelStatus(int(self.set_value('ec.ChB', int(self.ChannelStatus.ON) if turn_on else int(self.ChannelStatus.OFF))))

    def resetb(self):
        self.setb(False)
        return self.setb(True)

    def get_opt(self):
        return self.CommonOpts( int( self.get_value('ec.optAB', after='now')))

    def set_opt(self, opts):
        assert(type(opts) == self.CommonOpts)
        return self.CommonOpts(int( self.set_value('ec.optAB', int(self.get_opt() | opts))))

    def clr_opt(self, opts):
        assert(type(opts) == self.CommonOpts)
        return self.CommonOpts(int( self.set_value('ec.optAB', int(self.get_opt() & ~opts))))

    def geta_opt(self):
        return self.ChannelOpts( int( self.get_value('ec.optA', after='now')))

    def seta_opt(self, opts):
        assert(type(opts) == self.ChannelOpts)
        return self.ChannelOpts( int( self.set_value('ec.optA', int(self.geta_opt() | opts))))

    def clra_opt(self, opts):
        assert(type(opts) == self.ChannelOpts)
        return self.ChannelOpts(int( self.set_value('ec.optA', int(self.geta_opt() & ~opts))))

    def getb_opt(self):
        return self.ChannelOpts( int( self.get_value('ec.optB', after='now')))

    def setb_opt(self, opts):
        assert(type(opts) == self.ChannelOpts)
        return self.ChannelOpts(int( self.set_value('ec.optB', int(self.getb_opt() | opts))))

    def clrb_opt(self, opts):
        assert(type(opts) == self.ChannelOpts)
        return self.ChannelOpts(int( self.set_value('ec.optB', int(self.getb_opt() & ~opts))))

    def fetch_logs(self, log_range=[1, 10]):

        def decode_logs(logs):
            # find first log with full timestamp, if all is ok it should be the first one
            for log_idx in range(len(logs)):
                header = int(logs[log_idx][4:6], 16)
                if ((header & self.HEADER_MASK) == self.LOG_ID_TIME_CHANGE):
                    break

            if (log_idx != 0):
                _eprint('Timestamp missing, ', log_idx, ' logs discarded.')

            abstime = int(logs[log_idx][12:20], 16)
            time.ctime(abstime)
            start_idx = log_idx

            logs_data = []
            for log_idx in range(start_idx, len(logs), 1):
                header = int(logs[log_idx][4:6], 16) & self.HEADER_MASK

                if ((header == self.LOG_ID_ENERGY) or (header == self.LOG_ID_SUBMETERING) or (header == self.LOG_ID_ENERGY1)):
                    # Energy Log
                    t = int(logs[log_idx][6:10], 16)
                    t_msb = (t & 32768) / 32768
                    t = t * 2
                    t = t & 0xFFFF

                    tlast = abstime & 0xFFFF
                    tlast_msb = (abstime & 65536) / 65536

                    cas = (abstime & 0xFFFF0000)
                    cas = cas + t

                    if (t >= tlast):
                        if (t_msb != tlast_msb):
                            cas = cas + 65536
                    else:
                        if (t_msb != tlast_msb):
                            cas = cas + 65536
                        else:
                            cas = cas + 131072

                    abstime = cas
                    energy = int(logs[log_idx][10:16], 16) * 18e-5
                    tariff = int(logs[log_idx][4:6], 16) & self.HEADER_DATA_MASK
                    energyA = int(logs[log_idx][16:18], 16) / 255 * energy
                    energyB = int(logs[log_idx][18:20], 16) / 255 * energy
                    if (header == self.LOG_ID_ENERGY):
                        notes = 'ECL_SYNC'
                    elif (header == self.LOG_ID_SUBMETERING):
                        notes = 'SUBMETERING'
                    elif (header == self.LOG_ID_ENERGY1):
                        notes = 'TARIFF'
                    else:
                        notes = ''

                    data = dict()
                    data['time'] = abstime
                    data['type'] = 'ENERGY'
                    data['energy'] = energy
                    data['energyA'] = energyA
                    data['energyB'] = energyB
                    data['tariff'] = tariff
                    data['notes'] = notes
                    logs_data.append(data)
                    # print(time.ctime(abstime), '\t', energy, '\t', tariff, '\t ENERGY')

                elif (header == self.LOG_ID_TIME_CHANGE):
                    abstime = int(logs[log_idx][12:20], 16)
                    dT = int(logs[log_idx][6:12], 16)
                    reason = int(logs[log_idx][4:6], 16) & self.HEADER_DATA_MASK
                    if (reason == self.LOG_REASON_SYSTEM_POWER_UP):
                        reason = 'POWER_UP'
                    elif (reason == self.LOG_REASON_WDT_RESET_OCCUR):
                        reason = 'WDT_RESET'
                    elif (reason == self.LOG_REASON_TIME_CHANGE):
                        reason = 'TIME_CHANGE'
                        if (dT == 0):
                            reason = 'WEAK_TIMESTAMP'

                    tariff = int(logs[log_idx][4:6], 16) & self.HEADER_DATA_MASK

                    data = dict()
                    data['time'] = abstime
                    data['type'] = 'TIMECHANGE'
                    data['notes'] = reason
                    data['tariff'] = tariff
                    data['dt'] = dT
                    logs_data.append(data)
                    # print(time.ctime(abstime), '\t', dT, '\t', reason, '\t TIMECHANGE')

                elif (header == self.LOG_ID_FAULT):
                    abstime = int(logs[log_idx][6:14], 16)
                    loadA = int(logs[log_idx][14:16], 16)
                    loadB = int(logs[log_idx][16:18], 16)
                    fault = int(logs[log_idx][18:20], 16)
                    tariff = int(logs[log_idx][4:6], 16) & self.HEADER_DATA_MASK

                    data = dict()
                    data['time'] = abstime
                    data['type'] = 'FAULT'
                    data['tariff'] = tariff
                    data['loadA'] = loadA
                    data['loadB'] = loadB
                    data['fault'] = fault
                    logs_data.append(data)
                    # print(time.ctime(abstime), '\t', loadA, '\t', loadB, '\t', fault, '\t FAULT')

            return logs_data

        logs = []
        search_back_max_idx = max(log_range) + 100
        if (search_back_max_idx > self.EC_LOG_BUF_LEN):
            search_back_max_idx = self.EC_LOG_BUF_LEN

        search_idx = max(log_range)
        logs_buf = []
        timestamp_found = False

        # search for the first available log with complete timestamp
        _eprint("Preparing to fetch logs ...")
        while (search_idx < search_back_max_idx):
            self.set_value('ec.i', search_idx)
            system_args = self.get_args(15)['args']
            logs_buf.append(system_args)

            header = int(system_args[4:6], 16)
            if ((header & self.HEADER_MASK) == self.LOG_ID_TIME_CHANGE):
                timestamp_found = True
                break

            search_idx = search_idx + 1

        if (timestamp_found == False):
            raise ValueError('Log with Timestamp not found!')

            # copy already downloaded logs into buffer, do not download them again
        for i in range(len(logs_buf), 0, -1):
            logs.append(logs_buf[i - 1])

        min_idx = min(log_range) - 1
        if (min_idx < 0):
            min_idx = 0

        for log_idx in range(max(log_range) - 1, min_idx, -1):
            try:
                _eprint("Fetching:", log_idx, " ", end="\r")
                self.set_value('ec.i', log_idx)
                system_args = self.get_args(15)['args']
                logs.append(system_args)
            except:
                _eprint('Error: Stopped due to communication error at log', log_idx)
                return logs

        _eprint("Completed successfully.")
        return decode_logs(logs)

    @staticmethod
    def display_logs(logs_data, log_type='ENERGY'):
        if (log_type == 'ENERGY'):
            print('Time', '\t', 'Log Type', '\t', 'Energy [kWh]', '\t', 'EnergyA [kWh]', '\t', 'EnergyB [kWh]', '\t',
                'Tariff', '\t',
                'Notes')

        for i in range(len(logs_data)):
            if (logs_data[i]['type'] == 'ENERGY' and log_type == 'ENERGY'):
                print(time.ctime(logs_data[i]['time']), '\t', logs_data[i]['type'], '\t',
                    format(logs_data[i]['energy'], '.4f'),
                    '\t', format(logs_data[i]['energyA'], '.4f'), '\t', format(logs_data[i]['energyB'], '.4f'), '\t',
                    logs_data[i]['tariff'], '\t', logs_data[i]['notes'])

            if (logs_data[i]['type'] == 'TIMECHANGE' and log_type == 'TIMECHANGE'):
                print(time.ctime(logs_data[i]['time']), '\t', logs_data[i]['type'], '\t', logs_data[i]['tariff'],
                    '\t', logs_data[i]['dt'], '\t', logs_data[i]['notes'])

            if (logs_data[i]['type'] == 'FAULT' and log_type == 'FAULT'):
                print(time.ctime(logs_data[i]['time']), '\t', logs_data[i]['type'], '\t', logs_data[i]['tariff'],
                    '\t', logs_data[i]['loadA'], '\t', logs_data[i]['loadB'], '\t', logs_data[i]['fault'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Energy Control Modules Utility
            ----------------------------------------------------------------------
            Provide the device name of which module's you wish to fetch
            logs with -d option or leave blank to show available EC modules.
           '''))
    parser.add_argument("--gateway", help="gateway address, defaults to http://localhost:33000", required=False,
                        default='http://localhost:33000')
    parser.add_argument("--username", help="gateway username", required=False)    
    parser.add_argument("--password", help="gateway password", required=False)    
    parser.add_argument("-d",
                        help="Device to dump log data, like: 'EC-D16-20AHR-L2A-1.2.0-1901-1 50678419 (00043E29B4CD)'",
                        required=False, default=None)
    parser.add_argument("-N", help="Number of logs to dump, default is 20 and max is 992", required=False, type=int,
                        default=20)
    parser.add_argument("-t", help="Type of log, defaults to ENERGY", required=False, default='ENERGY',
                        choices=['ENERGY', 'FAULT', 'TIMECHANGE'])
    args = parser.parse_args()

    gw = gateway.Group(gateway=args.gateway, username=args.username, password=args.password)
    last_log = args.N
    if last_log > EC.EC_LOG_BUF_LEN:
        last_log = EC.EC_LOG_BUF_LEN
        _eprint("EC may contains up to", EC.EC_LOG_BUF_LEN, "logs.")

    if args.d:
        ec = EC(gw, args.d)
        logs = ec.fetch_logs([1, last_log])
        EC.display_logs(logs, args.t)
    else:
        for x in gw.get_device_list():
            if 'EC-' in x['name']:
                _eprint(x['root'], x['name'], EC(gw, x['name']).get_status() )
