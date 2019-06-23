# coding=utf-8

# pylint: disable=missing-docstring


from django.test import TestCase

from . import models


class TestModels(TestCase):

    def setUp(self):
        self.default_language = None
        self.block_type = models.PageBlock.objects.create(
            block_type="__TEST__"
        )

    def test_test_not_existent_type(self):
        self.assertIsNone(
            models.PageBlock.objects.get_language_version("__not_existent__", "en")
        )

    def test_type_without_transactions(self):
        self.assertIsNone(
            models.PageBlock.objects.get_language_version(
                "__TEST__", "en"
            )
        )

    def create_default_language(self):
        self.default_language = models.PageBlockTranslation.objects.create(
            page_block=self.block_type,
            language="en",
            default_translation=True,
            title="Workforce description",
            contents_md="Something **strong**"
        )

    def test_default_language(self):
        self.create_default_language()
        actual = models.PageBlock.objects.get_language_version(
            "__TEST__", "en"
        )
        self.assertEqual(self.default_language, actual)

    def test_fallback_to_default(self):
        self.create_default_language()
        actual = models.PageBlock.objects.get_language_version(
            "__TEST__", "pl"
        )
        self.assertEqual(self.default_language, actual)

    def test_get_different_language(self):
        self.create_default_language()
        polish = models.PageBlockTranslation.objects.create(
            page_block=self.block_type,
            language="pl",
            default_translation=False,
            title="Workforce description",
            contents_md="Something"
        )
        actual = models.PageBlock.objects.get_language_version(
            "__TEST__", "pl"
        )
        self.assertEqual(polish, actual)

    def test_convert_markdown(self):
        self.create_default_language()
        self.assertEqual(
            self.default_language.contents_html,
            "<p>Something <strong>strong</strong></p>"
        )

    def test_update_default_translation(self):
        self.create_default_language()
        models.PageBlockTranslation.objects.create(
            page_block=self.block_type,
            language="pl",
            default_translation=True,
            title="Workforce description",
            contents_md="Something"
        )
        self.default_language.refresh_from_db()
        self.assertFalse(self.default_language.default_translation, False)

    def test_block_str(self):
        self.assertEqual(
            self.block_type.block_type,
            str(self.block_type)
        )
