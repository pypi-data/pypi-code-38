from setuptools import setup

setup(name='newconan',
      version='1.65',
      description='New cmake project based on conan',
      url='https://github.com/wumo/newconan',
      author='wumo',
      license='MIT',
      packages=['newconan'],
      entry_points={
          'console_scripts': ['newconan=newconan.newconan:main'],
      },
      install_requires=[
          'conan'
      ],
      include_package_data=True,
      zip_safe=False)
