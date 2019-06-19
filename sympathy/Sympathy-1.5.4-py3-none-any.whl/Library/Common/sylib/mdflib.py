# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import datetime
import pytz
import struct as S
import itertools
import io
import os
from collections import defaultdict, OrderedDict
from math import ceil, log
from bisect import bisect
import six
import sys
import numpy as np
from numpy import (ndarray, multiply, bitwise_and, right_shift,
                   dtype, square)
from numpy import log as ln


def getbuffer(array):
    if len(array) == 0:
        return b''
    return array.tobytes()


(BYTE_SIZE,) = (8,)

(LITTLE_ENDIAN, BIG_ENDIAN) = ('<', '>')

(SINT64, SINT32, SINT16, SINT8, SINT1) = ('q', 'i', 'h', 'b', '?')
(UINT64, UINT32, UINT16, UINT8, UINT1) = ('Q', 'I', 'H', 'B', '?')
(REAL, FLOAT64, FLOAT32, LINK, BOOL, NULL) = ('d', 'd', 'f', 'I', 'H', '')


def STRING(n):
    return '{}s'.format(n)


struct_to_numpy = {'?': 'b1',
                   's': 'S',
                   'B': 'u1',
                   'H': 'u2',
                   'I': 'u4',
                   'Q': 'u8',
                   'b': 'i1',
                   'h': 'i2',
                   'i': 'i4',
                   'q': 'i8',
                   'f': 'f4',
                   'd': 'f8'}


def zeroterm(string):
    if isinstance(string, six.text_type):
        string = string.encode('latin1')

    if len(string) == 0:
        string = b'\0'
    elif string[-1] != b'\0':
        string += b'\0'
    return string


def flatten(lists):
    return [item for list_ in lists for item in list_]


def required_bits(datacolumn):
    if datacolumn.dtype == dtype(bool):
        return 1
    else:
        return datacolumn.dtype.itemsize * BYTE_SIZE


def warn_or_err(env, msg):
    if env[MdfFile.allow_partial]:
        print('WARNING: {}'.format(msg), file=sys.stderr)
    else:
        raise MdfError(msg)


def err_overlapping():
    raise UnsupportedData(
        'Data storage appears to be overlapping, '
        'this is not supported by the importer and may '
        'indicate a problem with the file')


class MdfError(Exception):
    pass


class UnsupportedData(MdfError):
    pass


class VersionError(MdfError):
    pass


