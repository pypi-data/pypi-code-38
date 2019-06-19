#! /usr/bin/env python3
from setuptools import setup, find_packages
from os import path
from subprocess import check_output, CalledProcessError
from time import strftime, gmtime
from setuptools.command.egg_info import egg_info
import pkg_resources


SETUP_DIR = path.dirname(__file__)
README = path.join(SETUP_DIR, 'README.md')


SETUPTOOLS_VER = pkg_resources.get_distribution("setuptools").version.split('.')


RECENT_SETUPTOOLS = int(SETUPTOOLS_VER[0]) > 40 or (
    int(SETUPTOOLS_VER[0]) == 40 and int(SETUPTOOLS_VER[1]) > 0) or (
        int(SETUPTOOLS_VER[0]) == 40 and int(SETUPTOOLS_VER[1]) == 0 and
        int(SETUPTOOLS_VER[2]) > 0)


class EggInfoFromGit(egg_info):
    """
    Tag the build with git commit timestamp.
    If a build tag has already been set (e.g., "egg_info -b", building
    from source package), leave it alone.
    """

    def git_timestamp_tag(self):
        gitinfo = check_output(
            ['git', 'log', '--first-parent', '--max-count=1',
             '--format=format:%ct', '.']).strip()
        return strftime('.%Y%m%d%H%M%S', gmtime(int(gitinfo)))

    def tags(self):
        if self.tag_build is None:
            try:
                self.tag_build = self.git_timestamp_tag()
            except CalledProcessError:
                pass
        return egg_info.tags(self)

    if RECENT_SETUPTOOLS:
        vtags = property(tags)


tagger = EggInfoFromGit


setup(
    name='cwl-airflow-tester',
    description='Tester for cwl-airflow-parser',
    long_description=open(README).read(),
    long_description_content_type="text/markdown",
    version='1.0',
    url='https://github.com/michael-kotliar/cwl-airflow-tester',
    download_url='https://github.com/michael-kotliar/cwl-airflow-tester',
    author='Michael Kotliar',
    author_email='misha.kotliar@gmail.com',
    license='Apache-2.0',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'requests',
        'cwltool',
        'ruamel.yaml',
        'cwltest==1.0.20180601100346'
    ],
    zip_safe=False,
    cmdclass={'egg_info': tagger},
    entry_points={
        'console_scripts': [
            "cwl-airflow-tester=cwl_airflow_tester.main:main"
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 8.1',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ]
)
