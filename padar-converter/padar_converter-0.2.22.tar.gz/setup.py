from setuptools import setup, find_packages

setup(
    name='padar_converter',
    version='0.2.22',
    packages=find_packages(),
    include_package_data=True,
    description='Extension of converters for sensor data used in padar package',
    long_description=open('README.md').read(),
    install_requires=[
        "gpxpy>=1.3.2",
        "pandas>=0.23.0",
        "chardet>=3.0.4"
    ],
)
