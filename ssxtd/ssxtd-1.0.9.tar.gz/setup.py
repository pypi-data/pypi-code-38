import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ssxtd',
    version='1.0.9',
    packages=['ssxtd',],
    install_requires=['bs4','tqdm'],
    license='MIT',
    author='Xavier Godon',
    author_email='xavier.godon@protonmail.com',
    url='https://github.com/xgodon/ssxtd',
    description='semi structured xml to dict',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)