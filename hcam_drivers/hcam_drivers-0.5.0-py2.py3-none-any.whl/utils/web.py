# Some utility tools to handle rising and setting etc.
from __future__ import print_function, unicode_literals, absolute_import, division
import traceback
import struct
import os
import json

import numpy as np
import yaml
from tornado.web import RequestHandler
from tornado.escape import json_encode
from astropy.io import fits
from astropy.utils.decorators import lazyproperty
from six.moves import urllib


MSG_TEMPLATE = "MESSAGEBUFFER: {}\nRETCODE: {}"
FRAME_NUMBER_URL = 'http://localhost:5000/status/DET.FRAM2.NO'


def getLastFrameNumber():
    """
    Polls the Hipercam server to find the current frame number

    Raises an exception in cases of failure
    """
    response = urllib.request.urlopen(FRAME_NUMBER_URL, timeout=0.5).read()
    try:
        data = json.loads(response)
    except:
        raise Exception('cannot parse server response')
    if data['RETCODE'] != 'OK':
        raise Exception('server response not OK')
    msg = data['MESSAGEBUFFER']
    try:
        frame_number = int(msg.split()[1])
    except:
        raise Exception('getLastFrameNumber error: msg = ' + msg)
    return frame_number


class BaseHandler(RequestHandler):
    """
    Abstract class for request handling
    """
    def initialize(self, db):
        self.db = db

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        resp = MSG_TEMPLATE.format(self._reason, 'NOK')
        resp_dict = yaml.load(resp)
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            resp_dict['traceback'] = lines
        self.finish(json_encode(resp_dict))


class FastFITSPipe:
    def __init__(self, fileobj):
        """
        Simple class to quickly read raw frame bytes from HiPERCAM FITS cube.

        For example::

            >> fileobj = open('example.fits', 'rb')
            >> ffp = FastFITSPipe(fileobj)
            >> ffp.seek_frame(100)
            >> hdu_data = ffp.read_frame_bytes()

        Parameters
        -----------
        fileobj : file-like object or str
            the file-like object representing a FITS file, readonly
        """
        # assume fileobj is string
        try:
            self._fileobj = open(fileobj, 'rb')
        except:
            self._fileobj = fileobj
        self._header_bytesize = None
        self.dtype = np.dtype('int16')

    @property
    def num_frames(self):
        # first, see if it's in the headers
        try:
            num = self.hdr['NAXIS3']
            if num == 0:
                raise ValueError('run still in progress')
        except (KeyError, ValueError) as err:
            # try and use ESO fileserver if it is running
            try:
                num = getLastFrameNumber()
            except:
                # last, desperate, chance to try to guess from the filesize
                current_size = os.stat(self._fileobj.name).st_size
                # cant use integer division because timestamps are buffered and 2800 fits
                # block size causes trouble. Also, for some crazy reason the filesize
                # from os.stat seems to be the header size and multiple of the frame
                # size *without the timing bytes*. I don't understand this, but still...
                data_size = current_size - self.header_bytesize
                num = int(round(data_size / (self.framesize - 36)))
        return num

    @lazyproperty
    def hdr(self):
        self._fileobj.seek(0)
        return fits.Header.fromfile(self._fileobj)

    @property
    def header_bytesize(self):
        if self._header_bytesize is None:
            self._fileobj.seek(0)
            _ = fits.Header.fromfile(self._fileobj)
            self._header_bytesize = self._fileobj.tell()
        return self._header_bytesize

    @lazyproperty
    def framesize(self):
        # get nsamples per pixel, old format should default to 1
        # since NX and NY are always right in old format, but
        # NX is four times too high when NSAMP = 4
        nsamp = self.hdr.get('ESO DET NSAMP', 1)
        size = 18 + (self.hdr['ESO DET ACQ1 WIN NX'] * self.hdr['ESO DET ACQ1 WIN NY']) // nsamp
        bitpix = self.hdr['BITPIX']
        size = abs(bitpix) * size // 8
        # currently metadata consists of 36 bytes per frame (for timestamp)
        return size

    def seek_frame(self, frame_number):
        """
        Try and find the start of a given frame

        Raises exception if frame not written yet
        """
        self._fileobj.seek(self.header_bytesize + self.framesize*(frame_number-1))

    def read_frame_bytes(self):
        start_pos = self._fileobj.tell()
        raw_bytes = self._fileobj.read(self.framesize)
        if len(raw_bytes) != self.framesize:
            # go back to start position
            self._fileobj.seek(start_pos)
            raise EOFError('frame not written yet')
        return raw_bytes


