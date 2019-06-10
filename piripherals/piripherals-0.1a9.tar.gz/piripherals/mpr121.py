"""a sane and complete interface to the MPR121 touch sensor

This is thought to be a replacement of the incomplete and undocumented
Adafruit.MPR121_ library.

.. note::

    To fully understand this device, please read the datasheet_.


Wiring the MPR121 to the RaspberryPi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect the pins of the MPR121 to the RaspberryPi according to the following table.
In this doc and in the code, all Pi pin numbers are BCM_ pin numbers, physical
pin numbers are set in round braces.

========= ============
MPR121    RaspberryPi
========= ============
3.3V      3.3V (1)
GND       GND (6)
SDA       BCM 2 (3)
SCL       BCM 3 (5)
IRQ*      BCM 4 (7)
========= ============

Connecting the IRQ line is optional but highly recommended to avoid unneccessary bus
traffic and CPU load due to polling. To be able to use the IRQ, you need to have
RPi.GPIO_ installed (``apt-get install python-rpi.gpio`` or ``pip install RPi.GPIO``).
You may use a different pin, adjust the number accordingly.

If you want to connect multiple MPR121s to the same bus, you can change their
address with the address pin. Refer to the datasheet_ on how to do this.

Enable I2C access
~~~~~~~~~~~~~~~~~

The MPR121 uses I2C for communication. On the RaspberryPi running
Raspbian_ Stretch, you need to enable the I2C bus. To ``/boot/config.txt``
add the lines::

    dtparam=i2c_arm=on
    dtparam=i2c1=on

and to ``/etc/modules`` add::

    i2c-dev

This should enable the ``/dev/i2c-1`` (bus=1) device on boot. Install i2c-tools with::

    apt-get install i2c-tools

and list the addresses of connected devices::

    i2cdetect -y 1

For MPR121 being able to access the I2C bus, you need to have a Python smbus
implementation installed. Use ``python-smbus`` from the distro or smbus2_
(``apt-get install python-smbus`` or ``pip install smbus2``). Other implementations
may work, too.

Using MPR121
~~~~~~~~~~~~

Attach the MPR121 to the Pi as described above and use it like::

    from piripherals import MPR121

    # MPR121 should come up and be running with 12 channels
    mpr = MPR121(irq=4)
    for i in range(12): # print status on touch and release
        mpr.on_touch(i, lambda *x: print(x))

Simply instanciante it and assign touch handlers. For fine tuning and to userthe
GPIO functionality, see the doc below.

.. tip::

    Use the ``mpr121-dump`` script to examine the MPR121's response and to tune
    the settings.

.. _datasheet: https://www.sparkfun.com/datasheets/Components/MPR121.pdf
.. _BCM: https://pinout.xyz/
.. _Raspbian: https://www.raspberrypi.org/downloads/raspbian/
.. _RPi.GPIO: https://pypi.python.org/pypi/RPi.GPIO
.. _smbus2: https://pypi.python.org/pypi/smbus2
.. _Adafruit.MPR121: https://github.com/adafruit/Adafruit_Python_MPR121
"""

__all__ = ['MPR121']

from .util import *

NCH = 13  # number of channels
# REGISTERS
ETS = 0x00  # touch status
OOR = 0x02  # out of range status
EFD = 0x04  # electrode filtered data
EBL = 0x1e  # baseline value
MHD = 0x2b  # MHD rising
MHDX = 0x36  # MHD rising proximity
TTH = 0x41  # touch threshold 0
RTH = 0x42  # release threshold 0
DEB = 0x5b  # debounce
AFE1 = 0x5c  # parameters 1
AFE2 = 0x5d  # parameters 2
ECR = 0x5e  # electrode control register
CDC = 0x5f  # electrode current
CDT = 0x6c  # charge time
GPIO_CTL0 = 0x73  # GPIO control 0
GPIO_CTL1 = 0x74  # GPIO control 1
GPIO_DAT = 0x75  # GPIO data
GPIO_DIR = 0x76  # GPIO direction
GPIO_EN = 0x77  # GPIO enable
GPIO_SET = 0x78  # GPIO set data
GPIO_CLR = 0x79  # GPIO clear data
GPIO_TOG = 0x7a  # GPIO toggle data
ACNF_C0 = 0x7b  # auto config control 0
ACNF_C1 = 0x7c  # auto config control 1
ACNF_USL = 0x7d  # auto config
ACNF_LSL = 0x7e  # auto config
ACNF_TL = 0x7f  # auto config target level
SRESET = 0x80  # soft reset


