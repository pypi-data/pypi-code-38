from setuptools import setup, find_packages
import os

def read_file(filename):
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ''

setup(
    name='dong',
    version='0.2.1.0',
    description='Universal Command Line Interface for Libgirl AI Platform',
    long_description=read_file('readme.md'),
    long_description_content_type="text/markdown",
    url='https://dong.libgirl.com/',
    author='Team Libgirl',
    author_email='team@libgirl.com',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=['requests==2.22.0', 'tinynetrc==1.3.0', 'click==7.0'],
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    entry_points='''
        [console_scripts]
        dong=dong.cliapp:main
    '''
)
