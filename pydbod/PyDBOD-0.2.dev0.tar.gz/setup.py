from distutils.core import setup
import setuptools

setup(
    name='PyDBOD',
    version='0.2dev',
    author="Miguel Ángel López Robles",
    description="A Distances Based Outlier Detector package",
    packages=setuptools.find_packages(),
    url="https://github.com/miki97/TFG-OutlierDetection",
    license='Licencia pública general de GNU Versión 3',
    long_description=open('README.md').read(),
)
