"""
    This is a wrapper from invoke
"""
import logging
from invoke import Collection
from invoke import Program
from .bump_version import bump_version

logging.basicConfig(level=logging.INFO)

ns = Collection()
ns.add_task(bump_version)

program = Program(version="0.0.46", namespace=ns)
