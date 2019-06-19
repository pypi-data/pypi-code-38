from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='imagehash3',
    version='0.1.3',
    description='Utility for images hashing',
    long_description=readme(),
    url='https://github.com/ThothMedia/image-utils',
    author='WISESIGHT DEV',
    author_email='dev@wisesight.com',
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=[
        'Pillow',
        'pywt',
        'numpy',
        'scipy'
    ],
    keywords='imagehash3',
    packages=['imagehash3'],
    package_dir={'imagehash3': './imagehash3'},
    package_data={'imagehash3': ['*.py']
    },
)
