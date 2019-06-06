import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='jblib',
                version='1.6.39',
                description='JustBard\'s Python Utilities',
                long_description=long_description,
                long_description_content_type="text/markdown",
                author='Justin Bard',
                author_email='JustinBard@gmail.com',
                url='http://justbard.com',
                packages=setuptools.find_packages(),
                classifiers=[
                    "Programming Language :: Python :: 3",
                    "License :: OSI Approved :: MIT License",
                    "Operating System :: POSIX :: Linux",
                ],
                )
