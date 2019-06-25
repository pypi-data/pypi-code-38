import os

import setuptools

readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_path, 'r') as fp:
    long_description = fp.read()

setuptools.setup(
    name="sprig",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="AP Ljungquist",
    author_email="ap@ljungquist.eu",
    description="A home to code that would otherwise be homeless",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/apljungquist/sprig",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
