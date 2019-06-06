
import pkg_resources
from io import TextIOWrapper

from govuk_country_register.register import Register


def __load__():
    return Register.from_csv(
        TextIOWrapper(
            pkg_resources.resource_stream("govuk_country_register", "country.csv"),
            encoding="utf-8",
        )
    )


register = __load__()


def to_country(country_code):
    """Find the name for a country from its two-letter country code

    :param country_code str:  the two-letter country code
    :return str:  the country's commonly-used name in English

    The country codes used are two-letter ISO 3166-2 alpha-2 codes,
    which are also typically used as a country's top-level domain on the
    internet.

    The data is drawn from GOV.UK's country register at
    https://www.registers.service.gov.uk/registers/country.
    """

    return register.find(country_code)["name"]
