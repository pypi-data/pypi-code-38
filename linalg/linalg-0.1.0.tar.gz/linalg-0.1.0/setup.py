from setuptools import setup

NAME = "linalg"
DESCRIPTION = "A simple linear algebra package written in vanilla python3"
URL = "https://github.com/rocketll/linalg"
EMAIL = "rocketll@lucas.land"
AUTHOR = "Lucas Lee"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = "0.1.0"

setup(
  name = NAME,
  version = VERSION,
  description = DESCRIPTION,
  author = AUTHOR,
  author_email = EMAIL,
  python_requires = REQUIRES_PYTHON,
  url = URL,
  include_package_data = True,
  # packages = ["linalg"],
  keywords = ["linear algebra", "math"],
  license = "MIT")

