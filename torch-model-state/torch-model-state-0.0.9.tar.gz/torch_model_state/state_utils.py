import datetime
import logging
from pathlib import Path
from typing import List, Union

import box
import torch
import torch.nn as nn
from torch.optim import Optimizer

from .configs import StateFile


def save_state_file(state: StateFile, file_path: Union[str, Path]):
    Path(file_path).parent.mkdir(exist_ok=True, parents=True)
    torch.save(vars(state), str(file_path))


def load_state_file(file_path: Union[str, Path], device: str = 'cuda') -> StateFile:
    checkpoint = torch.load(str(file_path),
                            map_location=(lambda tensor, _: tensor.cuda()) if device == 'cuda' else device)
    return StateFile(checkpoint)


def to_state(model: nn.Module, config: dict = None, optimizers: List[Optimizer] = (), info: dict = None) -> StateFile:
    state = StateFile()
    state.model = model.state_dict()
    state.config = config
    state.optimizers = [optimizer.state_dict() for optimizer in optimizers]
    state.info = info
    state.timestamp = str(datetime.datetime.now())
    return state


def from_state(state: StateFile, model: nn.Module = None, optimizers: List[Optimizer] = (),
               device: str = 'cuda', strict: bool = True) -> nn.Module:
    if model is None:
        model: nn.Module = box.factory(state.config, tag='model').to(device)
    model.load_state_dict(state.model, strict=strict)
    if not strict:  # pragma: no cover
        model_keys = set(model.state_dict().keys())
        saved_keys = state.model.keys()
        missing_keys = model_keys - saved_keys
        if missing_keys:
            logging.warning('caution: model state missing keys {}'.format(list(missing_keys)))
    for optimizer, state_dict in zip(optimizers, state.optimizers):
        optimizer.load_state_dict(state_dict)
    return model


def load_model_from_state(file_path: Union[str, Path], device: str = 'cuda', strict: bool = True) -> nn.Module:
    state = load_state_file(file_path=file_path, device=device)
    return from_state(state=state, device=device, strict=strict)
