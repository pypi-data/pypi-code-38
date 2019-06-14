from django.db import models

from django_amazon_translate.translator import TranslationTracker


class NonTranslatedModel(models.Model):
    pass


class TranslatedModel(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(blank=True)

    tt = TranslationTracker()
