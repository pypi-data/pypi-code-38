from __future__ import absolute_import, division, print_function

import io
import os
import tempfile

import psutil


def set_working_dataset(dataset):
    ds_file = get_dataset_file()
    try:
        with io.open(ds_file, 'w+') as f:
            f.write(dataset.id)
        # double check
        assert working_dataset_id() is not None, "Error writing to working dataset file"
    except:
        print("We encountered an error while setting your working dataset.")
    return None

def get_dataset_file():
    try:
        if os.name == 'nt':
            parent_shell_pid = psutil.Process(os.getpid()).parent().parent().pid
        else:
            parent_shell_pid = psutil.Process(os.getpid()).parent().pid
    except:
        return None
    fname = 'blackfynn_working_dataset_{}'.format(parent_shell_pid)
    return os.path.join(tempfile.gettempdir(), fname)

def working_dataset_id():
    ds_file = get_dataset_file()
    if os.path.exists(ds_file):
        try:
            with io.open(ds_file, 'r+') as f:
                ds_id = f.read().strip()
                return ds_id
        except:
            pass
    return None

def require_working_dataset(bf):
    ds = working_dataset_id()
    if ds is None:
        exit("Dataset required. You can set your working dataset with:" \
             "\n\n\tbf use <dataset>" \
             "\n\nor by specifying it in your command:" \
             "\n\n\t bf --dataset=<dataset> <command> ..." \
             "\n")
    try:
        return bf.get_dataset(ds)
    except Exception as e:
        exit(e)
