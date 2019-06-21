# TODO: What to do about the python dbus warning? `notify-send` should be fine.
from plyer import notification


from delivery.utils import DEFAULT_DURATION


# TODO: Default icon
def notify(title, message, app_name=None, icon=None, duration=DEFAULT_DURATION):
    # `plyer` will fail silently if an empty title is provided. Protect against
    # this by making it overt.
    if not title:
        # TODO: Extract this check into a generic module - don't duplicated
        # between platforms
        ValueError("Notifications may not have an empty title.")
    # TODO: Convert png icons to ico files on windows 10
    notification.notify(
        message=message, title=title, app_name=app_name, app_icon=icon, timeout=duration
    )
