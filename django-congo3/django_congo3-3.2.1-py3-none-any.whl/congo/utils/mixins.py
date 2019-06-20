# -*- coding: utf-8 -*-

from copy import copy
from copy import deepcopy

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models, transaction
from django.db.models.fields import DateTimeField, BooleanField
from django.db.models.fields.related import ManyToManyField
from django.forms.models import model_to_dict
from django.template.base import Template
from django.utils import timezone, formats
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel


class PositionMixin(models.Model):
    """
    Mixin dodający możliwość ustawiania obiektów w kolejności z poziomu admina. Dodaje nowe pole `position`.
    """

    position = models.IntegerField("#", blank = True, null = True)

    class Meta:
        abstract = True
        ordering = ("position",)

    def _set_position(self, manager):
        if self.position is None:
            try:
                self.position = manager.values_list('position', flat = True).order_by('-position')[0] + 1
            except (IndexError, TypeError):
                self.position = 0

    def save(self, *args, **kwargs):
        self._set_position(self.__class__.objects)
        return super(PositionMixin, self).save(*args, **kwargs)


class TextContentMixin(object):

    def get_content(self):
        if not hasattr(self, '_content'):
            content = self.safe_translation_getter('content', any_language = True) or ""
            self._content = self.parse_content(content)
        return self._content

    @classmethod
    def parse_content(cls, content):
        try:
            template_tags = getattr(settings, 'CONGO_NESTED_TAGS', 'nested common')
            template_string = "{% load %s %}%s" % (template_tags, content.replace('\xa0', ' '))
            return Template(template_string).render()
        except Exception as e:
            return e if settings.DEBUG else content


class LogMixin(models.Model):

    class Meta:
        abstract = True

    @classmethod
    def get_field_names(cls):
        return [f.name for f in cls._meta.get_fields()]

    def get_change_fields(self):
#        exclude = ['id', 'category', 'secret_key', 'progress', 'change_date', 'parameters', 'photo', 'has_full_cable', 'has_20_cable']
#        return [field for field in self.get_field_names() if field not in exclude]
#        return ['field_1', 'field_2', 'field_3', 'field_4', 'field_5']
        return self.get_field_names()

    @classmethod
    def get_change_details_for_objs(cls, original_obj, changed_obj, **kwargs):
        tz = kwargs.get('tz', None)
        current_state_only = kwargs.get('current_state_only', False)

        template_obj = cls()
        detail_list = []

        if isinstance(template_obj, TranslatableModel):
            # agregujemy wszystkie tłumaczenia, o ile występuja
            languages = []

            if original_obj:
                if changed_obj is None and not hasattr(original_obj, '_translations'):
                    # dla original_obj agregujemy tłumaczenia tylko wówczas, gdy nie istnieje changed_obj
                    # wpp należy przepuścić original_obj przez metodę get_object_copy() przed zmianą obiektu
                    original_obj._translations = list(original_obj.translations.all())
                languages += [t.language_code for t in original_obj._translations]

            if changed_obj:
                changed_obj._translations = list(changed_obj.translations.all())
                languages += [t.language_code for t in changed_obj._translations]

            languages = set(languages)

        for field_name in template_obj.get_change_fields():
            if field_name.startswith('translations__'):
                # jesli pole jest tlumaczone, bedzimy szukac zmian w tlumaczeniu dla kazdego jezyka

                if original_obj:
                    # jeśli original_obj nie ma atrybutu _translations, to znaczy, że nie został przepuszczony przez metodę get_object_copy()
                    assert hasattr(original_obj, '_translations'), "In order to compare TranslatableModel you need to copy original object with get_object_copy() method before changing it."

                field_name = field_name.replace('translations__', '')
                field = template_obj._get_translated_model(None, auto_create = True)._meta.get_field(field_name)
                label = getattr(field, 'short_description', getattr(field, 'verbose_name', field.name)).lower()

                for l in languages:
                    original_translation = None
                    changed_translation = None

                    if original_obj:
                        for t in original_obj._translations:
                            if t.language_code == l:
                                original_translation = t
                                break

                    if changed_obj:
                        for t in changed_obj._translations:
                            if t.language_code == l:
                                changed_translation = t
                                break

                    old_value = getattr(original_translation, field_name, None)
                    new_value = getattr(changed_translation, field_name, None)

                    if current_state_only:
                        detail_list.append("%s (%s): %s" % (label, l, old_value if old_value else _("Brak")))

                    elif old_value != new_value:
                        if old_value and new_value:
                            detail_list.append(_("""Zmieniono %(label)s (%(lang)s) z "%(old_value)s" na "%(new_value)s\"""") % {'label': label, 'lang': l, 'old_value': old_value, 'new_value': new_value})
                        elif not old_value and new_value:
                            detail_list.append(_("""Ustawiono %(label)s (%(lang)s) na "%(new_value)s\"""") % {'label': label, 'lang': l, 'new_value': new_value})
                        elif old_value and not new_value:
                            detail_list.append(_("""Wyczyszczono %(label)s (%(lang)s) z "%(old_value)s\"""") % {'label': label, 'lang': l, 'old_value': old_value})

                continue

            else:
                # wpp procedujemy normlanie porównując pole po polu

                field = template_obj._meta.get_field(field_name)
                label = getattr(field, 'short_description', getattr(field, 'verbose_name', field.name)).lower()
                old_value = getattr(original_obj, field_name, None)
                new_value = getattr(changed_obj, field_name, None)

            if isinstance(field, ManyToManyField):
                if original_obj:
                    if hasattr(original_obj, '_%s' % field.name):
                        original_rel_objects = getattr(original_obj, '_%s' % field.name)
                    elif changed_obj is None:
                        original_rel_objects = getattr(original_obj, field.name).all()
                    else:
                        # jeśli original_obj nie ma atrybutu _field_name, to znaczy, że nie został przepuszczony przez metodę get_object_copy()
                        raise AssertionError("In order to compare ManyToManyField you need to copy original object with get_object_copy() method before changing it.")
                else:
                    original_rel_objects = []

                if changed_obj:
                    changed_rel_objects = getattr(changed_obj, field.name).all()
                else:
                    changed_rel_objects = []

                for obj in changed_rel_objects:
                    if not obj in original_rel_objects:
                        detail_list.append(_("""Dodano %(verbose_name)s "%(obj)s\"""") % {'verbose_name': field.verbose_name, 'obj': obj})
                for obj in original_rel_objects:
                    if not obj in changed_rel_objects:
                        detail_list.append(_("""Usunięto %(verbose_name)s "%(obj)s\"""") % {'verbose_name': field.verbose_name, 'obj': obj})

