from typing import Optional

_autocomplete_mode: Optional[bool] = None


def is_autocomplete_mode() -> bool:
    if _autocomplete_mode is None:
        raise Exception("whether automcomplete mode is used has not been determined, "
                        "call set_autocomplete_mode during application initialization "
                        "and autocompletion initialization hook with respective values")
    return _autocomplete_mode


def set_autocomplete_mode(autocomplete_mode: bool):
    global _autocomplete_mode
    _autocomplete_mode = autocomplete_mode
