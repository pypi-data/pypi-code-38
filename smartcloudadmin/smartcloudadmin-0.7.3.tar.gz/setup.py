from setuptools import setup

setup(
    name='smartcloudadmin',
    version='0.7.3',
    packages=['smartcloudadmin', 'smartcloudadmin.utils', 'smartcloudadmin.models', 'smartcloudadmin.json'],
    url='https://github.com/cathaldi/smartcloud-administrator',
    include_package_data=True,
    license='apache2',
    download_url='https://github.com/cathaldi/smartcloud-administrator/releases/download/0.7.2/smartcloudadmin-0.7.3.tar.gz',
    author='Cathal A. Dinneen',
    install_requires=['requests'],
    author_email='cathal.a.dinneen@gmail.com',
    description='A package that provides functions to help interacting with companies, subscriptions and subscribers on IBM Smartcloud'
)
