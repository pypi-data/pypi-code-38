import pathlib
from setuptools import setup
from py_ng_deploy import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'readme.md').read_text()

# This call to setup() does all the work
setup(
    name='py-ng-deploy',
    version=__version__,
    description='Compile angular project and upload to sftp',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/ccmorataya/py-ng-deploy',
    author='Cristian Morataya',
    author_email='cris.morataya@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    packages=['py_ng_deploy'],
    entry_points={
        'console_scripts': [
            'pyngDeploy=py_ng_deploy.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=['pysftp>=0.2.9', 'colorama'],
)
