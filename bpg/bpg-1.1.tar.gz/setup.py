from setuptools import setup
setup(
    name='bpg',
    packages = ['bpg', 'tests'],
    version = '1.1',
    url='http://era.nutanix.com',
    license='Apache 2.0',
    long_description='Template engine\nwith Expression Support',
    description='template engine with expression',
    author='nobody',
    author_email='era@nutanix.com',
    install_requires = ['pyyaml'],
    package_data= {'templates':['templates/*.*']},
    include_package_data=True
)