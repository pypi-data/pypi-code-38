from django import test

from ievv_opensource.utils import choices_with_meta


class TestChoice(test.TestCase):
    def test_init_label_fallback_to_value(self):
        choice = choices_with_meta.Choice(value='test')
        self.assertEqual('test', choice.label)

    def test_get_short_label(self):
        choice = choices_with_meta.Choice(value='test', label='Test')
        self.assertEqual('Test', choice.get_short_label())

    def test_get_long_label_without_description(self):
        choice = choices_with_meta.Choice(value='test', label='Test')
        self.assertEqual('Test', choice.get_long_label())

    def test_get_long_label_with_description(self):
        choice = choices_with_meta.Choice(value='test', label='Test', description='A description')
        self.assertEqual('Test - A description', choice.get_long_label())

    def test_value_to_attributename(self):
        self.assertEqual('TEST',
                         choices_with_meta.Choice(value='test').attributename)
        self.assertEqual('MULTI_WORD',
                         choices_with_meta.Choice(value='multi word').attributename)
        self.assertEqual('LINE_SEPARATED_WORDS',
                         choices_with_meta.Choice(value='line-separated-words').attributename)
        self.assertEqual('_0',
                         choices_with_meta.Choice(value=0).attributename)

    def test_custom_attributename(self):
        self.assertEqual('first',
                         choices_with_meta.Choice(value=0, attributename='first').attributename)


class TestChoicesWithMeta(test.TestCase):
    def test_add_adds_to_choices(self):
        choices = choices_with_meta.ChoicesWithMeta()
        choice = choices_with_meta.Choice(value='test1')
        choices.add(choice)
        self.assertEqual(choice, choices.choices['test1'])

    def test_add_adds_to_attributes(self):
        choices = choices_with_meta.ChoicesWithMeta()
        choice = choices_with_meta.Choice(value='test1')
        choices.add(choice)
        self.assertEqual(choice, choices.TEST1)

    def test_getitem_value_exists(self):
        choices = choices_with_meta.ChoicesWithMeta()
        choice = choices_with_meta.Choice(value='test1')
        choices.add(choice)
        self.assertEqual(choice, choices['test1'])

    def test_getitem_value_does_not_exist(self):
        choices = choices_with_meta.ChoicesWithMeta()
        with self.assertRaises(KeyError):
            choices['somevalue']

    def test_get_by_value_value_exists(self):
        choices = choices_with_meta.ChoicesWithMeta()
        choice = choices_with_meta.Choice(value='test1')
        choices.add(choice)
        self.assertEqual(choice, choices.get_by_value('test1'))

    def test_get_by_value_value_does_not_exist(self):
        choices = choices_with_meta.ChoicesWithMeta()
        self.assertIsNone(choices.get_by_value('somevalue'))

    def test_get_by_value_value_does_not_exist_custom_fallback(self):
        choices = choices_with_meta.ChoicesWithMeta()
        self.assertEqual('fall back', choices.get_by_value('somevalue', 'fall back'))

    def test_getattr_invalid_value(self):
        choices = choices_with_meta.ChoicesWithMeta()
        with self.assertRaises(AttributeError):
            choices.INVALID

    def test_getattr_valid_value(self):
        choices = choices_with_meta.ChoicesWithMeta()
        choice = choices_with_meta.Choice(value='test1')
        choices.add(choice)
        self.assertEqual(choice, choices.TEST1)

    def test_contains(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1'))
        self.assertTrue('test1' in choices)
        self.assertFalse('test2' in choices)

    def test_len(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1'),
            choices_with_meta.Choice(value='test2'))
        self.assertEqual(2, len(choices))

    def test_get_choice_at_index(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1'),
            choices_with_meta.Choice(value='test2'))
        self.assertEqual('test1', choices.get_choice_at_index(0).value)
        self.assertEqual('test2', choices.get_choice_at_index(1).value)

    def test_get_choice_at_index_invalid_index(self):
        choices = choices_with_meta.ChoicesWithMeta()
        with self.assertRaises(IndexError):
            choices.get_choice_at_index(0)

    def test_get_first_choice(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1'),
            choices_with_meta.Choice(value='test2'))
        self.assertEqual('test1', choices.get_first_choice().value)

    def test_get_first_choice_none(self):
        choices = choices_with_meta.ChoicesWithMeta()
        self.assertIsNone(choices.get_first_choice())

    def test_init(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1', label='Test1'),
            choices_with_meta.Choice(value='test2', label='Test2'))
        self.assertEqual('Test1', choices['test1'].label)
        self.assertEqual('Test2', choices['test2'].label)

    def test_itervalues(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1'),
            choices_with_meta.Choice(value='test2'))
        self.assertEqual(['test1', 'test2'], list(choices.itervalues()))

    def test_get_values_as_list(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1'),
            choices_with_meta.Choice(value='test2'))
        self.assertEqual(['test1', 'test2'], choices.get_values_as_list())

    def test_iterchoices(self):
        choice1 = choices_with_meta.Choice(value='test1')
        choice2 = choices_with_meta.Choice(value='test2')
        choices = choices_with_meta.ChoicesWithMeta(choice1, choice2)
        self.assertEqual([choice1, choice2], list(choices.iterchoices()))

    def test_iter_as_django_choices_short(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1', label='Test1'),
            choices_with_meta.Choice(value='test2', label='Test2'))
        self.assertEqual(
            [
                ('test1', 'Test1'),
                ('test2', 'Test2'),
            ],
            list(choices.iter_as_django_choices_short()))

    def test_iter_as_django_choices_long(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1', label='Test1', description='A description'),
            choices_with_meta.Choice(value='test2', label='Test2'))
        self.assertEqual(
            [
                ('test1', 'Test1 - A description'),
                ('test2', 'Test2'),
            ],
            list(choices.iter_as_django_choices_long()))

    def test_get_values_as_commaseparated_string(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1'),
            choices_with_meta.Choice(value='test2'))
        self.assertEqual('test1, test2', choices.get_values_as_commaseparated_string())

    def test_str(self):
        choices = choices_with_meta.ChoicesWithMeta(
            choices_with_meta.Choice(value='test1'),
            choices_with_meta.Choice(value='test2'))
        self.assertEqual('ChoicesWithMeta(test1, test2)', str(choices))

    def test_get_default_choices_added_in_init(self):
        class MyChoicesWithMeta(choices_with_meta.ChoicesWithMeta):
            def get_default_choices(self):
                return [
                    choices_with_meta.Choice(value='default1'),
                    choices_with_meta.Choice(value='default2')
                ]

        choices = MyChoicesWithMeta(
            choices_with_meta.Choice(value='test1'))
        self.assertEqual(
            ['default1', 'default2', 'test1'],
            choices.get_values_as_list()
        )
