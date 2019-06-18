import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='lutils',  
     version='0.7',
     #this will add to \Scripts folder
     #scripts=['lutils.py'] ,
     author="Tran Duc Loi",
     author_email="loitranduc@gmail.com",
     description="A Public Loitd utility package",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/loitd/lutils",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )