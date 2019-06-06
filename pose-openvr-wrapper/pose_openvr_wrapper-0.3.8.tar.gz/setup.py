# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pose_openvr_wrapper',
    packages=find_packages(exclude=["examples/*"]),
    version='0.3.8',
    description='PyOpenvr Library convenience wrapper'
                ' for recovery of pose data',
    author=u'Virgile Daugé',
    author_email='virgile.dauge@pm.me',
    url='https://github.com/virgileTN/pyopenvr_wrapper',
    # download_url='',
    keywords=['vive', 'tracking'],
    install_requires=['openvr >= 1.0.1701', 'numpy >= 1.15.4',
                      'pose_transform'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    data_files=[('pose_openvr_wrapper', ['pose_openvr_wrapper/config.json'])],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        ],
)
