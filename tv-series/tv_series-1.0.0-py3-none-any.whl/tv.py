import logging

import click
from tabulate import tabulate

from . import data
from .exceptions import SeriesNotFound
from .tvdb import tvdb

logger = logging.getLogger(__name__)


def print_table(series):
    print(
        tabulate(
            [
                [
                    s.id,
                    s.name,
                    s.seen,
                    s.find_available(),
                    s.next_on_air(),
                    s.status,
                    s.category,
                    s.language,
                ]
                for s in series
            ],
            headers=[
                "TVDB ID",
                "Series",
                "Last seen",
                "Available",
                "Next on air",
                "Status",
                "Category",
                "Language",
            ],
        )
    )


def identify_series(query, series_list):
    if query.strip() == "":
        raise SeriesNotFound()

    if query.isdigit():
        try:
            return [s for s in series_list if s.id == int(query)][0]
        except IndexError:
            # Continue to string match in the unlikely case that a series is
            # named with purely digits
            pass

    # First try exact match
    try:
        return [s for s in series_list if query.lower() == s.name.lower()][0]
    except IndexError:
        try:
            return [s for s in series_list if query.lower() in s.name.lower()][0]
        except IndexError:
            raise SeriesNotFound()


@click.group()
def cli():
    pass


@cli.command(help="create the config file with your api key")
def init():
    tvdb.initialize()
    data.initialize()
    print(f"Your API key and login token is saved at: {tvdb.CONFIG_PATH}")
    print(f"Your TV series database is saved at: {data.DATABASE_PATH}")


@cli.command(help="search for series by name in thetvdb")
@click.argument("query", nargs=-1)
def search(query):
    for result in tvdb.search(query):
        print(f"{result['id']}: {result['seriesName']} ({result['status']})")
        print(f"  {result['overview']}")
        print()


@cli.command(help="list tracked series")
@click.option("-a", "--all", is_flag=True, help="ignore filters")
@click.option("-c", "--category", help="filter by category (default: active)")
@click.option("-n", "--name", help="filter by series name")
@click.option("-i", "--id", type=int, help="filter by tvdb id")
def list(all, category, name, id):
    series = data.load()

    # Default to active category only if no other filters are specified
    if not any((all, category, name, id)):
        category = "active"

    if not all and category:
        series = [s for s in series if s.category.lower() == category.lower()]
    if not all and name:
        series = [s for s in series if name.lower() in s.name.lower()]
    if not all and id:
        series = [s for s in series if s.id == id]
    print_table(series)


@cli.command(help="sync episode data from thetvdb api")
@click.option("-c", "--category", help="filter by category")
@click.option("-n", "--name", help="filter by series name")
@click.option("-i", "--id", type=int, help="filter by tvdb id")
def sync(category, name, id):
    series_list = data.load()
    series_filtered = series_list.copy()

    if category:
        series_filtered = [
            s for s in series_filtered if s.category.lower() == category.lower()
        ]
    if name:
        series_filtered = [s for s in series_filtered if name.lower() in s.name.lower()]
    if id:
        series_filtered = [s for s in series_filtered if s.id == id]

    for i, series in enumerate(series_filtered, 1):
        print(f"{series.name} ({i}/{len(series_filtered)})")
        series.synchronize()

    data.save(series_list)


@cli.command(help="add new series")
@click.argument("series_id", type=int)
@click.option("-l", "--language", default="en", help="Language code (default: en)")
def add(series_id, language):
    print(f"Looking up series by id {series_id}")

    series_list = data.load()
    if any(s.id == series_id for s in series_list):
        print(f"Series {series_id} is already being tracked")
        exit()

    series = data.Series.new(series_id, language)
    series_list.append(series)
    data.save(series_list)
    print(f"Added series {series.name} with default category {series.category}")


@cli.command(help="set properties on the given series")
@click.argument("series", nargs=-1)
@click.option("-c", "--category", help="category")
@click.option("-s", "--seen", help="last seen episode")
@click.option("-l", "--language", help="language")
def set(series, category, seen, language):
    try:
        series_list = data.load()
        query = " ".join(series)
        series = identify_series(query, series_list)
    except SeriesNotFound:
        print(f"Can not find any series with id or name {query}")
        exit()

    if category:
        series.category = category

    if seen:
        if seen.lower() == "next":
            if not series.seen:
                seen_episode = data.Episode(1, 1)
            else:
                seen_episode = data.Episode(*data.parse_episode(series.seen))
                index = series.episodes.index(seen_episode)
                try:
                    seen_episode = series.episodes[index + 1]
                except IndexError:
                    print(f"{seen_episode} is the last episode in {series.name}")
        else:
            seen_episode = data.Episode(*data.parse_episode(seen.upper()))

        if not any([seen_episode == e for e in series.episodes]):
            print(f"{series.name} does not have an episode {seen_episode}")
        else:
            series.seen = str(seen_episode)

    if language:
        series.language = language

    data.save(series_list)
    print_table([series])


@cli.command(help="shortcut to increment seen episode for given series")
@click.argument("series", nargs=-1)
@click.pass_context
def seen(context, series):
    context.invoke(set, series=series, seen="next")


@cli.command(help="list available episodes for given series")
@click.argument("series", nargs=-1)
def episodes(series):
    try:
        query = " ".join(series)
        series = identify_series(query, data.load())
    except SeriesNotFound:
        print(f"Can not find any series with id or name {query}")

    height = max(e.episode for e in series.episodes)
    width = max(e.season for e in series.episodes)
    table = [[""] * width for _ in range(height)]
    for episode in series.episodes:
        description = f"{episode} ({episode.aired})"
        if str(episode) == series.seen:
            description = f"{description} *seen*"
        table[episode.episode - 1][episode.season - 1] = description

    print(tabulate(table, headers=[f"Season {n + 1}" for n in range(len(table))]))
