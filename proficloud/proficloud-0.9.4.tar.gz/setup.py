from setuptools import setup, find_packages
import os

#Get Version:
version_file = open(os.path.join(os.path.join(os.path.dirname(__file__)), 'VERSION'))
version = version_file.read().strip()

setup(name='proficloud',
    version=version,
    description='Easy access for PROFICLOUD',
    url='https://proficloud.atlassian.net/wiki/spaces/PP/overview',
    author='Proficloud',
    author_email='proficloud@proficloud.net',
    license='GPLv3',
    packages=find_packages(),
    install_requires=['requests', 'pandas', 'numpy', 'streamz', 'ntplib', 'somoclu', 'sklearn', 'bokeh', 'matplotlib', 'paho-mqtt', 'jsonpickle'],
    zip_safe=False,
    include_package_data=True,
    )
