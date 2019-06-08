import setuptools


with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="msz_svr_conn",
    version="0.0.1",
    author="Nyamu Kang'alia",
    author_email="kangalia@mesozi.com",
    description="Server Connection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/mesozi/market-force-360/msz-svr-conn",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.7"
    ],
    install_requires=[
        'requests[security]',
    ],
)
