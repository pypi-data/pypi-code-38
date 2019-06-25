from setuptools import setup


def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(name="filemaker-api",
      version="1.0.1",
      description="Connect easily to a FileMaker instance.",
      long_description=readme(),
      long_description_content_type="text/markdown",
      url="https://caoslab.psy.cmu.edu:32443/caoskids/filemaker_api",
      author="Hugo Angulo",
      author_email="hugoanda@andrew.cmu.edu",
      license="MIT",
      classifiers=["License :: OSI Approved :: MIT License",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.7", ],
      packages=["filemaker"],
      include_package_data=True,
      install_requires=["requests"],
      entry_points={"console_scripts": ["filemaker-api=filemaker.__main__:main", ]}, )
