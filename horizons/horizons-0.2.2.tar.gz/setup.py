from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='horizons',
    version='0.2.2',
    description='JPL HORIZONS System client',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='David Dupre',
    license='MIT License',
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Development Status :: 3 - Alpha',
    ],
)
