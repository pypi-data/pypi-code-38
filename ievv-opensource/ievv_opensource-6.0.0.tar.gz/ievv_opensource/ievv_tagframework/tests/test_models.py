from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy


class TestTagModel(TestCase):
    def test_clean_invalid_tagtype(self):
        testtag = mommy.prepare('ievv_tagframework.Tag', tagtype='invalidstuff')
        with self.settings(IEVV_TAGFRAMEWORK_SITE_TYPE_CHOICES=[('', ''), ('mytype', 'My Type')]):
            with self.assertRaisesMessage(ValidationError,
                                          "Must be one of: '', 'mytype'. Current value: 'invalidstuff'."):
                testtag.clean()

    def test_clean_valid_tagtype(self):
        testtag = mommy.prepare('ievv_tagframework.Tag', tagtype='mytype')
        with self.settings(IEVV_TAGFRAMEWORK_SITE_TYPE_CHOICES=[('', ''), ('mytype', 'My Type')]):
            testtag.clean()  # No ValidationError
