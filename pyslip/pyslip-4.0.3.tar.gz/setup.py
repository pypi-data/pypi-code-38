from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pyslip',
      version='4.0.3',
      description='A slipmap widget for wxPython',
      long_description=readme(),
      url='http://github.com/rzzzwilson/pySlip',
      author='Ross Wilson',
      author_email='rzzzwilson@gmail.com',
      license='MIT',
      packages=['pyslip'],
      install_requires=['wxpython'],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3'],
      keywords='python wxpython slipmap map',
      download_url='https://github.com/rzzzwilson/pySlip/releases/tag/4.0.3',
      include_package_data=True,
      zip_safe=False)
