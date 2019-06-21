from setuptools import setup

setup(name="sobolt",
      version="0.3.1",
      description="Client code to query Sobolt's AI services",
      url="http://sobolt.com",
      author="Sobolt",
      author_email="info@sobolt.com",
      zip_safe=False,
      license="All rights reserved",
      packages=["sobolt"],
      install_requires=[
        "requests"
      ])
