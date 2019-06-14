from setuptools import setup

setup(
    name='snw',
    version='2.4.0',
    description='snw client tool',
    author='Jean Senellart',
    author_email='jean.senellart@systrangroup.com',
    url='http://www.systransoft.com',
    scripts=['client/snw'],
    package_dir={'client': 'nmt-wizard/client', 'lib': 'client/lib'},
    packages=['client', 'lib'],
    install_requires=[
        'configparser',
        'prettytable',
        'regex',
        'requests',
        'six',
        'setuptools',
        'jsonschema',
        'packaging>=17.0'
    ]
)
