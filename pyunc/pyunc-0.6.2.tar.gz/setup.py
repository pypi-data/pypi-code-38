import codecs
import os.path
from setuptools import find_packages, setup

project = 'pyunc'
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

about = {}
with open(os.path.join(here, project, "__version__.py")) as f:
    exec(f.read(), about)


setup(
    name=project,
    version=about['__version__'],
    packages=find_packages(exclude=['tests']),
    zip_safe=True,
    author='Jon Stutters',
    author_email='j.stutters@ucl.ac.uk',
    description='Classes for reading UNC format MRI files',
    long_description=long_description,
    url='https://github.com/jstutters/pyunc',
    install_requires=[
        "arrow",
        "nibabel",
        "numpy",
    ],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'unc2nii = pyunc.cli:unc_to_nifti'
        ]
    },
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
    ]
)
