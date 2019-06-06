"""
    helpers
    ~~~~~~~

    Some helper functions for angreal functions in this project


"""

from angreal.integrations.virtual_env import venv_required
#Enforce the virtual environment for this command so that docker/Ipython etc are loaded
@venv_required('{{ angreal._cleaned_name }}')
def load_venv():
    pass
load_venv()

from subprocess import Popen, PIPE
from distutils import spawn
import os
import platform
import docker
from angreal import win,warn,error


CLIENT = docker.from_env()
BASE_DEV_CPU_IMAGE = "dockerrepay/vilya:ubuntu-{{ angreal.ubuntu_version }}-py{{ angreal.python_version }}{{ angreal._tensorflow_string }}-lab"
BASE_DEV_GPU_IMAGE = "dockerrepay/vilya:ubuntu_nvidia-{{ angreal.ubuntu_version }}-py{{ angreal.python_version }}{{ angreal._tensorflow_string }}-lab"
BASE_CPU_IMAGE = "dockerrepay/vilya:ubuntu-{{ angreal.ubuntu_version }}-py{{ angreal.python_version }}{{ angreal._tensorflow_string }}"
BASE_GPU_IMAGE = "dockerrepay/vilya:ubuntu_nvidia-{{ angreal.ubuntu_version }}-py{{ angreal.python_version }}{{ angreal._tensorflow_string }}"

def gpu_available():
    """
    If we have access to GPUs we should know about it and should launch GPU enabled notebooks.
    :return:
    """
    if platform.system() == "Windows":
        # If the platform is Windows and nvidia-smi
        # could not be found from the environment path,
        # try to find it from system drive with default installation path
        nvidia_smi = spawn.find_executable('nvidia-smi')
        if nvidia_smi is None:
            nvidia_smi = "{}\\Program Files\\NVIDIA Corporation\\NVSMI\\nvidia-smi.exe" ,format(os.environ['systemdrive'])
    else:
        nvidia_smi = "nvidia-smi"

    try:
        p = Popen([nvidia_smi,
                   "--query-gpu=index,uuid,utilization.gpu,memory.total,memory.used,memory.free,driver_version,name,gpu_serial,display_active,display_mode,temperature.gpu",
                   "--format=csv,noheader,nounits"], stdout=PIPE)
        stdout,stderr = p.communicate()
        return  True
    except:
        return False



def in_container():
    """
    determine if we're running within a container or not

    :return: bool
    """

    def text_in_file( text, file):
        try:
            return any(text in line for line in open(file))
        except FileNotFoundError:
            return False


    return ( os.path.exists('./.dockerenv') or
            text_in_file('docker', '/proc/self/cgroup') )



def image_build(docker_file,context,build_args,verbose=False):
    """
    build the docker file with given build_args

    :param build_args:
    :return:
    """
    win('Building Image, if this is the first build, it could take a few minutes.')

    image,log = CLIENT.images.build(
        path=context,
        tag='{{ angreal._cleaned_name }}_jupyter_server',
        pull=True,
        dockerfile=docker_file,
        quiet=False,
        buildargs=build_args
    )

    if verbose:
        for line in log:
            print(line)

    return image






def get_bound_host_ports():
    """
    Get a list of currently bound host ports

    :return:
    """

    ports_in_use = set()

    for c in CLIENT.containers.list():
        port_bindings = c.attrs.get('NetworkSettings', {}).get('Ports', {})

        for internal,external in port_bindings.items():
            for e in external:
                ports_in_use.add(e.get('HostPort',None))


    return ports_in_use


def get_open_port():
    """
    Get a potentially open port

    There is no reservation until the container run is called. As a result it is possible, however unlikely, that two
    containers would try to grab the same port.

    """
    possible_range = set([ str(x) for x in range(8000,9001) ]) ^ get_bound_host_ports()
    return  int(possible_range.pop())