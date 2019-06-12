from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="tailf",
    version="0.3.0",
    description="tail -f functionality for your python code. Track file appends and truncations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        # "Operating System :: POSIX :: Linux",  # some features are linux-only
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="http://gitlab.com/trooniee/tailf",
    author="Sergei Shilovsky",
    author_email="sshilovsky@gmail.com",
    license="MIT",
    packages=["tailf"],
    # install_requires=['inotify;platform_system=="Linux"'],
    zip_safe=False,
    test_suite="nose.collector",
    tests_require=["nose"],
)
