import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='adr-tools-python',  
     version='1.0',
     entry_points = {
        'console_scripts':[
            'adr-init = adr_init:main',
            'adr-new = adr_new:main',
            'adr-list = adr_list:main',
            'adr-config = adr_config:main'
        ]
     },
     author="Victor Sluiter",
     author_email="vsluiter@yahoo.com",
     license="MIT",
     description="A package to provide adr-tools to python",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://bitbucket.org/tinkerer_/adr-tools-python/",
     packages=setuptools.find_packages(),
     package_dir={"adr_func":"adr_func"},
     package_data={"adr_func":["template.md"]},
     classifiers=[
         "Development Status :: 5 - Production/Stable",
         "Intended Audience :: Developers",
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     keywords=["adr","architecture decision record"],
     py_modules = ["adr_func","adr_new","adr_init","adr_config","adr_list"],
     python_requires='>=3',
     install_requires=[
         'argparse'
     ]
 )
