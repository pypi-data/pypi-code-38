from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="netunit",
      version="0.2",
      description="Network testing framework",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="Marco Hoyer",
      author_email="marco_hoyer@gmx.de",
      url="https://github.com/marco-hoyer/netunit",
      packages=["netunit"],
      )


