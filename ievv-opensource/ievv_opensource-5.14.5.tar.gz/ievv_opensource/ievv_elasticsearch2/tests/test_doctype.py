import elasticsearch_dsl
from django import test
from elasticsearch_dsl.connections import connections
from model_mommy import mommy

from ievv_opensource import ievv_elasticsearch2
from ievv_opensource.ievv_elasticsearch2.tests.ievv_elasticsearch2_testapp.models import SimpleModel


class TestIevvDocType(test.TestCase):
    def setUp(self):
        self.es = connections.get_connection()
        self.es.indices.delete(index='_all')
        self.es.indices.flush(index='_all')

    def test_get_from_index(self):
        class MyDocType(ievv_elasticsearch2.DocType):
            name = elasticsearch_dsl.String()

            class Meta:
                index = 'main'

        MyDocType.ievvinitialize()
        MyDocType.init()
        document = MyDocType(name='Peter')
        document.meta.id = 1
        document.save()

        self.es.update(index='main', doc_type=MyDocType.get_doc_type_options().name,
                       id=1, body={'doc': {'name': 'Updated name'}})
        updated_document = document.get_from_index()
        self.assertEqual('Updated name', updated_document.name)

    def test_base_class_is_abstract(self):
        self.assertTrue(ievv_elasticsearch2.DocType.is_abstract_doctype)

    def test_subclass_is_not_abstract(self):
        class MyDocType(ievv_elasticsearch2.DocType):
            pass

        self.assertFalse(MyDocType.is_abstract_doctype)

    def test_subclass_can_be_abstract(self):
        class MyDocType(ievv_elasticsearch2.DocType):
            is_abstract_doctype = True

        self.assertTrue(MyDocType.is_abstract_doctype)

    # def test_get_all_fieldnames_simple(self):
    #     class MyDocType(ievv_elasticsearch2.DocType):
    #         name = elasticsearch_dsl.String()
    #         age = elasticsearch_dsl.Integer()
    #     MyDocType.ievvinitialize()
    #
    #     self.assertEqual(
    #         {'name', 'age'},
    #         MyDocType.get_all_fieldnames_set())
    #
    # def test_get_all_fieldnames_nested(self):
    #     class MyDocType(ievv_elasticsearch2.DocType):
    #         size = elasticsearch_dsl.Integer()
    #         parent = elasticsearch_dsl.Nested(
    #             properties={
    #                 'name': elasticsearch_dsl.String(),
    #                 'size': elasticsearch_dsl.Integer()
    #             }
    #         )
    #     MyDocType.ievvinitialize()
    #
    #     self.assertEqual(
    #         {'size', 'parent.name', 'parent.size'},
    #         MyDocType.get_all_fieldnames_set())

    # def test_baseclass_is_added_correctly_to_registry(self):
    #     registry = ievv_elasticsearch2.DocTypeRegistry.get_instance()
    #     ievv_elasticsearch2.DocType.ievvinitialize()
    #     self.assertNotIn(ievv_elasticsearch2.DocType, registry._doctypes)
    #     self.assertNotIn(ievv_elasticsearch2.DocType, registry._model_doctypes)
    #     self.assertIn(ievv_elasticsearch2.DocType, registry._abstract_doctypes)
    #
    # def test_nonabstract_is_added_correctly_to_registry(self):
    #     class MyDocType(ievv_elasticsearch2.DocType):
    #         pass
    #
    #     MyDocType.ievvinitialize()
    #     registry = ievv_elasticsearch2.DocTypeRegistry.get_instance()
    #     self.assertIn(MyDocType, registry._doctypes)
    #     self.assertNotIn(MyDocType, registry._model_doctypes)
    #     self.assertNotIn(MyDocType, registry._abstract_doctypes)
    #
    # def test_abstract_is_added_correctly_to_registry(self):
    #     class MyDocType(ievv_elasticsearch2.DocType):
    #         is_abstract_doctype = True
    #
    #     MyDocType.ievvinitialize()
    #     registry = ievv_elasticsearch2.DocTypeRegistry.get_instance()
    #     self.assertNotIn(MyDocType, registry._doctypes)
    #     self.assertNotIn(MyDocType, registry._model_doctypes)
    #     self.assertIn(MyDocType, registry._abstract_doctypes)


