import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='ganit',
     version='0.1.1',
     author="Palash Kanti Kundu",
     author_email="me@palash90.in",
     description="Ganit(गणित) means Calculation in Sanskrit. As the name suggests this is a calculation utility",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/Palash90/ganit/tree/master/python",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
