from unittest import TestCase

from crossref_commons.iteration import iterate_publications_as_json


class IterationTestCase(TestCase):
    def test_iterate_all_publications(self):
        returned = 0
        for p in iterate_publications_as_json(max_results=-10):
            returned += 1
        self.assertEqual(returned, 0)

        returned = 0
        for p in iterate_publications_as_json(max_results=0):
            returned += 1
        self.assertEqual(returned, 0)

        returned = 0
        dois = set()
        for p in iterate_publications_as_json(max_results=150):
            returned += 1
            dois.add(p['DOI'])
        self.assertEqual(returned, 150)
        self.assertEqual(len(dois), 150)

        returned = 0
        dois = set()
        for p in iterate_publications_as_json(max_results=7519):
            returned += 1
            dois.add(p['DOI'])
        self.assertEqual(returned, 7519)
        self.assertEqual(len(dois), 7519)

    def test_iterate_filter(self):
        returned = 0
        dois = set()
        for p in iterate_publications_as_json(
                max_results=10000, filter={'funder': '10.13039/100000925'}):
            returned += 1
            dois.add(p['DOI'])
            self.assertTrue('10.13039/100000925' in
                            [f.get('DOI', '') for f in p['funder']])
        self.assertEqual(returned, len(dois))

        returned = 0
        dois_type = set()
        for p in iterate_publications_as_json(max_results=10000,
                                              filter={
                                                  'funder':
                                                  '10.13039/100000925',
                                                  'type': 'journal-article'
                                              }):
            returned += 1
            dois_type.add(p['DOI'])
            self.assertTrue('10.13039/100000925' in
                            [f.get('DOI', '') for f in p['funder']])
            self.assertEqual(p['type'], 'journal-article')
        self.assertEqual(returned, len(dois_type))
        for d in dois_type:
            self.assertTrue(d in dois)

    def test_iterate_query(self):
        returned = 0
        dois = set()
        for p in iterate_publications_as_json(max_results=10000,
                                              queries={'query.title':
                                                       'floyd'}):
            returned += 1
            dois.add(p['DOI'])
        self.assertEqual(returned, len(dois))

        returned = 0
        dois_aff = set()
        for p in iterate_publications_as_json(max_results=10000,
                                              queries={
                                                  'query.title': 'floyd',
                                                  'query.affiliation':
                                                  'university'
                                              }):
            returned += 1
            dois_aff.add(p['DOI'])
        self.assertEqual(returned, len(dois_aff))
        for d in dois_aff:
            self.assertTrue(d in dois)

    def test_iterate(self):
        returned = 0
        dois = set()
        for p in iterate_publications_as_json(max_results=10000,
                                              filter={
                                                  'funder':
                                                  '10.13039/501100000038',
                                                  'type': 'journal-article'
                                              },
                                              queries={
                                                  'query.author': 'li',
                                                  'query.affiliation':
                                                  'university'
                                              }):
            returned += 1
            dois.add(p['DOI'])
            self.assertTrue('10.13039/501100000038' in
                            [f.get('DOI', '') for f in p['funder']])
            self.assertEqual(p['type'], 'journal-article')
        self.assertEqual(returned, len(dois))

        max_results = int(returned / 2)
        returned = 0
        dois = set()
        for p in iterate_publications_as_json(max_results=max_results,
                                              filter={
                                                  'funder':
                                                  '10.13039/501100000038',
                                                  'type': 'journal-article'
                                              },
                                              queries={
                                                  'query.author': 'li',
                                                  'query.affiliation':
                                                  'university'
                                              }):
            returned += 1
            dois.add(p['DOI'])
            self.assertTrue('10.13039/501100000038' in
                            [f.get('DOI', '') for f in p['funder']])
            self.assertEqual(p['type'], 'journal-article')
        self.assertEqual(max_results, returned)
        self.assertEqual(max_results, len(dois))
