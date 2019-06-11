from setuptools import setup
from vtrtool import __version__

setup(
    name='vtrtool',
    version=__version__,
    author='Tim Lin (S-Cube)',
    author_email='tlin@s-cube.com',
    description='Python utilities for Fullwave3D VTR model files',
    license='3-clause BSD',
    keywords='fullwave3d vtr',
    url='http://not-yet',
    py_modules=['vtrtool.vtrtool_script', 'vtrtool.vtrmodel', 'vtrtool.aux_funcs'],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[
        'future',
        'numpy',
        'docopt',
        'segyio>=1.6',
    ],
    entry_points={
        'console_scripts': [
            'vtrtool = vtrtool.vtrtool_script:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ]
)
