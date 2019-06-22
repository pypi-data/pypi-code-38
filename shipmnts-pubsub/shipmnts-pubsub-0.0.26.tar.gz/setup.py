import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shipmnts-pubsub",
    version="0.0.26",
    author="Vimox Shah",
    author_email="vimox@shipmnts.com",
    description="Pubsub error handler",
    long_description_content_type="text/markdown",
    install_requires=["google-cloud-pubsub==0.40.0"],
    url="https://github.com/vimox-shah/shipmnts_pubsub",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)