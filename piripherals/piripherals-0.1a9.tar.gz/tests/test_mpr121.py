"""Testing the MPR121

Testing a hardware device is hard. This test aims to test the MPR121 class, not
the actual hardware. It will test, whether the MPR121 class reads and writes
the right bits to the right registers.

A test with the actual hardware MPR121 can only happen interactively on the Pi
with the MPR121 connected.
"""

import pytest
from unittest.mock import Mock, patch, ANY
from time import sleep
from piripherals import MPR121, Bus

HARDWARE = 0
ADDR = 0x5a
RESET_CODE = 0 if HARDWARE else 0x63


@pytest.fixture
def bus():
    if HARDWARE:
        from smbus import SMBus
        b = SMBus(1)
        # wrap in mock to record calls
        m = b = Mock(wraps=b)
    else:  # use a mock i2c bus
        m = b = Mock(spec=['read_byte_data', 'write_byte_data'])
        reg = [0] * 129  # registers of the MPR121
        reg[0x5c] = 0x10  # defauts according to datasheet
        reg[0x5d] = 0x24

    if not HARDWARE:
        def read(a, r): return reg[r]
        m.read_byte_data.side_effect = read

        def write(a, r, b): reg[r] = b & 0xff
        m.write_byte_data.side_effect = write

    b = Bus(b)
    yield b
    # print(m.mock_calls)
    if not HARDWARE:
        for i in range(len(reg)):
            if reg[i]:
                print('0x{0:02x} = 0x{1:02x} {1:08b}'.format(i, reg[i]))


def assert_reg(dev, non_zero_regs, only_non_zero=0):
    for i in range(129):
        v = non_zero_regs.get(i)
        if only_non_zero and v is None:
            continue
        v = v if v else 0
        w = dev[i]
        assert w == v, '0x{0:02x} = 0x{1:02x} {1:08b}'.format(i, w)


def test_mpr121_init_default(bus):
    # turn all initialization off, but reset --> MPR121 in default state
    mpr = MPR121(bus=bus, handlers=0, setup=0)

    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24, 0x80: RESET_CODE})


def test_mpr121_configure(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    mpr.configure()
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24,
                     0x80: RESET_CODE, 0x5e: 0xcc}, only_non_zero=HARDWARE)


def test_mpr121_filter(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    mpr.filter(cdc=33, cdt=5, ffi=2, sfi=1, esi=1)
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0xa1, 0x5d: 0xa9, 0x80: RESET_CODE})


def test_mpr121_charge(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    for i in range(13):
        mpr.charge(i, i + 1, (i + 1) % 7)
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24, 0x80: RESET_CODE,
                     0x5f: 1,
                     0x60: 2,
                     0x61: 3,
                     0x62: 4,
                     0x63: 5,
                     0x64: 6,
                     0x65: 7,
                     0x66: 8,
                     0x67: 9,
                     0x68: 10,
                     0x69: 11,
                     0x6a: 12,
                     0x6b: 13,
                     0x6c: 2 << 4 | 1,
                     0x6d: 4 << 4 | 3,
                     0x6e: 6 << 4 | 5,
                     0x6f: 1 << 4 | 0,
                     0x70: 3 << 4 | 2,
                     0x71: 5 << 4 | 4,
                     0x72: 6,
                     })


def test_mpr121_auto_config(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    mpr.auto_config(ace=1, are=1, bva=3, retry=2, afes=1, scts=0,
                    acfie=1, arfie=1, oorie=1, usl=200, lsl=130, tl=180)
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24, 0x80: RESET_CODE,
                     0x7b: (1 << 6) | (2 << 4) | (3 << 2) | 1 << 1 | 1,
                     0x7c: (0 << 7) | (1 << 2) | (1 << 1) | 1,
                     0x7d: 200,
                     0x7e: 130,
                     0x7f: 180,
                     })


def test_mpr121_electrode_data(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    mpr.filter(cdc=30, cdt=1, ffi=1, sfi=1, esi=0)
    mpr.configure(prox=1)
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x5e, 0x5d: 0x28, 0x5e: 0xdc, 0x80: RESET_CODE},
               only_non_zero=HARDWARE)
    for i in range(13):
        dev.write_byte(0x04 + 2 * i, 3 * i)
        dev.write_byte(0x05 + 2 * i, i % 3)
    ed = mpr.electrode_data()
    if HARDWARE:
        assert all([v > 0 for v in ed])
    else:
        assert ed == [0, 259, 518, 9, 268, 527, 18, 277, 536, 27, 286, 545, 36]


def test_mpr121_get_baseline(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24, 0x80: RESET_CODE})
    for i in range(13):
        dev.write_byte(0x1e + i, i)
    bl = mpr.baseline()
    assert bl == [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48]


