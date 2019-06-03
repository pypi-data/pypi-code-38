import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='MoreSim',
                 version="0.0.1",
                 description='The funniest joke in the world',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url='http://github.com/raimon-fa/',
                 author='Raimon Fabregat',
                 author_email="raimon.fa@gmail.com",
                 license='MIT',
                 packages=setuptools.find_packages(),
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 )
