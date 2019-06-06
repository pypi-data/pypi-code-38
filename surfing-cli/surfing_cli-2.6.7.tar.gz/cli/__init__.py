import click


def info(content):
    click.echo(click.style(content, "green"))


def warning(content):
    click.echo(click.style(content, "yellow"))


def error(content):
    click.echo(click.style(content, "red"))
