from setuptools import setup

def readme():
    with open('README.rst', 'r') as f:
        return f.read()

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: MacOS X',
    'Environment :: Win32 (MS Windows)',
    'Operating System :: OS Independent',
    'Intended Audience :: Science/Research',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Topic :: Scientific/Engineering',
    'Topic :: Database']

setup(name='dsws',
      version='0.14',
      description='Data Science Work Space for Jupyter & CDSW',
      long_description=readme(),
      long_description_content_type="text/markdown",
      url='https://github.com/babarka/dsws',
      author='Brad Barker',
      author_email='brad@ratiocinate.com',
      license='MIT',
      packages=['dsws'],
      classifiers=CLASSIFIERS,
      platforms='any',
      python_requires='>=3.6',
      install_requires=[
          'thrift==0.9.3',
          'sasl>=0.2.1',
          'thrift_sasl==0.2.1',
          #'iopro',
          #'pyodbc',
          'impyla'],

      zip_safe=False)
