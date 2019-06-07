import os
import re
import subprocess
from time import sleep
from egcg_core.app_logging import logging_default as log_cfg
from egcg_core.exceptions import ArchivingError

app_logger = log_cfg.get_logger(__name__)
state_re = re.compile('^(.+): \((0x\w+)\)(.+)?')


def _get_stdout(cmd):
    p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_status = p.wait()
    o, e = p.stdout.read(), p.stderr.read()
    msg = '%s -> (%s, %s, %s)' % (cmd, exit_status, o, e)
    if exit_status:
        app_logger.error(msg)
        return None
    else:
        app_logger.debug(msg)
        return o.decode('utf-8').strip()


def archive_states(file_path):
    val = _get_stdout('lfs hsm_state ' + file_path)
    match = state_re.match(val)
    if match:
        file_name = match.group(1)
        assert file_name == file_path
        state_and_id = match.group(3)
        if state_and_id:
            state, archive_id = state_and_id.split(',')
            states = state.strip().split()
            return states
        else:
            return []
    else:
        raise ArchivingError('Could not hsm_state file %s' % file_path)


def is_of_state(state, file_path, known_states=None):
    states = known_states or archive_states(file_path)
    return state in states


def is_registered_for_archiving(file_path, known_states=None):
    return is_of_state('exists', file_path, known_states)


def is_archived(file_path, known_states=None):
    return is_of_state('archived', file_path, known_states)


def is_released(file_path, known_states=None):
    return is_of_state('released', file_path, known_states)


def is_dirty(file_path, known_states=None):
    return is_of_state('dirty', file_path, known_states)


def release_file_from_lustre(file_path):
    states = archive_states(file_path)  # store the states to avoid querying multiple times
    if is_dirty(file_path, states):
        raise ArchivingError('File %s is in a dirty state' % file_path)
    if not is_archived(file_path, states):
        raise ArchivingError('Cannot release %s from Lustre because it is not archived to tape' % file_path)

    if not is_released(file_path, states):
        val = _get_stdout('lfs hsm_release ' + file_path)
        if val is not None:
            return is_released(file_path)
    else:
        app_logger.debug('Trying to release a %s already released from Lustre', file_path)
        return True


def register_for_archiving(file_path, strict=False):
    if is_registered_for_archiving(file_path):
        return True

    val = _get_stdout('lfs hsm_archive ' + file_path)
    if val is None or not is_registered_for_archiving(file_path):
        if strict:
            raise ArchivingError('Registering %s for archiving to tape failed' % file_path)
        sleep(1)  # registering can sometimes take time, so give it a second...
        return register_for_archiving(file_path, strict=True)  # ... and try again (once only)

    return True


def recall_from_tape(file_path):
    states = archive_states(file_path)
    if is_dirty(file_path, states):
        raise ArchivingError('File %s is in a dirty state' % file_path)

    if is_archived(file_path, states) and is_released(file_path, states):
        val = _get_stdout('lfs hsm_restore ' + file_path)
        if val is not None:
            return True


def archive_directory(directory):
    """Recursively archive all the files in a directory"""
    success = True
    for f in os.listdir(directory):
        fp = os.path.join(directory, f)
        if os.path.isdir(fp):
            success = success and archive_directory(fp)
        elif os.path.isfile(fp):
            success = success and register_for_archiving(fp)
    return success
