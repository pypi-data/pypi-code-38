from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import pygments_shader

setup(
    name='pygments-shader',
    version=pygments_shader.__version__,
    description='Pygments lexer for Unity shader',
    long_description=open('README.rst').read(),
    url='https://github.com/midnightSuyama/pygments-shader',
    author='midnightSuyama',
    author_email='midnightSuyama@gmail.com',
    license='MIT',
    classifiers=[
        'Environment :: Plugins',
        'License :: OSI Approved :: MIT License'
    ],
    keywords='pygments shader unity',
    packages=find_packages(exclude=['tests*']),
    install_requires=['Pygments'],
    entry_points={'pygments.lexers': 'shader=pygments_shader:ShaderLexer'},
    tests_require=['pytest']
)
