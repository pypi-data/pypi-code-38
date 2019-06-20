from unittest import TestCase

from crossref_commons.sampling import get_sample_chunk, \
    get_sample_of_max_size, get_sample


class IterationTestCase(TestCase):
    def setUp(self):
        self.f = {'funder': '10.13039/501100000038'}
        self.q = {'query.affiliation': 'university'}

    def verify_sample_items(self, sample):
        for s in sample:
            self.assertTrue('10.13039/501100000038' in
                            [f.get('DOI', '') for f in s['funder']])
            aff_not_empty = False
            for a in s.get('author', []) + s.get('editor', []):
                for aff in a.get('affiliation', []):
                    if aff.get('name', ''):
                        aff_not_empty = True
            self.assertTrue(aff_not_empty)

    def test_get_sample_chunk(self):
        with self.assertRaises(ConnectionError) as context:
            sample = get_sample_chunk(150)
        self.assertTrue('400' in context.exception.args[0])

        sample = get_sample_chunk(87, filter=self.f, queries=self.q)
        self.assertEqual(87, len(sample))
        self.assertEqual(87, len(set([s['DOI'] for s in sample])))
        self.verify_sample_items(sample)

    def test_get_sample_of_max_size(self):
        sample = get_sample_of_max_size(87, filter=self.f, queries=self.q)
        self.assertEqual(len(set([s['DOI'] for s in sample])), len(sample))
        self.assertTrue(len(sample) <= 87)
        self.verify_sample_items(sample)

        sample = get_sample_of_max_size(387, filter=self.f, queries=self.q)
        self.assertEqual(len(set([s['DOI'] for s in sample])), len(sample))
        self.assertTrue(len(sample) <= 387)
        self.verify_sample_items(sample)

        sample = get_sample_of_max_size(5787, filter=self.f, queries=self.q)
        self.assertEqual(len(set([s['DOI'] for s in sample])), len(sample))
        self.assertTrue(len(sample) <= 5787)
        self.verify_sample_items(sample)

    def test_get_sample(self):
        sample = get_sample(87, filter=self.f, queries=self.q)
        self.assertEqual(87, len(sample))
        self.assertEqual(87, len(set([s['DOI'] for s in sample])))
        self.verify_sample_items(sample)

        sample = get_sample(387, filter=self.f, queries=self.q)
        self.assertEqual(387, len(sample))
        self.assertEqual(387, len(set([s['DOI'] for s in sample])))
        self.verify_sample_items(sample)

        sample = get_sample(5787, filter=self.f, queries=self.q)
        self.assertEqual(5787, len(sample))
        self.assertEqual(5787, len(set([s['DOI'] for s in sample])))
        self.verify_sample_items(sample)
