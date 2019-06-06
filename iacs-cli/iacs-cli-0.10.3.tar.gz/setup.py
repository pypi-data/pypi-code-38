import pathlib
from setuptools import setup


DIR = pathlib.Path(__file__).parent
README = (DIR / "README.md").read_text()


setup(name='iacs-cli',
      version='0.10.3',
      description="Command line tool for Harvard IACS course",
      long_description=README,
      long_description_content_type="text/markdown",
      url='https://github.com/richardskim111/iacs-cli',
      author='Richard Kim',
      author_email='richardskim111@gmail.com',
      license='MIT',
      packages=['iacs'],
      install_requires=[
          'click',
          'pelican',
          'markdown',
          'gitpython',
          'beautifulsoup4'
      ],
      entry_points = {
          'console_scripts': ['iacs=iacs.iacs_cli:main']
      },
      zip_safe=False)
