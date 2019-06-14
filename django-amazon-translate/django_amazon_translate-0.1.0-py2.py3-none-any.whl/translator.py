import re

import boto3
from django.db import models
from modeltranslation.settings import AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname


class _amazonTranslate(object):
    def __init__(self, client=None):
        self.translate = client or boto3.client('translate')

    def translate_text(self, text, source_language, dest_language):
        return self.translate.translate_text(
                            Text=text,
                            SourceLanguageCode=source_language,
                            TargetLanguageCode=dest_language
        )


def get_translate_client():
    return _amazonTranslate()


def translate_po_file(po, language):
    """
    Update a given .po file with translated strings from Amazon Translate.
    """

    translate = get_translate_client()

    for s in po.untranslated_entries():
        # We replace the formatting specifiers with something
        # that Amazon Translate will just assume is a title and
        # not translate.
        subbed_message = re.sub(
            r"%\((\w+)\)s", r"FORMAT_\1_END", s.msgid
        )

        response = translate.translate_text(
            subbed_message,
            "en",
            language,
        )

        # Put back the correct gettext formatting
        s.msgstr = re.sub(
            r"FORMAT_(\w+)_END", r"%(\1)s",
            response['TranslatedText']
        )

    return po


class TranslationTracker(object):
    """
    Django Model addition/plugin to provide automated translations
    in conjunction with modeltranslation and Amazon Translate
    """

    def contribute_to_class(self, cls, name):
        self.name = name

        models.signals.class_prepared.connect(self.finalize_class, sender=cls)

    def finalize_class(self, sender, **kwargs):
        self.model_class = sender
        setattr(sender, self.name, self)

        self.patch_save(sender)

    @staticmethod
    def patch_save(model):
        original_save = model.save

        def save(instance, *args, **kwargs):
            translate = get_translate_client()

            cls = instance.__class__
            old = cls.objects.filter(pk=instance.pk).first()
            new = instance

            opts = translator.get_options_for_model(cls)

            # Loop through the fields and work out what actually changed
            changed_fields = []
            if old:
                for field in cls._meta.get_fields():
                    field_name = field.name

                    if getattr(old, field_name) != getattr(new, field_name):
                        changed_fields.append(field_name)

            # Go through each translatable field
            for field_name in opts.fields.keys():
                def_lang_fieldname = build_localized_fieldname(
                    field_name, DEFAULT_LANGUAGE
                )

                for lang in AVAILABLE_LANGUAGES:
                    if lang == DEFAULT_LANGUAGE:
                        continue

                    lang_fieldname = build_localized_fieldname(
                        field_name, lang
                    )

                    # If they updated the translation as well as
                    # the source.
                    if lang_fieldname in changed_fields:
                        continue

                    if (
                        def_lang_fieldname in changed_fields
                        or not getattr(new, def_lang_fieldname)
                        or not old
                    ):
                        r = translate.translate_text(
                            getattr(new, def_lang_fieldname),
                            DEFAULT_LANGUAGE,
                            lang
                        )
                        setattr(new, lang_fieldname, r['TranslatedText'])

            return original_save(instance, *args, **kwargs)

        model.save = save
