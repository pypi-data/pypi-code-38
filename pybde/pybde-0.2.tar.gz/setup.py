from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()
        
setup(name='pybde',
      version='0.2  ',
      description='Binary Delay Equation simulator',
      long_description=readme(),
      long_description_content_type='text/markdown',
      python_requires='>=3.5',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
        'Operating System :: OS Independent',
      ],
      keywords='BDE, binary, delay, equations, solver, simulator',
      url='https://github.com/EPCCed/pybde/wiki/pybde',
      author='Ally Hume',
      author_email='a.hume@epcc.ed.ac.uk',
      license='MIT',
      packages=['pybde'],
      install_requires=['numpy','matplotlib'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
