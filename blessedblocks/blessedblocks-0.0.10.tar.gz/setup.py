from setuptools import find_packages, setup

setup(
    name='blessedblocks',
    packages=find_packages(),
    version='0.0.10',
    description='Display a terminal window in blocks using the blessed module.',
    author='Mark Libucha',
    author_email='mlibucha@gmail.com',
    url='http://nowhere.click',
    license='Apache 2.0',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='test',
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',        
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    install_requires=[
        "blessed>=1.15.0, <2.0.0",
        "six>=1.11.0, <2.0.0",
        "tabulate>=0.8.2, <2.0.0",
        "wcwidth>=0.1.7, <2.0.0",
        "atomicwrites>=1.1.5, <2.0.0",
        "attrs>=18.1.0, < 19.0.0",
        "more-itertools>=4.2.0, <5.0.0",
        "pluggy>=0.6.0, < 1.0.0",
        "py>=1.5.3, <2.0.0",
        "pytest>=3.6.0, <4.0.0"
    ]
)
