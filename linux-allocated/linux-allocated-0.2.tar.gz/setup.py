from setuptools import setup
from os import path
cwd = path.abspath(path.dirname(__file__))
with open(path.join(cwd, 'README.md'), encoding='utf-8') as file_handle:
    long_description = file_handle.read()
# yapf: disable
setup(
    name='linux-allocated',
    version='0.2',
    url='https://github.com/svidovich/lad',
    author='svidovich',
    author_email='samuel.vidovich@gmail.com',
    license='MIT',
    packages=['lad'],
    package_data={'lad': ['data/*.txt']},
    description='Linux Allocated Devices for Python',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
# yapf: enable
