import setuptools

setuptools.setup(
    name="py-ravenworker",
    version="1.1.5",
    author="Brandon van Houten && Bouke Hendriks",
    author_email="brandon.vanhouten@dutchsec.com",
    description="Run Python functions against streaming data",
    long_description="Run Python functions against streaming data. Used by Python workers in Raven",
    url="https://gitlab.com/dutchsec/tools/py-worker",
    packages=setuptools.find_packages()
)
