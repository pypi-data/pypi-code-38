
"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tec-embrace',
    version='0.2',
    url='https://github.com/embrace-inpe/tec',
    license='MIT',
    author='Estudo e Monitoramento Brasileiro do Clima Espacial (EMBRACE/INPE)',
    author_email='desenvolvimento.embrace@gmail.com',
    description='TEC and receiver bias estimation model',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),   
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ])
