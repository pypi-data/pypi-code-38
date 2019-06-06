#!/usr/bin/python
import os
import subprocess
import sys

from setuptools import setup, find_packages
from setuptools.command.install_lib import install_lib as _install_lib
from distutils.command.build import build as _build
from setuptools.command.sdist import sdist as _sdist
from distutils.cmd import Command


class test(Command):
    description = 'run django tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os
        try:
            from django.core.management import call_command
        except ImportError:
            raise RuntimeError('You need django in your PYTHONPATH')
        os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
        call_command('test', 'django_journal')


class compile_translations(Command):
    description = 'compile message catalogs to MO files via django compilemessages'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        curdir = os.getcwd()
        try:
            os.environ.pop('DJANGO_SETTINGS_MODULE', None)
            from django.core.management import call_command
            os.chdir(os.path.realpath('django_journal'))
            call_command('compilemessages')
        except ImportError:
            print
            sys.stderr.write('!!! Please install Django >= 1.4 to build translations')
            print
            print
        finally:
            os.chdir(curdir)


class build(_build):
    sub_commands = [('compile_translations', None)] + _build.sub_commands


class sdist(_sdist):
    sub_commands = [('compile_translations', None)] + _sdist.sub_commands


class install_lib(_install_lib):
    def run(self):
        self.run_command('compile_translations')
        _install_lib.run(self)


def get_version():
    '''Use the VERSION, if absent generates a version with git describe, if not
       tag exists, take 0.0- and add the length of the commit log.
    '''
    if os.path.exists('VERSION'):
        with open('VERSION', 'r') as v:
            return v.read()
    if os.path.exists('.git'):
        p = subprocess.Popen(
            ['git', 'describe', '--dirty=.dirty', '--match=v*'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = p.communicate()[0]
        if p.returncode == 0:
            result = result.decode('ascii').strip()[1:]  # strip spaces/newlines and initial v
            if '-' in result:  # not a tagged version
                real_number, commit_count, commit_hash = result.split('-', 2)
                version = '%s.post%s+%s' % (real_number, commit_count, commit_hash)
            else:
                version = result
            return version
        else:
            return '0.0.post%s' % len(
                    subprocess.check_output(
                            ['git', 'rev-list', 'HEAD']).splitlines())
    return '0.0'


setup(name='django-journal',
      version=get_version(),
      license='AGPLv3',
      description='Keep a structured -- i.e. not just log strings -- journal'
                  ' of events in your applications',
      url='http://dev.entrouvert.org/projects/django-journal/',
      download_url='http://repos.entrouvert.org/django-journal.git/',
      author="Entr'ouvert",
      author_email="info@entrouvert.com",
      packages=find_packages(os.path.dirname(__file__) or '.'),
      include_package_data=True,
      cmdclass={
          'build': build,
          'install_lib': install_lib,
          'compile_translations': compile_translations,
          'sdist': sdist,
          'test': test
      },
      install_requires=[
          'django >= 1.7,<1.9',
          'django-model-utils',
      ])
