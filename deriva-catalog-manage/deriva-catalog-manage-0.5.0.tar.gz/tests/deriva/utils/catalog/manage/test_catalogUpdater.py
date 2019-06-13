from unittest import TestCase

from deriva.utils.catalog.manage.update_catalog import CatalogUpdater
from deriva.utils.catalog.manage.utils import LoopbackCatalog, TempErmrestCatalog
from deriva.core import get_credential
import deriva.core.ermrest_model as em


from tests.deriva.utils.catalog.test_utils import *


logging.basicConfig(
    level=logging.DEBUG,
 #   format='[%(lineno)d] %(funcName)20s() %(message)s'
)


logger = logging.getLogger(__name__)


class TestCatalogUpdater(TestCase):
    def setUp(self):
        self.server = 'dev.isrd.isi.edu'
        self.credentials = get_credential(self.server)

    def test_update_catalog(self):
        catalog = create_catalog(self.server)
        try:
            updater = CatalogUpdater(catalog)

            # Check if basic setting works....
            updated_annotations = {'tag:misd.isi.edu,2015:display': {'name': 'foo'}}
            updated_acls = {'insert': ['bill']}
            logger.info('Checking update annotations.')
            updater.update_catalog('acls', updated_annotations, updated_acls, merge=True)
            self.assertEqual(catalog.acls['insert'], updated_acls['insert'])

            updater.update_catalog('annotations', updated_annotations, updated_acls)
            self.assertEqual(catalog.annotations, updated_annotations)

            # Check updates...
            updated_annotations = {'tag:misd.isi.edu,2015:display': {'name': 'bar'},
                                   'tag:isrd.isi.edu,2016:export': {'templates': 1}}
            updated_acls = {'insert': ['carl']}

            # Check updates...
            updater.update_catalog('acls', updated_annotations, updated_acls, merge=True)
            self.assertEqual(catalog.acls['insert'], updated_acls['insert'])

            updater.update_catalog('annotations', updated_annotations, updated_acls)
            self.assertEqual(catalog.annotations, updated_annotations)

            # Check replace.
            updated_annotations = {'tag:isrd.isi.edu,2016:export': {'newtemplates': {}}}
            updater.update_catalog('annotations', updated_annotations, updated_acls, replace=True)
            self.assertEqual(catalog.annotations, updated_annotations)
        finally:
            delete_catalog(catalog.ermrest_catalog)

    def test_update_schema(self):
        catalog = create_catalog(self.server)
        try:
            updater = CatalogUpdater(catalog)

            # Create empty schema.
            schema_name = 'TestSchema'
            updater.update_schema('schema', em.Schema.define(schema_name))
            self.assertEqual(catalog[schema_name].name, schema_name)

            updated_annotations = {'tag:misd.isi.edu,2015:display': {'name': 'foo'}}
            updated_acls = {'owner': ['carl']}
            updated_comment = 'Updated comment'

            # Check if basic setting works....
            updated_annotations = {'tag:misd.isi.edu,2015:display': {'name': 'foo'}}
            updated_acls = {'owner': ['bob']}
            updated_comment = 'Updated comment'
            schema_def = em.Schema.define(schema_name, comment=updated_comment, acls=updated_acls,
                                          annotations=updated_annotations)
            updater.update_schema('acls', schema_def)
            print('answer', catalog[schema_name].acls)
            self.assertEqual(catalog[schema_name].acls, updated_acls)

            updater.update_schema('comment', schema_def)
            self.assertEqual(catalog[schema_name].comment, updated_comment)

            updater.update_schema('annotations', schema_def)
            self.assertEqual(catalog[schema_name].annotations, updated_annotations)

            # Check updates...
            updated_annotations = {'tag:misd.isi.edu,2015:display': {'name': 'bar'},
                                   'tag:isrd.isi.edu,2016:export': {'templates': []}}
            updated_acls = {'owner': ['carl']}
            updated_comment = 'Updated comment two'
            schema_def = em.Schema.define(schema_name, comment=updated_comment, acls=updated_acls,
                                          annotations=updated_annotations)

            # Check updates...
            updater.update_schema('acls', schema_def)
            self.assertEqual(catalog[schema_name].acls, updated_acls)

            updater.update_schema('comment', schema_def)
            self.assertEqual(catalog[schema_name].comment, updated_comment)

            updater.update_schema('annotations', schema_def)
            self.assertEqual(catalog[schema_name].annotations, updated_annotations)

            # Check replace.
            updated_annotations = {'tag:isrd.isi.edu,2016:export': {'newtemplates': {}}}
            schema_def = em.Schema.define(schema_name, comment=updated_comment, acls=updated_acls,
                                          annotations=updated_annotations)
            updater.update_schema('annotations', schema_def, replace=True)
            self.assertEqual(catalog[schema_name].annotations, updated_annotations)
        finally:
            delete_catalog(catalog.ermrest_catalog)

    def test_update_table(self):
        catalog = create_catalog(self.server)
        try:
            updater = CatalogUpdater(catalog)

            schema_name = 'TestSchema'
            table_name = 'TestTable'

            # Create empty table.
            updater.update_schema('schema', em.Schema.define('TestSchema'))
            self.assertEqual(catalog[schema_name].name, 'TestSchema')
            updater.update_table('table', schema_name, em.Table.define('TestTable'), really=True)
            self.assertEqual(catalog[schema_name].tables[table_name].name, 'TestTable')
        finally:
            delete_catalog(catalog.ermrest_catalog)
