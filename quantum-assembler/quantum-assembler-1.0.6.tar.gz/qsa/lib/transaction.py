import contextlib


class Transaction:

    def __init__(self):
        self.statements = []
        self.committed = []

    def add(self, commit, rollback=None):
        """Add a new statement to the transaction."""
        self.statements.append([commit, rollback])

    def commit(self):
        """Executes all statements in the transaction."""
        for commit, rollback in self.statements:
            commit()
            if rollback:
                self.committed.append(rollback)

    def rollback(self):
        """Rollback all operations if they have defined a function
        for it.
        """
        for rollback in self.committed:
            if rollback is None:
                continue
            rollback()


@contextlib.contextmanager
def atomic():
    """Returns a context-guard that ensures that all invocations
    finish succesfully or not at all.
    """
    tx = Transaction()
    try:
        yield tx
        tx.commit()
    except Exception:
        tx.rollback()
        raise
