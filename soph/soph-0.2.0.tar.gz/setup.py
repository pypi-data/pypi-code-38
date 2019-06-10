from io import open

from setuptools import find_packages, setup

with open('soph/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

with open('requirements.txt') as f:
    REQUIRES = f.read().splitlines()

setup(
    name='soph',
    version=version,
    description='Tools I find useful',
    # long_description=readme,
    author='artificialsoph',
    author_email='s@soph.info',
    maintainer='artificialsoph',
    maintainer_email='s@soph.info',
    url='https://github.com/artificialsoph/soph.py',
    license='MIT',
    keywords=[
        '',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],
    packages=find_packages(),
)