class Block():
    """Provides basic reading functionality and encapsulates common fields."""

    _format_000_head = [STRING(2), UINT16]
    _format_000 = []
    _identifier = '--'
    _default_000_head = (_identifier, 0)
    _fixed_block_size = False

    def __init__(self):
        self._fsock = None
        self._offset = None
        self._env = None

        self.set_init_000_head(self._default_000_head)

    def read_init(self, fsock, offset, env):
        self._fsock = fsock
        self._offset = offset
        self._env = env

        fsock.seek(offset)
        self.read_init_head(fsock, offset, env)

    def read_init_head(self, fsock, offset, env):
        self.set_init_000_head(self.read_format(fsock,
                                                Block._format_000_head,
                                                env))
        self.read_init_body(fsock, offset, env)

    def read_init_body(self, fsock, offset, env):
        self.read_version(fsock, 000, env)
        self.read_init_after_body(fsock, offset, env)

    def read_init_after_body(self, fsock, offset, env):
        pass

    def read_format(self, fsock, in_format, env):
        out_format = env[Identification.endianness] + "".join(in_format)
        format_size = S.calcsize(out_format)
        currently_read = fsock.tell() - self._offset
        extra = currently_read + format_size - self.block_size
        # Handling of reading more than the specified block_size (if any).
        if self.block_size > 0 and extra > 0:
            return S.unpack(out_format, fsock.read(format_size - extra) +
                            b'\x00' * extra)
        else:
            return S.unpack(out_format, fsock.read(format_size))

    def read_text(self, fsock, format_func, env):
        bytesize = self.block_size - self.get_head_size(env)
        number = int(bytesize // S.calcsize(format_func(1)))
        return self.read_format(fsock, [format_func(number)], env)

    def read_version(self, fsock, version, env):
        # check file version
        if env[Identification.version] >= version:
            for (ver, form, getter) in self.get_format()[1:]:
                if version == ver:
                    fieldvalues = self.read_format(fsock, form, env)
                    # initialize MDF version fields
                    settername = getter.__name__.replace('get', 'set')
                    getattr(self, settername)(fieldvalues)

    def set_init_000_head(self, fieldvalues):
        (self.block_type_identifier,
         self.block_size) = fieldvalues

    def get_init_000_head(self):
        return (self.block_type_identifier,
                self.block_size)

    def get_init_000(self):
        pass

    def before_write(self):
        pass

    def write(self, fsock, env):
        self.before_write()

        pos = fsock.tell()
        fieldvalues = []
        size = self.get_size(env)

        if not self._fixed_block_size:
            self.block_size = size
            self.block_type_identifier = self._identifier

        for (ver, form, fieldgetter) in self.get_format():
            fields = fieldgetter()
            if env[Identification.version] >= ver:
                for i in range(len(form)):
                    field = fields[i]
                    if isinstance(field, six.text_type):
                        field = field.encode('latin1')

                    fieldvalues.append(
                        S.pack(env[Identification.endianness] + form[i],
                               field))

        out_fieldvalues = b"".join(fieldvalues)
        fsock.write(out_fieldvalues)

        if self._fixed_block_size:
            fsock.seek(pos + size)

        return pos

    def get_format(self):
        return (self.get_format_head() +
                self.get_format_body() +
                self.get_format_after_body())

    def get_format_head(self):
        return [(000, self._format_000_head, self.get_init_000_head)]

    def get_format_body(self):
        return [(000, self._format_000, self.get_init_000)]

    def get_format_after_body(self):
        return []

    def get_format_size(self, forms, env):
        size = 0
        for (ver, form, fields) in forms:
            if env[Identification.version] >= ver:
                size += S.calcsize(env[Identification.endianness] +
                                   "".join(form))
        return size

    def get_size(self, env):
        return self.get_format_size(self.get_format(), env)

    def get_head_size(self, env):
        return self.get_format_size(self.get_format_head(), env)

    def get_link(self, field, fieldclass):
        if field > 0:
            cls = fieldclass()
            cls.read_init(self._fsock, field, self._env)
            return cls

    def get_links(self, bound_fieldgetter, cls_unbound_fieldgetter):
        cls = bound_fieldgetter()

        while cls is not None:
            yield cls
            cls = cls_unbound_fieldgetter(cls)

    def get_string(self, stringfield):
        nullindex = stringfield.find(b'\x00')
        if nullindex == - 1:
            return stringfield
        return stringfield[:nullindex]

    def show(self):
        def pad(line, maxlen):
            return line + (' ' * (maxlen - len(line)))

        def wordify(fieldname):
            words = fieldname.split('_')
            return ' '.join(words)

        def maxlen(fieldnames):
            currmax = 0
            for fieldname in fieldnames:
                currlen = len(fieldname)
                if currlen > currmax:
                    currmax = currlen
            return currmax

        fieldnames = self.__dict__.keys()
        fielddict = self.__dict__
        length = maxlen(fieldnames)

        print(self.__class__.__name__)
        print('-' * (length + 1))
        for fieldname in fieldnames:
            print("{0}:{1}".format(wordify(pad(fieldname, length)),
                                   fielddict[fieldname]))
        print('-' * (length + 1))


class Identification(Block):
    """Provides identification of the MDF file."""

    offset = 0
    size_max = 64
    version = 'version_number'
    endianness = 'default_byte_order'
    float_format = 'default_float_format'

    _fixed_block_size = True
    _format_000 = [STRING(8), STRING(8), STRING(8), UINT16, UINT16, UINT16]
    _format_330 = [UINT16]
    _default_000 = ('MDF', '3.00', 'Sympathy', 0, 0, 300)
    _default_330 = (0,)
    _identifier = 'ID'

    def __init__(self, env):
        Block.__init__(self)
        self.env = env
        self._env = env
        self.set_init_000(self._default_000)
        self.set_init_330(self._default_330)

    def read_init_head(self, fsock, offset, env):
        # assuming little endian
        env[Identification.endianness] = LITTLE_ENDIAN

        # initialize MDF 0.00 fields
        fsock.seek(Identification.offset)
        self.read_version(fsock, 000, env)

        # verify assumption
        if self.default_byte_order > 0:
            env[Identification.endianness] = BIG_ENDIAN

            # re-initialize MDF 0.00 fields
            fsock.seek(Identification.offset)
            self.read_version(fsock, 000, env)

        env[Identification.version] = self.version_number
        env[Identification.float_format] = self.default_float_format
        self.env = env

        # initialize MDF 3.30 fields
        self.read_version(fsock, 330, env)

    def set_init_000(self, fieldvalues):
        (self.file_identifier,
         self.format_identifier,
         self.program_identifier,
         self.default_byte_order,
         self.default_float_format,
         self.version_number) = fieldvalues

    def set_init_330(self, fieldvalues):
        (self.code_page_number,) = fieldvalues

    def get_init_000(self):
        return (self.file_identifier,
                self.format_identifier,
                self.program_identifier,
                self.default_byte_order,
                self.default_float_format,
                self.version_number)

    def get_init_330(self):
        return (self.code_page_number,)

    def before_write(self):
        def pad8(string):
            ldelta = 8 - len(string)
            if ldelta > 0:
                string += ' ' * ldelta
            return string

        self.file_identifier = pad8(self.file_identifier)

    def get_format(self):
        return [(000, [], lambda: ()),
                (000, self._format_000, self.get_init_000)]

    def get_size(self, env):
        return self.size_max

    def get_program_identifier(self):
        return self.get_string(self.program_identifier)


class Header(Block):
    """Provides information describing the MDF file."""

    _offset = Identification.size_max
    _identifier = 'HD'
    _format_000 = [LINK,
                   LINK,
                   LINK,
                   UINT16,
                   STRING(10),
                   STRING(8),
                   STRING(32),
                   STRING(32),
                   STRING(32),
                   STRING(32)]
    _format_320 = [UINT64, SINT16, UINT16, STRING(32)]
    _default_000 = (0, 0, 0, 0,
                    "01:01:1970",
                    "00:00:00",
                    "Unknown Author",
                    "Unknown Organization",
                    "Unknown Project",
                    "Unknown Subject")
    _default_320 = (0, 0, 0,
                    "Unknown Timer")

    def __init__(self):
        Block.__init__(self)
        self.set_init_000(self._default_000)
        self.set_init_320(self._default_320)

    def read_init_after_body(self, fsock, offset, env):
        # initialize MDF 3.20 fields
        self.read_version(fsock, 320, env)

    def set_init_000(self, fieldvalues):
        (self.data_group_block,
         self.file_comment,
         self.program_block,
         self.number_of_data_groups,
         self.date,
         self.time,
         self.author,
         self.organization_or_department,
         self.project,
         self.subject_measurement_object) = fieldvalues

    def set_init_320(self, fieldvalues):
        (self.time_stamp,
         self.utc_time_offset,
         self.time_quality_class,
         self.timer_identification) = fieldvalues

    def get_init_000(self):
        return (self.data_group_block,
                self.file_comment,
                self.program_block,
                self.number_of_data_groups,
                self.date,
                self.time,
                self.author,
                self.organization_or_department,
                self.project,
                self.subject_measurement_object)

    def get_init_320(self):
        return (self.time_stamp,
                self.utc_time_offset,
                self.time_quality_class,
                self.timer_identification)

    def get_format_body(self):
        return [(000, self._format_000, self.get_init_000),
                (320, self._format_320, self.get_init_320)]

    def get_data_group_block(self):
        return self.get_link(self.data_group_block, DataGroup)

    def get_file_comment(self):
        return self.get_link(self.file_comment, Text)

    def get_program_block(self):
        return self.get_link(self.program_block, Program)

    def get_author(self):
        return self.get_string(self.author)

    def get_organization_or_department(self):
        return self.get_string(self.organization_or_department)

    def get_project(self):
        return self.get_string(self.project)

    def get_subject_measurement_object(self):
        return self.get_string(self.subject_measurement_object)

    def get_data_group_blocks(self):
        return self.get_links(self.get_data_group_block,
                              DataGroup.get_next_data_group_block)


# Data block
# Data records of Channel signal data
class DataBlock():
    """
    DataBlock class.
        Contains: Data records of Channel signal data
    """

    def __init__(self, dgblock):
        self.dgblock = dgblock
        self.signal_tables = {}

    def read_init(self, fsock, offset, env):
        self.record_ids = OrderedDict()
        endianness = env[Identification.endianness]
        number_of_records = 0
        for cgblock in self.dgblock.get_channel_group_blocks():
            self.record_ids[cgblock.record_id] = cgblock
            number_of_records += cgblock.number_of_records

        fsock.seek(self.dgblock.data_block)

        # sorted Writing - no record ids
        if self.dgblock.number_of_record_ids == 0:
            cgblock = list(self.record_ids.values())[0]
            self.read_data_records(cgblock, fsock, env)
        else:
            block_data = {}

            for i in range(number_of_records):
                record_id, = S.unpack(endianness + UINT8, fsock.read(1))
                cgblock = self.record_ids[record_id]

                block_data.setdefault(record_id, []).append(
                    fsock.read(cgblock.size_of_data_record))
                if self.dgblock.number_of_record_ids == 2:
                    fsock.read(1)

            for record_id, cgblock in self.record_ids.items():
                fsock_ = io.BytesIO(b''.join(block_data[record_id]))
                fsock_.seek(0)
                self.read_data_records(cgblock, fsock_, env)

    def _data_sizes(self, fsock, cgblock, env):
        pos = fsock.tell()
        max_chunksize = 100 * (2 ** 20)  # 100 MiB
        size_of_data_record = cgblock.size_of_data_record

        if size_of_data_record:
            # whole structure
            full_data_block_size = (size_of_data_record *
                                    cgblock.number_of_records)
            fsock.seek(0, os.SEEK_END)
            file_data_size = max(fsock.tell() - pos, 0)
            data_block_size = min(full_data_block_size, size_of_data_record * (
                file_data_size // size_of_data_record))
            if data_block_size < full_data_block_size:
                warn_or_err(
                    env, 'Data block is smaller than requested, '
                    'file may be incomplete. Expected {} bytes, but only '
                    '{} is available'.format(full_data_block_size,
                                             data_block_size))
            number_of_records = data_block_size // size_of_data_record
            chunksize = (
                (max_chunksize // size_of_data_record) * size_of_data_record)
        else:
            number_of_records = 0
            data_block_size = 0
            chunksize = 0

        fsock.seek(pos)
        return data_block_size, number_of_records, chunksize

    def read_data_records_slow(self, cgblock, fsock, env):
        """
        Fallback routine used when there are signals other than bit signals
        which are not byte aligned.
        """
        def rowiter(databytes, width):
            for i in range(0, len(databytes), width):
                row = databytes[i: i + width]
                if row:
                    yield row
                else:
                    break

        tell = fsock.tell()
        signal_table = self.signal_tables.setdefault(
            cgblock.record_id, {})

        # sort channels on start bit so as to process them in order
        channels = sorted(
            [cnblock for cnblock in cgblock.get_channel_blocks()],
            key=Channel.startbit)

        size_of_data_record = cgblock.size_of_data_record

        fsock.seek(tell)
        data_block_size, number_of_records, chunksize = self._data_sizes(
            fsock, cgblock, env)

        # Precompute offsets.
        channelsdata = []
        namesdata = []
        ntypesdata = []

        bit_offset = 0
        bit_offset_prev = 0

        for i, cnblock in enumerate(channels):
            name = cnblock.get_signal_name()
            if name == '':
                name = Channel.EMPTY_SIGNAL_NAME

            bit_offset = (
                cnblock.additional_byte_offset * BYTE_SIZE +
                cnblock.start_offset_in_bits)

            if bit_offset_prev > bit_offset:
                err_overlapping()

            byte_offset = bit_offset // BYTE_SIZE

            # right shift amount
            right_shift_amount = (
                cnblock.start_offset_in_bits % BYTE_SIZE)
            signal_bytes = int(ceil((cnblock.number_of_bits +
                                     right_shift_amount) / 8))

            (endianness, signal_type) = cnblock.get_signal_read_data_type(env)
            mask = (2 ** cnblock.number_of_bits) - 1
            integral = cnblock.get_signal_is_integral()
            padbytes = b''
            if integral:
                padbytes = b'\x00' * (
                    int(2 ** ceil(log(signal_bytes, 2))) - signal_bytes)

            channelsdata.append(
                (cnblock, name, byte_offset, right_shift_amount,
                 signal_bytes, endianness, signal_type, mask, padbytes))
            namesdata.append(name)

            # set number of bytes for type string/ array
            ntype = (endianness + struct_to_numpy[signal_type])
            if signal_type == 's':
                ntype += bytes(signal_bytes)
            ntypesdata.append(ntype)

            bit_offset_prev = bit_offset + cnblock.number_of_bits

        for name, ntype in zip(namesdata, ntypesdata):
            # create output signal
            if number_of_records > 0:
                try:
                    signal_table[name] = np.empty(
                        shape=(number_of_records,),
                        dtype=ntype)
                except RuntimeError:
                    print("WARNING, not storing channel:{0}".format(name),
                          file=sys.stderr)
            else:
                signal_table[name] = np.array([], dtype=ntype)

        # Must seek again since cnblock.get_signal_name()
        # affects the file position when long name pointer is used.
        fsock.seek(tell)
        bytes_read = 0

        while bytes_read < data_block_size:

            rowsdata = []

            for i, _ in enumerate(channels):
                rowsdata.append([])

            readsize = min(chunksize, data_block_size - bytes_read)
            records = fsock.read(readsize)

            try:
                lbound = bytes_read // size_of_data_record
                ubound = (bytes_read + readsize) // size_of_data_record
            except Exception:
                lbound = 0
                ubound = 0
            bytes_read += readsize

            for row in rowiter(records, size_of_data_record):
                for i, (cnblock, name, byte_offset, right_shift_amount,
                        signal_bytes, endianness, signal_type, mask, padbytes
                        ) in enumerate(channelsdata):

                    cellbytes = row[byte_offset:byte_offset + signal_bytes]

                    if signal_type == 's':
                        stype = (endianness + six.text_type(signal_bytes) +
                                 signal_type)
                    elif signal_type == '?':
                        stype = endianness + 'b'
                    else:
                        stype = endianness + signal_type

                    if padbytes:
                        if endianness == '<':
                            celldata, = S.unpack(stype, cellbytes + padbytes)
                        else:
                            celldata, = S.unpack(stype, padbytes + cellbytes)
                    else:
                        celldata, = S.unpack(stype, cellbytes)

                    if right_shift_amount:
                        celldata = right_shift(celldata, right_shift_amount)

                    if cnblock.number_of_bits % BYTE_SIZE != 0:
                        if signal_type == '?':
                            celldata = bitwise_and(celldata, 1)
                        else:
                            celldata = bitwise_and(celldata, mask)

                    rowsdata[i].append(celldata)

            # Copy signals.
            for i, name in enumerate(namesdata):
                signal = signal_table[name]

                if signal.shape[0] != 0:
                    signal[lbound:ubound] = rowsdata[i]

    def read_data_records(self, cgblock, fsock, env):
        tell = fsock.tell()
        size_of_data_record = cgblock.size_of_data_record
        fsock.seek(tell)
        data_block_size, number_of_records, chunksize = self._data_sizes(
            fsock, cgblock, env)

        # sort channels on start bit so as to process them in order
        channels = sorted(
            [cnblock for cnblock in cgblock.get_channel_blocks()],
            key=Channel.startbit)

        for cnblock in channels:
            oddbits = cnblock.number_of_bits % BYTE_SIZE > 0
            right_shift_amount = cnblock.start_offset_in_bits % BYTE_SIZE
            signal_bytes = int(ceil((cnblock.number_of_bits +
                                     right_shift_amount) / 8))

            padint = (cnblock.get_signal_is_integral() and
                      signal_bytes not in [1, 2, 4, 8])
            if (padint or (cnblock.number_of_bits > 1 and
                           (oddbits or right_shift_amount))):
                # Use fallback method.
                fsock.seek(tell)
                return self.read_data_records_slow(cgblock, fsock, env)

        signal_table = self.signal_tables.setdefault(cgblock.record_id, {})

        type_list_in = []
        type_list_out = []
        unaligned_signals = []
        aligned_signals = []

        in_dict = {}

        byte_offset_prev = 0
        signal_bytes_prev = 0

        bit_offset = 0
        bit_offset_prev = 0

        for cnblock in channels:
            # determine Byte offset in record
            bit_offset = (
                cnblock.additional_byte_offset * BYTE_SIZE +
                cnblock.start_offset_in_bits)

            if bit_offset_prev > bit_offset:
                err_overlapping()

            byte_offset = bit_offset // BYTE_SIZE

            # right shift amount
            right_shift_amount = cnblock.start_offset_in_bits % BYTE_SIZE
            signal_bytes = int(ceil((cnblock.number_of_bits +
                                     right_shift_amount) / 8))
            # bitmask for unused bits
            signal_mask = (2 ** cnblock.number_of_bits) - 1
            (endianness, signal_type) = cnblock.get_signal_data_type(env)

            number_of_gap_bytes = byte_offset - (byte_offset_prev +
                                                 signal_bytes_prev)

            if number_of_gap_bytes > 0:
                type_list_in.extend([endianness + 'B'] * number_of_gap_bytes)

            # set number of bytes for type string/ array
            ntype = (endianness + struct_to_numpy[signal_type])
            if signal_type == 's':
                ntype += six.text_type(signal_bytes)

            signal_name = cnblock.get_signal_name()
            # create output signal
            if number_of_records > 0:
                try:
                    signal_table[signal_name] = np.empty(
                        shape=(number_of_records,),
                        dtype=ntype)
                except RuntimeError:
                    print("WARNING, not storing channel:{0}".format(
                        signal_name), file=sys.stderr)
            else:
                signal_table[signal_name] = np.array([], dtype=ntype)

            in_dict[signal_name] = len(type_list_in)

            if right_shift_amount != 0 or (cnblock.number_of_bits & 7) > 0:
                # signal is not byte aligned
                share_byte = ((byte_offset_prev + signal_bytes_prev) -
                              byte_offset) == 1
                in_array_index = len(type_list_in) - 1
                number_of_bytes = signal_bytes - 1

                if not share_byte:
                    # signal does not share byte with previous signal
                    number_of_bytes += 1
                    in_array_index = len(type_list_in)

                if number_of_bytes > 0:
                    # extending with raw byte types
                    type_list_in.extend([endianness + 'B'] * number_of_bytes)

                unaligned_signals.append((in_array_index,
                                          ntype,
                                          signal_bytes,
                                          right_shift_amount,
                                          signal_mask,
                                          signal_name))
                type_list_out.append(ntype)
            else:
                aligned_signals.append(signal_name)
                type_list_in.append(ntype)

            byte_offset_prev = byte_offset
            signal_bytes_prev = signal_bytes

            bit_offset_prev = bit_offset + cnblock.number_of_bits

        # Must seek again since cnblock.get_signal_name()
        # affects the file position when long name pointer is used.
        fsock.seek(tell)
        bytes_read = 0

        while bytes_read < data_block_size:

            readsize = min(chunksize, data_block_size - bytes_read)
            records = fsock.read(readsize)

            try:
                lbound = bytes_read // size_of_data_record
                ubound = (bytes_read + readsize) // size_of_data_record
            except Exception:
                lbound = 0
                ubound = 0
            bytes_read += readsize

            # create signal_table for the in-data (aligned/unaligned)
            if len(type_list_in) is 1:
                # Making sure to create a structured array in all cases.
                data = ndarray(shape=(readsize // size_of_data_record,),
                               dtype=[(str('f0'), type_list_in[0])],
                               buffer=records)
            else:
                data = ndarray(shape=(readsize // size_of_data_record,),
                               dtype=",".join(type_list_in),
                               buffer=records)

            # copy aligned signals
            for signal_name in aligned_signals:
                i = in_dict[signal_name]
                signal = signal_table[signal_name]

                if signal.shape[0] != 0:
                    signal[lbound:ubound] = data["f%s" % i]

            fieldindices_prev = []
            # process unaligned signals
            for (index_in,
                 out_type,
                 signal_bytes,
                 right_shift_amount,
                 signal_mask,
                 signal_name) in unaligned_signals:

                fieldindices = ["f%s" % (index_in + byte)
                                for byte in range(signal_bytes)]

                if len(fieldindices) == 1:
                    fieldindices = fieldindices[0]

                if signal_bytes > 1:
                    raise NotImplementedError('Unaligned signal crossing byte')

                if fieldindices != fieldindices_prev:
                    fields = data[fieldindices].copy()

                if dtype(out_type) == dtype(bool):
                    # Integer signals are required for bitwise operations.
                    # View the data as a one byte integer.
                    signal_type = 'i1'
                else:
                    # Integral type, proceed.
                    signal_type = out_type

                column = fields.view(dtype=signal_type)

                if right_shift_amount > 0:
                    # integral signal with bit offset
                    column = right_shift(column, right_shift_amount)

                column = bitwise_and(column, signal_mask)

                if dtype(out_type) == dtype(bool):
                    # Bit wise operations completed, view the data as boolean.
                    column = column.view(dtype=out_type)

                signal = signal_table[signal_name]

                if signal.shape[0] != 0:
                    signal[lbound:ubound] = column

                fieldindices_prev = fieldindices

    @staticmethod
    def write_datacolumns(
            fsock, data, next_data_group_block, env):

        def chunk(sequence, n):
            iterator = iter(sequence)
            current = list(itertools.islice(iterator, n))
            while current:
                yield current
                current = list(itertools.islice(iterator, n))

        def datacolumns(data):
            data_by_bits = sorted(((required_bits(x[0]), x)
                                   for x in data),
                                  key=lambda x: x[0], reverse=True)

            for pack, group in itertools.groupby(data_by_bits,
                                                 lambda x: x[0] is 1):
                if not pack:
                    for bits, (datacolumn, _, _, _, _) in group:
                        yield datacolumn
                else:
                    for chunk_group in chunk(group, 8):

                        byte_column = np.zeros(
                            (datacolumn.size,), dtype='u1')

                        for i, (bits, (datacolumn, _, _, _, _)) in enumerate(
                                chunk_group):
                            byte_column += np.left_shift(
                                datacolumn.view(dtype='u1'), i % BYTE_SIZE)

                        yield byte_column

        pos = fsock.tell()
        types = []
        number_of_channels = 0
        for datacolumn in datacolumns(data):
            types.append(datacolumn.dtype.str)
            number_of_channels += 1

        table_len = 0

        if number_of_channels > 0:
            table_len = datacolumn.size

            if number_of_channels is 1:
                # Making sure to create a structured array in all cases.
                signal_table = ndarray(
                    shape=(table_len,), dtype=[(str('f0'), types[0])])
            else:
                signal_table = ndarray(
                    shape=(table_len,), dtype=(",".join(types)))

            for i, datacolumn in enumerate(datacolumns(data)):
                signal_table['f%s' % i][:] = datacolumn

            buff = getbuffer(signal_table)
            len_buff = len(buff)

            # chunks
            max_chunksize = 100 * (2 ** 20)  # 100 MiB

            for i in range(0, len_buff, max_chunksize):
                fsock.write(buff[i:i+max_chunksize])

        return pos

    def get_channel_signal(self, cgblock, cnblock):
        # assuming signal table of record array type
        signal = self.signal_tables[
            cgblock.record_id][cnblock.get_signal_name()]

        if signal.shape[0] == 0:
            return (ndarray(shape=signal.shape, dtype=signal.dtype), None)

        if cnblock.conversion_formula == 0:
            return (signal, None)
        else:
            try:
                return cnblock.get_converted_signal(signal)
            except Exception:
                print('WARNING: not converting {0}'.format(
                    cnblock.get_signal_name()), file=sys.stderr)
                return (signal, None)


class Text(Block):
    """Provides string text block."""

    _format_000 = staticmethod(lambda n: STRING(n))
    _default_000 = ("Unknown text",)
    _identifier = 'TX'

    def __init__(self):
        Block.__init__(self)
        self.set_init_000(self._default_000)

    def read_init_body(self, fsock, offset, env):
        # initialize variable length MDF 0.00 fields
        self.set_init_000(self.read_text(fsock, Text._format_000, env))

    def set_init_000(self, fieldvalues):
        (self.text,) = fieldvalues

    def get_init_000(self):
        return (self.text,)

    def before_write(self):
        self.text = zeroterm(self.text)

    def get_text(self):
        return self.get_string(self.text)

    @staticmethod
    def write_text(fsock, env, text):
        txblock = Text()
        txblock.text = text
        return txblock.write(fsock, env)

    @staticmethod
    def write_group(fsock, env, groupname):
        return Text.write_text(fsock, env, b"Group:%s," % groupname)

    def get_format_body(self):
        return [(000, [self._format_000(len(self.text))], self.get_init_000)]


class Program(Block):
    """Provides string text containing program specific data."""

    _format_000 = staticmethod(lambda n: STRING(n))
    _default_000 = ("Unknown program specific data",)
    _identifier = 'PR'

    def __init__(self):
        Block.__init__(self)
        self.set_init_000(self._default_000)

    def read_init_body(self, fsock, offset, env):
        # initialize variable length MDF 0.00 fields
        self.set_init_000(self.read_text(fsock, Program._format_000, env))

    def set_init_000(self, fieldvalues):
        (self.program_specific_data,) = fieldvalues

    def get_init_000(self):
        return (self.program_specific_data,)

    def before_write(self):
        self.program_specific_data = zeroterm(self.program_specific_data)

    def get_format_body(self):
        return [(000,
                 [self._format_000(len(self.program_specific_data))],
                 self.get_init_000)]


class DataGroup(Block):
    """Provides information about one or many ChannelGroup:s."""

    _format_000 = [LINK, LINK, LINK, LINK, UINT16, UINT16, UINT32]
    _default_000 = (0, 0, 0, 0, 1, 0, 0)
    _identifier = 'DG'

    def __init__(self):
        Block.__init__(self)
        self.set_init_000(self._default_000)

    def set_init_000(self, fieldvalues):
        (self.next_data_group_block,
         self.first_channel_group_block,
         self.trigger_block,
         self.data_block,
         self.number_of_channel_groups,
         self.number_of_record_ids,
         self.reserved) = fieldvalues

    def get_init_000(self):
        return (self.next_data_group_block,
                self.first_channel_group_block,
                self.trigger_block,
                self.data_block,
                self.number_of_channel_groups,
                self.number_of_record_ids,
                self.reserved)

    @staticmethod
    def write_channel_group(
            fsock, name, data, sampling_rate, next_data_group_block, env):
        dgblock = DataGroup()
        dgblock.next_data_group_block = next_data_group_block

        dgblock.first_channel_group_block = ChannelGroup.write_datacolumns(
            fsock, name, data, sampling_rate, env)
        dgblock.data_block = DataBlock.write_datacolumns(
            fsock, data, next_data_group_block, env)

        return dgblock.write(fsock, env)

    def get_next_data_group_block(self):
        return self.get_link(self.next_data_group_block, DataGroup)

    def get_first_channel_group_block(self):
        return self.get_link(self.first_channel_group_block, ChannelGroup)

    def get_trigger_block(self):
        return self.get_link(self.trigger_block, Trigger)

    def get_data_block(self):
        return self.get_link(self.data_block, lambda: DataBlock(self))

    def get_channel_group_blocks(self):
        return self.get_links(self.get_first_channel_group_block,
                              ChannelGroup.get_next_channel_group_block)


class ChannelGroup(Block):
    """Provides information about one or (usually) many Channel:s."""

    _format_000 = [LINK, LINK, LINK, UINT16, UINT16, UINT16, UINT32]
    _format_330 = [LINK]
    _default_000 = (0, 0, 0, 0, 0, 0, 0)
    _default_330 = (0,)
    _identifier = 'CG'

    def __init__(self):
        Block.__init__(self)
        self.set_init_000(self._default_000)
        self.set_init_330(self._default_330)

    def read_init_after_body(self, fsock, offset, env):
        # initialize MDF 3.30 fields
        self.read_version(fsock, 330, env)

    def set_init_000(self, fieldvalues):
        (self.next_channel_group_block,
         self.first_channel_block,
         self.comment,
         self.record_id,
         self.number_of_channels,
         self.size_of_data_record,
         self.number_of_records) = fieldvalues

    def set_init_330(self, fieldvalues):
        (self.first_sample_reduction_block,) = fieldvalues

    def get_init_000(self):
        return (self.next_channel_group_block,
                self.first_channel_block,
                self.comment,
                self.record_id,
                self.number_of_channels,
                self.size_of_data_record,
                self.number_of_records)

    def get_init_330(self):
        return (self.first_sample_reduction_block,)

    @staticmethod
    def write_datacolumns(
            fsock, name, data, sampling_rate, env):

        cgblock = ChannelGroup()

        bit_offset = 0
        columnoffsets = {}
        datacolumn = None
        number_of_channels = 0

        data_by_bits = sorted(enumerate((required_bits(x[0]), x)
                                        for x in data),
                              key=lambda x: x[1][0], reverse=True)

        for i, (bits, (datacolumn, _, _, _, _)) in data_by_bits:
            number_of_channels += 1
            columnoffsets[i] = bit_offset
            bit_offset += bits

        reverse_lookup = dict(zip(range(number_of_channels),
                                  reversed(range(number_of_channels))))
        prev_cnblock = 0
        # Reverse data ordering.
        data.reverse()
        lastindex = number_of_channels - 1

        for i, (datacolumn, unit, description, conversion,
                signal_name) in enumerate(data):
            if i == lastindex:
                channel_type = Channel.Types.TIMECHANNEL
            else:
                channel_type = Channel.Types.DATACHANNEL

            start_offset_in_bits = columnoffsets[reverse_lookup[i]]
            number_of_bits = required_bits(datacolumn)

            prev_cnblock = Channel.write_datacolumn(
                fsock, signal_name, datacolumn, unit, description,
                sampling_rate, conversion, channel_type, start_offset_in_bits,
                prev_cnblock, env, number_of_bits)

        cgblock.first_channel_block = prev_cnblock
        cgblock.comment = Text.write_group(fsock, env, name)
        cgblock.number_of_channels = number_of_channels

        if number_of_channels > 0:
            cgblock.size_of_data_record = (
                (bit_offset // BYTE_SIZE) +
                (1 if bit_offset % BYTE_SIZE > 0 else 0))
            cgblock.number_of_records = datacolumn.size

        # Restore data ordering.
        data.reverse()
        return cgblock.write(fsock, env)

    def get_next_channel_group_block(self):
        return self.get_link(self.next_channel_group_block, ChannelGroup)

    def get_first_channel_block(self):
        return self.get_link(self.first_channel_block, Channel)

    def get_comment_block(self):
        return self.get_link(self.comment, Text)

    def get_channel_blocks(self):
        return self.get_links(self.get_first_channel_block,
                              Channel.get_next_channel_block)


class Trigger(Block):
    """Provides information about a trigger event."""

    _format_000 = [LINK, UINT16]
    _format_000x = staticmethod(lambda n: n * [REAL, REAL, REAL])
    _default_000 = (0, 0)
    _identifier = 'TR'

    def __init__(self):
        Block.__init__(self)
        self.set_init_000(self._default_000)
        self.trigger_event_times = None

    def read_init_body(self, fsock, offset, env):
        # initialize variable length MDF 0.00 field
        form = Trigger._format_000x(self.number_of_trigger_events)
        self.trigger_event_times = self.read_format(fsock, form, env)

    def set_init_000(self, fieldvalues):
        (self.trigger_comment_text,
         self.number_of_trigger_events) = fieldvalues

    def set_init_000x(self, fieldvalues):
        (self.trigger_event_times,) = fieldvalues

    def get_init_000(self):
        return (self.trigger_comment_text,
                self.number_of_trigger_events)

    def get_init_000x(self):
        return (self.trigger_event_times,)

    def get_format_body(self):
        return [(000,
                 self._format_000x(self.number_of_trigger_events),
                 self.get_init_000x)]

    def get_trigger_comment_text(self):
        return self.get_link(self.trigger_comment_text, Text)


class Channel(Block):
    """Provides information about a channel."""

    _format_000 = [LINK,
                   LINK,
                   LINK,
                   LINK,
                   LINK,
                   UINT16,
                   STRING(32),
                   STRING(128),
                   UINT16,
                   UINT16,
                   UINT16,
                   BOOL,
                   REAL,
                   REAL,
                   REAL]
    _format_212 = [LINK]
    _format_300 = [LINK, UINT16]
    _default_000 = (0, 0, 0, 0, 0, 0,
                    "Unknown Signal Name",
                    "Unknown Signal Description",
                    0, 0, 0, 0, 0.0, 0.0, 0.0)
    _default_212 = (0,)
    _default_300 = (0, 0)
    _identifier = 'CN'

    (START_OFFSET_IN_BITS_MAX,) = (8192 * BYTE_SIZE,)
    (SHORT_SIGNAL_NAME_MAX,) = (31,)
    (SIGNAL_DESCRIPTION_MAX,) = (128,)
    (EMPTY_SIGNAL_NAME,) = ('__MDFLIB_EMPTY_SIGNAL_NAME__',)

    class Types():
        """Provides information about channel type numbers."""

        UINT = {1: UINT1, 8: UINT8, 16: UINT16, 32: UINT32, 64: UINT64}
        SINT = {1: SINT1, 8: SINT8, 16: SINT16, 32: SINT32, 64: SINT64}
        FLOAT = {32: FLOAT32, 64: FLOAT64}
        DOUBLE = {64: FLOAT64}

        STRING = defaultdict(lambda: 's', {})
        BYTEARRAY = defaultdict(lambda: 's', {})

        type_dict = {0: UINT,
                     1: SINT,
                     2: FLOAT,
                     3: DOUBLE,
                     7: STRING,
                     8: BYTEARRAY}

        (DATACHANNEL, TIMECHANNEL) = (0, 1)

    def __init__(self):
        Block.__init__(self)
        self.set_init_000(self._default_000)
        self.set_init_212(self._default_212)
        self.set_init_300(self._default_300)

    def read_init_after_body(self, fsock, offset, env):
        # initialize MDF 212 fields
        self.read_version(fsock, 212, env)
        # initialize MDF 3.00 fields
        self.read_version(fsock, 300, env)

    def set_init_000(self, fieldvalues):
        (self.next_channel_block,
         self.conversion_formula,
         self.source_depending_extensions,
         self.dependency_block,
         self.comment,
         self.channel_type,
         self.short_signal_name,
         self.signal_description,
         self.start_offset_in_bits,
         self.number_of_bits,
         self.signal_data_type,
         self.value_range_valid,
         self.minimum_signal_value,
         self.maximum_signal_value,
         self.sampling_rate) = fieldvalues

    def set_init_212(self, fieldvalues):
        (self.long_signal_name,) = fieldvalues

    def set_init_300(self, fieldvalues):
        (self.display_name,
         self.additional_byte_offset) = fieldvalues

    def get_init_000(self):
        return (self.next_channel_block,
                self.conversion_formula,
                self.source_depending_extensions,
                self.dependency_block,
                self.comment,
                self.channel_type,
                self.short_signal_name,
                self.signal_description,
                self.start_offset_in_bits,
                self.number_of_bits,
                self.signal_data_type,
                self.value_range_valid,
                self.minimum_signal_value,
                self.maximum_signal_value,
                self.sampling_rate)

    def get_init_212(self):
        return (self.long_signal_name,)

    def get_init_300(self):
        return (self.display_name,
                self.additional_byte_offset)

    def before_write(self):
        self.short_signal_name = zeroterm(self.short_signal_name)
        self.signal_description = zeroterm(self.signal_description)

    @staticmethod
    def write_datacolumn(
            fsock, signal_name, datacolumn, unit, description,
            sampling_rate, conversion, channel_type, start_offset_in_bits,
            previous_channel_block, env, number_of_bits):

        ccblock = ChannelConversion.write_datacolumn(
            fsock, datacolumn, unit, conversion, env)
        cnblock = Channel()
        cnblock.conversion_formula = ccblock
        cnblock.next_channel_block = previous_channel_block

        if len(signal_name) > Channel.SHORT_SIGNAL_NAME_MAX:
            cnblock.long_signal_name = Text.write_text(fsock, env, signal_name)

        cnblock.short_signal_name = signal_name[:Channel.SHORT_SIGNAL_NAME_MAX]
        cnblock.signal_description = description[
            :Channel.SIGNAL_DESCRIPTION_MAX]
        cnblock.channel_type = channel_type
        cnblock.number_of_bits = number_of_bits

        if start_offset_in_bits >= Channel.START_OFFSET_IN_BITS_MAX:
            if env[Identification.version] >= 300:
                times = (start_offset_in_bits //
                         Channel.START_OFFSET_IN_BITS_MAX)
                nbytes = (
                    times * Channel.START_OFFSET_IN_BITS_MAX // BYTE_SIZE)
                cnblock.additional_byte_offset = nbytes
                start_offset_in_bits %= Channel.START_OFFSET_IN_BITS_MAX
            else:
                raise VersionError("Bit offset, requires MDF version >= 3.00")

        cnblock.start_offset_in_bits = start_offset_in_bits
        cnblock.signal_data_type = Channel.get_signal_data_type_from_ndtype(
            datacolumn.dtype)

        if channel_type == Channel.Types.TIMECHANNEL:
            cnblock.sampling_rate = sampling_rate
        cnblock.channel_type = channel_type

        return cnblock.write(fsock, env)

    def get_format_after_body(self):
        return [(212, self._format_212, self.get_init_212),
                (300, self._format_300, self.get_init_300)]

    def _get_signal_type_index(self, env):
        endianness = env[Identification.endianness]

        if self.signal_data_type < 9:
            type_index = self.signal_data_type

        elif self.signal_data_type < 17:
            if self.signal_data_type < 13:
                type_index = self.signal_data_type - 9
                endianness = BIG_ENDIAN
            else:
                type_index = self.signal_data_type - 13
                endianness = LITTLE_ENDIAN
        else:
            raise Exception('Unknown signal data type:%s' %
                            self.signal_data_type)
        return (endianness, type_index)

    def get_signal_data_type(self, env, number_of_bits=None):
        endianness, type_index = self._get_signal_type_index(env)

        dtype = Channel.Types.type_dict[type_index]
        if number_of_bits is None:
            number_of_bits = self.number_of_bits

        if type_index in [0, 1]:
            if number_of_bits > 8:
                number_of_bits = int(2 ** ceil(log(number_of_bits, 2)))
            elif number_of_bits > 1:
                number_of_bits = 8
        return (endianness, dtype[number_of_bits])

    def get_signal_is_integral(self):
        fakeenv = {Identification.endianness: '<'}
        endianness, type_index = self._get_signal_type_index(fakeenv)
        return type_index in [0, 1]

    def get_signal_read_data_type(self, env):
        right_shift_amount = self.start_offset_in_bits % BYTE_SIZE
        signal_bytes = int(ceil((self.number_of_bits +
                                 right_shift_amount) / 8.0))
        number_of_bits = self.number_of_bits

        if number_of_bits != 1:
            number_of_bits = signal_bytes * 8

        return self.get_signal_data_type(env, number_of_bits)

    @staticmethod
    def get_signal_data_type_from_ndtype(ndtype):
        kind_dict = {'b': (lambda n: 0),
                     'u': (lambda n: 0),
                     'i': (lambda n: 1),
                     'f': (lambda n: 1 + n // 4),
                     'S': (lambda n: 7)}

        return kind_dict[ndtype.kind](ndtype.itemsize)

    def get_next_channel_block(self):
        return self.get_link(self.next_channel_block, Channel)

    def get_conversion_formula(self):
        return self.get_link(self.conversion_formula, ChannelConversion)

    def get_source_depending_extensions(self):
        raise NotImplementedError

    def get_dependency_block(self):
        raise NotImplementedError

    def get_comment(self):
        return self.get_link(self.comment, Text)

    def get_channel_type(self):
        return self.channel_type

    def get_signal_description(self):
        return self.get_string(self.signal_description)

    def get_short_signal_name(self):
        return self.get_string(self.short_signal_name)

    def get_signal_name(self):
        txblock = self.get_long_signal_name()

        if txblock is not None:
            return self.get_string(txblock.text)

        return self.get_short_signal_name()

    def get_sampling_rate(self):
        return self.sampling_rate

    def get_long_signal_name(self):
        return self.get_link(self.long_signal_name, Text)

    def get_display_name(self):
        return self.get_link(self.display_name, Text)

    def get_converted_signal(self, array):
        return self.get_conversion_formula().get_converted_signal(array)

    @staticmethod
    def startbit(cnblock):
        """
        Get the start bit of a cnblock, considering additional byte offset.
        This is useful for sorting channels in memory order.
        """
        return (cnblock.additional_byte_offset * BYTE_SIZE +
                cnblock.start_offset_in_bits)


class ChannelConversion(Block):
    """Provides information about how to process Channel."""

    class Types():
        """Channel conversion types. Provides functions for processing
        signals.
        """

        (PARAMETRIC_LINEAR,
         TABULAR_INTERPOLATION,
         POLYNOMIAL_FUNCTION,
         EXPONENTAL_FUNCTION,
         RATIONAL_CONVERSION_FORMULA_FUNCTION,
         ASAM_MCD2_TABLE,
         ONE_TO_ONE) = (0, 1, 6, 7, 9, 11, 65535)

        def _get_parametric_linear(self,
                                   additional_conversion_data,
                                   array):
            (p1, p2) = additional_conversion_data
            if p1 == 0 and p2 == 1.0:
                return array

            return multiply(array, p2) + p1

        def _get_tabular_interpolation(
                self,
                additional_conversion_data,
                array):
            int_values = additional_conversion_data[::2]
            ind_min = 0
            ind_max = len(int_values) - 1

            phy_values = additional_conversion_data[1::2]
            phy_min = phy_values[0]
            phy_max = phy_values[-1]

            result = []

            for index, value in ((bisect(int_values, value) - 1, value)
                                 for value in array):
                if index < ind_min:
                    result.append(phy_min)
                elif value == ind_max:
                    result.append(phy_max)
                else:
                    fraction = ((value - int_values[index]) /
                                (int_values[index + 1] - int_values[index]))
                    result.append((phy_values[index + 1] - phy_values[index]) *
                                  fraction + phy_values[index])
            return np.array(result)

        def _get_polynomial_function(self,
                                     additional_conversion_data,
                                     array):
            p = list(additional_conversion_data)

            lendiff = 6 - len(p)
            if lendiff > 0:
                p.extend([0] * lendiff)

            p1 = p[0]
            p2 = p[1]
            p3 = p[2]
            p4 = p[3]
            p5 = p[4]
            p6 = 0  # Not using 2s complement representation

            numer = p2 - (p4 * (array - (p5 + p6)))
            denom = p3 * (array - (p5 + p6)) - p1

            return numer / denom

        def _get_exponental_function(self,
                                     additional_conversion_data,
                                     array):
            (p1, p2, p3, p4, p5, p6, p7) = list(additional_conversion_data)

            if p4 is 0:
                return ln(((array - p7) * p6 - p3) / p1) / p2
            elif p1 is 0:
                return ln((p3 / (array - p7) - p6) / p4) / p5

        def _get_rational_conversion_formula_function(
                self,
                additional_conversion_data,
                array):
            (p1, p2, p3, p4, p5, p6) = list(additional_conversion_data)

            array2 = square(array)
            return ((p1 * array2 + p2 * array + p3) /
                    (p4 * array2 + p5 * array + p6))

        def _get_asam_mcd2_text_table(self, additional_conversion_data, array):
            table = additional_conversion_data
            return (array, {
                'conversion': {
                    'conversion_type': 'lookup_dict',
                    'lookup_dict': list(zip(
                        np.array(table[::2], dtype=int),
                        np.array(table[1::2])))}})

        def _get_one_to_one(self, additional_conversion_data, array):
            return array

        _conversiondict = {PARAMETRIC_LINEAR: _get_parametric_linear,
                           TABULAR_INTERPOLATION: _get_tabular_interpolation,
                           POLYNOMIAL_FUNCTION: _get_polynomial_function,
                           EXPONENTAL_FUNCTION: _get_exponental_function,
                           RATIONAL_CONVERSION_FORMULA_FUNCTION:
                           _get_rational_conversion_formula_function,
                           ASAM_MCD2_TABLE: _get_asam_mcd2_text_table,
                           ONE_TO_ONE: _get_one_to_one}

        def get_conversion(self, conversion_type):
            return self._conversiondict[conversion_type]

    _format_000 = [BOOL, REAL, REAL, STRING(20), UINT16, UINT16]
    _format_000x = {Types.PARAMETRIC_LINEAR: [REAL],
                    Types.TABULAR_INTERPOLATION: [REAL],
                    Types.POLYNOMIAL_FUNCTION: [REAL],
                    Types.EXPONENTAL_FUNCTION: [REAL],
                    Types.RATIONAL_CONVERSION_FORMULA_FUNCTION: [REAL],
                    Types.ASAM_MCD2_TABLE: [REAL, STRING(32)],
                    Types.ONE_TO_ONE: [NULL]}
    _default_000 = (0, 0.0, 0.0, 'Unknown Unit', Types.ONE_TO_ONE, 0)
    _default_000x = (None,)

    _identifier = 'CC'

    def __init__(self):
        Block.__init__(self)
        self.set_init_000(self._default_000)
        self.set_init_000x(self._default_000x)

    def read_init_after_body(self, fsock, offset, env):
        # initialize variable length MDF 0.00 field
        fieldvalues = self.read_format(fsock,
                                       self.get_format_after_body()[0][1],
                                       env)
        self.set_init_000x(fieldvalues)

    def set_init_000(self, fieldvalues):
        (self.physical_value_range_valid,
         self.minimum_physical_signal_value,
         self.maximum_physical_signal_value,
         self.physical_unit,
         self.conversion_type,
         self.size_information) = fieldvalues

    def set_init_000x(self, fieldvalues):
        (self.additional_conversion_data) = fieldvalues

    def get_init_000(self):
        return (self.physical_value_range_valid,
                self.minimum_physical_signal_value,
                self.maximum_physical_signal_value,
                self.physical_unit,
                self.conversion_type,
                self.size_information)

    def get_init_000x(self):
        return (self.additional_conversion_data)

    def before_write(self):
        self.physical_unit = zeroterm(self.physical_unit)

    @staticmethod
    def write_datacolumn(fsock, datacolumn, unit, conversion, env):
        ccblock = ChannelConversion()
        if conversion:
            if conversion['conversion_type'] == 'lookup_dict':
                data = conversion.get('lookup_dict')
                if data:
                    ccblock.size_information = len(data)
                    ccblock.conversion_type = (
                        ChannelConversion.Types.ASAM_MCD2_TABLE)
                    ccblock.set_init_000x(
                        flatten(
                            [[float(k), zeroterm(v)] for k, v in data]))

        ccblock.physical_unit = unit
        return ccblock.write(fsock, env)

    def get_format_after_body(self):
        return [(000,
                 (ChannelConversion._format_000x[self.conversion_type] *
                  self.size_information),
                 self.get_init_000x)]

    def get_physical_unit(self):
        return self.get_string(self.physical_unit)

    def get_converted_signal(self, array):
        conv = ChannelConversion.Types()
        method = conv.get_conversion(self.conversion_type)
        result = method(conv, self.additional_conversion_data, array)
        if not isinstance(result, tuple):
            return (result, None)
        return result


class MdfFile():
    """Provides convenient access to top level MDF blocks."""

    allow_partial = 'allow_partial'

    def __init__(self, file_object, mode='rb',
                 byte_order=LITTLE_ENDIAN, version=300,
                 allow_partial=False):

        self.env = {Identification.endianness: byte_order,
                    Identification.version: version,
                    self.allow_partial: allow_partial}

        if mode in ['rb', 'w+b']:
            if isinstance(file_object, six.string_types):
                self._fsock = open(file_object, mode)
                self._close = True
            else:
                self._fsock = file_object
                self._close = False

            if mode == 'rb':
                self.read_init()

            elif mode == 'w+b':
                self.default_init()

    def read_init(self):
        self.idblock = self.read_identification()
        self.hdblock = self.read_header()

    def read_identification(self):
        idblock = Identification(self.env)
        idblock.read_init(self._fsock, Identification.offset, self.env)
        return idblock

    def read_header(self):
        hdblock = Header()
        hdblock.read_init(self._fsock,
                          Identification.size_max,
                          self.idblock.env)
        return hdblock

    def default_init(self):
        self.idblock = self.default_identification()
        self.hdblock = self.default_header()
        self._fsock.seek(self.idblock.get_size(self.env) +
                         self.hdblock.get_size(self.env))

    def default_identification(self):
        idblock = Identification(self.env)
        return idblock

    def default_header(self):
        hdblock = Header()
        now = datetime.datetime.now(pytz.utc)
        epoch = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)
        hdblock.date = now.strftime('%d:%m:%Y')
        hdblock.time = now.strftime('%H:%M:%S')
        # Only used in format 3.2 and later.
        hdblock.time_stamp = int((now - epoch).total_seconds() * 10 ** 9)
        return hdblock

    def write(self):
        self._fsock.seek(Identification.offset)
        self.idblock.write(self._fsock, self.idblock.env)
        self.hdblock.write(self._fsock, self.idblock.env)

    def write_channel_groups(self, channel_groups):
        """
        channel_groups is an iterable over (name, channel_group_data,
        sampling_rate) and channel_group_data is also an iterator, over
        (data, unit, name) with a reverse method.
        """
        number_of_data_groups = 0
        prev_dgblock = 0
        env = self.idblock.env

        for channel_group in channel_groups:
            name, channel_group_data, sampling_rate = channel_group
            prev_dgblock = DataGroup.write_channel_group(
                self._fsock, name, channel_group_data, sampling_rate,
                prev_dgblock, env)
            number_of_data_groups += 1

        return (prev_dgblock, number_of_data_groups)

    def write_text(self, text):
        return Text.write_text(self._fsock, self.idblock.env, text)

    def printall(self):
        self.idblock.show()
        self.hdblock.show()

        for dgblock in self.hdblock.get_data_group_blocks():
            dgblock.show()
            dgblock.get_data_block()

            for cgblock in dgblock.get_channel_group_blocks():
                cgblock.show()

                for cnblock in cgblock.get_channel_blocks():
                    cnblock.show()

    def close(self):
        if self._close:
            self._fsock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.close()


def is_mdf(filename):
    """Returns True if filename refers to a MDF file and False otherwise."""
    try:
        idblock = MdfFile(filename).idblock
        return (idblock.file_identifier == b'MDF     ' and
                idblock.version_number < 400)
    except Exception:
        return False


def main():
    mdffile = 'mdf.dat'

    with MdfFile(mdffile) as mdf:
        mdf.printall()


if __name__ == '__main__':
    main()
