from setuptools import setup


def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(name="qualtrics-api",
      version="1.0.5",
      description="Easy connection to a Qualtrics API.",
      long_description=readme(),
      long_description_content_type="text/markdown",
      url="https://caoslab.psy.cmu.edu:32443/caoskids/qualtrics_api",
      author="Hugo Angulo",
      author_email="hugoanda@andrew.cmu.edu",
      license="MIT",
      classifiers=["License :: OSI Approved :: MIT License",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.7", ],
      packages=["qualtrics"],
      include_package_data=True,
      install_requires=["requests"],
      entry_points={"console_scripts": ["qualtrics-api=qualtrics.__main__:main", ]}, )
