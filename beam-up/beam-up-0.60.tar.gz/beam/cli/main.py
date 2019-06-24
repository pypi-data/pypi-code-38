#!/usr/bin/env python3
import click
import logging

from beam.cli import commands

@click.group()
@click.option('-v', '--verbose', count=True)
def beam(verbose):
    #we want to always show errors and warnings
    if verbose == 0:
        verbose = 1
    levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(verbose,len(levels)-1)]
    logging.basicConfig(level=level, format='%(message)s')

for command in commands:
    beam.add_command(command)

if __name__ == '__main__':
    beam()