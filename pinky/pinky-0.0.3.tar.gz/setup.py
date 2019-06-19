from setuptools import setup, find_packages

VERSION = '0.0.3'

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pinky',
    description='pinky - molecular fingerprint library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Andrew E. Bruno',
    url='https://github.com/ubccr/pinky',
    license='BSD',
    author_email='aebruno2@buffalo.edu',
    include_package_data=True,
    version=VERSION,
    install_requires=[
        'bitarray'
    ],
    packages=find_packages(exclude=['tests*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
     ]
)
