from setuptools import setup, find_packages

setup(
    name="geocelery",
    version="1.1",
    author="zhouxiaohua",
    author_email="zhouxiaohua@cnic.cn",
    packages=find_packages(),
    install_requires=["celery", "redis==2.10.6"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
