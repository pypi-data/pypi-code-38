from setuptools import setup

setup(
    name='papyru',
    version='0.0.1.dev29',
    description=(
        'minimal REST library with OpenAPI-based validation for django'),
    author='puzzle & play GmbH',
    author_email='papyru@puzzleandplay.de',
    url='https://www.fotopuzzle.de/',
    license='AGPLv3',
    platforms=['any'],
    packages=['papyru'],
    package_data={},
    install_requires=[
        'bravado<9.2',
        'bravado-core',
        'Cerberus',
        'pyyaml',
        'Django',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3.6',
    ],
)
