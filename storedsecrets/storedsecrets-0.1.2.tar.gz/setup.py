import re
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("storedsecrets/__init__.py", "r") as fh:
    version=None
    rexp=re.compile(r'^\s*__version__\s*=\s*(?P<quote>[\'\"])(.*?)(?P=quote)')
    for l in fh:
        m = rexp.search(l)
        if m is not None:
            version = m.group(2)
            break
            
    
setuptools.setup(
    name="storedsecrets",
    version=version,
    author="Benjamin THOMAS",
    author_email="bth0mas@free.fr",
    description="A module to handle secrets outside of projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/bth0mas/storedsecrets/tree/master/python_module",
    packages=setuptools.find_packages(),
    # scripts=['scripts/storedsecrets_demo_mod_json.py'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
