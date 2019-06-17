import setuptools

VERSION = "0.2.3"

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(name='termite_toolkit',
                 version=VERSION,
                 description='Python library for calling TERMite and TExpress and processing results',
                 url='https://github.com/SciBiteLabs/termite_toolkit',
                 install_requires=[
                     "requests>=2.8.1"
                 ],
                 author='SciBite DataScience',
                 author_email='joe@scibite.com',
                 long_description=long_description,
                 long_description_content_type='text/markdown',
                 license='Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License',
                 packages=setuptools.find_packages(),
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "Operating System :: OS Independent",
                 ],
                 data_files=[("", ["LICENSE.txt"])],
                 zip_safe=False)
