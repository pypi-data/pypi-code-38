from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='tsfaker',
    version='0.1.2',
    license='MPL-2.0',
    url='https://gitlab.com/healthdatahub/tsfaker/',
    author='Pierre-Alain Jachiet - DREES',
    author_email='ld-lab-github@sante.gouv.fr',
    description='Generate fake data conforming to a Table Schema',
    long_description=long_description,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    python_requires='~=3.5',
    install_requires=[
        'click',
        'numpy',
        'pandas',
        'rstr',
        'tableschema',
        'dsfaker',
    ],
    extras_require={
        'dev': [
            'sphinx',
            'pytest',
            'goodtables'
        ],
    },
    entry_points={
        'console_scripts': [
            'tsfaker = tsfaker.main:cli',
        ]
    }
)
