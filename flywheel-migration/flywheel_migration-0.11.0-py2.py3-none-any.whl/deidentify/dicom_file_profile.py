"""File profile for de-identifying dicom files"""
import collections
import datetime
import gzip
import logging
import os
import re

import pydicom
import pydicom.datadict
import pydicom.tag
import six

from ..util import date_delta
from .file_profile import FileProfile

log = logging.getLogger(__name__)

DICOM_TAG_HEX_RE = re.compile(r'^(0x)?[0-9a-fA-F]{8}$')
DICOM_TAG_TUPLE_RE = re.compile(r'\(\s*([0-9a-fA-F]{4})\s*,\s*([0-9a-fA-F]{4})\s*\)')


class DicomTagStr(str):
    """Subclass of string that has a _dicom_tag attribute"""
    def __new__(cls, value, *_args, **_kwargs):
        return super(DicomTagStr, cls).__new__(cls, value)

    def __init__(self, _value, tag=None):
        super(DicomTagStr, self).__init__()
        self._dicom_tag = tag


def parse_tag(name):
    """Parse the given string to determine if it's a property or tag.

    Params:
        name (str|int): The field name or tag value

    Returns:
        tuple: True, Tag if this is a tag, otherwise False, s
    """
    if isinstance(name, int):
        tag = pydicom.tag.Tag(name)
        return DicomTagStr(str(tag), tag)

    name = name.strip()
    match = DICOM_TAG_HEX_RE.match(name)
    if match:
        tag = pydicom.tag.Tag(int(name, 16))
        return DicomTagStr(name, tag)

    match = DICOM_TAG_TUPLE_RE.match(name)
    if match:
        tag = pydicom.tag.Tag(int(match.group(1) + match.group(2), 16))
        return DicomTagStr(name, tag)

    return DicomTagStr(name)


class DicomFileProfile(FileProfile):
    """Dicom implementation of load/save and remove/replace fields"""

    name = 'dicom'
    hash_digits = 16  # How many digits are supported for 'hash' action
    log_fields = ['StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID']

    def __init__(self):
        super(DicomFileProfile, self).__init__(packfile_type='dicom')

        self.patient_age_from_birthdate = False
        self.patient_age_units = None

        self.remove_private_tags = False

    def add_field(self, field):
        # Handle tag conversion for later
        field.fieldname = parse_tag(field.fieldname)
        super(DicomFileProfile, self).add_field(field)

    def create_file_state(self):
        """Create state object for processing files"""
        return {
            'series_uid': None,
            'session_uid': None,
            'sop_uids': set()
        }

    def get_dest_path(self, state, record, path):
        # Destination path is sop_uid.modality.dcm
        sop_uid = self.get_value(state, record, 'SOPInstanceUID')
        if not sop_uid:
            return path
        modality = self.get_value(state, record, 'Modality') or 'NA'
        return u'{}.{}.dcm'.format(sop_uid, modality)

    def to_config(self):
        result = super(DicomFileProfile, self).to_config()

        result['patient-age-from-birthdate'] = self.patient_age_from_birthdate
        if self.patient_age_units:
            result['patient-age-units'] = self.patient_age_units

        result['remove-private-tags'] = self.remove_private_tags

        return result

    def load_config(self, config):
        super(DicomFileProfile, self).load_config(config)

        self.patient_age_from_birthdate = config.get('patient-age-from-birthdate', False)
        self.patient_age_units = config.get('patient-age-units')
        self.remove_private_tags = config.get('remove-private-tags', False)

    def load_record(self, state, src_fs, path):
        modified = False
        try:
            with src_fs.open(path, 'rb') as f:
                # Extract gzipped dicoms
                _, ext = os.path.splitext(path)
                if ext.lower() == '.gz':
                    f = gzip.GzipFile(fileobj=f)

                # Read and decode the dicom
                dcm = pydicom.dcmread(f)

                # Remove private tags before decoding
                if self.remove_private_tags:
                    dcm.remove_private_tags()
                    modified = True

                dcm.decode()
        except (pydicom.errors.InvalidDicomError, ValueError):
            log.warning('IGNORING %s - it is not a DICOM file!', path)
            return None, False

        # Validate the series/session
        series_uid = dcm.get('SeriesInstanceUID')
        session_uid = dcm.get('StudyInstanceUID')

        if state['series_uid'] is not None:
            # Validate SeriesInstanceUID
            if series_uid != state['series_uid']:
                log.warning('DICOM %s has a different SeriesInstanceUID (%s) from the rest of the series: %s', path, series_uid, state['series_uid'])
            # Validate StudyInstanceUID
            elif session_uid != state['session_uid']:
                log.warning('DICOM %s has a different StudyInstanceUID (%s) from the rest of the series: %s', path, session_uid, state['session_uid'])
        else:
            state['series_uid'] = series_uid
            state['session_uid'] = session_uid

        # Validate SOPInstanceUID
        sop_uid = dcm.get('SOPInstanceUID')
        if sop_uid:
            if sop_uid in state['sop_uids']:
                log.error('DICOM %s re-uses SOPInstanceUID %s, and will be excluded!', path, sop_uid)
                return None, False
            state['sop_uids'].add(sop_uid)

        # Set patient age from date of birth, if specified
        if self.patient_age_from_birthdate:
            dob = dcm.get('PatientBirthDate')
            study_date = dcm.get('StudyDate')

            if dob and study_date:
                try:
                    study_date = datetime.datetime.strptime(study_date, self.date_format)
                    dob = datetime.datetime.strptime(dob, self.date_format)

                    # Max value from dcm.py:84
                    age, units = date_delta(dob, study_date, desired_unit=self.patient_age_units, max_value=960)
                    dcm.PatientAge = '%03d%s' % (age, units)
                    modified = True
                except ValueError as err:
                    log.debug('Unable to update patient age in file %s: %s', path, err)

        return dcm, modified

    def save_record(self, state, record, dst_fs, path):
        with dst_fs.open(path, 'wb') as f:
            record.save_as(f)

    def read_field(self, state, record, fieldname):
        # Ensure that value is a string
        dcm_tag = getattr(fieldname, '_dicom_tag', None)
        if dcm_tag:
            value = record.get(dcm_tag)
        else:
            value = getattr(record, fieldname, None)

        if value is not None and not isinstance(value, six.string_types):
            if isinstance(value, collections.Sequence):
                value = ','.join([str(x) for x in value])
            else:  # Unknown value, just convert to string
                value = str(value)
        return value

    def remove_field(self, state, record, fieldname):
        dcm_tag = getattr(fieldname, '_dicom_tag', None)
        if dcm_tag:
            if dcm_tag in record:
                del record[dcm_tag]
        else:
            if hasattr(record, fieldname):
                delattr(record, fieldname)

    def replace_field(self, state, record, fieldname, value):
        dcm_tag = getattr(fieldname, '_dicom_tag', None)
        if dcm_tag:
            record[dcm_tag].value = value
        else:
            setattr(record, fieldname, value)
