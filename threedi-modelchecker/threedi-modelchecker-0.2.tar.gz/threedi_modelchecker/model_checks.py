from .schema import ModelSchema
from .config import Config


class ThreediModelChecker:
    def __init__(self, threedi_db):
        self.db = threedi_db
        self.schema = ModelSchema(self.db)
        self.schema.validate_schema()
        self.config = Config(self.models)

    @property
    def models(self):
        """Returns a list of declared models"""
        return self.schema.declared_models

    def errors(self):
        """Iterates and applies checks, returning any failing rows.

        :return: Tuple of the applied check and the failing row.
        """
        session = self.db.get_session()
        for check in self.checks():
            model_errors = check.get_invalid(session)
            for error_row in model_errors:
                yield check, error_row

    def checks(self):
        """Iterates over all configured checks

        :return: implementations of BaseChecks
        """
        for check in self.config.checks:
            yield check

    def check_table(self, table):
        pass

    def check_column(self, column):
        pass
