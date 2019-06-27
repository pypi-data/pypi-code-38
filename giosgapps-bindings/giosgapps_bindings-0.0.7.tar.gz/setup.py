import setuptools
from distutils.core import setup
with open('requirements.txt') as f:
    setup(
      name='giosgapps_bindings',
      packages=setuptools.find_packages(),
      version='0.0.7',
      license='MIT',
      description='Module for Giosg Apps development',
      author='Giosg',
      author_email='developers@giosg.com',
      url='https://github.com/giosg/giosgapps_bindings',
      download_url='https://github.com/giosg/giosgapps_bindings/archive/v0.0.7.tar.gz',
      keywords=['AUTH', 'GIOSG'],
      install_requires=list(f.read().splitlines()),
      classifiers=[
        'Development Status :: 3 - Alpha',  # "3 - Alpha" or "4 - Beta" or "5 - Production/Stable"
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],
    )
