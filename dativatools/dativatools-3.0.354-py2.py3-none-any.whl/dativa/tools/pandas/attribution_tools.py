"""Attribution methods implemented on pandas dataframes."""
import math
from itertools import combinations
from datetime import datetime
import logging

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from blist import blist
except ImportError:
    blist = None

from .columns import get_unique_column_name

logger = logging.getLogger('dativa.attribution.shapley')


class Shapley:
    """Shapley attribution of scores to members of sets.

    See `medium <https://towardsdatascience.com/one-feature-attribution-method-to-supposedly-rule-them-all-shapley-values-f3e04534983d>`_
    or `wiki <https://en.wikipedia.org/wiki/Shapley_value>`_ for details on the math. The aim is to apportion scores between the members of a set
    responsible for producing that score.

    :param df_impression: impression data to be parsed.
    :param df_conversions: conversion events to score
    :param id_column: column containing the id values of users who viewed impressions / converted.
    :param sets_column: label of the column containing features
    :param default_score: score to assign to any combination that has not been observed, defaults to 0.
    :param infer_missing: {'average', 'regression', 'filter', False} defaults to False. To be implemented
    :param metric: The column used to calculate the Shapley value
    :param normalize_impressions: defaults to True, normalize the score column according to the number of impressions

    :type df_impressions:  pandas.DataFrame
    :type df_conversions:  pandas.DataFrame
    :type id_column: str
    :type sets_column: str
    :type default_score: int or float
    :type infer_missing: bool or str
    """

    def __init__(self,
                 df_impression,
                 df_conversions,
                 id_column,
                 sets_column,
                 default_score=0,
                 infer_missing=False,
                 normalize_impressions=True,
                 metric='conversions'):

        if not blist:
            raise ImportError("blist must be installed to use Shapley")

        if not pd:
            raise ImportError("pandas must be installed to run Shapley")

        if infer_missing and infer_missing not in ('filter'):  # to be extended
            raise KeyError('{} is not a valid option for infer_missing'.format(infer_missing))

        self.infer_missing = infer_missing
        self.normalize_impressions = normalize_impressions

        if metric in df_conversions.columns.tolist():
            self.conversion_col = metric
        elif metric in ['conversions']:
            # this is redundant because we've already checked if it's in the df, which sort of defeats the purpose?
            # i'll have to think about how anyone would actually use this
            self.conversion_col = get_unique_column_name(df_conversions, metric)
        else:
            raise KeyError('{} is not a valid option for metric'.format(metric))

        try:
            self.scores = blist([float(default_score)])  # what does pycharm have against this?
        except ValueError:
            raise TypeError('default_score: {} is not valid - must be numeric'.format(default_score))

        self.sets_column = sets_column

        self.population = df_impression[sets_column].unique()
        self.conversion_dict = self._build_conversion_dict(self.population)

        self._build_df(df_impression, df_conversions, id_column)

    def _build_df(self, df_campaigns, df_conversions, id_column):

        g = df_campaigns.drop_duplicates().groupby(id_column, as_index=False).agg(
            {self.sets_column: lambda x: sorted(list(x))})

        if self.conversion_col not in df_conversions.columns:
            df_conversions[self.conversion_col] = 1  # so we can count them
            m = pd.merge(g, df_conversions, on=id_column, how='left')
            df_conversions.drop(columns=self.conversion_col, inplace=True)
        else:
            m = pd.merge(g, df_conversions, on=id_column, how='left')

        # need a delimiter to join our lists into strings so we can group by them
        # needs to be a character that isn't in any of the set items

        delim = self._get_delim(self.population)
        m[self.sets_column] = m[self.sets_column].apply(delim.join)

        df_scored = m.groupby(self.sets_column, as_index=False).agg({self.conversion_col: sum,
                                                                     id_column: pd.Series.nunique})

        df_scored[self.sets_column] = df_scored[self.sets_column].apply(lambda x: x.split(delim))

        # factor by the number of values
        if self.normalize_impressions:
            df_scored[self.conversion_col] = df_scored[self.conversion_col] / df_scored[id_column]  # ie conversion rate

        marked_df = df_scored.loc[:, [self.sets_column, self.conversion_col]]
        self._add_marker_int(marked_df)

        # because we're converting from sets to integers we can use those
        # as indexes in a list
        # initialised full of default values.
        self.scores *= 2 ** len(self.population)
        for i, j in marked_df[self.conversion_col].iteritems():
            self.scores[i] = j

    def _filter_subsets_exist(self, subset, ix):

        val_s = sum((self.conversion_dict[s] for s in subset))

        for i in subset:
            val_i = self.conversion_dict[i]

            if val_i not in ix:
                return False

            if ((val_s - val_i) not in ix) and ((val_s - val_i) != 0):
                return False

            if not self._filter_subsets_exist([j for j in subset if j != i], ix):
                return False

        return True

    def _get_delim(self, s, delim=':'):
        """Recursively find a valid delimiter for a series s, which contains lists of strings."""

        if any(delim in i for i in s):
            return self._get_delim(s, chr(
                ord(delim) + 1))  # this should run until i == 1,114,111 but i'm not sure that's a good idea?

        return delim

    @staticmethod
    def _build_conversion_dict(population):
        # Convert a subset {x_i} into a unique integer sum( 2 ** i ) for i in [0, n)
        # vastly better performance
        return {member: 2 ** i for i, member in enumerate(population)}

    def _convert_subset(self, subset):

        return sum([self.conversion_dict[i] for i in subset])

    def _add_marker_int(self, df, mcol='marker'):

        if mcol in df.columns:
            return self._add_marker_int(df, mcol + '_unique')

        df[mcol] = df[self.sets_column].apply(self._convert_subset)

        df.set_index(mcol, inplace=True)

    def _find_population(self, df):
        """deprecated - we now read in a impressions file that contains all members of the population"""
        population = set()
        for i in df[self.sets_column].values:
            for entry in i:
                population.add(entry)
        return list(population)

    def marginal_score(self, i):

        N = len(self.population)  # https://xkcd.com/163/

        score = (1 / math.factorial(N)) * sum(self._score_vs_subset(s, i) for s in self._generate_subsets(i))

        if score < 0:
            logger.warning("Negative score for {0} = {1}".format(i,
                                                                 score))
        return score

    def _generate_subsets(self, exclude=None):

        i = 0

        pop_size = len(self.population)
        while i < pop_size:  # < so stops at len - 1, so doesn't IndexError
            for c in combinations([p for p in self.population if p != exclude], i):
                yield c
            i += 1
            logger.debug(
                'completed for combination of length {0} / {1} at {2:%H:%M:%S}'.format(i, pop_size, datetime.now()))

    def _score_vs_subset(self, subset, i):
        """Implement everything within the sum notation."""
        S = len(subset)  # https://xkcd.com/163/

        permutation_term = math.factorial(S) * math.factorial(len(self.population) - S - 1)

        # these labels are unique but also conserve arithmetic
        # a set [x_1, x_3] would be represented by 101 in base 2 (2**0 + 2**2)
        # take out x_1 (1 or 2**0) 101 - 001 = 100 which is [x_3]

        subset_label = self._convert_subset(subset)
        item_label = self.conversion_dict[i]

        scoring_term = self.scores[subset_label + item_label] - self.scores[subset_label]

        total_score = permutation_term * scoring_term

        if (self.scores[subset_label + item_label] == 0 or
            self.scores[subset_label] == 0) and self.infer_missing == 'filter':
            logger.debug("filtering zero values for {0} [{1}], +{2} [{3}]".format(subset,
                                                                                  self.scores[subset_label],
                                                                                  i,
                                                                                  self.scores[
                                                                                      subset_label + item_label]))
            return 0

        if total_score < 0:
            logger.debug("Negative shapley {4} for {0} [{1}], +{2} [{3}]".format(subset,
                                                                                 self.scores[subset_label],
                                                                                 i,
                                                                                 self.scores[
                                                                                     subset_label + item_label],
                                                                                 total_score))

        return total_score

    def run(self):

        results = dict()
        for element in self.population:
            results[element] = self.marginal_score(element)

        df = pd.DataFrame.from_dict(results, orient='index')
        df.reset_index(inplace=True)

        df.rename(columns={'index': self.sets_column, 0: 'Shapley_val'}, inplace=True)
        df.sort_values('Shapley_val', ascending=False, inplace=True)
        df.reset_index(inplace=True, drop=True)

        return df
