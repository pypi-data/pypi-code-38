import platform


_system = platform.system().lower()
_version = platform.version()


# TODO: Bundle fontawesome with the notifier, for a large set of default icons.


if platform == "darwin":
    # `plyer` doesn't support Mac, so we have to use a fallback.
    from delivery.mac import notify
else:
    from delivery.default import notify
