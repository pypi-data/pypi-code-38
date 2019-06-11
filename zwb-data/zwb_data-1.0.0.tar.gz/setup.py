from setuptools import setup, find_packages

setup(
    name="zwb_data",
    version="1.0.0",
    keywords=("util"),
    description="zwb_data",
    long_description="zwb_data",
    url="https://github.com/weibin268/zwb_data",
    author="zhuang weibin",
    author_email="448075543@qq.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["SQLAlchemy==1.3.4","mysql-connector==2.2.9"]
)
