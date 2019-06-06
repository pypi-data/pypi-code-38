"""
Error types that support the `microcosm-flask` conventions.

"""


class Neo4JError(Exception):
    @property
    def status_code(self):
        # internal server error
        return 500


class ModelIntegrityError(Neo4JError):
    """
    An attempt to create or update a model violated a schema constraint.

    Usually the result of a programming error.

    """
    pass


class DuplicateModelError(ModelIntegrityError):
    """
    An attempt to create or update a module violated a uniqueness constraint.

    Unlike `ModelIntegrityError`, duplicates are often expected behavior.

    """
    @property
    def status_code(self):
        # conflict
        return 409

    @property
    def include_stack_trace(self):
        return False


class MissingDependencyError(ModelIntegrityError):
    """
    An attempt to create a model didn't first create a depedency.

    """
    @property
    def status_code(self):
        # not found
        return 404

    @property
    def include_stack_trace(self):
        return False


class NoSuchConstraintError(Neo4JError):
    pass


class NoSuchIndexError(Neo4JError):
    pass


class NotFoundError(Neo4JError):
    @property
    def status_code(self):
        return 404