#                 print()
#                 print('changed_obj', type(changed_obj), changed_obj)
#                 print('original_obj', type(original_obj), original_obj)
#                 print('field', field)
#                 print('label', label)
#                 print('old_value', old_value)
#                 print('new_value', new_value)
#                 print('original_rel_objects', original_rel_objects)
#                 print('changed_rel_objects', changed_rel_objects)
#                 print('detail_list', detail_list)
#                 print()

                continue

            elif isinstance(field, DateTimeField):
                if old_value:
                    if timezone.is_naive(old_value):
                        old_value = timezone.make_aware(old_value, tz = tz)
                    old_value = formats.date_format(timezone.localtime(old_value, timezone = tz), "DATETIME_FORMAT")
                if new_value:
                    if timezone.is_naive(new_value):
                        new_value = timezone.make_aware(new_value, tz = tz)
                    new_value = formats.date_format(timezone.localtime(new_value, timezone = tz), "DATETIME_FORMAT")

            elif isinstance(field, BooleanField):
                if old_value is not None:
                    old_value = _("Tak") if old_value else _("Nie")
                if new_value is not None:
                    new_value = _("Tak") if new_value else _("Nie")

            elif getattr(field, 'flatchoices', None):
                if old_value is not None:
                    old_value = force_text(dict(field.flatchoices).get(old_value, old_value), strings_only = True)
                if new_value is not None:
                    new_value = force_text(dict(field.flatchoices).get(new_value, new_value), strings_only = True)

            elif hasattr(field, 'get_prep_value'):
                if old_value is not None:
                    old_value = field.get_prep_value(old_value)
                if new_value is not None:
                    new_value = field.get_prep_value(new_value)

            if current_state_only:
                detail_list.append("%s: %s" % (label, old_value if old_value else _("Brak")))

            elif old_value != new_value:
                if old_value and new_value:
                    detail_list.append(_("""Zmieniono %(label)s z "%(old_value)s" na "%(new_value)s\"""") % {'label': label, 'old_value': old_value, 'new_value': new_value})
                elif not old_value and new_value:
                    detail_list.append(_("""Ustawiono %(label)s na "%(new_value)s\"""") % {'label': label, 'new_value': new_value})
                elif old_value and not new_value:
                    detail_list.append(_("""Wyczyszczono %(label)s z "%(old_value)s\"""") % {'label': label, 'old_value': old_value})

        return detail_list

    def get_change_details(self, original_obj = None, reverse = False, **kwargs):
        """
        Zwraca różnice między obiektem oryginalnym podanym jako argument, a aktualnym.
        Jeśli argument nie zostanie podany, lub zostanie podana wartość `None`, metoda zwróci opis utworzonego obiektu.
        Jeśli zostanie przekazany argument kluczowy `reverse`, metoda uzna bieżący obiekt za źródłowy.
        W szczególności, jeśli obiektem podanym jako argument będzie wartość `None`, metoda zwróci opis usuwanego obiektu.

        W przypadku obiektów zawierających pola klasy `DateTimeField` trzeba pamiętać, że w opisie czasy mogą zostać zlokalizowane do strefy czasowej podanej jako argument kluczowy `tz`.
        """
        if reverse:
            changed_obj = original_obj
            original_obj = self
        else:
            changed_obj = self
        return self.get_change_details_for_objs(original_obj, changed_obj, **kwargs)

    def get_object_details(self, **kwargs):
        kwargs['current_state_only'] = True
        return self.get_change_details_for_objs(self, None, **kwargs)

    def get_object_copy(self):
        obj_copy = deepcopy(self)

        for field_name in self.get_change_fields():
            try:
                field = self._meta.get_field(field_name)
                if isinstance(field, ManyToManyField):
                    setattr(obj_copy, "_%s" % field_name, list(getattr(self, field_name).all()))
            except FieldDoesNotExist:
                if field_name.startswith('translations__') and not hasattr(obj_copy, '_translations'):
                    obj_copy._translations = list(self.translations.all())

        return obj_copy

    @transaction.atomic
    def get_change_details_for_m2m_objects(self, old_obj_list, actual_obj_list, **kwargs):
        model = kwargs.get('model', getattr(actual_obj_list, 'model', getattr(old_obj_list, 'model', None)))
        label = model._meta.verbose_name.lower() if model else "obiekt"

        new_obj_list = [obj for obj in actual_obj_list if obj not in old_obj_list]
        del_obj_list = [obj for obj in old_obj_list if obj not in actual_obj_list]

        details = []

        # zbieramy info o usunietych i usuwamy
        for obj in del_obj_list:
            details.append(_("Wyczyszczono %(label)s: %(obj)s") % {'label': label, 'obj': obj})

        # zbieramy info o dodanych i dodajemy
        for obj in new_obj_list:
            details.append("Ustawiono %(label)s: %(obj)s" % {'label': label, 'obj': obj})

        return details
