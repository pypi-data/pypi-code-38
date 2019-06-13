import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='scrapepath',
     version='0.1.1',
     author="Will Sijp",
     author_email="wim.sijp@gmail.com",
     description="Templated scraping syntax",
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
