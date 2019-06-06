from setuptools import setup, find_packages

from os import path


def read_from_file(*filename):
    with open(path.join(*filename), 'r') as f:
        return f.read()

print(find_packages(exclude=["test*", "test_*", "*_test*"]))

setup(
    name='zaber_motion_bindings_windows',
    version='0.0.20',
    packages=find_packages(exclude=["test*", "test_*", "*_test*"]),
    package_data={
        '': ['*.dll']
    },
    description='Windows bindings for Zaber Motion Library',
    long_description='Windows bindings for Zaber Motion Library',
    url='https://gitlab.com/zaber-core-libs/zaber-motion-lib',
    author='Zaber Technologies Inc.',
    author_email='contact@zaber.com',
    license='Apache Software License v2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
    ],
    keywords='',
    install_requires=[],
    extras_require={'build':['invoke']}
)
