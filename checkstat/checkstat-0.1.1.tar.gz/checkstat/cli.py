import click
import checkstat


@click.command()
@click.argument('host')
def main(host):
    """CLI for checkstat package."""
    print('Status: ', end='')
    if checkstat.is_up(host):
        click.secho('Up and running.', bold=True, fg='green')
    else:
        click.secho('Server is down.', bold=True, fg='red')


if __name__ == '__main__':
    main()
