from setuptools import setup
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


setup(
    name='kaldi_spotter',
    version='0.1',
    packages=['kaldi_spotter'],
    url='https://github.com/JarbasAl/kaldi_spotter',
    install_requires=required('requirements.txt'),
    license='apache2.0',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='wake word spotting with kaldi'
)
