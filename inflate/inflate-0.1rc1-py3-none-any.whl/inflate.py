# -*- coding: utf-8 -*-

import click

from inflate.main import get_inflation_amount, CURRENCY
from colorama import Fore, Style

__version__ = "0.1rc1"


@click.command()
@click.option(
    "--country", "-c", help="Country [either US/UK], default is UK", default="UK"
)
@click.option(
    "--inclusive",
    "-i",
    help="Include ending year, default no",
    is_flag=True,
    default=False,
)
@click.argument("start", type=click.INT)
@click.argument("end", type=click.INT)
@click.argument("amount", default=1.0)
@click.version_option(__version__)
def main(
    country: str = "UK",
    start: str = "",
    end: str = "",
    amount: int = 1,
    inclusive: bool = True,
):
    inflated_amount = get_inflation_amount(country, start, end, amount, inclusive)
    inclusive_text = "inclusive" if inclusive else "exclusive"
    is_was = "was" if start > end else "is"
    formatted_string = "{}{}{}{} in {}{}{} {} worth {}{}{}{} in {}{}{} ({}).".format(
        Fore.BLUE,
        CURRENCY[country.lower()],
        amount,
        Style.RESET_ALL,
        Fore.BLUE,
        start,
        Style.RESET_ALL,
        is_was,
        Fore.GREEN,
        CURRENCY[country.lower()],
        inflated_amount,
        Style.RESET_ALL,
        Fore.GREEN,
        end,
        Style.RESET_ALL,
        inclusive_text,
    )
    print(formatted_string)


if __name__ == "__main__":
    main()
