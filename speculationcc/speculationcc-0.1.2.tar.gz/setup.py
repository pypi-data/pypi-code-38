from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='speculationcc',
      version='0.1.2',
      description='sentiment analysis for speculationcc',
      url='http://github.com/wilkosz/crypto-profiler',
      author='joshua wilkosz',
      author_email='joshua@wilkosz.com.au',
      license='MIT',
      keywords='sentiment analyzer',
      packages=['speculationcc'],
      scripts=['bin/speculationcc-cmd'],
      install_requires=[
        'nltk'
      ],
      dependency_links=[],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False,
      entry_points = {
        'console_scripts': ['speculationcc=speculationcc.__main__:main'],
      },
      classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
      ],
)