class MPR121:
    """MPR121 capacitive touch sensor and GPIO/LED controller.

    It will be configured with sane defaults and started immediately.

    Args:
        bus (int): I2C bus, 1 = /dev/i2c-1
        addr (int): I2C address of the device
        irq (int): BCM_ pin # that is connect to interrupt line,
            0 disables IRQ, uses polling instead
        handlers (bool): enable IRQ handler/polling, if disabled ``update_touch_state()``
            has to be called explicitly
        setup (bool): configure with (sane) defaults
        reset (bool): reset on initialization
        **kwargs: arguments to setup()
    """

    def __init__(self,
                 bus=1,
                 addr=0x5a,
                 irq=0,
                 handlers=1,
                 setup=1,
                 reset=1,
                 **kwargs):
        from .bus import Bus
        self.addr = addr
        self.overcurrent = False
        if not hasattr(bus, 'device'):
            bus = Bus(bus)
        self._bus = bus.device(addr)
        self._handlers = [noop] * NCH
        self._touched = 0

        if handlers:
            if irq:
                IRQHandler(irq, self.update_touch_state)
            else:
                Poller(self.update_touch_state)

        if setup:
            self.setup(reset=reset, **kwargs)
        elif reset:
            self.reset()

    def update_touch_state(self):
        """Update touch state, calls touched()"""
        t0 = self._touched
        t1 = self._touched = self.touched()
        ch = t0 ^ t1
        if ch:
            self._handle_touch(t1, ch)

    def _handle_touch(self, touched, changed):
        """Invokes touch handlers if touch status changed.

        Args:
            touched (int): byte containing touch status bits
                bit is 1 if channel is touched
            changed (int): byte containing status change bits
                bit is 1 if touch status has changed
        """

        for i in range(NCH):
            m = 1 << i
            if changed & m:
                try:
                    self._handlers[i]((touched & m) > 0, i)
                except TypeError:
                    self._handlers[i]((touched & m) > 0)

    def is_touched(self, channel):
        """Get touch status.

        Args:
            channel (int): channel to get status for, 0-12

        Returns:
            bool: True if touched
        """
        return (self._touched & (1 << channel)) > 0

    def on_touch(self, channel, handler):
        """Register touch handler, invoked on state change.

        Args:
            channel (int): channel to attach the handler to (0-12, 12=proximity)
            handler (callable(boolean, [channel])): handler,
                it gets passed a channel number [optional] and a boolean (True=touched),
                Pass None to remove any assigned handler.
        """
        self._handlers[channel] = not_raising(handler) or noop

    def reset(self):
        """Perform soft reset."""
        self._bus.write_byte(SRESET, 0x63)

    def configure(self, cl=3, prox=0, touch=12):
        """activate/deactivate measurement.

        Measurement is activated when setting prox>0 or touch>0 (run mode).
        Deactivate measurement with prox=0 and touch=0 (stop mode).

        Args:
            cl (int): calibration lock:
                0 = baseline tracking enabled,
                1 = baseline tracking disabled,
                2 = baseline tracking enabled, init 5MSBs with initial measurement,
                3 = baseline tracking enabled, init with initial measurement.
            prox (int): proximity detection:
                0 = disabled,
                1 = enabled on electrodes 0-1,
                2 = enabled on electrodes 0-3,
                3 = enabled on electrodes 0-11.
            touch (int): enable electrodes:
                0 = disabled,
                1 = enable electrode 0,
                2 = enable electrodes 0-1,
                3 = enable electrodes 0-2,
                ...,
                12 = enable electrodes 0-11.
        """
        self._bus.write_byte(ECR, (cl << 6) | (prox << 4) | touch)

    def touched(self, raise_on_failure=1):
        """Get touch status bits to the device.

        Returns:
            int: first 12 bits contain touch status, 1=touched

        Args:
            raise_on_failure (bool): raise if failure bits are set

        Raises:
            Exception: on overcurrent and out of range
        """
        word = self._bus.read_word(ETS)
        if raise_on_failure:
            overcurrent = (word & (1 << 15)) > 0
            if overcurrent:
                raise Exception('overcurrent')
            if self.out_of_range():
                raise Exception('out of range')
        return word & 0x1fff

    def electrode_data(self):
        """Get raw eletrode measurement data.

        Returns:
            list of int: raw 10 bit eletrode measurement per eletrode
        """
        bytes = self._bus.read_block(EFD, 2 * NCH)
        data = []
        for i in range(NCH):
            data.append((bytes[2 * i + 1] << 8) + bytes[2 * i])
        return data

    def baseline(self, rft=-1, mhd=0, nhd=0, ncl=0, fdl=0, prox=0):
        """Get raw baslines or configure baseline tracking.

        Args:
            rft (int): scenario to set the values for:
                0 = rising, raw eletrode data > current baseline,
                1 = falling, raw eletrode data < current baseline,
                2 = touched, eletrode in touch status.
            mhd (int): max. half delta 0-63 (for rft=0 or 1 only),
                largest magnitude of variation to pass through the baseline filter.
            nhd (int): noise half delta 0-63,
                incremental change when non-noise drift is detected.
            ncl (int): noise count limit 0-255,
                number of samples consecutively greater than mhd necessary
                before if can be determined that it is non-noise.
            fdl (int): filter delay count limit 0-255,
                rate of operation of the filer, greater values makes it operate slower.
            prox (bool): if True set values for proximity mode.

        Returns:
            list of ints: raw 10 bit baseline values per eletrode, if invoked with no args.
        """
        if rft < 0:
            return [b << 2 for b in self._bus.read_block(EBL, NCH)]
        else:
            reg = (MHDX if prox else MHD) + 4 * rft
            if rft > 1:
                self._bus.write_block(reg, [nhd, ncl, fdl])
            else:
                self._bus.write_block(reg, [mhd, nhd, ncl, fdl])

    def threshold(self, touch, release=-1, channel=-1):
        """Set touch and release thresholds.

        Usually touch > release for hysteresis.

        Args:
            touch (int): touch threshold 0-255
            release (int): release threshold 0-255
                if ommited release=0.6*touch
            channel (int): channel to set thresholds for 0-12 (12=proximity)
                if ommited apply thresholds to all channels
        """
        if release < 0:
            release = int(0.6 * touch)
        if channel < 0:
            for i in range(NCH):
                self.threshold(touch, release, i)
        else:
            self._bus.write_byte(TTH + 2 * channel, touch)
            self._bus.write_byte(RTH + 2 * channel, release)

    def debounce(self, touch=0, release=-1):
        """Configure debouncing.

        # of consecutiv measurements with same result needed to trigger state change.

        Args:
            touch (int): for touch 0-7
            release (int): for release 0-7, if ommited release=touch
        """
        if release < 0:
            release = touch
        self._bus.write_byte(DEB, (release << 4) | touch)

    def filter(self, cdc=16, cdt=1, ffi=0, sfi=0, esi=4):
        """Settings for global eletrode charging, sampling and filtering.

        Effective measurement cycle period is sfi*esi.

        Args:
            cdc (int): charge-discharge-current 0-63 (uA)
            cdt (int): charge-discharge-time 0-7 (0.5*2**(cdt-1) us)
            ffi (int): first filter iterations 0-3 (6,10,18,34)
            sfi (int): second filter iterations 0-3 (4,6,10,18)
            esi (int): eletrode sample interval 0-7 (2**esi ms)
        """
        lb = (ffi << 6) | cdc
        hb = (cdt << 5) | (sfi << 3) | esi
        self._bus.write_word(AFE1, (hb << 8) | lb)

    def charge(self, channel, cdc=0, cdt=0):
        """Configure change current and time per channel.

        These values are determined automatically when ``auto_config()`` is activated.

        Args:
            channel (int): channel to configure 0-11
            cdc (int): charge-discharge-current 0-63 (uA)
            cdt (int): charge-discharge-time 0-7 (0.5*2**(cdt-1) us)
        """
        self._bus.write_byte(CDC + channel, cdc)
        reg = CDT + channel // 2
        s = 4 * (channel % 2)
        self._bus.write_byte(
            reg, (self._bus.read_byte(reg) & ~(0xf << s)) | (cdt << s))

    def auto_config(self,
                    ace=1,
                    are=1,
                    bva=3,
                    retry=2,
                    afes=1,
                    scts=0,
                    acfie=1,
                    arfie=1,
                    oorie=1,
                    usl=200,
                    lsl=130,
                    tl=180):
        """Configure automatic adjustment eletrode change current and time.

        Args:
            ace (bool): enable auto configuration
            are (bool): enable auto reconfiguration
            bva (int): baseline adjustment after current and time have been set:
                0 = no change,
                1 = set to zero,
                2 = set 5MSBs to measured value,
                3 = set to measured value.
            retry (int): # of retries for auto configuration: 0-3 (0,2,4,8)
            afes (int): # of AFE sample during search process, set to values
                as filter(ffi): 0-3 (6,10,18,34)
            scts (bool): skip charge time search
            acfie (bool): enable IRQ on auto config failure
            arfie (bool): enable IRQ on auto reconfig failure
            oorie (bool): enable IRQ on out of range event
        """
        lb = (afes << 6) | (retry << 4) | (bva << 2) | (are << 1) | (ace)
        hb = (scts << 7) | (oorie << 2) | (arfie << 1) | (acfie)
        self._bus.write_word(ACNF_C0, (hb << 8) + lb)
        self._bus.write_byte(ACNF_USL, usl)
        self._bus.write_byte(ACNF_LSL, lsl)
        self._bus.write_byte(ACNF_TL, tl)

    def out_of_range(self, raise_on_failure=1):
        """get out of range status.

        Returns:
            int: first 12 bits contain oor status.

        Args:
            raise_on_failure (bool): raise if failure bits are set

        Raises:
            Exception: if auto (re)config has failed
        """
        word = self._bus.read_word(OOR)
        if raise_on_failure:
            auto_config_failed = (word & (1 << 15)) > 0
            if auto_config_failed:
                raise Exception('auto config failed')
            auto_reconfig_failed = (word & (1 << 14)) > 0
            if auto_reconfig_failed:
                raise Exception('auto reconfig failed')
        return word & 0x1fff

    def gpio_setup(self, channel, output, mode=0, enable=1):
        """Setup GPIO configuration.

        If the channel is configured as touch eletrode with ``configure()``, then
        this GPIO setting has not effect. Sensing eletrode have precedence.

        Args:
            channel (int): channel to configure (4-11)
            output (bool): configure as 1=output or 0=input
            mode (int): pin mode, when output:
                0 = CMOS output,
                2 = open drain output, low side MOS only,
                3 = open drain output, high side MOS only,
                when input:
                0 = input,
                2 = input with pull-down,
                3 = input with pull-up.
            enable (bool): enable/disbale GPIO functionality
        """
        assert 4 <= channel <= 11
        if mode == 1:
            mode = 0
        channel -= 4

        def set_bit(addr, bit, value):
            print('0x{:02x}={:08b}'.format(addr, (
                self._bus.read_byte(addr) & ~(1 << bit)) |
                ((1 if value else 0) << bit)))
            self._bus.write_byte(addr,
                                 (self._bus.read_byte(addr) & ~(1 << bit)) |
                                 ((1 if value else 0) << bit))

        set_bit(GPIO_CTL0, channel, mode & 0b10)
        set_bit(GPIO_CTL1, channel, mode & 0b01)
        set_bit(GPIO_DIR, channel, output & 0b1)
        set_bit(GPIO_EN, channel, enable & 0b1)

    def gpio_status(self):
        """Get GPIO status bits.

        Returns:
            GPIO status byte for channels 4-11
        """
        return self._bus.read_byte(GPIO_DAT)

    def gpio_set(self, channel, value):
        """Set GPIO channel.

        Args:
            channel (int): channel to set 4-11
            value (bool): set 1=HIGH or 0=LOW
        """
        assert 4 <= channel <= 11
        self._bus.write_byte(GPIO_SET
                             if value else GPIO_CLR, 1 << (channel - 4))

    def dump(self, regs=1, up=1, loop=1):
        """Dump raw values, baseline and touch status to console.

        Uses this repeatedly to adjust the configuration.

        Args:
            regs (bool): dump register values
            up (bool): move cursor up after dump
            loop (int): run in loop for given # of rounds
        """
        import sys

        tth, rth = [], []
        for i in range(NCH):
            tth.append(self._bus.read_byte(TTH + 2 * i))
            rth.append(self._bus.read_byte(RTH + 2 * i))

        for q in range(loop):
            cols = 4
            fs = '{}0x{:02x} = 0x{:02x} b{:08b} {:3d}\033[0m    ' * cols
            if up and q:
                sys.stdout.write('\033[F' * ((regs * 32) + NCH + 1))
            if regs:
                data = []
                for i in range(cols):
                    data += self._bus.read_block(32 * i, 32)
                for j in range(32):
                    x = []
                    for i in range(cols):
                        k = j + 32 * i
                        c = '\033[33m' if data[k] else ''
                        x += (c, k, data[k], data[k], data[k])
                    print(fs.format(*x))

            print(' E:  raw base diff (touched) [GPIO]' + ' ' * 73 +
                  '  cdc     cdt oor')
            n = 80
            ts = self.touched(raise_on_failure=0)
            oo = self.out_of_range(raise_on_failure=0)
            gp = self.gpio_status()
            ed = self.electrode_data()
            bl = self.baseline()
            for i in range(NCH):
                e = int(n * ed[i] / 0x3ff)
                b = int(n * bl[i] / 0x3ff)
                bar = ['='] * e + ['-'] * (n - e)
                bar[b] = '\033[0m|\033[34m'
                nt = max(0, int(n * ((bl[i] - tth[i]) / 0x3ff)))
                nr = max(0, int(n * ((bl[i] - rth[i]) / 0x3ff)))
                bar[nt] = '\033[33m' + bar[nt]
                bar[nr] = '\033[32m' + bar[nr]
                t = '1' if (ts & (1 << i)) else '0'
                g = '-' if i < 4 or i > 11 else '1' if (gp &
                                                        (1 <<
                                                         (i - 4))) > 0 else '0'
                cdc = self._bus.read_byte(CDC + i)
                s = 4 * (i % 2)
                cdt = (self._bus.read_byte(CDT + i // 2) >> s) & 0x0f
                o = '1' if (oo & (1 << i)) else '0'
                print(
                    '{:2d}: {:4d} {:4d} {:4d} ({}) [{}] \033[31m{}\033[0m {:3d}uA {:5.1f}us  {}   '.
                    format(i, ed[i], bl[i], ed[i] - bl[i], t, g, ''.join(bar),
                           cdc, (0.5 * 2**(cdt - 1)), o))

    def setup(self,
              reset=1,
              channels=12,
              prox=0,
              threshold=50,
              debounce=2,
              auto_config=1):
        """Configure the device with sane defaults.

        Args:
            reset (bool): perform soft reset
            channels (int): number of channels to activate 0-12
            threshold (int): touch threshold 0-255
            debounce (int): debounce count 0-7
            auto_config (bool): enable charge auto config
        """
        if reset:
            self.reset()
        self.configure(prox=0, touch=0)
        self.filter(cdc=30, cdt=1, ffi=1, sfi=1, esi=0)
        if auto_config:
            self.auto_config()
        self.threshold(touch=threshold)
        self.threshold(channel=12, touch=threshold >> 2)
        self.debounce(debounce)
        for i in range(2):
            self.baseline(rft=i, mhd=5, nhd=1, ncl=3, fdl=20)
            self.baseline(rft=i, mhd=1, nhd=1, ncl=3, fdl=20, prox=1)
        self.configure(prox=prox, touch=channels)


if __name__ == '__main__':
    main()


def main():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(
        description='MPR121 register and status dump',
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-a', '--address', type=int, default=0x5a, help='device address')
    parser.add_argument(
        '-p', '--prox', type=int, default=0, help='enable proximity')
    parser.add_argument(
        '-T', '--threshold', type=int, default=50, help='touch threshold')
    parser.add_argument(
        '-c', '--channels', type=int, default=12, help='# of channels')
    parser.add_argument(
        '-q',
        '--irq',
        type=int,
        default=0,
        help='BCM# of IRQ pin 0=use polling')
    parser.add_argument('-b', '--bus', type=int, default=1, help='I2C bus')
    parser.add_argument(
        '-r', '--regs', action='store_true', help='dump registers')
    parser.add_argument(
        '-t',
        '--touch',
        action='store_true',
        help='no dump, log touche events')
    parser.add_argument(
        '-A',
        '--no-auto',
        action='store_false',
        help='disable charge auto config')
    parser.add_argument(
        '-R', '--no-reset', action='store_false', help='no initial reset')
    parser.add_argument(
        '-S', '--no-setup', action='store_false', help='no initial setup')
    parser.add_argument(
        '-B', '--scan-bus', action='store_true', help='scan bus for devices')
    args = parser.parse_args()

    from time import sleep
    from functools import partial

    if args.scan_bus:
        from .bus import Bus
        bus = Bus(args.bus)
        print('used addresses')
        for a in range(256):
            try:
                bus.read_byte(a, 0)
                print('0x{:02x} '.format(a))
            except:
                pass
        exit()

    m = MPR121(
        bus=args.bus,
        addr=args.address,
        irq=args.irq,
        handlers=args.touch,
        setup=args.no_setup,
        reset=args.no_reset,
        auto_config=args.no_auto,
        channels=args.channels,
        prox=args.prox,
        threshold=args.threshold)

    if args.touch:
        print('touch events')
        for i in range(NCH):
            m.on_touch(i, lambda s, c: print(c, s))
    else:
        fork(partial(m.dump, regs=args.regs, loop=1000000))
    on_change(__file__, exit, forking=0)
