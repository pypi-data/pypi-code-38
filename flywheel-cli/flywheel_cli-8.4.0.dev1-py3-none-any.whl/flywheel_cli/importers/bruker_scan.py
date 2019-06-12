from datetime import datetime
import fs.path
import logging
import re

from .folder import FolderImporter
from .template import parse_template_string, StringMatchNode
from ..bruker import extract_bruker_metadata_fn

log = logging.getLogger(__name__)

def format_timestamp_fn(dst_key):
    """Create a function to format a unix epoch string to iso8601 format.

    Arguments:
        dst_key (str): The destination key name

    Returns:
        function: The function that will format a datetime
    """
    def format(val, **kwargs):
        # Could be a tuple, e.g.: (352523325, 323, 43)
        if val and val[0] == '(':
            parts = val.strip('()').split(',')
            val = parts[0].strip()

        # Convert first part from seconds UTC
        try:
            val = datetime.utcfromtimestamp(int(val))
            return dst_key, val.isoformat() + 'Z'
        except ValueError:
            return None
    return format


def acquisition_label(value, path=None, **kwargs):
    """Convert acquisition label to '<folder> - <label>'"""
    acq_dir = fs.path.dirname(path)
    acq_folder = fs.path.basename(acq_dir)
    return 'acquisition.label', '{} - {}'.format(acq_folder, value)


SUBJECT_PARAMS = {
    'SUBJECT_id': 'subject.label',
    'SUBJECT_study_name': 'session.label',
    'SUBJECT_abs_date': format_timestamp_fn('session.timestamp')
}

ACQP_PARAMS = {
    'ACQ_protocol_name': acquisition_label,
    'ACQ_abs_time': format_timestamp_fn('acquisition.timestamp')
}


def create_bruker_scanner(group, project, follow_symlinks, config, folder_template=None):
    """Create a bruker importer instance

    Arguments:
        group (str): The group id
        project (str): The project label
        config: (Config): The config object
        folder_template: (str): The subject folder template pattern

    Returns:
        FolderImporter: The configured folder importer instance
    """
    # Build the importer instance
    importer = FolderImporter(group=group, project=project, config=config)

    # Parse a template string for the subject node
    if folder_template is None:
        folder_template = '.*'

    subject_node = parse_template_string(folder_template)
    subject_node.metadata_fn = extract_bruker_metadata_fn('subject', SUBJECT_PARAMS)
    importer.add_template_node(subject_node)

    acq_metadata_fn = extract_bruker_metadata_fn('acqp', ACQP_PARAMS)
    importer.add_composite_template_node([
        StringMatchNode(re.compile('AdjResult'), packfile_type='zip', packfile_name='AdjResult.zip'),
        StringMatchNode('acquisition', packfile_type='pv5', metadata_fn=acq_metadata_fn)
    ])

    return importer

