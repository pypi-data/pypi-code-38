from algonaut.settings import settings
import datetime
import re

class InFuture():

    def __call__(self, name, value, form, field):
        if value < datetime.datetime.utcnow():
            return [form.t('access-tokens.valid-until-in-past')], None, True
        return [], value, False
