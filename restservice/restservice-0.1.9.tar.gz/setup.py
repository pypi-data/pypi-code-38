import setuptools


setuptools.setup(
    name='restservice',
    version='0.1.9',
    author='Sergey Mokeyev',
    author_email='sergey.mokeyev@gmail.com',
    description='A small JSON API service template',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SergeyMokeyev/RESTService',
    data_files=[
        ('README.md', ['README.md'])
    ],
    packages=[
        'restservice'
    ],
    py_modules=[
        'restservice',
        'restservice.config',
        'restservice.exception',
        'restservice.handler',
        'restservice.service'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
    ],
    install_requires=[
        'aiohttp>=3.5.4',
        'marshmallow>=3.0.0rc7',
        'inflection>=0.3.1',
        'pyyaml>=5.1.1'
    ]
)
