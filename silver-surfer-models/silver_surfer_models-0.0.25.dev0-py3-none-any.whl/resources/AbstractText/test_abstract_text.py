from src.silver_surfer_models.resources.Patent import Patent
from src.silver_surfer_models.resources.AbstractText import AbstractText
from test.mixins.BasicDataMixin import BasicDataMixin
from test.backendtestcase import TestCase
from test.utils import second_equals_first


class AbstractTextResourceTestCase(BasicDataMixin, TestCase):
    def setUp(self):
        super(AbstractTextResourceTestCase, self).setUp()
        self.inst = AbstractText()
        self.inst_patent = Patent()
        self.patent3 = self.inst_patent.create({
            'patent_number': '3000',
            'app_grp_art_number': '1999',
            'jurisdiction': 'USPAT',
        })
        self.abstract_text1 = self.inst.create({
            'patent_id': self.patent1['id'],
            'abstract_text': 'some text1',
        })
        self.abstract_text2 = self.inst.create({
            'patent_id': self.patent2['id'],
            'abstract_text': 'some text2',
        })

    def test_create(self):
        data = {
            'patent_id': self.patent3['id'],
            'abstract_text': 'some text',
        }
        resp = self.inst.create(data)
        second_equals_first(
            {
                'patent_id': self.patent3['id'],
                'abstract_text': data['abstract_text'],
            },
            resp,
        )

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

    def test_read_w_patent_id(self):
        resp = self.inst.read({
            'patent_id': self.patent1['id'],
        })
        self.assertEqual(len(resp), 1)
        second_equals_first(
            self.abstract_text1,
            resp[0],
        )

    def test_update(self):
        new_data = {
            'patent_id': 9999,
            'abstract_text': 'what what',
        }
        resp = self.inst.update(
            id=self.abstract_text1['id'],
            params=new_data,
        )
        second_equals_first(
            {
                'id': self.abstract_text1['id'],
                'patent_id': self.abstract_text1['patent_id'],
                'abstract_text': new_data['abstract_text'],
            },
            resp,
        )

    def test_delete(self):
        response = self.inst.read({'id': self.abstract_text1['id']})
        self.assertEqual(len(response), 1)
        response = self.inst.delete(id=self.abstract_text1['id'])
        self.assertEqual(response, 'Successfully deleted')
        response = self.inst.read({'id': self.abstract_text1['id']})
        self.assertEqual(len(response), 0)
