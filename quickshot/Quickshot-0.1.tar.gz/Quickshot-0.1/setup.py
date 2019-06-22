import setuptools

setuptools.setup(
    name='Quickshot',
    version='0.1',
    author="Shawn Eisenach",
    author_email="shawn@wholewheattoast.com",
    packages=setuptools.find_packages(),
    description="A simple tool to visdiff two web pages.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
)