def test_mpr121_set_baseline(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    for r in range(3):
        for p in (0, 1):
            x = ((r << 1) | p) << 3
            mpr.baseline(rft=r, mhd=x + 1, nhd=x + 2,
                         ncl=x + 3, fdl=x + 4, prox=p)
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24, 0x80: RESET_CODE,
                     0x2b: 0x01,  # MHD # rising
                     0x2c: 0x02,  # NHD
                     0x2d: 0x03,  # NCL
                     0x2e: 0x04,  # FDL
                     0x2f: 0x11,  # falling
                     0x30: 0x12,
                     0x31: 0x13,
                     0x32: 0x14,
                     0x33: 0x22,  # touched
                     0x34: 0x23,
                     0x35: 0x24,
                     0x36: 0x09,  # prox rising
                     0x37: 0x0a,
                     0x38: 0x0b,
                     0x39: 0x0c,
                     0x3a: 0x19,  # prox falling
                     0x3b: 0x1a,
                     0x3c: 0x1b,
                     0x3d: 0x1c,
                     0x3e: 0x2a,  # prox touched
                     0x3f: 0x2b,
                     0x40: 0x2c,
                     })


def test_mpr121_set_threshold(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    mpr.threshold(touch=111)
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24, 0x80: RESET_CODE,
                     0x41: 111,
                     0x42: 66,
                     0x43: 111,
                     0x44: 66,
                     0x45: 111,
                     0x46: 66,
                     0x47: 111,
                     0x48: 66,
                     0x49: 111,
                     0x4a: 66,
                     0x4b: 111,
                     0x4c: 66,
                     0x4d: 111,
                     0x4e: 66,
                     0x4f: 111,
                     0x50: 66,
                     0x51: 111,
                     0x52: 66,
                     0x53: 111,
                     0x54: 66,
                     0x55: 111,
                     0x56: 66,
                     0x57: 111,
                     0x58: 66,
                     0x59: 111,
                     ADDR: 66,
                     })


def test_mpr121_set_threshold2(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    for i in range(13):
        mpr.threshold(channel=i, touch=7 * (i + 1), release=6 * (i + 1))
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24, 0x80: RESET_CODE,
                     0x41: 1 * 7,
                     0x42: 1 * 6,
                     0x43: 2 * 7,
                     0x44: 2 * 6,
                     0x45: 3 * 7,
                     0x46: 3 * 6,
                     0x47: 4 * 7,
                     0x48: 4 * 6,
                     0x49: 5 * 7,
                     0x4a: 5 * 6,
                     0x4b: 6 * 7,
                     0x4c: 6 * 6,
                     0x4d: 7 * 7,
                     0x4e: 7 * 6,
                     0x4f: 8 * 7,
                     0x50: 8 * 6,
                     0x51: 9 * 7,
                     0x52: 9 * 6,
                     0x53: 10 * 7,
                     0x54: 10 * 6,
                     0x55: 11 * 7,
                     0x56: 11 * 6,
                     0x57: 12 * 7,
                     0x58: 12 * 6,
                     0x59: 13 * 7,
                     ADDR: 13 * 6,
                     })


def test_mpr121_debounce(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    mpr.debounce(touch=2, release=3)
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24, 0x80: RESET_CODE,
                     0x5b: (3 << 4) | 2
                     })
    mpr.debounce(touch=5)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24, 0x80: RESET_CODE,
                     0x5b: (5 << 4) | 5
                     })


