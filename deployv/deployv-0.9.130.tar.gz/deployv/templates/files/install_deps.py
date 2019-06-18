import fnmatch
import platform
import pwd
import subprocess
import shlex
import sys
import os
from reqgen import reqgen


def read_lines(file_name):
    with open(file_name, 'r') as fileobj:
        lines = fileobj.readlines()
    return [line.strip() for line in lines]


def create_user():
    """ Creates the odoo user inside the container without password if it does not
     exists and then changes the password for the root user to odoo.
    """
    try:
        pwd.getpwnam('odoo')
    except KeyError:
        commands = [
            'adduser --home=/home/odoo --disabled-password --gecos "" --shell=/bin/bash odoo',
            'echo "root:odoo" | chpasswd',
            'chown odoo:odoo /home/odoo', ]
        for command in commands:
            subprocess.check_call(shlex.split(command))


def entry_point():
    """ Downloads the entrypoint used as command for any container created with this image
        and gives execution permissions to it.
    """
    commands = [('wget -q -O /entry_point.py https://raw.githubusercontent.com/'
                 'Vauxoo/docker_entrypoint/master/entry_point.py'),
                'chmod +x /entry_point.py']
    for command in commands:
        subprocess.check_call(shlex.split(command))


def search_apt_requirements(folder_name, file_name=None, recursive=False):
    """ Searches for all requirements.txt file recursively in the given path
    :param folder_name: the folder where you want to search
    :param file_name: filename to search
    :param recursive: Searches recursively and don't stop if the file is found
    :return: A list with all the files found, empty if none
    """
    res = list()
    if file_name is None:
        file_name = 'apt_requirements.txt'
    for base, directories, files in os.walk(folder_name):
        for file_name in fnmatch.filter(files, file_name):
            res.append(os.path.join(base, file_name))
            if not recursive:
                # Clean the directories so the walk doesn't go any further
                del directories[:]
    return res


def check_packages(package_list, dist):
    white_list = read_lines('/tmp/apt-package-{dist_name}'.format(dist_name=dist))
    for package_name in package_list:
        if package_name not in white_list:
            print('Could not install {} package, not whitelisted'.format(package_name))
            sys.exit(1)


def install_apt_requirements(apt_file, dist_name):
    """ Reads the apt_dependencies.txt file copied by the dockerfile in /tmp and parses it to
    install all the apt dependencies inside the container
    """
    deps = read_lines(apt_file)
    check_packages(deps, dist_name)
    for dep in deps:
        cmd = 'apt-get install {name} -yq'.format(name=dep.strip('\n'))
        subprocess.check_call(shlex.split(cmd))


def install_requirements():
    """ Gathers the requirements from all the requirements.txt files it can find in
        the folder where all the repos are with the help of reqgen,
        merges them into one single requirements.txt, and installs them.
    """
    reqgen.generate_merged_file('/home/odoo/full_requirements.txt', '/home/odoo/instance')
    subprocess.check_call(shlex.split('pip install -r /home/odoo/full_requirements.txt'))


def download_files(file_list, destination):
    for src in file_list:
        dest = os.path.join(destination, os.path.basename(src))
        command = 'wget -q -O {destination} {source}'.format(destination=dest, source=src)
        subprocess.check_call(shlex.split(command))


def apt_install():
    """ Execute the install from all apt_files found in the repos folder, but first
    updates the apt cache
    """
    _, _, dist_name = platform.linux_distribution()
    apt_files = search_apt_requirements('/home/odoo/instance')
    apt_files.append('/tmp/apt_dependencies.txt')
    download_files([
        'https://git.vauxoo.com/vauxoo/apt_whitelist/raw/master/apt-package-{dist_name}'
        .format(dist_name=dist_name),
        'https://git.vauxoo.com/vauxoo/apt_whitelist/raw/master/apt-sources.json',
        ],
        '/tmp')

    subprocess.check_call(shlex.split('apt-get update'))
    for apt_file in apt_files:
        install_apt_requirements(apt_file, dist_name)


def create_paths():
    """ Creates the directories, and intermediate paths if needed, for some of the
        files that will be copied in the image.
    """
    paths = ['/home/odoo/.ssh', '/home/odoo/.local/share/Odoo', '/var/log/supervisor']
    for path in paths:
        try:
            os.makedirs(path)
        except OSError as error:
            if 'File exists' not in error.strerror:
                raise


def main():
    """ Main method in charge of following the logic required to set up the needed directories,
        install the python dependencies and set the addons path in the odoo config file.
    """
    commands = ['python /home/odoo/getaddons.py /home/odoo/instance/extra_addons', ]

    create_user()
    create_paths()
    entry_point()
    apt_install()
    install_requirements()
    for command in commands:
        subprocess.check_call(shlex.split(command))


if __name__ == "__main__":
    main()
