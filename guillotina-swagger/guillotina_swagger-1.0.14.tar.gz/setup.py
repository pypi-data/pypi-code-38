from setuptools import setup, find_packages

requires = ['guillotina>=4.0.0,<5', "jinja2"]

setup(
    name="guillotina_swagger",
    version='1.0.14',
    description="Swagger integration for viewing REST on your guillotina install",
    long_description=(
        open("README.rst").read() + "\n" + open("CHANGES.rst").read()
    ),
    keywords=["guillotina", "REST", "swagger"],
    author="Nathan Van Gheem",
    author_email="vangheem@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="https://github.com/guillotinaweb/guillotina_swagger",
    license="BSD",
    install_requires=requires,
)
