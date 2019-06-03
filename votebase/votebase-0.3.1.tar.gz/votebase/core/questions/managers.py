from django.db import models


class OptionQuerySet(models.query.QuerySet):
    def by_question(self, question):
        """ Gets options in question """
        return self.filter(question=question)

    def rows_by_question(self, question):
        """ Gets row options in question """
        return self.by_question(question).filter(
            orientation=self.model.ORIENTATION_ROW)

    def columns_by_question(self, question):
        """ Gets column options in question """
        return self.by_question(question).filter(
            orientation=self.model.ORIENTATION_COLUMN)

    def orientation_row(self):
        return self.filter(orientation=self.model.ORIENTATION_ROW)

    def orientation_column(self):
        return self.filter(orientation=self.model.ORIENTATION_COLUMN)

    def prepare_as_list(self):
        return self.values_list('id', 'title')

    def correct(self, question):
        return self.filter(question=question, is_correct=True)
