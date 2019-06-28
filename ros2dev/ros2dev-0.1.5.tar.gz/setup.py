from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.1.5'

install_requires = [
    'argparse',
    'jinja2'
]

setup(name='ros2dev',
    version=version,
    description="Setup a ROS 2.0 development environment in Docker",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='ROS robots',
    author='Kevin DeMarco',
    author_email='kevin.demarco@gmail.com',
    url='https://www.kevindemarco.com',
    license='GPLv3',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    package_data={
        'ros2dev': ['templates/*'],
    },
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['ros2dev=ros2dev:main']
    }
)
