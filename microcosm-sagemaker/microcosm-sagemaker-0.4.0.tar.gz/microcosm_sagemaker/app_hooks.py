from pkg_resources import iter_entry_points

from microcosm.object_graph import ObjectGraph

from microcosm_sagemaker.constants import (
    APP_HOOKS_GROUP,
    EVALUATE_APP_HOOK,
    SERVE_APP_HOOK,
    TRAIN_APP_HOOK,
)
from microcosm_sagemaker.exceptions import AppHookNotFoundError


def create_train_app(*args, **kwargs) -> ObjectGraph:
    return _create_app(TRAIN_APP_HOOK, args, kwargs)


def create_serve_app(*args, **kwargs) -> ObjectGraph:
    return _create_app(SERVE_APP_HOOK, args, kwargs)


def create_evaluate_app(*args, **kwargs) -> ObjectGraph:
    return _create_app(EVALUATE_APP_HOOK, args, kwargs)


def _create_app(name: str, args: tuple, kwargs: dict) -> ObjectGraph:
    try:
        entry_point = next(
            entry_point
            for entry_point in iter_entry_points(group=APP_HOOKS_GROUP)
            if entry_point.name == name
        )
    except StopIteration:
        raise AppHookNotFoundError(name)

    factory = entry_point.load()

    return factory(*args, **kwargs)
