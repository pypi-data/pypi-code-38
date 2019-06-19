from setuptools import setup, find_packages

setup(
    name="aitkit",
    version="0.0.9",
    author="aimasters team",
    author_email="kavcevich@action-media.ru",
    description="AI processing toolkit",
    packages= find_packages(exclude = [ 'tests' ]),
    zip_safe=True
)