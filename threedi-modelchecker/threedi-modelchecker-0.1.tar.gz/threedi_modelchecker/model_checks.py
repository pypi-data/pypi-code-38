from .schema import ModelSchema
from .config import Config


class ThreediModelChecker:
    def __init__(self, threedi_db):
        self.db = threedi_db
        self.schema = ModelSchema(self.db)
        self.config = Config(self.models)

    @property
    def models(self):
        return self.schema.declared_models

    def get_model_errors(self):
        model_errors = []
        session = self.db.get_session()
        for check in self.config.checks:
            model_errors += check.get_invalid(session)
        return model_errors

    def get_model_error_iterator(self):
        session = self.db.get_session()
        for check in self.config.checks:
            model_errors = check.get_invalid(session)
            for error_row in model_errors:
                yield check, error_row

    def check_table(self, table):
        pass

    def check_column(self, column):
        pass

    def apply(self, check):
        """Applies the check and returns any invalid rows"""
        return check.get_invalid(self.db.get_session())
