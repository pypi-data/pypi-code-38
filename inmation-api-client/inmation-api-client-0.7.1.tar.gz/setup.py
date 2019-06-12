import sys
import setuptools

py_version = sys.version_info[:2]

if py_version < (3, 6):
    raise Exception("websockets requires Python >= 3.6.")

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="inmation-api-client",
    version="0.7.1",
    author="Alexandr Sapunji",
    author_email="alexandr.sapunji@inmation.com",
    license='MIT',
    description="API client for system:inmation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://inmation.com",
    packages=setuptools.find_packages(),
    install_requires=[
        'websockets==7.0',
    ],
    classifiers=(
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",        
    ),
    zip_safe=True,
    python_requires='>=3.6',
)
