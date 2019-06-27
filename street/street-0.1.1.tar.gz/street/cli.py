#!/usr/bin/env python

import click

from .config import set_config
from .exceptions import RequestBlocked, EarningsTableNotFound
from .scrape import scrape


@click.group()
def cli():
    pass


@click.command(
    short_help='Set browser parameters to bypass bot blocker'
)
@click.option(
    '-u',
    '--user-agent',
    help='User agent name of your browser',
    prompt=True,
)
@click.option(
    '-c',
    '--cookie',
    help='Cookie generated from your browser',
    prompt=True,
)
def setup(user_agent, cookie):
    set_config(user_agent, cookie)


@click.command(
    short_help='Get earnings history for ticker symbol'
)
@click.option(
    '-o',
    '--outfile',
    type=click.Path(),
    help='Output file to save earnings history',
)
@click.argument(
    'symbol',
)
def ticker(outfile, symbol):
    try:
        earnings = scrape(symbol)
    except RequestBlocked:
        print('Request was blocked by StreetInsider.com!')
    except EarningsTableNotFound:
        print('Earnings table was not found!')
    else:
        print(earnings)
        if outfile:
            earnings.to_csv(outfile, index=False)


cli.add_command(setup)
cli.add_command(ticker)


if __name__ == '__main__':
    cli()
