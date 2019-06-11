import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as f:
    install_requires = [req for req in f.read().split('\n') if req]


setuptools.setup(
    name="fn-throttle",
    version="0.0.1",
    author="ZhenningLang",
    author_email="zhenninglang@163.com",
    description="Standalone python function call controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZhenningLang/throttle",
    packages=setuptools.find_packages(),
    python_requires='>=3.2',
    include_package_data=True,
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
