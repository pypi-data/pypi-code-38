#/usr/bin/env python
# -*- coding:Utf-8 -*-

#
#
# Ensemble de fonction rendant beaucoup plus pratique la résolution et l'élaboration des exercices de stat au lycée
#
#

from math import sqrt, ceil
from collections import Counter
from .dataset import Dataset
from ..calculus.generic import flatten_list
from .number_tools import number_factory


class WeightedDataset(dict):
    """ A weighted dataset with statistics and latex rendering methods

    >>> w = WeightedDataset([1, 2, 3, 4], "Enfants", [10, 11, 12, 13])
    >>> print(w)
    {1: 10, 2: 11, 3: 12, 4: 13}
    >>> w.effectif_total()
    46
    >>> w.sum()
    120
    >>> w.mean()
    2.61
    >>> w.deviation()
    56.96
    >>> w.variance()
    1.24
    >>> w.sd()
    1.11

    """

    def __init__(
            self,
            datas=[],
            data_name="Valeurs",
            weights=[],
            weight_name="Effectifs"):
        """
        Initiate the WeightedDataset
        """
        if datas and not weights:
            weightedDatas = Counter(datas)
        elif datas and weights:
            if len(datas) != len(weights):
                raise ValueError("Datas and weights should have same length")
            else:
                weightedDatas = {i[0]: i[1] for i in zip(datas, weights)}

        dict.__init__(self, weightedDatas)

        self.data_name = data_name
        self.weight_name = weight_name

    def add_data(self, data, weight=1):
        try:
            self[data] += weight
        except KeyError:
            self[data] = weight

    @number_factory
    def total_weight(self):
        return sum(self.values())

    def effectif_total(self):
        return self.total_weight()

    @number_factory
    def sum(self):
        """ Not really a sum but the sum of the product of key and values """
        return sum([k * v for (k, v) in self.items()])

    @number_factory
    def mean(self):
        return self.sum() / self.effectif_total()

    @number_factory
    def deviation(self):
        """ Compute the deviation (not normalized) """
        mean = self.mean()
        return sum([v * (k - mean)**2 for (k, v) in self.items()])

    @number_factory
    def variance(self):
        return self.deviation() / self.effectif_total()

    @number_factory
    def sd(self):
        """ Compute the standard deviation """
        return sqrt(self.variance())

    def quartiles(self):
        """
        Calcul les quartiles de la série.

        :return: un tuple avec (min, Q1, Me, Q3, Max)

        >>> w = WeightedDataset(flatten_list([i*[i] for i in range(5)]))
        >>> w.quartiles()
        (1, 2, 3, 4, 4)
        >>> w = WeightedDataset(flatten_list([i*[i] for i in range(6)]))
        >>> w.quartiles()
        (1, 3, 4, 5, 5)

        """
        return (min(self.keys()),
                self.quartile(1),
                self.quartile(2),
                self.quartile(3),
                max(self.keys()))

    @number_factory
    def quartile(self, quartile=1):
        """
        Calcul un quartile de la série.

        :param quartile: quartile à calculer (par defaut 1 -> Q1)

        :return: le quartile demandé

        : Example:

        >>> w = WeightedDataset(flatten_list([i*[i] for i in range(5)]))
        >>> w.quartile(1)
        2
        >>> w.quartile(2)
        3
        >>> w.quartile(3)
        4
        >>> w = WeightedDataset(flatten_list([i*[i] for i in range(6)]))
        >>> w.quartile(1)
        3
        >>> w.quartile(2)
        4
        >>> w.quartile(3)
        5

        """
        # -1 to match with list indexing
        position = self.posi_quartile(quartile) - 1
        expanded_values = flatten_list([v * [k] for (k, v) in self.items()])
        if position.is_integer():
            return (expanded_values[int(position)] +
                    expanded_values[int(position) + 1]) / 2
        else:
            return expanded_values[ceil(position)]

    def posi_quartile(self, quartile=1):
        """
        Calcul la position du quartile

        :param quartile: le quartile concerné

        :return : la position du quartile (arondis à l'entier suppérieur, non arrondis)
        """
        return quartile * self.effectif_total() / 4

    # --------------------------
    # Rendu latex

    def tabular_latex(self):
        """ Latex code to display dataset as a tabular """
        latex = "\\begin{{tabular}}{{|c|*{{{nbr_col}}}{{c|}}}} \n".format(
            nbr_col=len(self.keys()))
        latex += "\t \hline \n"
        data_line = "\t {data_name} ".format(data_name=self.data_name)
        weight_line = "\t {weight_name} ".format(weight_name=self.weight_name)

        # TODO: Il faudra trouver une solution pour le formatage des données
        # |sam. janv.  9 13:14:26 EAT 2016
        for (v, e) in self.items():
            data_line += "& {val} ".format(val=v)
            weight_line += "& {eff} ".format(eff=e)

        latex += data_line + "\\\\ \n \t \\hline \n"
        latex += weight_line + "\\\\ \n \t \\hline \n"
        latex += "\\end{tabular}"

        return latex


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
