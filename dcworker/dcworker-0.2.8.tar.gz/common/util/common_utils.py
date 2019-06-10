from os.path import splitext
import tarfile
import requests
import os
import shutil
from shutil import copy2, Error, copystat
import json


class TokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Token ' + self.token
        return r

################################################################################

def copytree(src, dst, symlinks=False, allowed_extension = None):
    names = os.listdir(src)
    if allowed_extension is None:
        allowed_extension = []
    os.makedirs(dst)
    errors = []
    for name in names:
        _, file_extension = splitext(name)
        if file_extension not in allowed_extension:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, allowed_extension)
            else:
                copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
    try:
        copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)


def delete_all_from_dir(dir):
    for item in os.listdir(dir):
        path = os.path.join(dir, item)
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

    return

################################################################################

def request_server(url, verb, **kwargs):
    try:
        # Allow a 30s timeout for the request.
        if verb == 'post':
            response = requests.post(url, timeout=30, **kwargs)
        elif verb == 'put':
            response = requests.put(url, timeout=30, **kwargs)
        elif verb == 'get':
            response = requests.get(url, timeout=30, **kwargs)
        else:
            return False, None, None, "supported http verb: {}".format(verb)
    except requests.Timeout:
        return False, None, None, "server side timeout"
    except:
        return False, None, None, "server side unknown error"

    if response is None:
        return False, None, None, "server side empty response"

    status_code = response.status_code
    try:
        response_body = json.loads(response.text)
    except:
        response_body = {}

    return True, status_code, response_body, None

################################################################################

def make_tarfile(output_filename, source_dir):
    if not source_dir.endswith(os.path.sep):
        source_dir = source_dir + os.path.sep
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))



def unzip_tarfile(source_tar, target_dir):
    tar = tarfile.open(source_tar, "r:gz")
    tar.extractall(path=target_dir)
    tar.close()