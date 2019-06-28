#!/usr/bin/env python
"""
computes cost of storing camera data
"""
from __future__ import division


class Cam():
    def __init__(self, npix, fps, hddTB, cost, nbit=16, goodfrac=0.05):
        self.goodfrac = goodfrac
        hoursrecday = 8  # avg hours per night cameras on
        self.monthsseason = 8  # months of year recording
        dayspermonth = 30
        self.hoursperseason = self.monthsseason * dayspermonth * hoursrecday

        self.npix = npix
        self.fps = fps
        self.nbit = nbit
        self.hddTB = hddTB
        self.costTB = cost / self.hddTB

        self.bytesec = self.npix * self.nbit // 8 * self.fps
        self.bytehour = self.bytesec * 3600

        self.HDDcosthour = self.costTB * self.bytehour / 1e12

        self.hourstorage = self.hddTB / (self.bytehour / 1e12)

        self.TBseason = self.hoursperseason * self.bytehour / 1e12 * self.goodfrac


# %%
print('quantities are for full data rate')

Zyla = Cam(2560 * 2160, 100, 4, 1500)
print('\n--------------------------')
print('Zyla')
print(f'MB/sec: {Zyla.bytesec/1e6:.1f}    GB/hour: {Zyla.bytehour/1e9:.0f}')
print(f'SSD: ${Zyla.HDDcosthour:.2f}/hour')
print(f'{Zyla.hddTB} TB SSD fills in {Zyla.hourstorage:.2f} hours')

NeoDMC = Cam(2560 / 4 * 2160 / 4, 30, 8, cost=220)
print('\n--------------------------')
print('Neo Marshall DMC (4x4 full frame binning)')
print(f'MB/sec: {NeoDMC.bytesec/1e6:.1f}    GB/hour: {NeoDMC.bytehour/1e9:.0f}')
print(f'SSD: ${NeoDMC.HDDcosthour:.2f}/hour')
print(f'{NeoDMC.hddTB} TB HDD fills in {NeoDMC.hourstorage:.2f} hours')

U897 = Cam(512 * 512, 56, 8, 220)
print('\n--------------------------')
print('Ultra 897')
print('MB/sec: {:.1f}    GB/hour: {:.0f}'.format(U897.bytesec /
                                                 1e6, U897.bytehour / 1e9))
print('HDD: ${:.2f}/hour'.format(U897.HDDcosthour))
print('{} TB HDD fills in {:.1f} hours'.format(U897.hddTB, U897.hourstorage))

U888 = Cam(1024 * 1024, 26, 8, 220)
print('\n--------------------------')
print('Ultra 888')
print('MB/sec: {:.1f}    GB/hour: {:.0f}'.format(U888.bytesec /
                                                 1e6, U888.bytehour / 1e9))
print('HDD: ${:.2f}/hour'.format(U888.HDDcosthour))
print('{} TB HDD fills in {:.1f} hours'.format(U888.hddTB, U888.hourstorage))
# %%

print('{} month season {} % retained: {:.1f} TB'.format(
    U888.monthsseason, U888.goodfrac * 100, U888.TBseason))
