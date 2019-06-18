# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains function to help gather system information use for the
provenance of the Job execution.
"""

import getpass
import os
import platform
import sys

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False


def namedtuple_to_dict(ntuple):
    """
    Helper function to convert a named tuple into a dict

    :param namedtuple ntuple: the namedtuple to convert
    :return: named tuple as a dict
    :rtype: dict
    """
    # Pylint does not play nice with namedtuples (does not recognize their methods)
    # pylint: disable=no-member,maybe-no-member,protected-access
    return dict(ntuple._asdict())


def get_cpu_usage():
    """
    Get the current CPU usage

    :return: CPU usage info
    :rtype: dict
    """
    cpu_usage = namedtuple_to_dict(psutil.cpu_times())
    cpu_usage['percent'] = psutil.cpu_percent()

    return cpu_usage


def get_memory_usage():
    """
    Get the current memory usage

    :return: memory usage info
    :rtype: dict
    """
    virtual_memory = namedtuple_to_dict(psutil.virtual_memory())
    swap_memory = namedtuple_to_dict(psutil.swap_memory())

    return {
            'virtual': virtual_memory,
            'swap': swap_memory}


def get_mounts():
    """
    Get the current mounts known on the system

    :return: mount info
    :rtype: dict
    """
    mounts = []
    for mount in psutil.disk_partitions():
        mount = namedtuple_to_dict(mount)

        try:
            usage = psutil.disk_usage(mount['mountpoint'])
            mount["disk_total"] = usage.total
            mount["disk_used"] = usage.used
            mount["disk_free"] = usage.free
            mount["disk_use_percent"] = usage.percent
        except OSError:
            pass

        mounts.append(mount)

    return mounts


def get_users():
    """
    Get current users on the system

    :return: user info
    :rtype: dict
    """
    users = []
    for user in psutil.users():
        user = namedtuple_to_dict(user)
        users.append(user)

    return users


def get_processes():
    """
    Get a list of all currently running processes

    :return: process information
    :rtype: list
    """
    # List all running processes
    processes = []
    for process in psutil.process_iter():
        proc = {'pid': process.pid,
                'name': process.name,
                'status': process.status,
                'memoryuse': process.get_memory_percent(),
                'cpu_user': process.get_cpu_times()[0],
                'cpu_system': process.get_cpu_times()[1],
                'nrthreads': process.get_num_threads()}
        try:
            proc["user"] = process.username
        except psutil.AccessDenied:
            pass
        try:
            proc["workdir"] = process.getcwd()
        except psutil.AccessDenied:
            pass
        try:
            proc["nice"] = process.get_nice()
        except psutil.AccessDenied:
            pass

        processes.append(proc)

    return processes


def get_sysinfo():
    """
    Get system information (cpu, memory, mounts and users)

    :return: system information
    :rtype: dict
    """
    if _PSUTIL_AVAILABLE:
        sysinfo = {'cpu_usage': get_cpu_usage(),
                   'memory_usage': get_memory_usage(),
                   'mounts': get_mounts(),
                   'users': get_users()}
    else:
        sysinfo = {}
    return sysinfo


def get_os():
    """
    Get information about the OS

    :return: OS information
    :rtype: dict
    """
    os_ = {'system': platform.system(),
           'is64bits': int(sys.maxsize > 2 ** 32),
           'maxsize': sys.maxsize}

    version = {}

    # Save version depending on platform
    if platform.system() == 'Linux':
        linux_distribution = platform.linux_distribution()
        version["distname"] = linux_distribution[0]
        version["version"] = linux_distribution[1]
        version["id"] = linux_distribution[2]

        libc = dict(zip(['libname', 'version'], platform.libc_ver()))
        version["libc"] = libc
    elif platform.system() == 'Windows':
        win32_version = platform.win32_ver()
        version["release"] = win32_version[0]
        version["version"] = win32_version[1]
        version["servicepack"] = win32_version[2]
        version["ptype"] = win32_version[3]
    elif platform.system() == 'Java':
        java_ver = platform.java_ver()
        version["release"] = java_ver[0]
        version["vendor"] = java_ver[1]
        version["vm_name"] = java_ver[2][0]
        version["vm_release"] = java_ver[2][1]
        version["vm_vendor"] = java_ver[2][2]
        version["os_name"] = java_ver[3][0]
        version["os_version"] = java_ver[3][1]
        version["os_arch"] = java_ver[3][2]
    elif platform.system() == 'Darwin':
        mac_ver = platform.mac_ver()
        version["release"] = mac_ver[0]
        version["version"] = mac_ver[1][0]
        version["dev_stage"] = mac_ver[1][1]
        version["non_release_version"] = mac_ver[1][2]
        version["machine"] = mac_ver[2]

    os_['version'] = version

    return os_


def get_python():
    """
    Get information about the currently used Python implementation

    :return: python info
    :rtype: dict
    """
    return {"version": platform.python_version(),
            "branch": platform.python_branch(),
            "compiler": platform.python_compiler(),
            "implementation": platform.python_implementation(),
            "revision": platform.python_revision()}


def get_drmaa_info():
    """
    Get information about the SGE cluster (if applicable)

    :return: cluster info
    :rtype: dict
    """
    drmaa_info = {}
    drmaa_info['jobid'] = os.environ.get('JOB_ID', None)
    drmaa_info['taskid'] = os.environ.get('SGE_TASK_ID', None)
    drmaa_info['jobname'] = os.environ.get('JOB_NAME', None)
    return drmaa_info


def get_hostinfo():
    """
    Get all information about the current host machine

    :return: host info
    :rtype: dict
    """
    hostenv = {}
    hostenv['os'] = get_os()
    hostenv['uname'] = platform.uname()
    hostenv['username'] = getpass.getuser()
    hostenv['cwd'] = os.getcwd()
    hostenv['python'] = get_python()
    hostenv['envvar'] = dict(os.environ)
    hostenv['drmaa'] = get_drmaa_info()
    return hostenv
