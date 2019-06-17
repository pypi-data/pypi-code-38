import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

__version__ = '0.0.4'

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().split('\n')

install_requires = [x.strip() for x in requirements if 'git+' not in x]

setuptools.setup(
    name='deepscratch',
    version=__version__,
    author='Tuguldur O',
    author_email='thattuguldur@gmail.com',
    description='Deep Learning From Scratch.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tuguldurio/DeepScratch',
    packages=setuptools.find_packages(),
    license='GNU GPLv3',
    install_requires=install_requires,
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
