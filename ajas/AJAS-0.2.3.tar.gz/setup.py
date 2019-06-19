from distutils.core import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.readlines()
    print(requirements)


setup(name='AJAS',
      version='0.2.3',
      description='Lightweight REST Sever framework, based on bottle',
      author='Christian Schweigel',
      author_email='',
      url='https://github.com/swip3798/AJAS',
      packages=['AJAS'],
      long_description = long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3 :: Only",
          "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
          "Operating System :: OS Independent",
          "Development Status :: 3 - Alpha"
      ],
      install_requires=requirements
)