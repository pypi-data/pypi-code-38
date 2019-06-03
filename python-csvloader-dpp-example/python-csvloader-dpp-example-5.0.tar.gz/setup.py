from setuptools import setup, find_packages

setup(
    name='python-csvloader-dpp-example',
    version='5.0',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='An example python package',
    long_description=open('README.md').read(),
    install_requires=['pandas'],
    url='https://git.e-science.pl/rbaszak230509/81a_RBaszak_Package',
    author='Rafal Baszak',
    author_email='rbaszak230509@e-science.pl'
)