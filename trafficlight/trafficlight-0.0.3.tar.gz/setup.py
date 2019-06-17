import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="trafficlight",
    version="0.0.3",
    author="Andy Klier",
    author_email="andyklier@gmail.com",
    description="Start and stop EC2s using tags. now in color!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/rednap/trafficlight",
    packages = ['trafficlight'],
    entry_points = {
        'console_scripts': ['trafficlight=trafficlight.main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
