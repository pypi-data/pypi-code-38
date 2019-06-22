import setuptools


def long_description():
    with open('README.md', 'r') as file:
        return file.read()


setuptools.setup(
    name='lowhaio_redirect',
    version='0.0.1',
    author='Michal Charemza',
    author_email='michal@charemza.name',
    description='Lowhaio wrapper that follows HTTP redirects',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/michalc/lowhaio-redirect',
    py_modules=[
        'lowhaio_redirect',
    ],
    python_requires='>=3.6.3',
    test_suite='test',
    tests_require=[
        'lowhaio~=0.0.69',
        'aiohttp~=3.5.4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
    ],
)
