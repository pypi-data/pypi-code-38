class MigrationMissingError(Exception):
    """Raised when 3Di model is missing migrations."""
    pass


class MigrationTooHighError(Exception):
    """Raised when 3Di model has applied more migrations than expected.

    The expected migration id and name for the 3Di model is configured in
    threedi_modelchecker.threedi_model.constants in LATEST_MIGRATION_ID and
    LATEST_MIGRATION_NAME.
    """
    pass


class MigrationNameError(Exception):
    """Raised when last migration name is unexpected"""
    pass
