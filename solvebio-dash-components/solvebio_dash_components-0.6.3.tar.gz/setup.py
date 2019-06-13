from setuptools import setup

install_requirements = ['solvebio']

with open('solvebio_dash_components/version.py') as f:
    for row in f.readlines():
        exec(row)

with open('README.md') as f:
    long_description = f.read()

setup(
    name='solvebio_dash_components',
    version=__version__,
    description='The SolveBio Dash components suite',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Solve, Inc.',
    author_email='contact@solvebio.com',
    url='https://github.com/solvebio/solvebio-dash-components',
    packages=['solvebio_dash_components'],
    include_package_data=True,
    install_requires=install_requirements,
    classifiers=[
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ]
)
