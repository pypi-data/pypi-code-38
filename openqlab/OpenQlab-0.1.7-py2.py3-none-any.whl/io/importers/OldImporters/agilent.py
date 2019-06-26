from OpenQlab.io.importers import utils

try:
    import numpy as np

    has_numpy = True
except ImportError:
    has_numpy = False


def get_importers():
    if has_numpy:
        return {'ag_binary': binary, 'ag_csv': csv}
    else:
        return {}


def csv(file):
    return np.loadtxt(file, delimiter=',', skiprows=2, usecols=(0, 1), unpack=True)


def binary(filename):
    import struct
    def debug(s):
        # print(s)
        pass

    readuInt8 = lambda f: struct.unpack('<B', f.read(1))[0]
    readInt16 = lambda f: struct.unpack('<h', f.read(2))[0]
    readInt32 = lambda f: struct.unpack('<i', f.read(4))[0]
    readuInt32 = lambda f: struct.unpack('<I', f.read(4))[0]
    readFloat32 = lambda f: struct.unpack('<f', f.read(4))[0]
    readDouble64 = lambda f: struct.unpack('<d', f.read(8))[0]

    with open(filename, 'rb') as f:
        # read file header
        fileCookie = f.read(2)
        debug(("fileCookie", fileCookie))
        # verify cookie
        if (fileCookie != b'AG'):
            raise utils.UnknownFileType("Keysight Binary: Missing 'AG' header")

        fileVersion = f.read(2)
        debug(("fileVersion", fileVersion))
        fileSize = readInt32(f)
        debug(("fileSize", fileSize))
        nWaveforms = readInt32(f)
        debug(("nWaveforms", nWaveforms))

        # stores voltage values from all waveforms and all buffers
        voltageVectors = []

        for waveformIndex in range(nWaveforms):
            # read waveform header
            headerSize = readInt32(f)
            debug(("headerSize", headerSize))
            bytesLeft = headerSize - 4
            waveformType = readInt32(f)
            debug(("waveformType", waveformType))
            bytesLeft -= 4
            nWaveformBuffers = readInt32(f)
            debug(("nWaveformBuffers", nWaveformBuffers))
            bytesLeft -= 4
            nPoints = readInt32(f)
            debug(("nPoints", nPoints))
            bytesLeft -= 4
            count = readInt32(f)
            debug(("count", count))
            bytesLeft -= 4
            xDisplayRange = readFloat32(f)
            debug(("xDisplayRange", xDisplayRange))
            bytesLeft -= 4
            xDisplayOrigin = readDouble64(f)
            debug(("xDisplayOrigin", xDisplayOrigin))
            bytesLeft -= 8
            xIncrement = readDouble64(f)
            debug(("xIncrement", xIncrement))
            bytesLeft -= 8
            xOrigin = readDouble64(f)
            debug(("xOrigin", xOrigin))
            bytesLeft -= 8
            xUnits = readInt32(f)
            debug(("xUnits", xUnits))
            bytesLeft -= 4
            yUnits = readInt32(f)
            debug(("yUnits", yUnits))
            bytesLeft -= 4
            dateString = f.read(16)
            debug(("dateString", dateString))
            bytesLeft -= 16
            timeString = f.read(16)
            debug(("timeString", timeString))
            bytesLeft -= 16
            frameString = f.read(24)
            debug(("frameString", frameString))
            bytesLeft -= 24
            waveformString = f.read(16)
            debug(("waveformString", waveformString))
            bytesLeft -= 16
            timeTag = readDouble64(f)
            debug(("timeTag", timeTag))
            bytesLeft -= 8
            segmentIndex = readuInt32(f)
            debug(("segmentIndex", segmentIndex))
            bytesLeft -= 4

            # skip over any remaining data in the header
            f.seek(bytesLeft, 1)  # 1 = relative to current position

            # generate time vector from xIncrement and xOrigin values
            if (waveformIndex == 0):
                timeVector = xIncrement * np.arange(nPoints) + xOrigin

            for bufferIndex in range(nWaveformBuffers):
                debug(("bufferIndex:", bufferIndex))
                # read waveform buffer header
                headerSize = readInt32(f)
                debug(("headerSize", headerSize))
                bytesLeft = headerSize - 4
                bufferType = readInt16(f)
                debug(("bufferType", bufferType))
                bytesLeft -= 2
                bytesPerPoint = readInt16(f)
                debug(("bytesPerPoint", bytesPerPoint))
                bytesLeft -= 2
                bufferSize = readInt32(f)
                debug(("bufferSize", bufferSize))
                bytesLeft -= 4
                debug(("bytesLeft", bytesLeft))

                # skip over any remaining data in the header
                f.seek(bytesLeft, 1)  # 1 = relative to current position

                debug(("BufferType:", bufferType))
                if ((bufferType == 1) or (bufferType == 2) or (bufferType == 3)):
                    # bufferType is PB_DATA_NORMAL, PB_DATA_MIN or PB_DATA_MAX (float)
                    voltageVector = np.zeros(nPoints, dtype=np.float32)
                    for ii in range(nPoints):
                        voltageVector[ii] = readFloat32(f)
                else:
                    if (bufferType == 4):
                        # bufferType is PB_DATA_COUNTS (int32)
                        voltageVector = np.zeros(nPoints, dtype=np.int32)
                        for ii in range(nPoints):
                            voltageVector[ii] = readInt32(f)
                    else:
                        if (bufferType == 5):
                            # bufferType is PB_DATA_LOGIC (uint8)
                            voltageVector = np.zeros(nPoints, dtype=np.uint8)
                            for ii in range(nPoints):
                                voltageVector[ii] = readuInt8(f)
                        else:
                            # unrecognized bufferType read as unformatted bytes
                            voltageVector = np.zeros(nPoints, dtype=np.uint8)
                            for ii in range(nPoints):
                                voltageVector[ii] = readuInt8(f)
                voltageVectors.append(voltageVector)
    return (timeVector, voltageVectors)
