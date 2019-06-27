import logging
import os
import yaml
import shutil

logger = logging.getLogger(__name__)


def get_src_path(dir=''):
    return os.path.join(os.path.dirname(__file__), dir)


def copy_file_to_working_dir(filename, working_dir):
    src_path = get_src_path()
    shutil.copy(
        os.path.join(
            src_path, filename), os.path.join(
            working_dir, filename))


def get_docker_path():
    f = open(os.path.join(os.getcwd(), "kronos-config.yml"), "r+")
    yaml_data = yaml.load(f)
    return yaml_data['dockerpath']


def copy_files_to_working_dir(filename_list, working_dir):
    for filename in filename_list:
        copy_file_to_working_dir(filename, working_dir)


def base_command(use_gpu):
    if use_gpu:
        return ['docker-compose', '-f',
                '{}/docker-compose-gpu.yml'.format(get_docker_path())]
    return ['docker-compose', '-f',
            '{}/docker-compose-cpu.yml'.format(get_docker_path())]


def run_command(use_gpu):
    args = base_command(use_gpu)
    args.append('run')

    return args
