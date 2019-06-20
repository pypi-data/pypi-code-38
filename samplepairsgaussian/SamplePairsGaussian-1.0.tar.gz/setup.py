from setuptools import setup

setup(
    name='SamplePairsGaussian',
    version='1.0',
    author='Oliver K. Ernst',
    packages=['samplePairsGaussian','examples'],
    install_requires=[
          'numpy'
      ],
    license='GNU General Public License v3.0',
    description='Sample pairs of particles according to a discrete Gaussian distrbution',
    long_description=open('README.md').read(),
    url="https://github.com/smrfeld/sample-pairs-gaussian",
     classifiers=[
         "Development Status :: 5 - Production/Stable",
         "Intended Audience :: Developers",
         "Topic :: Scientific/Engineering :: Mathematics",
         "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
     ],
)
