import imp
import os.path
import sys
from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))
trosnoth_version = imp.load_source('trosnoth.version', os.path.join(
    here, 'trosnoth', 'version.py')).version

if __name__ == '__main__':
    setup(name = 'trosnoth',
        version = trosnoth_version,
        description = 'Trosnoth network platform game',
        author = 'J.D. Bartlett et al',
        author_email = 'josh@trosnoth.org',
        url = 'http://www.trosnoth.org/',
        packages=find_packages(exclude=['test']),
        package_data={'trosnoth': [
            'data/blocks/*.block',
            'data/blocks/*.trosblock',
            'data/config/*.cfg',
            'data/fonts/*.ttf',
            'data/fonts/*.TTF',
            'data/fonts/*.txt',
            'data/music/*.ogg',
            'data/sound/*.ogg',
            'data/sprites/*.png',
            'data/startupMenu/*.png',
            'data/startupMenu/*.txt',
            'data/statGeneration/*.htm',
            'data/achievements/*.png',
            'data/web/*.png',
            'data/*.db',
            'gpl.txt',
        ]},

        scripts = ['scripts/trosnoth', 'scripts/trosnoth-server'],
        long_description = 'Trosnoth is a fast-paced open source territory control team platform game.' ,

        install_requires = [
            'pygame',
            'twisted>=15.0',
            'simplejson'
        ],

        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications',
            'Framework :: Twisted',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Games/Entertainment :: Arcade',
            'Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games',
        ],
    )
