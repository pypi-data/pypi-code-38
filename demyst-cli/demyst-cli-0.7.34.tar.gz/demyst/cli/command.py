#!/usr/bin/env python3

import os
import sys
import json
import click

@click.group()
def cli():
    pass

@cli.command()
def my_first_command():
    print("LIVE")
