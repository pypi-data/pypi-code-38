import click
import models.settings.config as config


@click.group()
def general_commands_cli():
    pass


#get to version code
@general_commands_cli.command()
def version():
    click.echo(config.version_code
               )

#get to build version code
@general_commands_cli.command()
def build_version():
    click.echo(config.build_version_code
               )

#get to version code
@general_commands_cli.command()
def info():
    config.show_system_info()

#get to version name
@general_commands_cli.command()
def version_name():
    try:
        click.echo(config.get_version_name())

        pass
    except Exception as e:
        click.echo(str(e)
                   )


@general_commands_cli.command()
@click.option('--name', required=True, type=str)
@click.option('--age', required=False, type=int)
def input_params(name, age):
    click.echo("Name = " + name + "; age = " + str(age)
               )
