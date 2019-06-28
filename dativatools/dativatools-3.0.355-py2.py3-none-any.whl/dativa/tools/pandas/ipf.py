"""
(c) 2012-2019 Dativa, all rights reserved
-----------------------------------------
This code is licensed under MIT license (see license.txt for details)

Based on the IPFN module by Damien Forthomme:
https://github.com/Dirguis/ipfn/pull/11/files

Significant performance updated inspired by Haris Ballis' pull question
https://github.com/harisbal

"""
import logging


logger = logging.getLogger("dativa.tools.fastipf")

try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = None
    np = None

class Ipf:

    def __init__(self, aggregates, dimensions, weight_col='total',
                 convergence_rate=0.01, max_iteration=500, rate_tolerance=1e-8, validate_marginals=True):

        if not pd:
            raise ImportError("pandas must be installed to run Ipf")

        self.aggregates = aggregates
        self.dimensions = dimensions
        self.weight_col = weight_col
        self.convergence_rate = convergence_rate
        self.max_iteration = max_iteration
        self.rate_tolerance = rate_tolerance
        self.validate_marginals = validate_marginals

    @staticmethod
    def _iterate(series, aggregates, dimensions):
        """
        Runs the IPF iteration on the passed series
        """
        factors = []
        index_names = series.index.names

        for k, d in enumerate(dimensions):
            dfg = series.groupby(level=d).sum()
            dfg[dfg == 0] = 1
            f = aggregates[k].div(dfg)

            # Joining on multiindexes of not same length is not implemented

            series = series.multiply(f, fill_value=0)

            f = f.sub(1).abs().max()
            factors.append(f)

        # Check for convergence
        max_conv = max(factors)

        return series, max_conv

    @staticmethod
    def _get_marginals(aggregates, marginal):
        for agg in aggregates:
            if agg.index.name == marginal[0]:  # needs updating for compound marginals
                return agg

        raise ValueError("Marginal {0} is not present in aggregates".format(marginal))

    def _validate_marginals(self, df, aggregates, dimensions):
        # check the marginals are valid
        marginals_valid = True
        for marginal in dimensions:
            # get the values in the DataFrame for this marginal
            if len(marginal) > 1:
                raise NotImplementedError('Marginal {} has length greater than 1, which is not'
                                          ' implemented for this project'.format(marginal))
            source_marginals = pd.np.unique(df[marginal].values)

            # get the target marginals
            target_marginals = self._get_marginals(aggregates, marginal)  # needs updating for compound marginals

            # check each attribute in the DataFrame is present in the target marginal
            for attribute in source_marginals:

                if attribute not in target_marginals.index.tolist():
                    logger.error("Attribute '{0}' is not present in target marginal '{1}'".format(attribute, marginal))
                    marginals_valid = False

            # check each non-zero marginal in the target marginals is present in the DataFrame
            for attribute in target_marginals.index.tolist():
                if attribute not in source_marginals and target_marginals[attribute] > 0:
                    logger.error(
                        "Non-zero attribute '{0}' in target marginal '{1}' is not present in passed DataFrame".format(
                            attribute, marginal))
                    marginals_valid = False

        if not marginals_valid:
            raise ValueError("Marginals in passed DataFrame are missing from aggregates")

    def _run_iterations(self, m):

        conv = np.inf

        for iteration_number in range(self.max_iteration):

            old_conv = conv
            m, conv = self._iterate(m, self.aggregates, self.dimensions)

            logger.info("Completed IPF iteration {0}/{1}, convergence rate={2}".format(
                iteration_number + 1,
                self.max_iteration,
                conv))

            if conv <= self.convergence_rate:
                logger.warning('ipf converged: convergence_rate below threshold')
                return m
            elif abs(conv - old_conv) <= self.rate_tolerance:
                logger.warning('ipf converged: convergence_rate not updating or below rate_tolerance')
                return m

        logger.warning('Maximum iterations reached')
        return m

    def run(self, df):
        """
            Run IPFN on a pandas DataFrame

            df: dataframe to perform the ipf on.

            aggregates: list of numpy array or darray or pandas dataframe/series. The aggregates are the same as the marginals.
            They are the target values that we want along one or several axis when aggregating along one or several axes.

            dimensions: list of lists with integers if working with numpy objects, or column names if working with pandas objects.
            Preserved dimensions along which we sum to get the corresponding aggregates.

            convergence_rate: if there are many aggregates/marginal, it could be useful to loosen the convergence criterion.

            max_iteration: Integer. Maximum number of iterations allowed.

            rate_tolerance: float value. If above 0.0, like 0.001, the algorithm will stop once the difference between
                the conv_rate variable of 2 consecutive iterations is below that specified value
            """

        # validate the marginals
        if self.validate_marginals:
            logger.info("Validating marginals")
            self._validate_marginals(df, self.aggregates, self.dimensions)

        # prepare the series to run IPFN on
        m = df.copy()
        indexcols = list(set(x for l in self.dimensions for x in l))

        m.reset_index(inplace=True)
        m.set_index(indexcols, inplace=True)
        m = m[self.weight_col]

        logger.info("Running ipf")

        m = self._run_iterations(m)

        m.name = self.weight_col
        return df.join(m.to_frame(), on=indexcols, lsuffix="_old").drop("{0}_old".format(self.weight_col), axis=1)
