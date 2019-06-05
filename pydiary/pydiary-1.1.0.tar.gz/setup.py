import setuptools
import pydiary

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pydiary',
    version=pydiary.__version__,
    author='Nathan Lepori',
    author_email='nathan.lepori@hotmail.com',
    description='MatLab style commands logger for the Python interpreter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nathanlepori/pydiary',
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable'
    ],
)
