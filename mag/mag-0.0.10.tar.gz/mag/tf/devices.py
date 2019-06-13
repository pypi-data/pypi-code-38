from tensorflow.python.client import device_lib
import os

def available_devices():
    '''

    Returns:
        devices(dict): a list of devices by type (cpu / gpu)
    '''
    devices = device_lib.list_local_devices()
    cpus = [d for d in devices if d.device_type == 'CPU']
    gpus = [d for d in devices if d.device_type == 'GPU']
    return {'cpus': cpus, 'gpus': gpus}


def gpu_available_q():
    '''
    Returns:
        (bool): whether or not there is an availble gpu
    '''
    return len(available_devices()['gpus']) > 0


def set_env_devices(devices:list):
    '''
    Sets the environment variable CUDA_VISIBLE_DEVICES to devices

    Args:
        devices(list): a list of device names

    Returns:
        None

    '''
    os.environ["CUDA_VISIBLE_DEVICES"] = ','.join(devices)
