import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

requires = [
    'numpy',
    'matplotlib',
    'pyaudio'
]

tests_require = [
    'pytest',
    'pytest-cov',
]

setup(name='otoware',
      version='1.0.8',
      description='otoware',
      long_description=README,
      long_description_content_type="text/markdown",
      classifiers=[
          "Programming Language :: Python",
      ],
      author='kkiyama117',
      author_email='k.kiyama117@gmail.com',
      url='https://ku-jinja.net',
      keywords='python',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require={
          'testing': tests_require,
      },
      data_files=[('data', ['data/origin.wav'])],
      entry_points={
          'console_scripts': [
              'otowari = otoware.api:main',
          ],
      },
      )
