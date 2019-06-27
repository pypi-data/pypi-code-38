#/usr/bin/env python
# -*- coding:Utf-8 -*-

#
#
# Ensemble de fonction rendant beaucoup plus pratique la résolution et l'élaboration des exercices de stat au lycée
#
#

# TODO: Rendre toutes les réponses Explicable!! |mar. janv. 12 09:41:00
# EAT 2016

from math import sqrt, ceil
from .number_tools import number_factory
from .random_generator import random_generator


class Dataset(list):
    """ A dataset (a list) with statistics and latex rendering methods

    >>> s = Dataset(range(100))
    >>> s.sum()
    4950
    >>> s.mean()
    49.5
    >>> s.deviation()
    83325
    >>> s.variance()
    833.25
    >>> s.sd()
    28.87
    """

    @classmethod
    def random(cls, length, data_name="Valeurs",
               distrib="gauss", rd_args=(0, 1),
               nbr_format=lambda x: round(x, 2),
               v_min=None, v_max=None,
               exact_mean=None):
        """ Generate a random list of value

        :param length: length of the dataset
        :param distrib: Distribution of the data set. It can be a function or string from ["randint", "uniform", "gauss", "choice"]
        :param rd_args: arguments to pass to distrib
        :param nbr_format: function which format value
        :param v_min: minimum accepted value
        :param v_max: maximum accepted value
        :param exact_mean: if set, the last generated number will be create in order that the computed mean is exacly equal to "exact_mean"
        """
        data = random_generator(length,
                                distrib, rd_args,
                                nbr_format,
                                v_min, v_max,
                                exact_mean)

        return cls(data, data_name=data_name)

    def __init__(self, data=[], data_name="Valeurs"):
        """
        Create a numeric data set

        :param data: values of the data set
        :param data_name: name of the data set
        """
        list.__init__(self, data)

        self_name = data_name

    def add_data(self, data):
        """Add datas to the data set

        :param data: datas
        """
        try:
            self += data
        except TypeError:
            self += [data]

    # --------------------------
    # Stat tools

    def effectif_total(self):
        return len(self)

    @number_factory
    def sum(self):
        return sum(self)

    @number_factory
    def mean(self):
        return self.sum() / self.effectif_total()

    @number_factory
    def deviation(self):
        """ Compute the deviation (not normalized) """
        mean = self.mean()
        return sum([(x - mean)**2 for x in self])

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

        >>> w = Dataset(range(12))
        >>> w.quartiles()
        (0, 2.5, 5.5, 8.5, 11)
        """
        return (
            min(self),
            self.quartile(1),
            self.quartile(2),
            self.quartile(3),
            max(self))

    @number_factory
    def quartile(self, quartile=1):
        """
        Calcul un quartile de la série.

        :param quartile: quartile à calculer (par defaut 1 -> Q1)

        :return: le quartile demandé

        : Example:

        >>> w = Dataset(range(12))
        >>> w.quartile(1)
        2.5
        >>> w.quartile(2)
        5.5
        >>> w.quartile(3)
        8.5
        >>> w = Dataset(range(14))
        >>> w.quartile(1)
        3
        >>> w.quartile(2)
        6.5
        >>> w.quartile(3)
        10

        """
        # -1 to match with list indexing
        position = self.posi_quartile(quartile) - 1
        if position.is_integer():
            return (self[int(position)] + self[int(position) + 1]) / 2
        else:
            return self[ceil(position)]

    def posi_quartile(self, quartile=1):
        """
        Calcul la position du quartile

        :param quartile: le quartile concerné

        :return : la position du quartile (arondis à l'entier suppérieur, non arrondis)
        """
        return quartile * self.effectif_total() / 4

    # --------------------------
    # Rendu latex

    def tabular_latex(self, nbr_lines=1):
        """ Latex code to display dataset as a tabular """
        d_per_line = self.effectif_total() // nbr_lines
        d_last_line = self.effectif_total() % d_per_line
        splited_data = [self[x:x + d_per_line]
                        for x in range(0, self.effectif_total(), d_per_line)]
        # On ajoute les éléments manquant pour la dernière line
        if d_last_line:
            splited_data[-1] += [' '] * (d_per_line - d_last_line)

        # Construction du tableau
        latex = "\\begin{{tabular}}{{|c|*{{{nbr_col}}}{{c|}}}} \n".format(
            nbr_col=d_per_line)
        latex += "\t\t \hline \n"

        d_lines = [' & '.join(map(str, l)) for l in splited_data]
        latex += " \\\\ \n \\hline \n".join(d_lines)

        latex += " \\\\ \n \\hline \n"
        latex += "\\end{tabular}"

        return latex


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
