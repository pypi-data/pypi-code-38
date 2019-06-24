import click

from zenroom import zenroom


@click.command()
@click.option("-d", "--data", help="Data passed to zenroom", type=click.File("rb"))
@click.option("-k", "--keys", help="Keys passed to zenroom", type=click.File("rb"))
@click.argument("script", type=click.File("rb"), default="-", required=True)
def main(data, keys, script):
    data = data.read().decode() if data else None
    keys = keys.read().decode() if keys else None
    script = script.read().decode()
    result, _ = zenroom.zencode_exec(script=script, data=data, keys=keys)
    print(result)
    print(_)
