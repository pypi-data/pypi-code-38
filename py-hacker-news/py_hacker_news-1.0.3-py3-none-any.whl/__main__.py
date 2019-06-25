#!/usr/bin/env python

import argparse
from datetime import datetime, timedelta

from . import scraper
from . import ui
from . import validator


def main():
    argParser = initArgParser()
    args = argParser.parse_args()
    newsType, age, pages, proxy = validator.argValidator(args)
    # Obtain the results based on request newsType
    if newsType == "news":
        results = scraper.getArticles(pages, proxy, "news")
    elif newsType == "latest":
        results = scraper.getArticles(pages, proxy, "newest")
    elif newsType == "past":
        date = datetime.now() - timedelta(age)
        formattedDate = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
        print("Showing results from {} days ago  -  {}".format(age, formattedDate))
        results = scraper.getArticles(pages, proxy, "front", formattedDate)
    ui.printAllResults(results)
    exit()


def initArgParser():
    # Initialise the return the argParser
    parser = argparse.ArgumentParser(description="Hacker News Cli")
    parser.add_argument(
        "-number", type=int, help="Number of pages to display. Default = 1", default=1
    )
    parser.add_argument(
        "-proxy",
        type=str,
        help="Network Proxy. Default = Config Value or None",
        default=None,
    )
    parser.add_argument(
        "-type",
        type=str,
        help="Type of news ie, news, latest, past. Default = news",
        default="news",
    )
    parser.add_argument("-age", type=int, help="Age of results in DAYS")

    return parser


if __name__ == "__main__":
    main()
