from __future__ import print_function
import os
import subprocess
import sys

def create_directory(path):
    try:
        os.mkdir(path)
    except OSError:
        # TODO: handle exception someday
        raise


def create_file(path, content):
    with open(path, "w") as f:
        f.write(content)

            
def get_project_name(setup_py_path):
    args = ['python', setup_py_path, '--name']
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    
    return stdout.decode('UTF-8')[0:-1]

def get_version(setup_py_path):
    args = ['python', setup_py_path, '--version']
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    #print((stdout, stderr))
    return stdout.decode('UTF-8')[0:-1]

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
