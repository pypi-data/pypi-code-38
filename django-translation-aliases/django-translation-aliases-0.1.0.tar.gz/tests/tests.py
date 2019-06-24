from django.template.engine import Engine
from django.test import SimpleTestCase
from django.utils import translation


class TranslationAliasesTests(SimpleTestCase):
    def setUp(self):
        super(TranslationAliasesTests, self).setUp()
        self.engine = Engine()

    def get_engine(self, templates):
        loaders = [
            (
                "django.template.loaders.cached.Loader",
                [("django.template.loaders.locmem.Loader", templates)],
            )
        ]
        return Engine(loaders=loaders, libraries={"i18n": "django.templatetags.i18n"})

    def test_translate(self):
        engine = self.get_engine(
            {"t": '{% load i18n %}{% translate "Page not found" %}'}
        )
        with translation.override("de"):
            output = engine.render_to_string("t")
        self.assertEqual(output, "Seite nicht gefunden")

    def test_blocktranslate(self):
        engine = self.get_engine(
            {
                "t": "{% load i18n %}{% blocktranslate %}Page not found{% endblocktranslate %}"
            }
        )
        with translation.override("de"):
            output = engine.render_to_string("t")
        self.assertEqual(output, "Seite nicht gefunden")
