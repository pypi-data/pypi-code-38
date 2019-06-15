import sys,setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
if  sys.version_info < (3,0):
 req=["requests","PySocks","bs4","pexpect","paramiko","mysql-connector","scapy","stem","cfscrape"]
else:
 req=["requests","PySocks","bs4","pexpect","paramiko","mysql-connector","kamene","stem","cfscrape"]
setuptools.setup(
    name="bane",
    version="1.9.7",
    author="AlaBouali",
    author_email="trap.leader.123@gmail.com",
    description="cyber security library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlaBouali/bane",
    python_requires=">=2.7",
    install_requires=req,
    packages=["bane"],
    license="MIT License",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License ",
    ],
)
