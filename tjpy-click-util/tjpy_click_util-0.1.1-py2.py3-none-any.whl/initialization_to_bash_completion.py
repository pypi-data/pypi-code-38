from typing import Callable

import click._bashcomplete as internal_click_bashcomplete

from tjpy_click_util.autocomplete_mode_detection import set_autocomplete_mode

_original_click_get_choices_function = internal_click_bashcomplete.get_choices
assert _original_click_get_choices_function is not None


def set_initialization_function_on_auto_completion(initialization_fn: Callable[[], None]):
    def _overwritten_click_get_choices(*args):
        set_autocomplete_mode(True)
        initialization_fn()
        return _original_click_get_choices_function(*args)

    # TODO tjahoda replace hacky patch of click bash completion by creating pull request in Click
    internal_click_bashcomplete.get_choices = _overwritten_click_get_choices
