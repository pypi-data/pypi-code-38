import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cutter-ng",
    version="2.5",
    author="Johannes Graën",
    author_email="graen@cl.uzh.ch",
    description='Cutter is rule-based multilingual tokenizer that can be adapted to particular text types.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://pub.cl.uzh.ch/purl/cutter',
    packages=setuptools.find_packages(),
    install_requires=['regex', 'PyYAML'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
