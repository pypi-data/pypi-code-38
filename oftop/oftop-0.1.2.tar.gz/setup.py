import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='oftop',
    version='0.1.2',
    author='M. Schölling',
    author_email='manuel.schoelling@gmx.de',
    description='Open File Top',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/manuels/oftop',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
    entry_points={
    'console_scripts': [
        'oftop=oftop:main',
      ],
    },
    install_requires=['psutil'],
)
