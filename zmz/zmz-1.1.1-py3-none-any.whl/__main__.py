import click

from zmz.utility.api import API
from zmz.utility.helper import Helper


@click.group()
def main():
    pass


@click.command()
@click.argument('keyword')
def search(keyword):
    """Search resources by keyword."""
    if keyword is None:
        click.echo('You must enter some keywords to search resources.')
        return

    results = API.search(keyword)
    Helper.print_results(results)


@click.command()
@click.argument('resource_id')
def link(resource_id):
    """Fetch resource download links by ID."""
    if resource_id is None:
        click.echo('You must enter resource id for fetching download links.')
        return

    resource = API.fetch_resource(resource_id)
    Helper.print_download_links(resource)


# add command to group
main.add_command(search)
main.add_command(link)


if __name__ == "__main__":
    main()
