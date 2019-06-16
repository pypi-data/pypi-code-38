"""Nox helpers."""

import json
import os
from typing import Any, Dict, Iterator, Optional, Tuple

from ..format.helpers import Converter
from ...core.objects import ALL, Message
from ...keys import TTask, Task

__all__ = [
    'run',
    'write_output',
]


def run(session, *args: Any, **kwargs: Any) -> Tuple[Optional[int], str]:
    """Run nox command."""
    ret = session.run(*args, **kwargs, silent=True, success_codes=ALL)
    return ALL.last, ret


def write_output(task: TTask, output: str,
                 converter: Converter[str, Iterator[Message]],
                 posargs: Dict[Any, Any],
                 ) -> None:
    """Convert information to output."""
    path = posargs[0] + os.path.sep
    with open(path + task[Task.NAME] + '.json', 'w') as output_file:
        json.dump([m.to_dict() for m in converter(task, output)], output_file)
