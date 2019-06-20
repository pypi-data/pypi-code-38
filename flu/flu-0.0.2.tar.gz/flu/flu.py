import click
from hello import hello

# top level cmd for calling Flu
@click.group()
def flu():
    """CLI to generate beautiful & optimised website scaffolds"""
    pass

# sub commands supported by flu
flu.add_command(hello)

def main():
    flu()
