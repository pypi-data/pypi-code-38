from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '2.0.0'

install_requires = [
    'pyyaml',
]


setup(name='collectd_puppet',
    version=version,
    description="Collectd Plugin to Monitor Puppet Agents",
    long_description=README + '\n\n',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: System :: Monitoring",
    ],
    keywords='collectd puppet monitoring',
    author='Steve Traylen',
    author_email='steve.traylen@cern.ch',
    url='https://github.com/cernops/collectd-puppet',
    license='Apache II',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    data_files = [('/usr/share/collectd/', ['resources/puppet_types.db'])],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires
)
