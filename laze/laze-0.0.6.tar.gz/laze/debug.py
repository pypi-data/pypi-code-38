active_debug_levels = {"info", "uses", "verbose"}


def dprint(level, *args, **kwargs):
    if level in active_debug_levels:
        print(*args, **kwargs)
