# -*- coding: utf-8 -*-

from l10n_ar_api.documents import tribute
import pytest


class TestTribute:

    def test_invalid_type(self):
        with pytest.raises(NotImplementedError):
            tribute.Tribute.get_tribute('invalid_retention')
