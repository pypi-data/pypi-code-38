import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qt5-cef",
    version="0.0.46",
    author="Burgeon Developer",
    author_email="huai.y@burgeon.cn",
    description="A simple tool kit for create desktop application",
    long_description=long_description,
    url="https://gitee.com/hycool/qt5_cef.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    include_package_data=True,
    package_data={
        '': ['*.js'],
    },
    # install_requires=['PyQt5==5.11.2', 'cefpython3==57.1', 'pywin32==223'],
)
