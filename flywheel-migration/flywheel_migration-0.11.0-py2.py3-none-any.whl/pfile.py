"""P-File"""

import re
import struct
import logging
import datetime
import six

from . import util

log = logging.getLogger(__name__)

FILETYPE = 'pfile'
EFILE_RE = re.compile(r'E\d{5}S\d{3}P\d{5}\.7$')
PFILE_RE = re.compile(r'(?P<aux>P\d{5})\.7$')
HDR_RE = re.compile(r'(?P<aux>P\d{5})\.7\.hdr$')


class EFile:

    """EFile class"""

    # pylint: disable=too-few-public-methods

    DEID_RE = re.compile(r'(patient (id|name) =).*')

    def __init__(self, filepath, de_identify=False):
        if de_identify:
            lines = open(filepath).readlines()
            with open(filepath, 'w') as f:
                for line in lines:
                    f.write(EFile.DEID_RE.sub(r'\1', line))


class PFile:

    """PFile class"""

    # pylint: disable=too-few-public-methods

    def __init__(self, filepath, map_key=None, opt_key=None, timezone=None, de_identify=False):
        self.raw = pf = _RawPFile(filepath)
        self.opt = pf.accession_no if opt_key == 'AccessionNumber' else None
        sort_info = pf.patient_id if map_key == 'PatientID' else ''

        self.session_uid = pf.exam_uid
        self.series_uid = pf.series_uid
        self.acquisition_uid = pf.series_uid + '_' + str(pf.acq_no)
        self.acquisition_timestamp = util.localize_timestamp(pf.timestamp, timezone)
        self.acquisition_label = pf.series_desc
        self.subject_code, self.group__id, self.project_label = util.parse_sort_info(sort_info, 'ex' + str(pf.exam_no))
        self.file_type = FILETYPE

        if de_identify:
            pf.de_identify()


class _RawPFileError(Exception):
    pass


