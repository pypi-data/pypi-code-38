import sys
import os
import angreal
import subprocess


from angreal import warn, error

HERE = os.path.dirname(__file__)
DEV_DOCKER_FILE = os.path.join(HERE, '..', 'docker', 'DevelopmentImage')
CONTEXT = os.path.join(HERE, '..')


# small work around to import local files
sys.path.append(os.path.abspath(HERE))
from helpers import BASE_DEV_GPU_IMAGE, BASE_DEV_CPU_IMAGE, CLIENT, image_build, in_container


@angreal.command()
@angreal.option('--verbose', is_flag=True, help="Verbose outputs get you logs from build and container.")
@angreal.option('--cpu', is_flag=True, help="Force usage of CPU")
@angreal.option('--no_docker', is_flag=True, help="Don't attempt to run inside of a docker container")
def angreal_cmd(verbose, cpu, no_docker):
    """
         compile documentation for the project
    """
    if cpu:
        warn("Using CPU only")

        def gpu_available():
            """
            Over ride gpu_available
            """
            return False
    else:
        from helpers import gpu_available

    if no_docker or in_container():
        doc_roots = os.path.join(HERE, '..', 'docs')
        os.chdir(doc_roots)
        subprocess.run('sphinx-apidoc -fMTeE -o source ../{{ angreal._cleaned_name }}', shell=True)
        subprocess.run('make clean', shell=True)
        subprocess.run('make html', shell=True)

        return

    else:
        #  Other wise build+run
        if gpu_available():
            try:
                image = image_build(DEV_DOCKER_FILE,
                                    CONTEXT,
                                    {'BASE_CONTAINER': BASE_DEV_GPU_IMAGE}, verbose=verbose)

            except Exception as e:
                warn("GPU build/start failed for some reason, falling back to CPU.")
                error(str(e))
                image = image_build(DEV_DOCKER_FILE,
                                    CONTEXT,
                                    {'BASE_CONTAINER': BASE_DEV_CPU_IMAGE}, verbose=verbose)
                pass

        else:
            image = image_build(DEV_DOCKER_FILE,
                                CONTEXT,
                                {'BASE_CONTAINER': BASE_DEV_CPU_IMAGE}, verbose=verbose)

        args = [image.id, 'docs']
        kwargs = dict(
                      detach=True,
                      volumes={CONTEXT: {'bind': '/home/elrond/project', 'mode': 'rw'}})

        if gpu_available():
            kwargs['runtime'] = 'nvidia'

        container = CLIENT.containers.run(*args, **kwargs)

        log = container.logs(stream=True)

        for message in log:
                angreal.echo(message.strip())
