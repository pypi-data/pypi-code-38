import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="govuk-country-register",
    version="0.4.0",
    author="Laurence de Bruxelles",
    author_email="laurence.debruxelles@digital.cabinet-office.gov.uk",
    description="Jinja2 filter to look up country codes using the GOV.UK country and territory registers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={
        "govuk_country_register": ["country.csv"],
    },
    packages=setuptools.find_packages(),
    url="https://github.com/lfdebrux/govuk-country-register-python",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
