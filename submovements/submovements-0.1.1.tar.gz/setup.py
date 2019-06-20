"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Stas Steinberg, Liz Izakson, Meyrav Dayan",
    author_email='stanislavs1@mail.tau.ac.il, lizizakson@mail.tau.ac.il, meyravdayan@mail.tau.ac.il',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    description='Our goal is to detect submovements from motion data',
    install_requires=requirements,
    license="MIT license",
    long_description='',
    include_package_data=True,
    keywords='submovements',
    name='submovements',
    packages=find_packages(include=['submovements']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/sstbrg/submovements',
    version='0.1.1',
    zip_safe=False,
)