class _RawPFile:

    """_RawPFile class"""

    # pylint: disable=too-few-public-methods

    VERSION_ATTR_OFFSETS = {
        (b'\x0c\x02\xd8A',): {  # v27.001
            'logo': (110, '10s', True),
            'scan_date': (92, '10s'),
            'scan_time': (102, '8s'),
            'exam_no': (202548, 'H'),
            'exam_uid': (203280, '32s'),
            'patient_name': (203376, '65s', True),
            'patient_id': (203441, '65s', True),
            'patient_dob': (203523, '9s', True),
            'accession_no': (203506, '17s', True),
            'series_no': (204548, 'h'),
            'series_desc': (204794, '65s', True),
            'series_uid': (204957, '32s'),
            'prescribed_duration': (206684, 'f'),
            'im_datetime': (207420, 'i'),
            'acq_no': (207866, 'h'),
            'psd_name': (208004, '33s', True),
        },
        (b'\x19\x04\xd0A', b'\x00\x00\xd8A'): {  # v26, v27
            'logo': (110, '10s', True),
            'scan_date': (92, '10s'),
            'scan_time': (102, '8s'),
            'exam_no': (194356, 'H'),
            'exam_uid': (195088, '32s'),
            'patient_name': (195184, '65s', True),
            'patient_id': (195249, '65s', True),
            'patient_dob': (195331, '9s', True),
            'accession_no': (195314, '17s', True),
            'series_no': (196356, 'h'),
            'series_desc': (196602, '65s', True),
            'series_uid': (196765, '32s'),
            'prescribed_duration': (198492, 'f'),
            'im_datetime': (199228, 'i'),
            'acq_no': (199674, 'h'),
            'psd_name': (199812, '33s', True),
        },
        (b'\x00\x00\xc0A', b'V\x0e\xa0A'): {  # v23, v24, v25
            'logo': (34, '10s', True),
            'scan_date': (16, '10s'),
            'scan_time': (26, '8s'),
            'exam_no': (143516, 'H'),
            'exam_uid': (144248, '32s'),
            'patient_name': (144344, '65s', True),
            'patient_id': (144409, '65s', True),
            'patient_dob': (144491, '9s', True),
            'accession_no': (144474, '17s', True),
            'series_no': (145622, 'h'),
            'series_desc': (145762, '65s', True),
            'series_uid': (145875, '32s'),
            'prescribed_duration': (147652, 'f'),
            'im_datetime': (148388, 'i'),
            'acq_no': (148834, 'h'),
            'psd_name': (148972, '33s', True),
        },
        (b'J\x0c\xa0A',): {  # v22
            'logo': (34, '10s', True),
            'scan_date': (16, '10s'),
            'scan_time': (26, '8s'),
            'exam_no': (143516, 'H'),
            'exam_uid': (144240, '32s'),
            'patient_name': (144336, '65s', True),
            'patient_id': (144401, '65s', True),
            'patient_dob': (144483, '9s', True),
            'accession_no': (144466, '17s', True),
            'series_no': (145622, 'h'),
            'series_desc': (145762, '65s', True),
            'series_uid': (145875, '32s'),
            'prescribed_duration': (147652, 'f'),
            'im_datetime': (148388, 'i'),
            'acq_no': (148834, 'h'),
            'psd_name': (148972, '33s', True),
        },
        (b'\x00\x000A',): {  # v12
            'logo': (34, '10s', True),
            'scan_date': (16, '10s'),
            'scan_time': (26, '8s'),
            'exam_no': (61576, 'H'),
            'exam_uid': (61966, '32s'),
            'patient_name': (62062, '65s', True),
            'patient_id': (62127, '65s', True),
            'patient_dob': (62209, '9s', True),
            'accession_no': (62192, '17s', True),
            'series_no': (62710, 'h'),
            'series_desc': (62786, '65s', True),
            'series_uid': (62899, '32s'),
            'prescribed_duration': (64544, 'f'),
            'im_datetime': (65016, 'i'),
            'acq_no': (65328, 'h'),
            'psd_name': (65374, '33s', True),
        },
    }

    def __init__(self, filepath, encoding='ascii'):
        self.filepath = filepath
        self.encoding = encoding
        self.attrs, self.offsets = self.parse(filepath)
        attrs = self.attrs
        if attrs['im_datetime'] > 0:
            self.timestamp = datetime.datetime.utcfromtimestamp(attrs['im_datetime'])
        else:
            month, day, year = [int(i) for i in attrs['scan_date'].split(b'\0', 1)[0].split(b'/')]
            hour, minute = [int(i) for i in attrs['scan_time'].split(b'\0', 1)[0].split(b':')]
            self.timestamp = datetime.datetime(year + 1900, month, day, hour, minute)  # GE's epoch begins in 1900

    def __getattr__(self, name):
        if name in self.attrs:
            return self.decode(self.attrs[name], self.encoding)
        raise AttributeError

    def de_identify(self):
        """Set PHI field values to empty string on disk and memory"""
        with open(self.filepath, 'r+b') as fd:
            for attr in ('patient_name', 'patient_id', 'patient_dob'):
                offset, fmt = self.offsets[attr][:2]
                fd.seek(offset)
                fd.write(struct.pack(fmt, b'\0'))
                if hasattr(self, attr):
                    setattr(self, attr, '')

    @classmethod
    def parse(cls, filepath):
        """Return parsed attribute values and their offsets for the specific version"""
        attrs = {}
        offsets = {}
        with open(filepath, 'rb') as fd:
            version_bytes = fd.read(4)
            for versions, offsets in cls.VERSION_ATTR_OFFSETS.items():
                if version_bytes in versions:
                    logo = cls.unpacked_bytes(fd, *offsets['logo'])
                    if logo not in (b'GE_MED_NMR', b'INVALIDNMR'):
                        raise _RawPFileError(fd.name + ' is not a valid PFile')
                    break
            else:
                raise _RawPFileError(fd.name + ' is not a valid PFile or of an unsupported version')

            for attr, offset in offsets.items():
                value = cls.unpacked_bytes(fd, *offset)
                if attr.endswith('_uid'):
                    value = cls.unpack_uid(value)
                attrs[attr] = value
        return attrs, offsets

    @staticmethod
    def unpacked_bytes(fd, offset, fmt, split=False):
        # pylint: disable=missing-docstring
        fd.seek(offset)
        r = struct.unpack(fmt, fd.read(struct.calcsize(fmt)))[0]
        if split:
            r = r.split(b'\0', 1)[0]
        return r

    @staticmethod
    def unpack_uid(uid):
        # pylint: disable=missing-docstring
        if six.PY2:
            uid = [ord(c) for c in uid]
        return ''.join([str(i - 1) if i < 11 else '.' for pair in [(c >> 4, c & 15) for c in uid] for i in pair if i > 0])

    @staticmethod
    def decode(val, encoding):
        """Decode a bytes value using encoding, otherwise return the original value"""
        if isinstance(val, six.binary_type):
            return val.decode(encoding)
        return val
