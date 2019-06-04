from setuptools import setup
import versioneer


setup(name='firexbuilder',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='FireX builder',
      url='https://github.com/FireXStuff/firexbuilder',
      author='Core FireX Team',
      author_email='firex-dev@gmail.com',
      license='BSD-3-Clause',
      packages=['firexbuilder', ],
      zip_safe=True,
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: BSD License",
      ],
      install_requires=["wheel",],
      entry_points={
          'console_scripts': ['firex-build = firexbuilder.build:main']
      },
      )
