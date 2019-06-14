# coding: utf-8
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory


from modelformhistory.models import Entry
from sampleapp.models import Foo, Bar, Baz
from sampleapp.forms import FooModelForm, FooModelFormRequest


User = get_user_model()

__all__ = ("ModelFormHistoryTestCase",)


class ModelFormHistoryTestCase(TestCase):
    def setUp(self):
        self.user = User(username="test_user", last_name="TEST", first_name="User")
        self.user.save()

        bars = ["bar", "rab", "bra"]
        bazs = ["baz", "zab", "bza"]
        [Bar(name=bar).save() for bar in bars]
        [Baz(name=baz).save() for baz in bazs]
        bar = Bar.objects.get(name="bar")
        bazs = Baz.objects.all()

        self.foo = Foo(name="Test foo", integer=1, choose_somthing="ok", bar=bar)
        self.foo.save()
        [self.foo.baz.add(b) for b in bazs]
        self.indentical_datas = {
            "bar": self.foo.bar.id,
            "name": self.foo.name,
            "baz": [str(baz.id) for baz in self.foo.baz.all()],
            "integer": self.foo.integer,
            "choose_somthing": self.foo.choose_somthing,
        }

    def check_changed_data(self, changed_data, label, initial_value, changed_value):
        self.assertEqual(changed_data.label, label)
        self.assertEqual(changed_data.initial_value, initial_value)
        self.assertEqual(changed_data.changed_value, changed_value)

    def test_no_change(self):
        form = FooModelForm(user=self.user, instance=self.foo, data=self.indentical_datas)
        form.save()
        self.assertEqual(Entry.objects.all().count(), 0)

    def test_update_choicefield(self):
        data = self.indentical_datas.copy()

        # Save another value on the choiceField
        data["choose_somthing"] = "nok"
        form = FooModelForm(user=self.user, instance=self.foo, data=data)
        form.save()
        self.assertEqual(Entry.objects.all().count(), 1)
        entry = Entry.objects.all()[0]
        self.assertTrue(entry.is_change())
        self.assertFalse(entry.is_addition())
        self.assertFalse(entry.is_deletion())
        self.assertEqual(entry.changeddata_set.all().count(), 1)
        changed_data = entry.changeddata_set.all()[0]
        self.check_changed_data(changed_data, "Make your choice", "It's OK", "It's not OK")

    def test_update_foreign_key(self):
        data = self.indentical_datas.copy()

        # Save another value on the foreignKey
        data["bar"] = Bar.objects.get(name="rab").id
        form = FooModelForm(user=self.user, instance=self.foo, data=data)
        form.save()
        self.assertEqual(Entry.objects.all().count(), 1)
        entry = Entry.objects.all()[0]
        self.assertTrue(entry.is_change())
        self.assertFalse(entry.is_addition())
        self.assertFalse(entry.is_deletion())
        self.assertEqual(entry.changeddata_set.all().count(), 1)
        changed_data = entry.changeddata_set.all()[0]
        self.check_changed_data(changed_data, "Name of the bar", "bar", "rab")

        # Save an empty value on the foreignKey
        del data["bar"]
        form = FooModelForm(user=self.user, instance=self.foo, data=data)
        form.save()
        self.assertEqual(Entry.objects.all().count(), 2)
        entry = Entry.objects.all()[0]
        self.assertEqual(entry.changeddata_set.all().count(), 1)
        changed_data = entry.changeddata_set.all()[0]
        self.check_changed_data(changed_data, "Name of the bar", "rab", "Empty")

    def test_update_manytomany(self):
        data = self.indentical_datas.copy()

        # Save another multiple values on M2M
        data["baz"] = [b.id for b in Baz.objects.filter(name__startswith="b")]
        form = FooModelForm(user=self.user, instance=self.foo, data=data)
        form.save()
        self.assertEqual(Entry.objects.all().count(), 1)
        entry = Entry.objects.all()[0]
        self.assertTrue(entry.is_change())
        self.assertFalse(entry.is_addition())
        self.assertFalse(entry.is_deletion())
        self.assertEqual(entry.changeddata_set.all().count(), 1)
        changed_data = entry.changeddata_set.all()[0]
        self.check_changed_data(changed_data, "Select some baz", "baz, zab, bza", "baz, bza")

        # Save a single object on M2M
        data["baz"] = [Baz.objects.get(name="zab").id]
        form = FooModelForm(user=self.user, instance=self.foo, data=data)
        form.save()
        self.assertEqual(Entry.objects.all().count(), 2)
        entry = Entry.objects.all()[0]
        changed_data = entry.changeddata_set.all()[0]
        self.assertEqual(entry.changeddata_set.all().count(), 1)
        self.assertEqual(changed_data.label, "Select some baz")
        self.assertEqual(changed_data.initial_value, "baz, bza")
        self.assertEqual(changed_data.changed_value, "zab")
        self.check_changed_data(changed_data, "Select some baz", "baz, bza", "zab")

        # Save an empty value on M2M
        del data["baz"]
        form = FooModelForm(user=self.user, instance=self.foo, data=data)
        form.save()
        self.assertEqual(Entry.objects.all().count(), 3)
        entry = Entry.objects.all()[0]
        self.assertEqual(entry.changeddata_set.all().count(), 1)
        changed_data = entry.changeddata_set.all()[0]
        self.check_changed_data(changed_data, "Select some baz", "zab", "Empty")

    def test_add(self):
        data = self.indentical_datas.copy()
        form = FooModelForm(user=self.user, instance=None, data=data)
        form.save()
        self.assertEqual(Entry.objects.all().count(), 1)
        entry = Entry.objects.all()[0]
        self.assertEqual(entry.changeddata_set.all().count(), 0)
        self.assertTrue(entry.is_addition())
        self.assertFalse(entry.is_change())
        self.assertEqual(entry.short_message, "User TEST has added 'Foo Test foo'")

    def test_get_history_user(self):
        form = FooModelForm(user=self.user, instance=None, data=self.indentical_datas)
        self.assertEqual(form.get_history_user(), self.user)
        form = FooModelFormRequest(request=None, instance=None, data=self.indentical_datas)
        self.assertEqual(form.get_history_user(), None)
        request = RequestFactory()
        request.user = self.user
        form = FooModelFormRequest(request=request, instance=None, data=self.indentical_datas)
        self.assertEqual(form.get_history_user(), self.user)
