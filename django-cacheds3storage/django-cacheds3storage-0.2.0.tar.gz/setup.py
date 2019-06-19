from setuptools import setup

setup(
    name="django-cacheds3storage",
    version="0.2.0",
    author="Anders Pearson",
    author_email="ctl-dev@columbia.edu",
    url="https://github.com/ccnmtl/django-cacheds3storage",
    description="S3 cached storage",
    long_description="s3 cached storage",
    install_requires=[
        "django-storages",
        "python-dateutil",
        "boto3",
        ],
    scripts=[],
    license="BSD",
    platforms=["any"],
    zip_safe=False,
    packages=['cacheds3storage'],
    include_package_data=True,
    )
