

import importlib

import click


def generate_menu(
    extractor,
    override_name=None, override_url=None, **kwargs,
):
    """
    Call given extractor. Generate series of Markdown lines with
    menu of given restaurant. Pass any other keyword arguments to
    the extractor.
    Catch most exceptions, write them nicely.
    """
    try:
        e = importlib.import_module(".extractors." + extractor, __package__)
        name = override_name or e.get_name(**kwargs)
        url = override_url or e.get_url(**kwargs)
        title = "[{name}]({url})".format(name=name, url=url)
        yield title
        yield "-"*len(title)
        yield ""
        for meal, price in e.get_menu(**kwargs):
            yield "*  {meal} {price}". format(meal=meal, price=price)
    except ImportError as err:
        yield "Cannot import {extractor}: {err}".format(
            extractor=extractor, err=err,
        )
    except (AttributeError, ValueError) as err:
        yield "Error: {err}".format(err=err)
    yield ""


@click.command()
@click.option("--place-id", "-i", help="Extractor-specific place ID")
@click.option(
    "--option", "-o", help="Extractor-specific key-value option",
    multiple=True, type=(str, str), metavar="<KEY VALUE>…",
)
@click.argument("extractor")
def print_menu(extractor, place_id, option):
    """
    Print daily menu for a place identified by an extractor and
    optional extractor-dependent place_id.
    """
    kwargs = dict(option)
    if place_id:
        kwargs["place_id"] = place_id
    for line in generate_menu(extractor, **kwargs):
        print(line)
