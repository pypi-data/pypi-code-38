import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vulnx",
    version="1.6",
    author="anouarbensaad",
    author_email="bensaad.tig@gmail.com",
    description="vulnx is a cms and vulnerabilites detection, an intelligent auto shell injector",
    long_description="Vulnx is a cms and vulnerabilites detection, an intelligent auto shell injector,fast cms detection of target and fast scanner and informations gathering like subdomains,ipaddresses, country, org, timezone, region, ans and more ...Instead of injecting shell and checking it works like all the other tools do,vulnx analyses the response with and recieve if shell success uploaded or no.vulnx is searching for urls with dorks.",
    url="https://github.com/anouarbensaad/vulnx",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
