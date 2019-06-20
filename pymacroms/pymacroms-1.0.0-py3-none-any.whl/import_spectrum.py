# -*- coding: utf-8 -*-
#
# Method asNumpyArray() is copied from RawQuant, copyright (c) 2018 kevinkovalchik. All rights reserved.
#
# Copyright (c) 2019 Kevin De Bruycker and Tim Krappitz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys
from collections import OrderedDict
import pandas as pd
import numpy as np
import re
import ctypes
import clr, System
from System import Array, Int32
clr.AddReference('System.Runtime.InteropServices')
if (sys.platform is 'linux') | (sys.platform is 'darwin'):  # check if we are on a Linux or mac OS X system
    clr.AddReference('pymacroms/RawFileReader/Unix/ThermoFisher.CommonCore.Data')
else:
    clr.AddReference('pymacroms/RawFileReader/Windows/ThermoFisher.CommonCore.Data')
    # clr.AddReference('../RawQuant/RawFileReader/ThermoFisher.CommonCore.Data')
from System.Runtime.InteropServices import GCHandle, GCHandleType
from ThermoFisher.CommonCore.Data import Business


class MSData:

    def __init__(self, filename: str, chargeFilter: int = None, scanFilter: list = None, averageOverScanRange: list = None, averageOverRetentionTime: list = None):

        self.filename = re.sub("\A(.*)\.([^.]*)\Z", "\\1", filename)
        self.extension = re.sub("\A(.*)\.([^.]*)\Z", "\\2", filename)

        print("Loading spectrum...")
        if self.extension.lower() == "csv":
            self.scans = OrderedDict({'1': {'rt': 0.0, 'spectrum': pd.read_csv(filename, "\t", names=["mz", "abundance"])}})
            self.scanRange = range(1, 2)
        elif self.extension.lower() == "raw":
            rawfile = Business.RawFileReaderFactory.ReadFile(filename)
            rawfile.SelectInstrument(0, 1)
            self.scanRange = range(rawfile.RunHeaderEx.FirstSpectrum, rawfile.RunHeaderEx.LastSpectrum + 1)
            scanAverager = Business.ScanAveragerFactory.GetScanAverager(rawfile)

            if (averageOverScanRange and averageOverRetentionTime):
                sys.exit("Please provide either averageOverScanRange or averageOverRetentionTime, not both.")
            elif (averageOverScanRange == 'all' or averageOverRetentionTime == 'all'):
                print("--> Averaging all scans...")
                averageScan = scanAverager.GetAverageScanInScanRange(rawfile.RunHeaderEx.FirstSpectrum, rawfile.RunHeaderEx.FirstSpectrum, None)
            elif averageOverScanRange:
                print("--> Averaging scans " + str(averageOverScanRange[0]) + " to " + str(averageOverScanRange[1]) + "...")
                averageScan = scanAverager.GetAverageScanInScanRange(averageOverScanRange[0], averageOverScanRange[1], None)
            elif averageOverRetentionTime:
                print("--> Averaging scans with RT from " + str(averageOverRetentionTime[0]) + " to " + str(averageOverRetentionTime[1]) + " minutes...")
                averageScan = scanAverager.GetAverageScanInScanRange(rawfile.ScanNumberFromRetentionTime(averageOverRetentionTime[0]), rawfile.ScanNumberFromRetentionTime(averageOverRetentionTime[1]), None)
            else:
                averageScan = None

            if averageScan:
                peakData = pd.DataFrame(zip(self.asNumpyArray(averageScan.CentroidScan.Masses),
                                            self.asNumpyArray(averageScan.CentroidScan.Intensities),
                                            self.asNumpyArray(averageScan.CentroidScan.Charges)),
                                        columns=["mz", "abundance", "Charge"])
                if chargeFilter is not None:
                    peakData.drop(peakData[peakData["Charge"] != chargeFilter].index, inplace=True)
                peakData.drop(columns=["Charge"], inplace=True)
                peakData.reset_index(drop=True, inplace=True)
                self.scans = OrderedDict({'1': {'rt': 0.0, 'spectrum': peakData}})
            else:
                self.scans = OrderedDict()
                for scan in self.scanRange:
                    if scanFilter is not None:
                        if scan not in scanFilter:
                            continue
                    tempData = rawfile.GetCentroidStream(scan, None) # gives access to temp.Masses, .Intensities, .Resolutions, .Baselines, .Noises and .Charges
                    peakData = pd.DataFrame(zip(self.asNumpyArray(tempData.Masses), self.asNumpyArray(tempData.Intensities), self.asNumpyArray(tempData.Charges)), columns=["mz", "abundance", "Charge"])
                    if chargeFilter is not None:
                        peakData.drop(peakData[peakData["Charge"] != chargeFilter].index, inplace=True)
                    peakData.drop(columns=["Charge"], inplace=True)
                    peakData.reset_index(drop=True, inplace=True)
                    self.scans[str(scan)] = {'rt': rawfile.RetentionTimeFromScanNumber(scan), 'spectrum': peakData}
        else:
            sys.exit("Filename extension not recognised!")

        print("--> Done\n")

    def asNumpyArray(self, netArray):
        '''
        Given a CLR `System.Array` returns a `numpy.ndarray`.  See _MAP_NET_NP for
        the mapping of CLR types to Numpy dtypes.
        '''
        # _MAP_NP_NET = {
        #     np.dtype('float32'): System.Single,
        #     np.dtype('float64'): System.Double,
        #     np.dtype('int8'): System.SByte,
        #     np.dtype('int16'): System.Int16,
        #     np.dtype('int32'): System.Int32,
        #     np.dtype('int64'): System.Int64,
        #     np.dtype('uint8'): System.Byte,
        #     np.dtype('uint16'): System.UInt16,
        #     np.dtype('uint32'): System.UInt32,
        #     np.dtype('uint64'): System.UInt64,
        #     np.dtype('bool'): System.Boolean,
        # }
        _MAP_NET_NP = {
            'Single': np.dtype('float32'),
            'Double': np.dtype('float64'),
            'SByte': np.dtype('int8'),
            'Int16': np.dtype('int16'),
            'Int32': np.dtype('int32'),
            'Int64': np.dtype('int64'),
            'Byte': np.dtype('uint8'),
            'UInt16': np.dtype('uint16'),
            'UInt32': np.dtype('uint32'),
            'UInt64': np.dtype('uint64'),
            'Boolean': np.dtype('bool'),
        }

        dims = np.empty(netArray.Rank, dtype=int)
        for I in range(netArray.Rank):
            dims[I] = netArray.GetLength(I)
        netType = netArray.GetType().GetElementType().Name

        try:
            npArray = np.empty(dims, order='C', dtype=_MAP_NET_NP[netType])
        except KeyError:
            raise NotImplementedError("asNumpyArray does not yet support System type {}".format(netType) )

        try: # Memmove
            sourceHandle = GCHandle.Alloc(netArray, GCHandleType.Pinned)
            sourcePtr = sourceHandle.AddrOfPinnedObject().ToInt64()
            destPtr = npArray.__array_interface__['data'][0]
            ctypes.memmove(destPtr, sourcePtr, npArray.nbytes)
        finally:
            if sourceHandle.IsAllocated: sourceHandle.Free()
        return npArray
