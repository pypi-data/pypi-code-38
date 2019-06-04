import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='singularitytechnologies.singularitytechnologiesapi',
    version='0.2.4dev',
    author='Sam Lacey',
    author_email='sam.lacey@singularity-technologies.io',
    description='Python implementation of the Singularity Technologies API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/singularitydigitaltechnologies/singularitytechnologiesapi',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)
