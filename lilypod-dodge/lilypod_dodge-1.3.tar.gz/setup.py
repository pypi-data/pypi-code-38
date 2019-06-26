from setuptools import setup

setup(
    name='lilypod_dodge',
    version='1.3',
    packages=['lilypod_dodge', 'lilypod_dodge/resources'],

    license='MIT',
    long_description='My first game',
    install_requires=[
                    'pygame',
                     ],
    include_package_data=True,
    author='Gabriel Petersson',
    author_email='gabriielpetersson@gmail.com',
    url='https://github.com/gabrielpetersson/lilypod_dodge'
)
