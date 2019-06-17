import os
import errno
from setuptools import setup

from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
from setuptools.command.egg_info import egg_info as _egg_info

here = os.path.abspath(os.path.dirname(__file__))


def _mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise



SHARE_PATH_PART = 'share/ansible'


def is_shared_path(path):
    return SHARE_PATH_PART in SHARE_PATH_PART


def is_user_path(path):
    return SHARE_PATH_PART not in SHARE_PATH_PART


class CustomPostInstall(object):
    def _post_install(self):
        """
        Copy ovh_iplb/main.py $ANSIBLE_MODULE/ovh_iplb.py
        """
        from ansible.constants import DEFAULT_MODULE_PATH

        main_file = os.path.join(here, "ovh_iplb/main.py")

        error = None

        # We prefer installing to shared path first if possible (installing as root, so all user can use it)
        paths = list(filter(is_shared_path, DEFAULT_MODULE_PATH)) + list(filter(is_user_path, DEFAULT_MODULE_PATH))
        for ansible_module_path in paths:
            try:
                error = None
                ansible_module = os.path.join(ansible_module_path)
                ovh_iplb_file = os.path.join(ansible_module, "ovh_iplb.py")
                _mkdir_p(ansible_module)

                self.copy_file(main_file, ovh_iplb_file)

                print()
                print("Finished symlink %s to %s" % (main_file, ovh_iplb_file))
                break
            except Exception as e:
                error = e

                if error is not None:
                    raise e


class install(_install, CustomPostInstall):
    def run(self):
        _install.run(self)
        self._post_install()

class develop(_develop, CustomPostInstall):
    def run(self):
        _develop.run(self)
        self._post_install()

class egg_info(_egg_info, CustomPostInstall):
    def run(self):
        _egg_info.run(self)
        self._post_install()


setup(
    name="ansible-iplb",
    long_description="This is an ansible module for handling ovh iplb",
    packages=[
        'ovh_iplb',
    ],
    install_requires=[
        'ansible',
        'ovh',
    ],
    tests_require=[
        'mock',
    ],
    author="kubernatine",
    author_email="kubernatine@something.com",
    url="https://pypi.org/project/ansible-iplb/",
    cmdclass={'install': install, 'develop': develop, 'egg_info': egg_info},
    keywords="apiv6 ovh iplb load balancer ansible"
)
