import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
v = open(os.path.join(here, 'VERSION')).readlines()[3]
VERSION = [x.strip().strip("'") for x in v.split('=')][1]

setup(
    name='python-onemapsg',
    version=VERSION,
    packages=find_packages(),
    description='Python Client for OneMap SG',
    long_description=README,
    author='Thomas Jiang',
    author_email='thomasjiangcy@gmail.com',
    url='https://github.com/windspeed-io/python-onemapsg',
    license='MIT',
    install_requires=[
        'requests>=2.19.1',
        'polyline>=1.3.2'
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
