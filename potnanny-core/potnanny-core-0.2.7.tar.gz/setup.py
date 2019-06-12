from setuptools import setup
from glob import glob

setup(
    name='potnanny-core',
    version='0.2.7',
    packages=['potnanny_core'],
    include_package_data=True,
    description='Part of the Potnanny greenhouse controller application. Contains all core models, schemas, db interfaces, and utilities.',
    author='Jeff Leary',
    author_email='potnanny@gmail.com',
    url='https://github.com/jeffleary00/potnanny-core',
    install_requires=[
        'click',
        'dotenv',
        'passlib',
        'sqlalchemy',
        'marshmallow',
        'jinja2',
        'bluepy==1.3.0',
        'btlewrap==0.0.2',
        'miflora==0.5',
        'mitemp_bt==0.0.1',
        'vesync-outlet==0.1.1',
    ],
    data_files=[
        ('/usr/local/bin/', ['bin/rf_send', 'bin/rf_scan']),
        ('/opt/potnanny/plugins/action/', glob('plugins/action/*.py')),
        ('/opt/potnanny/plugins/ble/', glob('plugins/ble/*.py')),
    ],
    entry_points = {
        'console_scripts': [
            'potnanny=potnanny_core.cli:cli',
        ],
    },
)
