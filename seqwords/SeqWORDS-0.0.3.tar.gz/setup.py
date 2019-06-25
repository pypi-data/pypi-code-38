

from setuptools import setup, find_packages

setup(name='SeqWORDS',
      version='0.0.3',
      keywords = ("EM algorithm", "unsupervised method", "WDM", "Chinese word segmentation"),
      description='An unsupervised Chinese word segmentation',
      author='Harry Wu',
      author_email='tf00604520@gmail.com',
      license='MIT Licence',
      url='https://github.com/kkuanhui/SeqWORDS',
      packages= find_packages(),
      include_package_data = True,
      install_requires=[
          'numpy',
      ],
      )
