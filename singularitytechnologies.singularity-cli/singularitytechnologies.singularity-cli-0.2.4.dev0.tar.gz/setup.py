import setuptools

from singularity import __version__

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='singularitytechnologies.singularity-cli',
    version=__version__,
    author='Sam Lacey',
    author_email='sam.lacey@singularity-technologies.io',
    license='MIT',
    description='A CLI to run common singularity tasks.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/singularitydigitaltechnologies/singularity-cli',
    packages=setuptools.find_packages(),
    install_requires=[
        'asyncio',
        'docopt',
        'singularitytechnologies.singularitytechnologiesapi==0.2.3dev'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    entry_points='''
        [console_scripts]
        singularity-cli=singularity.singularity:main
    ''',
)
