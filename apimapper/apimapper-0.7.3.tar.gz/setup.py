from setuptools import setup, find_packages


# read the contents of your README file
from os import path
with open('README.md', 'r') as f:
    long_description = f.read()

setup(name='apimapper',
      version='0.7.3',
      description='API Mapper',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Information Analysis',
      ],
      keywords='API Mapper',
      url='https://github.com/acdh-oeaw/apimapper',
      author='Saranya Balasubramanian, Ksenia Zaytseva',
      author_email='saranya.balasubramanian@oeaw.ac.at',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'markdown',
          'requests',
      ],
      include_package_data=True,
      zip_safe=False)
