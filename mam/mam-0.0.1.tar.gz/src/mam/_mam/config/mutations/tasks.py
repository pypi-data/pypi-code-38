"""Handle merging tasks."""

import collections
import logging
from typing import (
    Dict, Iterable, Iterator, List, Optional, Set, Tuple,
)

from .typings import Task
from ...core.configs import MutationInfo
from ...core.objects import Format

__all__ = [
    'handle_tasks',
]

# nosa(1): pylint[C0103]
logger = logging.getLogger(__name__)


def _build_tasks(orig: List[Task],
                 parents: Dict[str, Task],
                 info: MutationInfo,
                 ) -> Tuple[Set[str], List[Task]]:
    base = info.config.root().output.get('base', {})
    used_parents = set()
    tasks = []
    for task in orig:
        if task.get('base', None) is not None:
            used_parents.add(task['base'])

        base_name = task.get('base')
        if base_name is None:
            parent_ = base
        elif not isinstance(base_name, str):
            raise ValueError('Task base can only be strings.')
        else:
            parent_ = parents.get(base_name, base)

        name = task.get('name') or parent_.get('name')
        if not isinstance(name, str):
            raise ValueError('Task name can only be strings.')
        tasks.append(info.merge(
            task,
            parent_,
            name,
        ))
    return used_parents, tasks


def _handle_tasks(tasks: Iterable[Task],
                  ) -> Iterator[Task]:
    for task_ in tasks:
        task_.pop('base', None)
        if task_.get('name', None) is None:
            raise ValueError('All tasks must define a name.')
        yield task_


def _tasks_to_mapping(tasks: Iterable[Task],
                      ) -> Dict[str, Task]:
    mapping: Dict[str, Task] = collections.OrderedDict()
    for task in tasks:
        if task['name'] in mapping:
            raise ValueError('Config defines two tasks with the same name.')

        mapping[task['name']] = task
    return mapping


def _gen_output_mapping(parents: Dict[str, Task],
                        info: MutationInfo,
                        ) -> Dict[str, Task]:
    if info.root:
        parents = {}
    return collections.OrderedDict(parents)


def _add_tasks(mapping: Dict[str, Task],
               output_mapping: Dict[str, Task],
               used_parents: Set[str],
               ) -> None:
    for name, task in mapping.items():
        if name in output_mapping and name not in used_parents:
            logger.warning(Format(
                'Overwriting uninherited parent {name}',
                name=name,
            ))
        output_mapping[name] = task


def handle_tasks(orig: Optional[List[Task]],
                 parent: Optional[List[Task]],
                 *,
                 info: MutationInfo,
                 ) -> List[Task]:
    """Merge tasks."""
    parents = _tasks_to_mapping(parent or [])
    output_mapping = _gen_output_mapping(parents, info)
    used_parents, tasks_ = _build_tasks(orig or [], parents, info)
    mapping = _tasks_to_mapping(_handle_tasks(tasks_))
    _add_tasks(mapping, output_mapping, used_parents)
    return list(output_mapping.values())
