#!/usr/bin/env python3

from distutils.core import setup
setup(name='gt',
        version='0.3.08',
        author='Raheman Vaiya',
        author_email='r.vaiya@gmail.com',
        url='http://gitlab.com/rvaiya/gt',
        keywords='git github gitlab ssh cli console management',
        description='A simple tool for managing repositories located accross various git sources (e.g gitlab/github/unix boxes).',
        long_description=open('README.rst').read(),
        packages=['gt.sources'],
        scripts=['bin/gt'],
        classifiers=[
            'Programming Language :: Python :: 3',
            'Development Status :: 3 - Alpha'
            ],
      install_requires=['requests', 'bs4']
)
