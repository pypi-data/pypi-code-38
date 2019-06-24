from fcopy import fcopy 
from setuptools import setup, find_packages

setup(
    name='fcopy',

    version=fcopy.__version_str__,

    description='A copying utility to keep files updated',
	long_description="""fcopy is an utility to copy several files from a source to different destinations by reading the configuration from a previously created JSON file. It allows also to watch if a file has changed to be automatically updated immediately.
    
For complete documentation please visit the project page on `GitHub <https://github.com/e2raptor/fcopy>`_.""",

    url='https://github.com/e2raptor/fcopy',

    author='Eduardo Pina Fonseca',
	author_email='epinaster@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],

    keywords='file utilities admin filesystem copy sync',

    packages=find_packages(exclude=['tests']),

    install_requires=[],
    entry_points={
        'console_scripts': [
            'fcopy=fcopy:main',
        ],
    },
)
