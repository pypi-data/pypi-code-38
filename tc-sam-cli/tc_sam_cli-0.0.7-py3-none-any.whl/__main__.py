#!/usr/bin/env python
import json
import sys
from operator import itemgetter

import click
import toml

import boto3
import samcli
import sh
import tclambda
import tclambda.auto_functions
from jinja2 import Environment, PackageLoader
from tclambda.function import LambdaFunction

from . import __version__

cloudformation = boto3.client("cloudformation")
version_message = "\n".join(
    [
        f"tcsamcli, version {__version__}",
        f"tclambda, version {tclambda.__version__}",
        f"aws-sam-cli, version {samcli.__version__}",
    ]
)


@click.group()
@click.version_option(message=version_message)
def cli():
    pass


@cli.command()
@click.option("--output", type=click.File("w"), default=sys.stdout)
def generate_template(output):
    with open("tc-sam.toml") as f:
        config = toml.load(f)

    loader = PackageLoader("tcsamcli", "templates")
    env = Environment(
        loader=loader, autoescape=False, keep_trailing_newline=True, trim_blocks=True
    )
    template = env.get_template("template.yaml.j2")
    output.write(
        template.render(
            config=config["Functions"], extra_policies=config.get("ExtraPolicies", [])
        )
    )


@cli.command()
@click.option(
    "--no-build", is_flag=True, default=False, help="Skip building the packages."
)
def deploy(**kwargs):
    with open("tc-sam.toml") as f:
        config = toml.load(f)

    stack_name = config["Default"]["StackName"]
    s3_bucket = config["Default"]["S3CodeBucket"]
    template_file = ".aws-sam/packaged.yaml"

    try:
        if not kwargs.get("no_build"):
            sh.sam.build(_fg=True)
        sh.sam.package(
            s3_bucket=s3_bucket, output_template_file=template_file, _fg=True
        )
        sh.sam.deploy(
            template_file=template_file,
            stack_name=stack_name,
            capabilities="CAPABILITY_IAM",
            _fg=True,
        )
    except Exception:
        pass


@cli.command()
@click.argument("module")
@click.option("--input-file", type=click.File("r"))
@click.option("--function-name")
@click.option("--args", type=json.loads, default="[]")
@click.option("--kwargs", type=json.loads, default="{}")
@click.option("--delay", type=float, default=5)
def invoke(module, input_file, function_name, args, kwargs, delay):
    lf = getattr(tclambda.auto_functions, module)
    if input_file:
        data = json.load(input_file)
        function_name = data["function_name"]
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})
    result = getattr(lf, function_name)(*args, **kwargs)
    click.echo_via_pager(
        json.dumps(result.result(delay=delay), indent=2, sort_keys=True)
    )


def environmental_variables():
    with open("tc-sam.toml") as f:
        config = toml.load(f)

    stack_name = config["Default"]["StackName"]
    response = cloudformation.describe_stacks(StackName=stack_name)
    stack = response["Stacks"][0]
    outputs = dict(map(itemgetter("OutputKey", "OutputValue"), stack["Outputs"]))
    result_bucket = outputs["ResultBucket"]
    for key, value in outputs.items():
        if key.endswith("Queue"):
            key = key[: -len("Queue")].upper()
            yield key, value, result_bucket


@cli.command()
@click.option("--env-vars", is_flag=True)
def env_export(env_vars):
    environmental_dict = {}
    for key, queue, result_bucket in environmental_variables():
        environmental_dict[f"TC_{key}_QUEUE"] = f"{queue}"
        environmental_dict[f"TC_{key}_BUCKET"] = f"{result_bucket}"

    if env_vars:
        with open("tc-sam.toml") as f:
            config = toml.load(f)
        obj = {}
        for function in config["Functions"].keys():
            obj[function] = {}
            obj[function].update(environmental_dict)
            obj[function]["TC_THIS_QUEUE"] = environmental_dict[
                f"TC_{function.upper()}_QUEUE"
            ]
            obj[function]["TC_THIS_BUCKET"] = environmental_dict[
                f"TC_{function.upper()}_BUCKET"
            ]

        click.echo(json.dumps(obj, indent=2, sort_keys=True))
    else:
        for key, value in environmental_dict.items():
            click.echo(f'{key}="{value}"')


@cli.command()
def ping():
    with open("tc-sam.toml") as f:
        config = toml.load(f)

    stack_name = config["Default"]["StackName"]
    response = cloudformation.describe_stacks(StackName=stack_name)
    stack = response["Stacks"][0]
    outputs = dict(map(itemgetter("OutputKey", "OutputValue"), stack["Outputs"]))
    result_bucket = outputs["ResultBucket"]
    pings = []
    for key, value in outputs.items():
        if key.endswith("Queue"):
            key = key[: -len("Queue")].upper()
            lf = LambdaFunction(value, result_bucket)
            result = lf.ping()
            pings.append((key, result))
            click.secho(f"Ping {key}")
    for key, ping in pings:
        try:
            if ping.result(delay=0.5) == "pong":
                click.secho(f"Pong {key}", fg="green")
            else:
                click.secho(f"No pong {key}: {ping.result()}")
        except TimeoutError as e:
            click.secho(f"Timeout {key}: {e}")
        except Exception as e:
            click.secho(f"Error {key}: {e}")


if __name__ == "__main__":
    cli()
