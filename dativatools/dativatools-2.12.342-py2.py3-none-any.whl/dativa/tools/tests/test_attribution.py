import unittest
import pandas as pd
import os
import logging
from dativa.tools.pandas.attribution_tools import Shapley
from pandas.util.testing import assert_frame_equal

logger = logging.getLogger("dativa.tools.attribution.tests")


class ShapleyTest(unittest.TestCase):
    base_path = "{0}/test_data/attribution/".format(
        os.path.dirname(os.path.abspath(__file__)))

    def _generate_test_data(self):

        results = pd.DataFrame([['a', 80],
                                ['b', 56],
                                ['c', 70],
                                ['a:b', 80],
                                ['a:c', 85],
                                ['b:c', 72],
                                ['a:b:c', 90],
                                ['a:b:c:d:e', 98]],
                               columns=['sets', 'score'])

        impressions = []
        conversions = []
        for s in results['sets']:
            score = results.loc[results['sets'] == s, 'score'].values[0]
            for i in range(1, 101):
                for a in s.split(':'):
                    impressions.append({'viewer': '{}_{}'.format(s, i),
                                        'campaign': a})
                if i <= score:
                    conversions.append({'viewer': '{}_{}'.format(s, i)})

        imp = pd.DataFrame(impressions)
        conv = pd.DataFrame(conversions)

        scored_impressions = []
        scored = []
        for i, s in enumerate(results['sets']):
            score = results.loc[results['sets'] == s, 'score'].values[0]
            for a in s.split(':'):
                scored_impressions.append({'viewer_id': str(i),
                                           'campaign': a})
            scored.append({'viewer_id': str(i), 'score': score})

        sc = pd.DataFrame(scored)

        sc_imp = pd.DataFrame(scored_impressions)

    def test_run(self):

        df_campaigns = pd.read_csv(self.base_path + 'impressions.csv')
        df_conversions = pd.read_csv(self.base_path + 'conversions.csv')

        s = Shapley(df_campaigns, df_conversions, 'viewer_id', 'campaign', normalize_impressions=False)

        results = s.run()
        expected = pd.DataFrame([['a', 39.16666666666667],
                                 ['c', 30.16666666666666],
                                 ['b', 20.66666666666667]],
                                columns=['campaign', 'Shapley_val'])
        assert_frame_equal(results, expected, check_exact=False)

    def test_filter(self):

        df_campaigns = pd.read_csv(self.base_path + 'impressions_to_filter.csv')
        df_conversions = pd.read_csv(self.base_path + 'conversions_to_filter.csv')

        s = Shapley(df_campaigns, df_conversions, 'viewer_id', 'campaign', infer_missing='filter',
                    normalize_impressions=False)

        results = s.run()
        expected = pd.DataFrame([['_0', 1.6166666666666667],  # there is a reason
                                 ['_10', 1.4166666666666667],
                                 ['c', 0.8666666666666667],
                                 ['b', 0.15],
                                 ['d', 0.0],
                                 ['e', 0.0]],
                                columns=['campaign', 'Shapley_val'])
        assert_frame_equal(results, expected, check_exact=False)

    def test_score_conversions(self):

        df_campaigns = pd.read_csv(self.base_path + 'impressions.csv')
        df_conversions = pd.read_csv(self.base_path + 'conversions.csv')

        s = Shapley(df_campaigns, df_conversions, 'viewer_id', 'campaign', metric='conversions',
                    normalize_impressions=False)

        results = s.run()
        expected = pd.DataFrame([['a', 39.16666666666667],
                                 ['c', 30.16666666666666],
                                 ['b', 20.66666666666667]],
                                columns=['campaign', 'Shapley_val'])
        assert_frame_equal(results, expected, check_exact=False)

    def test_score_conversions_normalized(self):

        df_campaigns = pd.read_csv(self.base_path + 'impressions.csv')
        df_conversions = pd.read_csv(self.base_path + 'conversions.csv')

        s = Shapley(df_campaigns, df_conversions, 'viewer_id', 'campaign', metric='conversions')

        results = s.run()
        expected = pd.DataFrame([['a', 0.39166666666667],
                                 ['c', 0.30166666666666],
                                 ['b', 0.20666666666667]],
                                columns=['campaign', 'Shapley_val'])
        assert_frame_equal(results, expected, check_exact=False)

    def test_metric_score(self):

        df_campaigns = pd.read_csv(self.base_path + 'scored_impressions.csv')
        df_conversions = pd.read_csv(self.base_path + 'scored_conversions.csv')

        s = Shapley(df_campaigns, df_conversions, 'viewer_id', 'campaign', metric='score', infer_missing='filter',
                    normalize_impressions=False)

        results = s.run()

        print(results)

        expected = pd.DataFrame([['a', 2.55],
                                 ['c', 1.3833333333333333],
                                 ['b', 0.26666666666666666],
                                 ['d', 0.0],
                                 ['e', 0.]],
                                columns=['campaign', 'Shapley_val'])
        assert_frame_equal(results, expected, check_exact=False)

    def test_invalid_default(self):

        df_campaigns = pd.read_csv(self.base_path + 'impressions.csv')
        df_conversions = pd.read_csv(self.base_path + 'conversions.csv')

        with self.assertRaises(TypeError):
            s = Shapley(df_campaigns, df_conversions, 'viewer_id', 'campaign', default_score='error')

    def test_invalid_metric(self):
        df_campaigns = pd.read_csv(self.base_path + 'impressions.csv')
        df_conversions = pd.read_csv(self.base_path + 'conversions.csv')

        with self.assertRaises(KeyError):
            s = Shapley(df_campaigns, df_conversions, 'viewer_id', 'campaign', metric='number_of_shrubberies')

    def test_invalid_infer(self):
        df_campaigns = pd.read_csv(self.base_path + 'impressions_to_filter.csv')
        df_conversions = pd.read_csv(self.base_path + 'conversions_to_filter.csv')

        with self.assertRaises(KeyError):
            s = Shapley(df_campaigns, df_conversions, 'viewer_id', 'campaign', infer_missing='but_im_not_dead_yet')

    def test_duplicate_columns(self):

        df_campaigns = pd.read_csv(self.base_path + 'impressions.csv').rename(columns={'campaign': 'marker'})
        df_conversions = pd.read_csv(self.base_path + 'conversions.csv')
        s = Shapley(df_campaigns, df_conversions, 'viewer_id', 'marker', normalize_impressions=False)
        results = s.run()
        expected = pd.DataFrame([['a', 39.16666666666667],
                                 ['c', 30.16666666666666],
                                 ['b', 20.66666666666667]],
                                columns=['marker', 'Shapley_val'])
        assert_frame_equal(results, expected, check_exact=False)

    def test_colon_in_sets(self):

        df_campaigns = pd.read_csv(self.base_path + 'impressions.csv')
        df_conversions = pd.read_csv(self.base_path + 'conversions.csv')

        df_campaigns['campaign'] = df_campaigns['campaign'].str.replace('a', 'a:')

        s = Shapley(df_campaigns, df_conversions, 'viewer_id', 'campaign', normalize_impressions=False)
        results = s.run()
        expected = pd.DataFrame([['a:', 39.16666666666667],
                                 ['c', 30.16666666666666],
                                 ['b', 20.66666666666667]],
                                columns=['campaign', 'Shapley_val'])
        assert_frame_equal(results, expected, check_exact=False)