def test_mpr121_gpio_setup(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    for i in range(8):
        mpr.gpio_setup(i + 4, output=i % 2, mode=i % 4)
    dev = bus.device(ADDR)
    assert_reg(dev, {0x5c: 0x10, 0x5d: 0x24, 0x80: RESET_CODE,
                     0x73: 0b11001100,
                     0x74: 0b10001000,
                     0x76: 0b10101010,
                     0x77: 0b11111111,
                     })


def test_mpr121_gpio_status(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    dev = bus.device(ADDR)
    dev.write_byte(0x75, 0b11001011)
    assert mpr.gpio_status() == 0b11001011


def test_mpr121_gpio_set(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    dev = bus.device(ADDR)
    for i in range(8):
        mpr.gpio_set(i + 4, 1)
        mpr.gpio_set(i + 4, 0)
        v = 0 if HARDWARE else (1 << i)
        assert_reg(dev, {0x78: v, 0x79: v}, only_non_zero=1)


@pytest.mark.skipif(HARDWARE, reason='not possible on actual hardware')
def test_mpr121_touched(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    dev = bus.device(ADDR)
    assert mpr.touched() == 0
    mpr.update_touch_state()
    handlers = []
    for i in range(13):
        handlers.append(Mock())
        mpr.on_touch(i, handlers[i])
        assert not mpr.is_touched(i)

    for i in range(13):
        dev.write_word(0, 1 << i)
        mpr.update_touch_state()
        for k in range(13):
            assert mpr.is_touched(k) == (k == i), '{} touched'.format(i)
            if k <= i:
                handlers[k].assert_called_with(k == i, k)
            elif k > i:
                handlers[k].assert_not_called()


@pytest.mark.xfail(strict=1)
@pytest.mark.skipif(HARDWARE, reason='not possible on actual hardware')
def test_mpr121_overcurrent(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    dev = bus.device(ADDR)
    dev.write_byte(1, 1 << 7)
    mpr.update_touch_state()


@pytest.mark.xfail(strict=1)
@pytest.mark.skipif(HARDWARE, reason='not possible on actual hardware')
def test_mpr121_out_of_range(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    dev = bus.device(ADDR)
    dev.write_byte(2, 1)
    mpr.update_touch_state()


@pytest.mark.xfail(strict=1)
@pytest.mark.skipif(HARDWARE, reason='not possible on actual hardware')
def test_mpr121_autoconf_failed(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    dev = bus.device(ADDR)
    dev.write_byte(3, 1 << 6)
    mpr.update_touch_state()


@pytest.mark.xfail(strict=1)
@pytest.mark.skipif(HARDWARE, reason='not possible on actual hardware')
def test_mpr121_autoreconf_failed(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=0)
    dev = bus.device(ADDR)
    dev.write_byte(3, 1 << 7)
    mpr.update_touch_state()


def test_mpr121_setup(bus):
    mpr = MPR121(bus=bus, handlers=0, setup=1)
    dev = bus.device(ADDR)
    assert_reg(dev, {0x2b: 0x05, 0x2c: 0x01, 0x2d: 0x03, 0x2e: 0x14, 0x2f: 0x05,
                     0x30: 0x01, 0x31: 0x03, 0x32: 0x14, 0x36: 0x01, 0x37: 0x01, 0x38: 0x03,
                     0x39: 0x14, 0x3a: 0x01, 0x3b: 0x01, 0x3c: 0x03, 0x3d: 0x14, 0x41: 0x32,
                     0x42: 0x1e, 0x43: 0x32, 0x44: 0x1e, 0x45: 0x32, 0x46: 0x1e, 0x47: 0x32,
                     0x48: 0x1e, 0x49: 0x32, 0x4a: 0x1e, 0x4b: 0x32, 0x4c: 0x1e, 0x4d: 0x32,
                     0x4e: 0x1e, 0x4f: 0x32, 0x50: 0x1e, 0x51: 0x32, 0x52: 0x1e, 0x53: 0x32,
                     0x54: 0x1e, 0x55: 0x32, 0x56: 0x1e, 0x57: 0x32, 0x58: 0x1e, 0x59: 0x0c,
                     ADDR: 0x07, 0x5b: 0x22, 0x5c: 0x5e, 0x5d: 0x28, 0x5e: 0xcc, 0x7b: 0x6f,
                     0x7c: 0x07, 0x7d: 0xc8, 0x7e: 0x82, 0x7f: 0xb4, 0x80: RESET_CODE},
               only_non_zero=HARDWARE)


@pytest.mark.skipif(HARDWARE, reason='not possible on actual hardware')
def test_mpr121_polling(bus):
    mpr = MPR121(bus=bus, handlers=1, irq=0, setup=1)
    handlers = []
    dev = bus.device(ADDR)
    for i in range(13):
        handlers.append(Mock())
        mpr.on_touch(i, handlers[i])

    for i in range(13):
        dev.write_word(0, 1 << i)
        sleep(0.05)  # give poller time pick up the state change
        handlers[i].assert_called_once_with(True, i)
        dev.write_word(0, 0)
        sleep(0.05)
        handlers[i].assert_called_with(False, i)


@pytest.mark.skipif(HARDWARE, reason='not possible on actual hardware')
@patch('piripherals.util.GPIO', create=1)
def test_mpr121_irq(GPIO, bus):
    mpr = MPR121(bus=bus, handlers=1, irq=4, setup=1)

    GPIO.setmode.assert_called_with(GPIO.BCM)
    GPIO.setup.assert_called_with(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect.assert_called_with(4, GPIO.FALLING, ANY)
    irq = GPIO.add_event_detect.call_args[0][2]

    handlers = []
    dev = bus.device(ADDR)
    for i in range(13):
        handlers.append(Mock())
        mpr.on_touch(i, handlers[i])

    for i in range(13):
        dev.write_word(0, 1 << i)
        irq()
        sleep(0.01)
        handlers[i].assert_called_once_with(True, i)
        dev.write_word(0, 0)
        irq()
        sleep(0.01)
        handlers[i].assert_called_with(False, i)


def test_mpr121_dump(bus, capsys):
    'see if dump() does not crash'
    mpr = MPR121(bus=bus, handlers=0, setup=1)
    mpr.dump()
    out, err = capsys.readouterr()
    assert 'raw base diff' in out
    assert '0x5c = 0x5e b01011110  94' in out
    assert '0x7b = 0x6f b01101111 111' in out
    assert '0x7b = 0x6f b01101111 111' in out
