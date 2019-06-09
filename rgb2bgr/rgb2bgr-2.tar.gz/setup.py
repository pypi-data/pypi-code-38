import setuptools

setuptools.setup(
    name="rgb2bgr",
    version=2,
    author="KironDevCoder",
    author_email="mojanghouse@gmail.com",
    description="A rgb to bgr converter for python.",
    long_description="""A rgb to bgr converter for python I made for sentdex's Q Learning tutorial series.""",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    project_urls={
        "Documentation": "https://rgb2bgr.readthedocs.io/en/latest/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
