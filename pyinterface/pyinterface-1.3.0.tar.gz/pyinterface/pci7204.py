
import struct
import time
from . import core


class InvalidChannelError(Exception):
    pass


class pci7204_driver(core.interface_driver):
    bit_flags_in = (
        (
            ('TD1', 'TD2', 'TD3', 'TD4', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', 'SIGT', 'SIGR', '', ''),
            ('', '', '', '', 'SIGT', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('ILOCK', '', '', '', '', '', '', ''),
            ('D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7'),
            ('BID0', 'BID1', 'BID2', 'BID3', '', '', '', ''),
        ),
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('Mode0', 'Mode1', '', '', '', '', '', ''),
            ('SYNC', '', '', '', '', '', '', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('Mode0', 'Mode1', '', '', '', '', '', ''),
            ('RFLG', '', '', '', '', '', '', ''),
        ),
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('Mode0', 'Mode1', '', '', '', '', '', ''),
            ('SYNC', '', '', '', '', '', '', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('Mode0', 'Mode1', '', '', '', '', '', ''),
            ('RFLG', '', '', '', '', '', '', ''),
        )
    )
     
    bit_flags_out = (
        (
            ('TCTL1', 'TCTL2', 'TCTL3', 'TCTL4', 'SCK1', 'SCK2', 'SCK3', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', 'SIGT', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
        ),
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('Mode0', 'Mode1', '', '', '', '', '', ''),
            ('SYNC', '', '', '', '', '', '', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('Mode0', 'Mode1', '', '', '', '', '', ''),
            ('RST', '', '', '', '', '', '', ''),
        ),
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('Mode0', 'Mode1', '', '', '', '', '', ''),
            ('SYNC', '', '', '', '', '', '', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('+SD', '-SD', '+EL', '-EL', '', 'ORG', 'ALM', ''),
            ('Mode0', 'Mode1', '', '', '', '', '', ''),
            ('RST', '', '', '', '', '', '', ''),
        )
    )
    

    soft_inter_lock = [True, True]
    base_clock = ['CLOCK_1_16M', 'CLOCK_1_16M']
    motion_config = [{'JOG': {}, 'PTP': {}},
                     {'JOG': {}, 'PTP': {}}]
    
    
    def get_board_id(self):
        bar = 0
        offset = 0x07
        size = 1
        
        ret = self.read(bar, offset, size)
        bid = ret.to_hex()[1]
        return bid
    
    
    def initialize(self, axis=1):
        self._verify_axis_num(axis)
        
        self.stop_motion(axis)
        self.set_base_clock(axis=axis)
        self.ppmc_init(axis=axis)
        self.set_pulse_out(None, 'CW/CCW N', axis=axis)
        self.set_limit_config('MASK', config='', axis=axis)
        self.set_limit_config('LOGIC', config='', axis=axis)
        self.write_counter(0, axis=axis)
        self.output_do([0,0,0,0], axis=axis)
        self.motion_config[axis-1] = {'JOG': {}, 'PTP': {}}
        return
    
    
    def _verify_axis_num(self, axis):
        if axis not in [1, 2]:
            raise InvalidAxisError('axis must be 1 or 2, not {0}'.format(ch))
        return
    
    
    def ppmc_read_data(self, axis=1, timeout=0.5):
        self._verify_axis_num(axis)
        bar = axis
        offset = 0x00
        size = 1
        
        t0 = time.time()
        while (time.time() - t0) < timeout:
            if self.ppmc_is_readable(axis):
                break
            time.sleep(0.0005)
            continue
        else:
            raise Exception('PPMC data register is busy')

        d = self.read(bar, offset, size)
        return d

    def ppmc_read_status(self, axis=1):
        self._verify_axis_num(axis)
        bar = axis
        offset = 0x01
        size = 1
        
        d = self.read(bar, offset, size)
        d.set_flag([['OBF', 'IBF', 'BUSY', '', 'INTS', 'INTE', 'IST', 'ERR']])
        return d
        
    def ppmc_write_data(self, data, axis=1, timeout=0.5):
        self._verify_axis_num(axis)
        bar = axis
        offset = 0x00
        
        if isinstance(data, int):
            data = data.to_bytes(1, 'little')
            pass
        
        t0 = time.time()
        while (time.time() - t0) < timeout:
            if self.ppmc_is_writable(axis):
                break
            time.sleep(0.0005)
            continue
        else:
            raise Exception('PPMC data register is busy')
        
        self.write(bar, offset, data)
        return
        
    def ppmc_write_command(self, data, axis=1, timeout=1):
        self._verify_axis_num(axis)
        bar = axis
        offset = 0x01
        
        if isinstance(data, int):
            data = data.to_bytes(1, 'little')
            pass
        
        t0 = time.time()
        while (time.time() - t0) < timeout:
            status = self.ppmc_read_status(axis)
            if (not status['IBF']) & (not status['IST']):
                break
            time.sleep(0.0005)
            continue
        else:
            raise Exception('PPMC command register is busy')
        
        self.write(bar, offset, data)
        return
        
    def ppmc_is_readable(self, axis):
        status = self.ppmc_read_status(axis)
        return bool(status['OBF'])

    def ppmc_is_writable(self, axis):
        status = self.ppmc_read_status(axis)
        return not status['IBF']
        
    def ppmc_is_command_ready(self, axis):
        status = self.ppmc_read_status(axis)
        return not status['IST']
        
    def ppmc_is_busy(self, axis):
        status = self.ppmc_read_status(axis)
        return bool(status['BUSY'])
        
    def ppmc_get_stop_status(self, axis=1):
        cmd = 0b01000000
        
        self.ppmc_write_command(cmd, axis)
        ret = self.ppmc_read_data(axis)
        ret.set_flag([['FNS', 'CMD', 'ORG', '-SD', '+SD', '-EL', '+EL', 'ALM']])
        return ret
    
    def ppmc_get_error(self, axis=1):
        cmd = 0b01000001
        
        self.ppmc_write_command(cmd, axis)
        ret = self.ppmc_read_data(axis)
        return ret
        
    def ppmc_get_counter(self, axis=1):
        cmd = 0b01000010
        
        self.ppmc_write_command(cmd, axis)
        ret = b''
        ret += self.ppmc_read_data(axis).bytes
        ret += self.ppmc_read_data(axis).bytes
        ret += self.ppmc_read_data(axis).bytes
        iret = int.from_bytes(ret, 'little')
        return iret
        
    def ppmc_set_counter(self, count, axis=1):
        cmd = 0b01000011
        
        self.ppmc_write_command(cmd, axis)
        
        ct = struct.pack('<I', count)
        self.ppmc_write_data(ct[0], axis)
        self.ppmc_write_data(ct[1], axis)
        self.ppmc_write_data(ct[2], axis)
        return
        
    def ppmc_get_limit_status(self, axis=1):
        cmd = 0b01000110
        
        self.ppmc_write_command(cmd, axis)
        ret = self.ppmc_read_data(axis)
        ret.set_flag([['+SD', '+EL', '-SD', '-EL', 'ORG', 'ALM', 'RUN', '']])
        return ret        
    
    def ppmc_get_aux_in(self, axis=1):
        cmd = 0b01000100
        
        self.ppmc_write_command(cmd, axis)
        ret = self.ppmc_read_data(axis)
        return ret
        
    def ppmc_set_aux_out(self, data, axis=1):
        cmd = 0b01000101
        
        self.ppmc_write_command(cmd, axis)
        self.ppmc_write_data(data, axis)
        return
        
    def ppmc_get_input_status(self, axis=1):
        cmd = 0b01000110
        
        self.ppmc_write_command(cmd, axis)
        ret = self.ppmc_read_data(axis)
        return ret
        
    def ppmc_init(self, clock='1/16 MHz', method='linear', 
                  rate_low=0x7fff, rate_high=0x7ffe, acc_pulse=8,
                  axis=1):
        cmd = 0b00000000
        
        rate_low = int(rate_low)
        rate_high = int(rate_high)
        acc_pulse = int(acc_pulse)
        
        if clock in ['1 MHz', 'CLOCK_1M']:
            cl = 0b00000000
        elif clock in ['1/4 MHz', 'CLOCK_1_4M']:
            cl = 0b00010000
        elif clock in ['1/16 MHz', 'CLOCK_1_16M']:
            cl = 0b00100000
        else:
            msg = "clock must be '1 MHz', '1/4 MHz' or '1/16 MHz'"
            msg += ', not {0}'.format(clock)
            raise TypeError(msg)
        
        if method in ['linear', 'NORMAL']:
            me = 0b00000000
        elif method in ['s-shaped', 'SIN']:
            me = 0b00000001
        elif method == 'free':
            me = 0b00000010
        else:
            msg = "method must be 'linear', 's-shaped' or 'free'",
            msg += ', not {0}'.format(method)
            raise TypeError(msg)
        
        if not (0x0010 <= rate_low <= 0x7fff):
            msg = 'rate_low must be in 0x0010-0x7fff'
            msg += ', not {0}'.format(hex(rate_low))
            raise TypeError(msg)
        
        if not (0x000f <= rate_high <= 0x7ffe):
            msg = 'rate_low must be in 0x000f-0x7ffe'
            msg += ', not {0}'.format(hex(rate_high))
            raise TypeError(msg)
        
        if acc_pulse < 8:
            msg = 'acc_pulse must be >=8'
            msg += ', not {0}'.format(acc_pulse)
            raise TypeError(msg)
        
        
        cmd |= cl | me
        self.ppmc_write_command(cmd, axis)
        
        rl = struct.pack('<H', rate_low)
        rh = struct.pack('<H', rate_high)
        pa = struct.pack('<H', acc_pulse)
        self.ppmc_write_data(rl[0], axis)
        self.ppmc_write_data(rl[1], axis)
        self.ppmc_write_data(rh[0], axis)
        self.ppmc_write_data(rh[1], axis)
        self.ppmc_write_data(pa[0], axis)
        self.ppmc_write_data(pa[1], axis)
        return
        
    def ppmc_stop(self, axis=1):
        cmd = 0b10000000
        
        if self.ppmc_is_busy(axis):
            self.ppmc_write_command(cmd, axis)
            return
            
        return
        
    def ppmc_stop_smooth(self, axis=1):
        cmd = 0b10000001
        
        if self.ppmc_is_busy(axis):
            self.ppmc_write_command(cmd, axis)
            return
        
        return
    
    def ppmc_move_single_step(self, direction='cw', axis=1):
        cmd = 0b10000010
        
        if direction == 'cw':
            dir_ = 0b00000000
        elif direction == 'ccw':
            dir_ = 0b00100000
        else:
            msg = "direction must be 'cw' or 'ccw'",
            msg += ', not {0}'.format(direction)
            raise TypeError(msg)
            
        cmd |= dir_
        
        if not self.ppmc_is_busy(axis):
            self.ppmc_write_command(cmd, axis)
            pass
            
        return
        
    def ppmc_move(self, direction='cw', move_pulse=10, axis=1):
        cmd = 0b10000011
        
        if direction == 'cw':
            dir_ = 0b00000000
        elif direction == 'ccw':
            dir_ = 0b00100000
        else:
            msg = "direction must be 'cw' or 'ccw'",
            msg += ', not {0}'.format(direction)
            raise TypeError(msg)
        
        cmd |= dir_
        self.ppmc_write_command(cmd, axis)
                
        pulse = struct.pack('<I', move_pulse)
        self.ppmc_write_data(pulse[0], axis)
        self.ppmc_write_data(pulse[1], axis)
        self.ppmc_write_data(pulse[2], axis)
        return
        
    def ppmc_cont_move(self, pulse_rate, direction='cw', axis=1):
        cmd = 0b10000101
        
        pulse_rate = int(pulse_rate)
        
        if direction == 'cw':
            dir_ = 0b00000000
        elif direction == 'ccw':
            dir_ = 0b00100000
        else:
            msg = "direction must be 'cw' or 'ccw'",
            msg += ', not {0}'.format(direction)
            raise TypeError(msg)
        
        cmd |= dir_
        self.ppmc_write_command(cmd, axis)
        
        pl = struct.pack('<H', pulse_rate)
        self.ppmc_write_data(pl[0], axis)
        self.ppmc_write_data(pl[1], axis)
        return
        
    def ppmc_set_speed(self, pulse_rate, axis=1):
        cmd = 0b10001001
        
        pulse_rate = int(pulse_rate)
        
        if not (0x000f <= pulse_rate <= 0x7ffe):
            msg = 'pulse_rate must be in 0x000f-0x7ffe'
            msg += ', not {0}'.format(hex(pulse_rate))
            raise TypeError(msg)
        
        self.ppmc_write_command(cmd, axis)
        
        pa = struct.pack('<H', pulse_rate)
        self.ppmc_write_data(pa[0], axis)
        self.ppmc_write_data(pa[1], axis)
        return
        
        
    def get_inter_lock(self):
        bar = 0
        offset = 0x05
        size = 1
        
        d = self.read(bar, offset, size)
        return d
        
    
    def set_base_clock(self, base_clock='CLOCK_1_16M', axis=1):
        """
        CLOCK_1M : 1 MHz
        CLOCK_1_4M : 1/4 MHz
        CLOCK_1_16M : 1/16 MHz (default)
        """
        self._verify_axis_num(axis)
        
        if base_clock not in ['CLOCK_1M', 'CLOCK_1_4M', 'CLOCK_1_16M']:
            msg = "base_clock must be 'CLOCK_1M', 'CLOCK_1_4M' or 'CLOCK_1_16M'"
            msg += ', not {0}'.format(base_clock)
            raise Exception(msg)
        
        self.base_clock[axis-1] = base_clock
        return
        

    def get_base_clock(self, axis=1):
        self._verify_axis_num(axis)
        return self.base_clock[axis-1]
    
        
    def get_base_clock_hz(self, axis=1):
        self._verify_axis_num(axis)
        bclock = self.get_base_clock(axis)
        if bclock == 'CLOCK_1M': return 1e6
        elif bclock == 'CLOCK_1_4M': return (1/4)*1e6
        elif bclock == 'CLOCK_1_16M': return (1/16)*1e6
        return 0


    def set_pulse_out(self, mode, config, axis=1):
        pulse, logic = config.split(' ')
        return self._set_pulse_out(pulse, logic, axis)
    
    def _set_pulse_out(self, pulse='CW/CCW', logic='N', axis=1):
        """
        pulse : 
            'CW/CCW' or 'OUT/DIR'
        LOGIC : 
            'N' : negative logic (default)
            'P' : positive logic
        """
        self._verify_axis_num(axis)
        bar = axis
        offset = 0x0a
        
        flags = ''
        if pulse == 'OUT/DIR':
            flags +=' Mode0'
            
        if logic == 'P':
            flags += ' Mode1'
            
        self.set_flag(bar, offset, flags)
        return
    
    
    def get_pulse_out(self, mode, axis=1):
        self._verify_axis_num(axis)
        bar = axis
        offset = 0x0a
        size = 1
        
        d = self.read(bar, offset, size)
        return d

    
    def set_motion(self, mode='JOG', acc_mode='SIN', low_speed=100,
                   speed=1000, acc=500, step=1000, axis=1):        
        self._verify_axis_num(axis)
        
        if mode not in ['JOG', 'PTP']:
            msg = "mode must be 'JOG' or 'PTP'"
            msg += ', not {0}'.format(mode)
            raise TypeError(msg)
        
        if acc_mode not in ['NORMAL', 'SIN']:
            msg = "acc_mode must be 'NORMAL' or 'SIN'"
            msg += ', not {0}'.format(mode)
            raise TypeError(msg)
        
        bclock = self.get_base_clock_hz(axis)
        min_speed_limit = bclock / 32767.
        max_speed_limit = bclock / 15.
        
        if not (min_speed_limit <= low_speed <= max_speed_limit):
            msg = 'low_speed must be in {0:.2f}-{1.2f} pps'.format(min_speed_limit,
                                                            max_speed_limit)
            msg += ' (clock={0})'.format(self.get_base_clock(axis))
            msg += ', not {0} pps'.format(low_speed)
            raise TypeError(msg)
            
        if not (min_speed_limit <= speed <= max_speed_limit):
            msg = 'speed must be in {0:.2f}-{1:.2f} pps'.format(min_speed_limit,
                                                                max_speed_limit)
            msg += ' (clock={0})'.format(self.get_base_clock(axis))
            msg += ', not {0} pps'.format(speed)
            raise TypeError(msg)
        
        mconf = {'acc_mode': acc_mode,
                 'low_speed': low_speed,
                 'speed': speed,
                 'acc': acc,
                 'step': step}

        self.motion_config[axis-1][mode] = mconf
        return
    
        
    def get_motion(self, mode='JOG', axis=1):
        self._verify_axis_num(axis)
        
        if mode not in ['JOG', 'PTP']:
            msg = "mode must be 'JOG' or 'PTP'"
            msg += ', not {0}'.format(mode)
            raise TypeError(msg)
        
        return self.motion_config[axis-1][mode]
    
    
    def start_motion(self, mode='JOG', axis=1):
        self._verify_axis_num(axis)
        
        if mode not in ['JOG', 'PTP']:
            msg = "mode must be 'JOG' or 'PTP'"
            msg += ', not {0}'.format(mode)
            raise TypeError(msg)
        
        conf = self.motion_config[axis-1][mode]
        if conf == {}:
            msg = 'motion parameters are not set'
            msg += ' for axis={0}, mode={1}.'.format(axis, mode)
            msg += ' set motion parameters before start_motion().'
            raise TypeError(msg)
            
        if mode == 'JOG':
            self._start_jog_motion(axis)
            
        elif mode == 'PTP':
            self._start_ptp_motion(axis)
            
        return
        
    def _start_jog_motion(self, axis):
        bclock = self.get_base_clock(axis)
        bclock_hz = self.get_base_clock_hz(axis)
        conf = self.get_motion('JOG', axis)
        
        method = conf['acc_mode']
        rate_low = 32767
        rate_high = 15
        pulse_rate = bclock_hz / conf['speed']
        acc_pulse = conf['acc']
        
        if conf['step'] > 0:
            direction = 'cw'
        else:
            direction = 'ccw'
        
        self.ppmc_init(bclock, method, rate_low, rate_high, acc_pulse, axis)
        self.ppmc_cont_move(pulse_rate, direction, axis)
        return
        
    def _start_ptp_motion(self, axis):
        bclock = self.get_base_clock(axis)
        bclock_hz = self.get_base_clock_hz(axis)
        conf = self.get_motion('PTP', axis)
        
        method = conf['acc_mode']
        rate_low = bclock_hz / conf['low_speed']
        rate_high = bclock_hz / conf['speed']
        acc_pulse = conf['acc']
        
        if conf['step'] > 0:
            direction = 'cw'
        else:
            direction = 'ccw'
            pass
            
        move_pulse = abs(conf['step'])
        
        self.ppmc_init(bclock, method, rate_low, rate_high, acc_pulse, axis)
        self.ppmc_move(direction, move_pulse, axis)
        return
        
    
    def single_step(self, direction='CW', axis=1):
        self._verify_axis_num(axis)

        if type(direction) in [int, float]:
            if direction > 0: direction = 'CW'
            elif direction < 0: direction = 'CCW'
            msg = "direction must be +1 or -1"
            msg += ', not {0}'.format(direction)
            raise TypeError(msg)
        
        if direction not in ['CW', 'CCW']:
            msg = "direction must be 'cw' or 'ccw'"
            msg += ', not {0}'.format(direction)
            raise TypeError(msg)
            
        self.ppmc_move_single_step(direction, axis)
        return
     
        
    def stop_motion(self, mode='IMMEDIATE', axis=1):
        self._verify_axis_num(axis)
        
        if mode == 'DEC':
            self.ppmc_stop_smooth(axis)
            
        else:
            self.ppmc_stop(axis)
            pass
        
        return
        
    
    def change_speed(self, speed, mode, axis=1):
        self._verify_axis_num(axis)
        
        bclock = self.get_base_clock_hz(axis)
        min_speed_limit = bclock / 32767.
        max_speed_limit = bclock / 15.
        
        if not (min_speed_limit <= speed <= max_speed_limit):
            msg = 'speed must be in {0:.2f}-{1:.2f} pps'.format(min_speed_limit,
                                                                max_speed_limit)
            msg += ' (clock={0})'.format(self.get_base_clock(axis))
            msg += ', not {0} pps'.format(speed)
            raise TypeError(msg)
        
        pulse_rate = bclock / speed
        self.ppmc_set_speed(pulse_rate, axis)
        return
        
    
    def get_status(self, mode, axis=1):
        self._verify_axis_num(axis)

        if mode in ['BUSY', 'ALL']:
            status = self.ppmc_read_status(axis)
            busy = status['BUSY']
        else:
            busy = None
            pass
        
        if mode in ['INTERLOCK', 'ALL']:
            ilock = self.get_inter_lock()
        else:
            ilock = None
            pass
        
        if mode in ['ERROR', 'ALL']:
            error = self.ppmc_get_error(axis)
        else:
            error = None
            pass
        
        #count = self.get_counter(axis)
        count = None
        
        if mode in ['FINISH', 'ALL']:
            fstatus = self.ppmc_get_stop_status(axis)
        else:
            fstatus = None
            pass
            
        if mode in ['LIMIT', 'ALL']:
            lstatus = self.ppmc_get_limit_status(axis)
        else:
            lstatus = None
            pass
            
        status = {'ppmc_status': status,
                  'busy': busy,
                  'interlock': ilock,
                  'finish': fstatus,
                  'limit': lstatus,
                  'error': error,
                  'count': count,}
        return status

    
    def read_counter(self, axis=1):
        self._verify_axis_num(axis)
        
        count = self.ppmc_get_counter(axis)
        return count
    
        
    def write_counter(self, count, axis=1):
        self._verify_axis_num(axis)
        
        self.ppmc_set_counter(count, axis)
        return

    
    def clear_counter(self, axis=1):
        self.write_counter(0, axis)
        return
    
    
    def get_limit_config(self, mode='MASK', axis=1):
        self._verify_axis_num(axis)
        
        if mode not in ['MASK', 'LOGIC']:
            msg = "mode must be 'MASK' or 'LOGIC'"
            msg += ', not {0}'.format(mode)
            raise TypeError(msg)
        
        bar = axis
        size = 1
        
        if mode == 'MASK':
            offset = 0x09
        elif mode == 'LOGIC':
            offset = 0x08
            pass
        
        d = self.read(bar, offset, size)
        return d
    
    
    def set_limit_config(self, mode='MASK', config='+SD -SD +EL -EL ORG ALM', 
                         axis=1):
        self._verify_axis_num(axis)
        
        if mode not in ['MASK', 'LOGIC']:
            msg = "mode must be 'MASK' or 'LOGIC'"
            msg += ', not {0}'.format(mode)
            raise TypeError(msg)
        
        bar = axis
        size = 1
        
        if mode == 'MASK':
            offset = 0x09
        elif mode == 'LOGIC':
            offset = 0x08
            pass
        
        d = self.set_flag(bar, offset, config)
        return d
    
    
    def output_do(self, outp, axis=1):
        self._verify_axis_num(axis)
        
        if len(outp) != 4:
            msg = 'outp must be list with length 4'
            TypeError(msg)
            
        outp += [0, 0, 0, 0]
        outp = core.list2bytes(outp)
        self.ppmc_set_aux_out(outp, axis)
        return
        
        
    def input_di(self, axis=1):
        self._verify_axis_num(axis)
        
        inp = self.ppmc_get_aux_in(axis)
        return inp.to_list()[:4]
            
