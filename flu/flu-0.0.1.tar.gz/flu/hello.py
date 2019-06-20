import click
from colors import all_colors

@click.command()
@click.option('--name',prompt='Your good name?', default='World',help='your name')
def hello(name):
    click.echo('Hello, {}!'.format(name))

    for color in all_colors:
        click.echo(click.style('I am colored %s' % color, fg=color))
    for color in all_colors:
        click.echo(click.style('I am colored %s and bold' % color,
                               fg=color, bold=True))
    for color in all_colors:
        click.echo(click.style('I am reverse colored %s' % color, fg=color,
                               reverse=True))

    click.echo(click.style('I am blinking', blink=True))
    click.echo(click.style('I am underlined', underline=True))