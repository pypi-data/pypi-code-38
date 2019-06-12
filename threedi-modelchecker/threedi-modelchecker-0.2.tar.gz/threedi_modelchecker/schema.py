from sqlalchemy import func

from .threedi_model import constants
from .threedi_model import models
from .errors import MigrationMissingError
from .errors import MigrationTooHighError
from .errors import MigrationNameError


class ModelSchema:
    def __init__(self, threedi_db, declared_models=models.DECLARED_MODELS):
        self.db = threedi_db
        self.declared_models = declared_models

    def _latest_migration(self):
        """Returns a tuple with latest migration id and name"""
        session = self.db.get_session()
        latest_migration_id = session.query(
            func.max(models.SouthMigrationHistory.id)
        ).scalar()
        latest_migration_name = (
            session.query(models.SouthMigrationHistory.migration)
            .filter(models.SouthMigrationHistory.id == latest_migration_id)
            .scalar()
        )
        return latest_migration_id, latest_migration_name

    def validate_schema(self):
        """Very basic validation of 3Di schema.

        Check that the database has the latest migration applied. If the
        latest migrations is applied, we assume the database also contains all
        tables and columns defined in threedi_model.models.py.

        :return: True if the threedi_db schema is valid, raises an error otherwise.
        :raise MigrationMissingError, MigrationTooHighError, MigrationNameError
        """
        migration_id, migration_name = self._latest_migration()
        if (migration_id is None
                or migration_id < constants.LATEST_MIGRATION_ID):
            raise MigrationMissingError
        elif migration_id > constants.LATEST_MIGRATION_ID:
            raise MigrationTooHighError
        elif migration_name != constants.LATEST_MIGRATION_NAME:
            raise MigrationNameError
        return (migration_id == constants.LATEST_MIGRATION_ID
                and migration_name == constants.LATEST_MIGRATION_NAME)

    def get_missing_tables(self):
        pass

    def get_missing_columns(self):
        pass
