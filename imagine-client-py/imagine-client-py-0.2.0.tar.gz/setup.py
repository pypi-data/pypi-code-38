import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='imagine-client-py',
     version='0.2.0',
     author="Steven Chand",
     author_email="steven@doc.ai",
     description="A python client for doc.ai's Imagine API",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/doc-ai/imagine-client-py.git",
     packages=setuptools.find_packages(),
)
