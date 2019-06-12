import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='functionfaker',
     version='0.1.3',
     author="Will Sijp",
     author_email="wim.sijp@gmail.com",
     description="Function Faker",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/wsijp/scrapepath",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
