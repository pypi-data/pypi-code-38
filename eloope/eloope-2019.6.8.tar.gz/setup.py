import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='eloope',
    version='2019.6.8',
    author='Czw',
    author_email='459749926@qq.com',
    description='Event loop engine.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Czw96/eloope',
    packages=setuptools.find_packages(exclude=('trash', 'demo')),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': ['eloope=eloope.main:main'],
    },
    install_requires=[
        'gevent',
        'requests',
        'toolset',
    ],
)
