import click
from datetime import datetime

def click_echo(message, with_timestamp=True):
    if with_timestamp:
        timestamp = datetime.now().strftime("%H:%M:%S")
        click.echo("{} {}".format(timestamp, message))
    else:
        click.echo(message)

def check_result(command, result):
    if result.failure():
        click_echo("Could not {}:\n{}".format(command, result.output))
    elif len(result.output) > 0:
        click_echo(result.output)
    return result.returncode
