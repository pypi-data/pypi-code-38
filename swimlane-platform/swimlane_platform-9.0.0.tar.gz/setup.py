from setuptools import setup, Command
from distutils.command.register import register as register_orig
from distutils.command.upload import upload as upload_orig
import shutil
import os
from glob import glob


def readme():
    with open('README.md') as f:
        return f.read()


def requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


def super_glob(*path):
    files = []
    for arg in path:
        files.extend(glob(arg))
    return files


class Register(register_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')


class Upload(upload_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')


class Clean(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        shutil.rmtree('build', ignore_errors=True)
        shutil.rmtree('swimlane_platform.egg-info', ignore_errors=True)


setup(
    name='swimlane_platform',
    version='9.0.0',
    packages=['swimlane_platform',
              'swimlane_platform.lib',
              'swimlane_platform.upgrade_steps',
              'swimlane_platform.backup',
              'swimlane_platform.environment_updater'],
    url='https://github.com/swimlane/platform-installer-linux',
    license='',
    author='Swimlane',
    author_email='info@swimlane.com',
    description='Swimlane platform on linux. Install, Upgrade, Backups etc. All maintenance.',
    long_description=readme(),
    long_description_content_type="text/markdown",
    install_requires=requirements(),
    include_package_data=True,
    cmdclass={
            'clean': Clean,
            'register': Register,
            'upload': Upload
        },
    entry_points={
        'console_scripts': ['swimlane-platform=swimlane_platform.wizard:run'],
    },
    data_files=[
        ('swimlane_scripts', ['swimlane_scripts/install.sh']),
        ('swimlane_template_dir', glob('swimlane_template_dir/*.yml')),
        ('swimlane_template_dir/db-init', glob('swimlane_template_dir/db-init/*.sh')),
        ('swimlane_template_dir/.secrets', glob('swimlane_template_dir/.secrets/.*'))
    ]
)
