from setuptools import setup, find_packages

setup(
    name="iotile_support_lib_controller_4",
    packages=find_packages(include=["iotile_support_lib_controller_4.*", "iotile_support_lib_controller_4"]),
    version="4.0.0.dev1",
    install_requires=['pyparsing>=2.2.1,<3', 'typedargs>=1,<2'],
    entry_points={'iotile.proxy_plugin': ['sensorgraph = iotile_support_lib_controller_4.sensorgraph', 'configmanager = iotile_support_lib_controller_4.configmanager', 'controllertest = iotile_support_lib_controller_4.controllertest', 'tilemanager = iotile_support_lib_controller_4.tilemanager', 'remotebridge = iotile_support_lib_controller_4.remotebridge'], 'iotile.type_package': ['lib_controller_types = iotile_support_lib_controller_4.lib_controller_types']},
    author="Arch",
    author_email="info@arch-iot.com"
)