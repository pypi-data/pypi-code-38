import json
from pathlib import Path

import argparse_schema
import torch.onnx

from .configs import ArgumentConfig
from .state_utils import load_state_file, from_state


def cli_main():  # pragma: no cover
    with open(str(Path(__file__).parent / 'schema' / 'argument_config.json')) as f:
        schema = json.load(f)
    argument = ArgumentConfig(argparse_schema.parse(schema))

    state = load_state_file(argument.state_file, device=argument.device)

    if argument.extra_import:
        __import__(argument.extra_import)
    model = from_state(state, device=argument.device) if argument.load_model or argument.export_onnx else None

    del state.model
    del state.optimizers

    print(json.dumps(vars(state), indent=2))
    if argument.load_model:
        print(model)

    if argument.export_onnx:
        dummy_input = torch.randn(1, 3, argument.input_size, argument.input_size)
        torch.onnx.export(model, dummy_input, argument.export_onnx, verbose=argument.verbose)
