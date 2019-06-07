import os
import shutil
from glob import glob
from egcg_core.exceptions import EGCGError
from egcg_core.app_logging import logging_default as log_cfg

app_logger = log_cfg.get_logger(__name__)


def check_if_nested(data):
    """Check whether a data structure contains lists/dicts."""
    if isinstance(data, dict):
        for k in data:
            if isinstance(data[k], (list, dict)):
                return True
    elif isinstance(data, list):
        for i in data:
            if isinstance(i, (list, dict)):
                return True
    return False


def find_files(*path_parts):
    return sorted(glob(os.path.join(*path_parts)))


def find_file(*path_parts):
    files = find_files(*path_parts)
    nfiles = len(files)
    if nfiles > 1:
        app_logger.warning('Searched pattern %s for one file, but got %s', path_parts, nfiles)
    elif nfiles == 1:
        return files[0]


def str_join(*parts, separator=''):
    return separator.join(parts)


def find_fastqs(location, project_id, sample_id, lane=None):
    """
    Find all .fastq.gz files in an input folder 'location/project_id'.
    :param location: Top-level directory
    :param str project_id: Project subdirectory to search
    :param str sample_id: Sample subdirectory to search
    :param lane: Specific lane to search for (optional)
    """
    basename = '*.fastq.gz'
    if lane:
        basename = '*L00' + str(lane) + basename

    pattern = os.path.join(location, project_id, sample_id, basename)
    fastqs = find_files(pattern)
    app_logger.debug('Found %s fastq files for %s', len(fastqs), pattern)
    return fastqs


def find_all_fastqs(location):
    """Find fastqs in an input folder, regardless of directory structure."""
    fastqs = []
    for name, dirs, files in os.walk(location):
        fastqs.extend(os.path.join(name, f) for f in files if f.endswith('.fastq.gz'))
    app_logger.debug('Found %s fastqs in %s', len(fastqs), location)
    return fastqs


def find_all_fastq_pairs(location):
    """
    Return the results of find_all_fastqs as a list of fastq pair tuples. Assumes that fastq pairs come
    together from sorting by name.
    :param str location: Directory to search
    :return: Full paths to all fastq.gz files in the input dir, aggregated per pair
    :rtype: list[tuple[str, str]]
    """
    fastqs = find_all_fastqs(location)
    if len(fastqs) % 2 != 0:
        raise EGCGError('Expected even number of fastq files in %s, found %s' % (location, len(fastqs)))
    fastqs.sort()
    return list(zip(*[iter(fastqs)] * 2))


def same_fs(file1, file2):
    if not file1 or not file2:
        return False
    if not os.path.exists(file1):
        return same_fs(os.path.dirname(file1), file2)
    if not os.path.exists(file2):
        return same_fs(file1, os.path.dirname(file2))

    dev1 = os.stat(file1).st_dev
    dev2 = os.stat(file2).st_dev
    return dev1 == dev2


def move_dir(src_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    for f in os.listdir(src_dir):
        src_file = os.path.join(src_dir, f)
        if os.path.isdir(src_file):
            move_dir(src_file, os.path.join(dest_dir, f))
        else:
            fp = os.path.realpath(src_file)
            dest_file = os.path.join(dest_dir, os.path.basename(src_file))
            shutil.move(fp, dest_file)
    return 0


def query_dict(data, query_string, ret_default=None):
    """
    Drill down into a dict using dot notation, e.g. query_dict({'this': {'that': 'other'}}, 'this.that'}).
    :param dict data:
    :param str query_string:
    :param ret_default:
    """
    _data = data.copy()

    for q in query_string.split('.'):
        d = _data.get(q)
        if d is not None:
            _data = d
        else:
            return ret_default

    return _data
