import os
from setuptools import setup, find_packages
import versioneer
import sys

# vagrant doesn't appreciate hard-linking
if os.environ.get('USER') == 'vagrant' or os.path.isdir('/vagrant'):
    del os.link

if sys.version_info < (3, 5):
    sys.exit('Sorry, Python < 3,5 is not supported')

# https://www.pydanny.com/python-dot-py-tricks.html
if sys.argv[-1] == 'test':
    test_requirements = [
        'pytest',
        'coverage',
        'pytest_cov',
    ]
    try:
        modules = map(__import__, test_requirements)
    except ImportError as e:
        err_msg = e.message.replace("No module named ", "")
        msg = "%s is not installed. Install your test requirments." % err_msg
        raise ImportError(msg)
    r = os.system('py.test test -v --cov=csirtg_indicator '
                  '--cov-fail-under=50')
    if r == 0:
        sys.exit()
    else:
        raise RuntimeError('tests failed')

setup(
    name="csirtg_indicator",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="CSIRTG Indicator Framework",
    long_description="",
    url="https://github.com/csirtgadgets/silver-meme",
    license='MPL2',
    classifiers=[
               "Topic :: System :: Networking",
               "Environment :: Other Environment",
               "Intended Audience :: Developers",
               "Programming Language :: Python",
               ],
    keywords=['network', 'security'],
    author="Wes Young",
    author_email="wes@csirtgadgets.com",
    packages=find_packages(exclude=['test']),
    install_requires=[
        'arrow',
        'pytricia',
        'ipaddress',
        'pendulum',
        'prettytable',
        'Faker',
        'networkx',
        'dnspython'
    ],
    entry_points={
       'console_scripts': [
           'csirtg-indicator=csirtg_indicator:main',
       ]
    },
)
