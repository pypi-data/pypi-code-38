import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__),
                       'VERSION')) as f:
    version = f.read().strip()


setup(
    name='python-geoip-geolite2-yplan',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    version=version,
    maintainer='Thomas Grainger',
    maintainer_email='python-geoip-geolite2-yplan@graingert.co.uk',
    url='https://github.com/YPlan/python-geoip/tree/master/geolite2',
    packages=['_geoip_geolite2'],
    description='Provides access to the geolite2 database.  This product '
        'includes GeoLite2 data created by MaxMind, available from '
        'https://www.maxmind.com/',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
