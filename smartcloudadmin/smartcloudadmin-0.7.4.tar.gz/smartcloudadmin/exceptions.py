
class BssServerError(Exception):
    """todo: this
    e.g. Suspending an org that is already suspended.
    Activating an org that is already actives

    maybe trying to add sub when its deleted etc.
    """
    pass


class BssResourceNotFound(Exception):
    """todo: this
    e.g. Suspending an org that is already suspended.
    Activating an org that is already actives

    maybe trying to add sub when its deleted etc.
    """
    pass


class BSSBadData(Exception):  # 5XX
    """todo: this
    e.g. Suspending an org that is already suspended.
    Activating an org that is already actives

    maybe trying to add sub when its deleted etc.
    """
    pass
