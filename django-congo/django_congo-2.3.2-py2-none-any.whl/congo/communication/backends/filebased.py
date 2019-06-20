# -*- coding: utf-8 -*-
from django.core.mail.backends.filebased import EmailBackend as DjangoEmailBackend
from django.utils.crypto import get_random_string
import datetime
import os

class EmailBackend(DjangoEmailBackend):
    def _get_filename(self):
        """Return a unique file name."""
        if self._fname is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = "%s-%s.eml" % (timestamp, get_random_string(4, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
            self._fname = os.path.join(self.file_path, filename)
        return self._fname
