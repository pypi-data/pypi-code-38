from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from .models import TranslatedModel


@register(TranslatedModel)
class TranslationOptions(TranslationOptions):
    fields = ('title', 'description',)
