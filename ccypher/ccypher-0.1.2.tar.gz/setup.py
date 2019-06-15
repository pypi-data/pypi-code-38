from setuptools import setup
from os import path

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='ccypher',
      version='0.1',
      description='Graphic user interface to encrypt or decrypt text.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing :: Filters',
        ],
      keywords='ccypher cypher encrypt decrypt text casear caesarcypher',
      url='https://github.com/iwkerr/ccypher.git',
      download_url='https://github.com/iwkerr/ccypher/blob/master/dist/ccypher-0.1.tar.gz',
      author='IK',
      author_email='iwkerr48@gmail.com',
      license='MIT',
      packages=['ccypher'],
      install_requires=[
          'pyperclip'
      ],
      include_package_data=True,
      scripts=['bin/ccypher'],
      zip_safe=False)