def raw_bytes_to_numpy(raw_data, bscale=1, bzero=32768, dtype='int16'):
    """
    Convert output from FastFITSPipe to numpy array

    For example::

        >> raw_data = ffp.read_frame_bytes()
        >> data = raw_bytes_to_numpy(raw_data)
        >> data = data.reshape(ffp.output_shape)

    Parameters
    -----------
    raw_data : bytes
        bytes returned from FastFITSPipe
    bscale : int, default = 1
        scaling to apply to raw data.
        FITS cannot stored unsigned 16-bit integers, so
        data is usually stored as signed 16-bit and then scaled
    bzero : int, default = 32768
        offset to apply to raw data
    dtype : string, default='int16'
        data type used to store data
    """
    data = np.fromstring(raw_data, np.dtype(dtype))
    data.dtype = data.dtype.newbyteorder('>')
    np.multiply(data, bscale, data)
    # now try and recast back to unsigned ints without a copy
    # see stackoverflow.com/questions/4389517/in-place-type-conversion-of-a-numpy-array
    view = data.view('uint16')
    view.dtype = view.dtype.newbyteorder('>')
    view += bzero
    return view


def decode_timestamp(ts_bytes):
    """
    Decode timestamp tuple from values saved in FITS file

    The timestamp is originally encoded to bytes as a series of
    32bit (4 bytes) unsigned integers in little endian byte format.

    Added to this is a pair of chars (1 byte) for the number of satellites
    tracked and a sync status.

    However, this is then stored as fake pixels in a FITS file, which
    performs some mangling of the data, since FITS assumes 16bit (2 byte)
    integers, and has no way to store unsigned integers. The following
    mangling occurs:

    - decode the timestamp byte string as two 16bit (2 bytes) little-endian unsigned integers;
    - subtract 32768 from each integer;
    - encode these integers as two 16bit signed integers in BIG ENDIAN format;
    - save to file as fits data.

    This routine reverses this process to recover the original timestamp tuple. We have to
    take some care because of all the endian-swapping going on. For example, the number 27
    starts off as \x1b\x00\x00\x00, which is interpreted by the FITS save process as (27, 0).
    If we ignore the signing issue for clarity, then (27, 0) encoded in big endian format is
    \x00\x1b, \x00\x00 so we've swapped the byte pairs around.

    The steps taken by this routine are:

    - decode timestamp string as big endian 16bit integers
    - add 32768 to each value
    - encode these values as little endian 16bit unsigned integers
    - re-interpret the new byte string as 32bit, little-endian unsigned integers

    The status bytes are handled slightly differently: after the re-encoding to little endian
    16 bit uints, they are decoded as chars, and the last two chars discarded.

    Parameters
    ----------
    ts_bytes: bytes
        a Python bytes object which contains the timestamp bytes as written in the
        FITS file

    Returns
    --------
    timestamp : tuple
        a tuple containing the (frameCount, timeStampCount,
                                years, day_of_year, hours, mins,
                                seconds, nanoseconds) values.
    """
    buf = struct.pack('<' + 'H'*18, *(val + 32768 for val in struct.unpack('>'+'h'*18, ts_bytes)))
    return struct.unpack('<' + 'I'*8, buf[:-4]) + struct.unpack('bb', buf[-4:-2])
