from setuptools import setup


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(name='gdsmerge',
      version='0.0.0',
      description='Merge cells of multiple GDS files into a single file.',
      long_description=readme(),
      long_description_content_type="text/markdown",
      keywords='gds gds2 merge converter klayout',
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Development Status :: 3 - Alpha',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
          'Programming Language :: Python :: 3'
      ],
      url='https://codeberg.org/tok/gdsmerge',
      author='T. Kramer',
      author_email='code@tkramer.ch',
      license='GPLv3+',
      packages=['gdsmerge'],
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'gdsmerge = gdsmerge.standalone:main',
          ]
      },
      install_requires=[
          'klayout',
      ],
      zip_safe=False)
