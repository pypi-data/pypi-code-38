import setuptools

with open("README.rst","r") as f:
   long_description = f.read()

setuptools.setup(
   name="xrdownloader",
   version="1.0.5",
   author="XploitsR Author (solomon narh)",
   author_email="solomonnarh97062@gmail.com",
   maintainer="XploitsR Authors",
   maintainer_email="xploitsr@gmail.com",
   platforms=['any'],
   license="MIT",
   description="XploitsR | XRDownloader is a module for faster downloading of files.",
   long_description=long_description,
   long_description_content_type="text/x-rst",
   url="https://github.com/XploitsR/XRDownloader",
   packages=setuptools.find_packages(),
   install_requires=[
       'urllib3',
       'certifi',
       'pyfiglet',
       'tqdm',
   ],
   python_requires='>=2.6, !=3.0.*, !=3.1.*',
   classifiers=[
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
       "Programming Language :: Python",
       "Programming Language :: Python :: 2",
       "Programming Language :: Python :: 2.6",
       "Programming Language :: Python :: 2.7",
       "Programming Language :: Python :: 3",
       "Programming Language :: Python :: 3.2",
       "Programming Language :: Python :: 3.3",
       "Programming Language :: Python :: 3.4",
       "Programming Language :: Python :: 3.5",
       "Programming Language :: Python :: 3.6",
       "Programming Language :: Python :: 3.7",
   ],
   keywords='xrdownloader fast-downloader xploitsr',
)
