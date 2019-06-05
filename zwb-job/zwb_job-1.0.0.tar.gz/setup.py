from setuptools import setup, find_packages

setup(
    name="zwb_job",
    version="1.0.0",
    keywords=("util"),
    description="zwb_job",
    long_description="zwb_job",
    url="https://github.com/weibin268/zwb_job",
    author="zhuang weibin",
    author_email="448075543@qq.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=['APScheduler==3.6.0']
)
