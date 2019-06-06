from angreal.integrations.virtual_env import venv_required
# Enforce the virtual environment for this command so that docker/Ipython etc are loaded


@venv_required('{{ angreal._cleaned_name }}')
def load_venv():
    pass
load_venv()

import sys
import os
import angreal
import docker
import atexit
import webbrowser
import time
from IPython.lib import passwd

from angreal.integrations.git import Git

from angreal import win,warn,error

HERE = os.path.dirname(__file__)
JUPYTER_SERVER_DOCKER_FILE = os.path.join(HERE, '..', 'docker', 'JupyterServer')
CONTEXT = os.path.join(HERE, '..')

# small work around to import local files
HERE = os.path.dirname(__file__)
sys.path.append(os.path.abspath(HERE))
from helpers import  BASE_DEV_GPU_IMAGE, BASE_DEV_CPU_IMAGE, CLIENT, get_open_port, image_build


@angreal.command()
@angreal.option('--verbose', is_flag=True, help="Verbose outputs get you logs from build and container.")
@angreal.option('--no_open', is_flag=True, help="Don't attempt to open my jupyter lab instance.")
@angreal.option('--password', default='', help="Token to use for security")
@angreal.option('--cpu', is_flag=True, help="Force usage of CPU")
def angreal_cmd(verbose, no_open, password, cpu):
    """
    launch the jupyter lab notebook
    """

    if cpu:
        warn("Using CPU only")

        def gpu_available():
            return False
    else:
        from helpers import gpu_available

    # build the image

    if gpu_available():
        try:
            image = image_build(JUPYTER_SERVER_DOCKER_FILE,
                                CONTEXT,
                                {'BASE_CONTAINER': BASE_DEV_GPU_IMAGE}, verbose=verbose)

        except Exception as e:
            warn("GPU build/start failed for some reason, falling back to CPU.")
            error(str(e))
            image = image_build(JUPYTER_SERVER_DOCKER_FILE,
                                CONTEXT,
                                {'BASE_CONTAINER': BASE_DEV_CPU_IMAGE}, verbose=verbose)
            pass

    else:
        image = image_build(JUPYTER_SERVER_DOCKER_FILE,
                            CONTEXT,
                            {'BASE_CONTAINER': BASE_DEV_CPU_IMAGE}, verbose=verbose)

    port = get_open_port()

    # Try to get a few starts in just in case we're spinning up a ton of containers
    for _ in range(10):
        try:
            args = [image.id]
            kwargs = dict(ports={8888: port},
                          detach=True,
                          volumes={CONTEXT: {'bind': '/home/elrond/project', 'mode': 'rw'}})

            if gpu_available():
                kwargs['runtime'] = 'nvidia'
            if password:
                kwargs['environment'] = {'JUPYTER_PASSWORD': passwd(password)}

            container = CLIENT.containers.run(*args, **kwargs)

        except docker.errors.APIError as e:
            err = e
            port = get_open_port()
            continue
        else:
            break
    else:
        raise err

    log = container.logs(stream=True)

    def kill_container():
        """
        Register container kill and removal when the function exits
        :return:
        """

        def check_git_status():
            """
            Check for un-committed changes.
            :return:
            """
            g = Git()
            status = g.status('-s')
            status_changed = status[2].decode().split('\\n')

            if status_changed[0] and len(status_changed) > 0:
                warn("The following files have been modified :")
                [angreal.echo("\t{}".format(x)) for x in status_changed]

                warn("Commit these files manually and push enter to continue. (Or just press enter now to not commit them)")
                input("<<<<<< Press Enter to finish shutting down the container >>>>>>")

        check_git_status()
        warn('Shutting down and removing {}'.format(container.name))
        container.remove(force=True)

    atexit.register(kill_container)

    win('Your instance is warming up.')
    time.sleep(5)
    if not no_open:
        webbrowser.open('http://127.0.0.1:{}'.format(port))

    win('JupyterLab instance being served at http://({} or 127.0.0.1):{}'.format(container.name, port))
    for message in log:
        if (verbose):
            print(message)

    return
