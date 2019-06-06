"""
Session context management.

"""
from contextlib import contextmanager
from functools import wraps

from neo4j import (
    READ_ACCESS,
    WRITE_ACCESS,
    Driver,
    Session,
    unit_of_work,
)


class SessionContext:
    """
    Save current session in well-known location and provide context management.

    """
    _driver: Driver = None
    session: Session = None

    def __init__(self, graph):
        self.graph = graph

    @property
    def driver(self):
        """
        Lazily construct or retrieve a single Neo4j Driver instance.

        We do this lazily this way to be worker-process safe in the uwsgi environment.
        It is *not* safe to initialize the Driver before the worker processes of uwsgi fork,
        which would be the case if we eagerly create it in import time / as part of the create_app
        invocation which is the wsgi entry point and is invoked pre-forking.

        """
        if not getattr(SessionContext, "_driver", None):
            SessionContext._driver = self.graph.neo4j()
        return SessionContext._driver

    def open(self):
        """
        Create a new session and transaction.

        Always run in transactional mode; otherwise the session will auto-commit.

        """
        SessionContext.session = self.driver.session()
        SessionContext.session.begin_transaction()
        return self

    def close(self):
        """
        Close the session.

        Without `transaction`, closing will rollback writes.

        """
        if SessionContext.session:
            SessionContext.session.close()
            SessionContext.session = None

    # session factory

    @classmethod
    def make(cls, graph):
        return cls(graph).open()

    # unit test shortcut

    def recreate_all(self):
        self.graph.neo4j_schema_manager.recreate_all()

    # context manager

    def __enter__(self):
        return self.open()

    def __exit__(self, *args, **kwargs):
        self.close()


class LightSessionContext:
    """
    Light-weight session that does not explicitly create transactions
    but with explicit access control for efficiency.

    """
    _driver: Driver = None
    session: Session = None

    def __init__(self, graph):
        self.graph = graph

    @property
    def driver(self):
        """
        Lazily construct or retrieve a single Neo4j Driver instance.

        We do this lazily this way to be worker-process safe in the uwsgi environment.
        It is *not* safe to initialize the Driver before the worker processes of uwsgi fork,
        which would be the case if we eagerly create it in import time / as part of the create_app
        invocation which is the wsgi entry point and is invoked pre-forking.

        """
        if not getattr(SessionContext, "_driver", None):
            SessionContext._driver = self.graph.neo4j()
        return SessionContext._driver

    def open(self):
        """
        Create a new session, but not transaction.

        """
        LightSessionContext.session = self.driver.session()
        return self

    def close(self):
        """
        Close the session.

        """
        if LightSessionContext.session:
            LightSessionContext.session.close()
            LightSessionContext.session = None

    def __enter__(self):
        return self.open()

    def __exit__(self, *args, **kwargs):
        self.close()

    def run_transaction(
            self,
            statement,
            parameters=None,
            access_mode="READ",
            **kwargs):

        assert(access_mode in ["READ", "WRITE"]), "Access mode must be in 'READ' or 'WRITE'"
        access_mode = READ_ACCESS if access_mode == "READ" else WRITE_ACCESS
        parameters = parameters or {}

        @unit_of_work()
        def exec_query(tx):
            return tx.run(
                statement,
                **parameters,
            )

        LightSessionContext.session._assert_open()
        return LightSessionContext.session._run_transaction(
            access_mode=access_mode,
            unit_of_work=exec_query,
            **kwargs,
        )


@contextmanager
def transaction():
    """
    Wrap a context with a commit/rollback.

    """
    try:
        # NB: In the local Flask development server, using per-process session state is unsafe.
        # Concurrent session operations may interleave and reset the session reference.
        assert SessionContext.session, "No Neo4J session: check your concurrency"
        if not SessionContext.session.has_transaction():
            SessionContext.session.begin_transaction()
        yield SessionContext.session
        SessionContext.session.commit_transaction()
    except Exception:
        if SessionContext.session and SessionContext.session.has_transaction():
            SessionContext.session.rollback_transaction()
        raise


def transactional(func):
    """
    Decorate a function call with a commit/rollback and pass the session as the first arg.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with transaction():
            return func(*args, **kwargs)
    return wrapper
