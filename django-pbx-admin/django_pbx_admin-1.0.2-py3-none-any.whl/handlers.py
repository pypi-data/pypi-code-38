from typing import Tuple, Any

from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.utils.html import format_html, format_html_join


def default_protected_error_handler(
    protected_error: ProtectedError, instance: Any
) -> Tuple[int, str]:
    """
    Handle protected error exception
    :param protected_error: exception raised on deleting protected objects
    :param instance: instance to delete
    :return: tuple of error level and message
    """
    protected_list = []
    for po in protected_error.protected_objects:
        protected = f'{po._meta.verbose_name} "{po}", id: {po.pk}'
        if protected not in protected_list:
            protected_list.append(protected)
        if len(protected_list) > 10:
            protected_list.append("...")
            break

    level = messages.ERROR
    message = format_html(
        "<p>{}</p><ul>{}</ul>",
        format_html(
            "Object <strong>{}</strong> could not be deleted "
            "because it is used in the following objects:",
            instance,
        ),
        format_html_join("", "<li>{}</li>", ((p,) for p in protected_list)),
    )
    return level, message
