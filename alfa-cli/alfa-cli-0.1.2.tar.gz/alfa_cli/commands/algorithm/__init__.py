import click
from alfa_sdk import AlgorithmClient
from alfa_cli.common.factories import create_session
from alfa_cli.commands.algorithm import deploy, invoke


@click.group()
@click.pass_context
def algorithm(ctx):
    """Manage algorithms deployed in ALFA."""
    session = create_session()
    ctx.obj["client"] = AlgorithmClient(session=session)


algorithm.add_command(deploy.deploy)
algorithm.add_command(invoke.invoke)
algorithm.add_command(invoke.invoke_local)
