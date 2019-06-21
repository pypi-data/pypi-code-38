#!/usr/bin/env python

# Copyright 2018 Intel Corporation.
"""Reads an ONNX model, and writes it as a TILE file."""

import click
import onnx
import onnx_plaidml.backend


@click.command()
@click.argument(
    'onnx_model_filename',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    metavar='<onnx_filename>')
@click.argument(
    'tile_filename', type=click.Path(dir_okay=False, writable=True), metavar='<tile_filename>')
def onnx_to_tile(onnx_model_filename, tile_filename):
    """Reads an ONNX model, and writes it as a TILE file."""
    model = onnx.load(onnx_model_filename)
    rep = onnx_plaidml.backend.prepare(model)
    rep.save(tile_filename)


if __name__ == '__main__':
    onnx_to_tile()
