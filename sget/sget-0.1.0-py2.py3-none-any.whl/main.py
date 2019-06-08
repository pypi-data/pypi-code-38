import click


from sget import api
from sget.prompt import prompt
from sget.storage import SnippetNotFoundError


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        run()


@cli.command()
@click.argument('content', type=str, nargs=-1)
@click.option('-d', '--description', prompt=True)
@click.option('-n', '--name', prompt=True)
@click.option('-g', '--groups', prompt=True, default='')
def add(content, description, name, groups):
    if groups:
        groups = groups.strip().split(',')
    content = ' '.join(content)
    try:
        api.add(content, description, name, groups)
        msg = 'Snippet successfully added!'
        _success(msg)
    except IOError as err:
        _error(str(err))


@cli.command()
@click.argument('snippet_file', type=click.File('r'), nargs=1)
@click.option('-d', '--description', prompt=True)
@click.option('-n', '--name', prompt=True)
@click.option('-g', '--groups', prompt=True, default='')
def fadd(snippet_file, description, name, groups):
    if groups:
        groups = groups.strip().split(',')
    try:
        api.fadd(snippet_file, description, name, groups)
        msg = 'Snippet successfully added!'
        _success(msg)
    except IOError as err:
        _error(str(err))


@cli.command()
@click.argument('name', default=None, required=False)
def rm(name):
    try:
        api.rm(name)
        msg = 'Snippet successfully removed!'
        _success(msg)
    except SnippetNotFoundError as err:
        _error(str(err))


@cli.command()
@click.argument('name', default=None, required=False)
def run(name):
    try:
        api.run(name)
    except SnippetNotFoundError as err:
        _error(str(err))


@cli.command()
def edit():
    api.edit_snippets()


@cli.command()
@click.argument('name', default=None, required=False)
def cp(name):
    try:
        api.cp(name)
        _success('Copied snippet to clipboard')
    except SnippetNotFoundError as err:
        _error(str(err))


@cli.command()
@click.argument('snippets_file', type=click.File('r'), nargs=1)
def install(snippets_file):
    errors = api.install(snippets_file)
    if errors:
        _error('\n'.join(errors))
    else:
        _success('Successfully installed all snippets!')


@cli.command()
def clear():
    msg = 'You are about to clear all your saved snippets, are you sure?'
    if prompt.confirm(msg):
        api.clear()
        _success('Cleared all snippets!')


@cli.command()
@click.option('-g', '--group', default=None)
def list(group):
    try:
        collection = api.get_all(group=group)
    except LookupError:
        _error('No such group {}'.format(group))
    else:
        for grp in collection.groups():
            click.echo(click.style(grp, fg='cyan'))
            for snippet in collection.get_group(grp):
                name = _add_tab('Name - {}'.format(snippet.name))
                desc = _add_tab('Description - {}'.format(snippet.description))
                content = _add_tab(snippet.content)
                click.secho(name, fg='red')
                click.secho(desc, fg='green')
                click.secho(content, fg='yellow')
                click.echo('\n')


def _add_tab(text):
    text = '\t' + text
    return text.replace('\n', '\n\t')


def _success(msg):
    click.echo(click.style(msg, fg='green'))


def _error(msg):
    click.echo(click.style(msg, fg='red'))


if __name__ == '__main__':
    cli()
