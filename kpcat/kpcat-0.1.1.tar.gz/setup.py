import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()


requirements = []
with open('requirements.txt', 'r') as f:
    requirements = f.readlines()


setup(
    name='kpcat',
    version='0.1.1',
    description='cat a keepass file',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/whwright/kpcat',
    author='Harrison Wright',
    author_email='mail@harrisonwright.me',
    py_modules=['kpcat'],
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        kpcat=kpcat:main
    '''
)
