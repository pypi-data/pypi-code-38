import os
import fcntl
import shutil
from os import path
import six
import hashlib

_STR_MAP = {
        ' ':'.',
        '/': '-',
        '--': '-',
        }

def listdir(dir, relative_path=False):
    for root, directories, filenames in os.walk(dir):
        for filename in filenames:
            filepath = path.join(root, filename)
            if relative_path:
                filepath = filepath.replace(dir, '')
            yield filepath

def ensure_dir(dir, mode=0o777):
    if not os.path.exists(dir):
        oldmask = os.umask(000)
        os.makedirs(dir, mode)
        os.umask(oldmask)

def ensure_dir_for_file(file, mode=0o777):
    dir = os.path.dirname(file)
    ensure_dir(dir, mode)

def compute_lock_filepath(sys_argv):
    filepath = ' '.join(sys_argv)
    for old, new in _STR_MAP.items():
        filepath = filepath.replace(old, new)
    return filepath + '.lock'

def obtain_lock(filepath):
    ensure_dir_for_file(filepath)
    pidfile = open(filepath, 'a+')
    try:
        fcntl.flock(pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        pidfile = None
        return None
    pidfile.seek(0)
    pidfile.truncate()
    pidfile.write(str(os.getpid()))
    pidfile.flush()
    pidfile.seek(0)
    return pidfile

def rmtree(folder_path):
    for file_object in os.listdir(folder_path):
        file_object_path = os.path.join(folder_path, file_object)
        if os.path.isfile(file_object_path) or os.path.islink(file_object_path):
            os.unlink(file_object_path)
        else:
            shutil.rmtree(file_object_path)

def copytree(src, dst, symlinks=False, ignore=None):
    for file_object in os.listdir(src):
        src_file_object_path = os.path.join(src, file_object)
        dst_file_object_path = os.path.join(dst, file_object)
        if os.path.isfile(src_file_object_path):
            shutil.copy(src_file_object_path, dst_file_object_path)
        elif os.path.islink(src_file_object_path):
            linkto = os.readlink(src_file_object_path)
            os.symlink(linkto, dst_file_object_path)
        else:
            shutil.copytree(src_file_object_path, dst_file_object_path, symlinks, ignore)

def free_space(path):
    if not os.path.isdir(path):
        return 0
    s = os.statvfs(path)
    free_space = (s.f_bavail * s.f_frsize)
    return free_space

def file_get_contents(file, mode='r'):
    with open(file, mode) as f:
        data = f.read()
        data = ensure_encode(data)
        return data

def ensure_encode(data):
    # for python 2, byte string should be convert to unicode
    if six.PY2 and type(data) == str:
        data = data.decode('utf-8')
    # for python 3, all string, type `str` is unicode
    return data

def ensure_decode(data):
    # for python 2, unicode should be encode to byte string, so that we can write them into file
    if six.PY2 and type(data) == unicode:
        data = data.encode('utf-8')
    return data

def file_put_contents(target_file, data, mode='w'):
    ensure_dir_for_file(target_file)
    data = ensure_decode(data)
    with open(target_file, mode) as f:
        f.write(data)

def md5_file(file):
    if not os.path.isfile(file):
        return ''
    hash_md5 = hashlib.md5()
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
