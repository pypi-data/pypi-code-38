from setuptools import setup, find_packages
from pkg_resources import resource_filename
# import pkg_resources


__version__ = '0.1.541'

versionFile = resource_filename(__name__, 'distnet/resources/VERSION')

with open(versionFile, 'w') as fd:
    fd.write(__version__)
    fd.close()

setup(
    name='distnet',
    version=__version__,
    author='p0licat',
    author_email='tbodica@gmail.com',
    install_requires=[
        'pygal_maps_world',
        'pygame',
        'python-whois', #TODO: check for whois package, conflicting?
        'cairosvg',
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    url='https://github.com/p0licat/distnet',
    license='LICENSE.txt',
    description='TCP connections visualizer.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: POSIX :: Linux",
    ],
)
