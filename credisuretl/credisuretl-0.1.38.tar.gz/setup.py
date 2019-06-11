from setuptools import setup, find_packages

version = {}
exec(open('credisur/version.py').read(), version)


setup(name='credisuretl',
      version=version['__version__'],
      description='ETL for Felsim',
      url='http://github.com/fedegos/credisuretl',
      author='Federico Gosman',
      author_email='federico@equipogsm.com',
      license='MIT',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'credisur = credisur.__main__:main'
          ]
      },
      install_requires=[
            'openpyxl==2.4.7',
            'xlrd'
      ],
      zip_safe=False)