class TestModelDocTypeMeta(test.TestCase):
    def test_simple(self):
        class MyModelDocType(ievv_elasticsearch2.ModelDocType):
            model_class = SimpleModel
        MyModelDocType.ievvinitialize()
        self.assertIn('name', MyModelDocType.get_doc_type_options().mapping)
        doctype_field = MyModelDocType.get_doc_type_options().mapping['name']
        self.assertTrue(isinstance(doctype_field, elasticsearch_dsl.String))


class TestModelDocType(test.TestCase):
    def setUp(self):
        self.es = connections.get_connection()
        self.es.indices.delete(index='_all')
        self.es.indices.flush(index='_all')

    def test_to_doctype_object(self):
        class MyModelDocType(ievv_elasticsearch2.ModelDocType):
            model_class = SimpleModel

        MyModelDocType.ievvinitialize()
        modelobject = mommy.make(SimpleModel, name='Test')
        doctypeobject = MyModelDocType.modelmapper.to_doctype_object(modelobject=modelobject)
        self.assertEqual(modelobject.id, doctypeobject._id)
        self.assertEqual('Test', doctypeobject.name)

    def test_save_model_in_elasticsearch(self):
        class MyModelDocType(ievv_elasticsearch2.ModelDocType):
            model_class = SimpleModel

            class Meta:
                index = 'main'

        MyModelDocType.ievvinitialize_and_create_in_index()
        modelobject = mommy.make(SimpleModel, name='Test')
        doctypeobject = MyModelDocType.modelmapper.to_doctype_object(modelobject=modelobject)
        doctypeobject.save()

        from_elasticsearch_doctypeobject = doctypeobject.get_from_index()
        self.assertEqual('Test', from_elasticsearch_doctypeobject.name)

    def test_save_updated_model_in_elasticsearch(self):
        class MyModelDocType(ievv_elasticsearch2.ModelDocType):
            model_class = SimpleModel

            class Meta:
                index = 'main'

        MyModelDocType.ievvinitialize_and_create_in_index()
        modelobject = mommy.make(SimpleModel, name='Test')
        MyModelDocType.modelmapper.to_doctype_object(modelobject=modelobject).save()
        self.assertEqual('Test', MyModelDocType.get(id=modelobject.id).name)

        modelobject.name = 'Updated name'
        MyModelDocType.modelmapper.to_doctype_object(modelobject=modelobject).save()
        self.assertEqual('Updated name', MyModelDocType.get(id=modelobject.id).name)

    def test_base_class_is_abstract(self):
        self.assertTrue(ievv_elasticsearch2.ModelDocType.is_abstract_doctype)

    def test_subclass_is_not_abstract(self):
        class MyDocType(ievv_elasticsearch2.ModelDocType):
            model_class = SimpleModel

        self.assertFalse(MyDocType.is_abstract_doctype)

    def test_subclass_can_be_abstract(self):
        class MyDocType(ievv_elasticsearch2.ModelDocType):
            is_abstract_doctype = True

        self.assertTrue(MyDocType.is_abstract_doctype)

    # def test_baseclass_is_added_correctly_to_registry(self):
    #     registry = ievv_elasticsearch2.DocTypeRegistry.get_instance()
    #     self.assertNotIn(ievv_elasticsearch2.ModelDocType, registry._doctypes)
    #     self.assertNotIn(ievv_elasticsearch2.ModelDocType, registry._model_doctypes)
    #     self.assertIn(ievv_elasticsearch2.ModelDocType, registry._abstract_doctypes)
    #
    # def test_nonabstract_is_added_correctly_to_registry(self):
    #     class MyDocType(ievv_elasticsearch2.ModelDocType):
    #         model_class = SimpleModel
    #
    #     registry = ievv_elasticsearch2.DocTypeRegistry.get_instance()
    #     self.assertIn(MyDocType, registry._doctypes)
    #     self.assertIn(MyDocType, registry._model_doctypes)
    #     self.assertNotIn(MyDocType, registry._abstract_doctypes)
    #
    # def test_abstract_is_added_correctly_to_registry(self):
    #     class MyDocType(ievv_elasticsearch2.ModelDocType):
    #         is_abstract_doctype = True
    #
    #     registry = ievv_elasticsearch2.DocTypeRegistry.get_instance()
    #     self.assertNotIn(MyDocType, registry._doctypes)
    #     self.assertNotIn(MyDocType, registry._model_doctypes)
    #     self.assertIn(MyDocType, registry._abstract_doctypes)
