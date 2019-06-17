#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# transmission: A tool for inferring endosymbiont biology from metagenome data.
# Copyright (C) 4-11-2018 Mark Juers

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import collections.abc
import functools
from multiprocessing import Pool, cpu_count
import sys

import msprime as ms
import numpy as np
from rpy2.rinterface import NULL
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri as numpy2ri
from rpy2.robjects.packages import importr
import rpy2.robjects.vectors as vectors
from tqdm import tqdm


class Abc(object):

    """
    Interface to R package abc for estimating tau and rho posteriors.
    """

    def __init__(
        self,
        target,
        param,
        sumstat,
        tol=0.1,
        method="loclinear",
        transf={"tau": "logit", "rho": "logit", "eta": None},
        logit_bounds={"tau": (0, 1), "rho": (0, 1), "eta": (1, 1)},
        **kwargs
    ):
        """
        target(np.ndarray): 0 x nstat array of calculated summary
            statistics from observed sample. If a structured array is provided,
            column names will be returned.
        param (np.ndarray): num_iterations x 3 array of eta, tau, rho values
            simulated from their prior distributions. If a structured array is
            provided, column names will be returned.
        sumstat(np.ndarray): num_iterations x num_simulations array of summary
            statistics from simulated data. If a structured array is provided,
            column names will be returned.
        tol (float): Accepted proportion of sumstats accepted.
            tol * sumstat.shape[0] must be >= 2
        method (str): The ABC algorithm to use. May take "loclinear",
            "neuralnet", "rejection", or "ridge" as values. "loclinear" is
            chosen as the default as rejection does not allow transformation
            of parameters.
        transf (str): A dictionary of parameter: transformation pairs to use
            for parameter values. Each may take "log", "logit", or None.
        logit_bounds (np.ndarray): A dictionary with elements "tau", "rho",
            and "eta" each representing a tuple of lower and upper bounds
            for logit transformation to use if transf="logit" is specified.
        **kwargs: Additional arguments for r function 'abc'. Must be formatted
            for passing to R as described in the documentation for rpy2.
        """

        if tol * sumstat.shape[0] <= 1:
            raise ValueError("tol * sumstat.shape[0] must be >= 2")
        logit_bounds_matrix = (
            np.array([logit_bounds[x] for x in param.dtype.names])
            .view(type=np.ndarray)
            .reshape((len(param.dtype.names), -1))
        )
        # Change transformation from None to "none" for R.
        for key, value in transf.items():
            if not value:
                transf[key] = "none"
        if param.dtype.names:
            transf_list = [transf[x] for x in param.dtype.names]
        else:
            raise AttributeError("No names for parameter array")

        numpy2ri.activate()
        importr("abc")
        importr("base")
        self.abc = robjects.r.abc(
            target=target,
            param=Abc.rmatrix(param),
            sumstat=Abc.rmatrix(sumstat),
            tol=vectors.FloatVector([tol]),
            method=vectors.StrVector([method]),
            transf=(
                vectors.StrVector(["none"])
                if not transf
                else vectors.StrVector(transf_list)
            ),
            logit_bounds=Abc.rmatrix(logit_bounds_matrix),
            **kwargs
        )
        if method != "rejection":
            self.adj_values = np.core.records.fromarrays(
                np.array(self.abc.rx2("adj.values")).T, names=param.dtype.names
            )
            self.weights = np.array(self.abc.rx2("weights"))
            self.residuals = np.array(self.abc.rx2("residuals"))
        if method == "neuralnet":
            self.lambda_0 = np.array(self.abc.rx2("lambda"))
        if self.abc.rx2("na.action") != NULL:
            self.na_action = robjects.vectors.BoolVector(
                self.abc.rx2("na.action")
            )
        if not self.abc.rx2("region") != NULL:
            self.region = robjects.vectors.BoolVector(self.abc.rx2("region"))
        self.unadj_values = np.core.records.fromarrays(
            np.array(self.abc.rx2("unadj.values")).T, names=param.dtype.names
        )
        self.ss = np.core.records.fromarrays(
            np.array(self.abc.rx2("ss")).T, names=sumstat.dtype.names
        )
        self.dist = np.array(self.abc.rx2("dist"))
        self.call = self.abc.rx2("call")
        self.transf = np.array(self.abc.rx2("transf"))
        self.logit_bounds = np.array(self.abc.rx2("logit.bounds"))
        self.method = self.abc.rx2("method")
        self.kernel = self.abc.rx2("kernel")
        self.numparam = np.array(self.abc.rx2("numparam"))
        self.numstat = np.array(self.abc.rx2("numstat"))
        self.aic = np.array(self.abc.rx2("aic"))
        self.bic = np.array(self.abc.rx2("bic"))
        self.names = {
            "paramater_names": self.abc.rx("names").rx2("parameter.names"),
            "statistics_names": self.abc.rx("names").rx2("statistics.names"),
        }
        numpy2ri.deactivate()

    def summary(self):
        return robjects.r.summary(self.abc, print=False)

    @staticmethod
    def rmatrix(rec_array):
        """
        Return an r matrix, preserving column and row names, from a
            numpy record array.

        Args:
            rec_array (np.ndarray): A n X m numpy structured array.
        """

        if isinstance(rec_array, np.recarray):
            # Extract data from record array, i.e. make into standard
            # ndarray.
            rec_array_in = rec_array.view(np.float64).reshape(
                (rec_array.shape + (-1,) if rec_array.shape else (1, -1))
            )
        else:
            rec_array_in = rec_array
        if rec_array.shape:
            out = robjects.r.matrix(
                rec_array_in,
                nrow=rec_array.shape[0],
                ncol=(
                    len(rec_array.dtype.names)
                    if rec_array.dtype.names
                    else rec_array.shape[1]
                ),
                dimnames=robjects.r.list(
                    NULL,
                    (
                        vectors.StrVector(rec_array.dtype.names)
                        if rec_array.dtype.names
                        else NULL
                    ),
                ),
            )
        else:
            out = robjects.vectors.FloatVector(rec_array_in)
            out.names = robjects.vectors.StrVector(rec_array.dtype.names)
        return out


class Sample(object):

    """
    Coalescent simulation output representing a population class and methods.
    Input argument should be a np.ndarray with 2 dimensions detailed
    in __init__ or an msprime.TreeSequence object.

    Attributes:
        nchrom: the number of chromosomes sampled
        gtmatrix: the original matrix supplied, consisting of [0, 1]
        type: the input type, either "TreeSequence" or "ndarray"
        popdata: the original object passed to instantiate the class

    """

    def __init__(self, popdata):
        """
        Args:
            popdata (np.ndarray OR msprime.TreeSequence): A 2D np.ndarray
                with individual chromosomes
                represented by rows and snp positions represented by columns.
                Alternatively, an object of class "TreeSequence" can be
                provided and the relevant attributes will be inferred.
                Note that this it the transpose of
                msprime.TreeSequence.genotype_matrix(). This accomodates
                generators output by msprime.simulate() num_replicates
                argument and accepts such an iterable  while returning
                a tuple of "TreeSequence" or "np.ndarray"
                objects.
        """

        # Make self.popdata iterable for consistency with multiple replicates.
        if isinstance(popdata, collections.abc.Iterator):
            self.popdata = tuple(popdata)
        elif isinstance(popdata, list) or isinstance(popdata, tuple):
            self.popdata = popdata
        else:
            self.popdata = tuple(popdata for _ in (0,))
        if type(self.popdata[0]).__name__ == "TreeSequence":
            self.nchrom = self.popdata[0].num_samples
            self.type = "TreeSequence"
        else:
            self.nchrom = self.popdata[0].shape[0]
            self.type = "ndarray"
        self.populations = np.zeros(self.nchrom, dtype=int)
        self.npop = 1
        self.pop_sample_sizes = np.array(self.nchrom)
        self.num_replicates = len(self.popdata)

    def __str__(self):
        print(
            "a {reps} replicate {nchrom} chromosome sample with "
            "{segsites} segregating sites".format(
                nchrom=self.nchrom,
                segsites=self.segsites(),
                reps=len(self.popdata),
            )
        )

    def gtmatrix(self):
        """
        Sample.gtmatrix() returns a
        self.nchrom X self.sites matrix of sample genotypes.
        """
        out = []
        for rep in self.popdata:
            if self.type == "TreeSequence":
                out.append(rep.genotype_matrix().T)
            else:
                out.append(rep)
        return out if len(out) > 1 else out[0]

    def h(self, average=False, bias=True, by_population=False):
        """
        Calculate heterozygosity over sites in sample.
        Returns a list of np.ndarrays of dimensions npop X segsites,
        or, if average==True, a npop X num_replicates np.ndarray.
        Args:
            average (bool): whether to average H values for all sites
            bias (bool): whether to apply bias-correction to calculations
            by_population (bool): whether to calculate heterozygosity by
                population, or alternatively, as a metapopulation (H_T).
            h_opts (dict): Extra arguments for self.h().
        """

        # Check if multiple populations are provided or desired
        populations = (
            self.populations
            if by_population
            else np.zeros(self.nchrom, dtype=int)
        )
        # populations for portability to MetaSample
        # Each row in harray is a population; each column a snp.
        sample_sizes = (
            self.pop_sample_sizes
            if by_population
            else np.array([[self.nchrom]])
        )
        out = []
        for repidx, replicate in enumerate(self.popdata):
            if replicate.num_sites != 0:
                num_mutants = self.num_mutants(populations, replicate)[0]
                parray = np.true_divide(num_mutants, sample_sizes.T)
                harray = 2 * parray * (1 - parray)
                if bias:
                    harray = (
                        np.true_divide(sample_sizes, (sample_sizes - 1)).T
                        * harray
                    )
                if average:
                    out.append(np.mean(harray, axis=1))
                else:
                    out.append(harray)
            elif by_population:
                out.append(np.full(self.npop, 0.0))
            else:
                out.append(np.full(1, 0.0))
        if not average:
            return tuple(out)
        else:
            return np.array(out).T

    def num_mutants(self, populations, popdata=None):
        """
        Returns the number of mutant alleles observed at each site.
        Used by other methods.

        Args:
            populations (numpy.ndarray): Ints corresponding to
                which population each chromosome belongs.
            popdata (TreeSequence object or np.ndarray): Single replicate for
                which to compute num_mutants.
        """
        # Allows computation of single replicate snps.
        popdata = self.popdata if not popdata else tuple(popdata for _ in (0,))
        popset = set(populations)
        out = []
        for repidx, replicate in enumerate(popdata):
            num_mutants = np.zeros(
                (len(popset), replicate.num_sites), dtype=int
            )
            if self.type == "TreeSequence":
                for siteidx, site in enumerate(replicate.variants()):
                    for pop in popset:
                        num_mutants[pop, siteidx] = np.count_nonzero(
                            site.genotypes[populations == pop]
                        )
            else:
                for pop in popset:
                    num_mutants[pop] = np.count_nonzero(
                        self.gtmatrix[np.nonzero(populations == pop)], axis=0
                    )
            out.append(num_mutants)
        # Return tuple if multiple replicates, otherwise single matrix.
        return tuple(out)

    def pi(self, pi_method="h", h_opts={}, **kwargs):
        """
        Calculates different metrics of nucleotide diversity.

        Args:
            pi_method (str): what method to use to calculate pi.
            available methods are 'nei', 'tajima', and 'h'.
                nei: sum_{ij} x_i x_j pi_{ij} where x_y is the
                    frequency of the yth sequence and pi_{ij} is the
                    number of pairwise differences
                tajima: sum_{ij} k_{ij} / n choose 2
                    k_{ij} is the number of pairwise differences between the
                    ith and jth samples. This is the implementation used
                    originally in Tajima's D.
                h: Simply the sum of heterozygosities across all sites.
                    Takes arguments to self.h() as optional arguments,
                    namely 'bias'.
            h_opts (dict): Extra arguments for self.h() in the form of a
                kwargs dictionary.
        """

        out = np.zeros((len(self.popdata),))
        if pi_method == "nei":
            for repidx, rep in enumerate(self.gtmatrix()):
                # Hash rows of genotype matrix to reduce time comparing.
                hashes = np.apply_along_axis(
                    lambda row: hash(tuple(row)), 1, rep
                )
                seqs = dict.fromkeys(set(hashes))
                # Loop over seqs keys to calculate sequence frequncies
                # as well as create dict items for sequences themselves.
                for seqid in seqs:
                    seqs[seqid] = {}
                    seqid_array = np.full(self.nchrom, seqid)
                    # Get frequencies.
                    if self.nchrom == 0:
                        seqs[seqid]["p"] = 0.0
                    else:
                        seqs[seqid]["p"] = (
                            np.count_nonzero(seqid_array == hashes)
                            / self.nchrom
                        )
                    # Associate sequences with hashes.
                    for i in np.arange(self.nchrom):
                        if seqid == hash(tuple(rep[i,])):
                            seqs[seqid]["seq"] = np.array(rep[i,])
                            break
                # Calculate nucleotide diversity.
                nucdiv = 0
                for i in seqs:
                    for j in seqs:
                        if i != j:
                            nucdiv += (
                                seqs[i]["p"]
                                * seqs[j]["p"]
                                * np.count_nonzero(
                                    seqs[i]["seq"] != seqs[j]["seq"]
                                )
                            )
                out[repidx] = nucdiv
        elif pi_method == "tajima":
            for repidx, rep in enumerate(self.gtmatrix()):
                k = 0
                # count number of pairwise differences for unique comparisons.
                for i in np.arange(self.nchrom - 1):
                    for j in np.arange(i, self.nchrom):
                        k += np.count_nonzero(rep[i,] != rep[j,])
                # Formula: \sum{k_ij} / (nchrom choose 2)
                out[repidx] = k / ((self.nchrom - 1) * self.nchrom / 2)
        elif pi_method == "h":
            out = np.array([np.sum(x) for x in self.h(**h_opts)])
        else:
            raise NameError("Unsupported method, {}".format(pi_method))
        return out if out.size > 1 else out[0]

    def polymorphic(self, threshold=0, output=("num", "which")):
        """
        Returns polymorphism attributes as dict or value.
        Attributes are number of polymorphic sites and index positions of
        polymorphic sites.

        Args:
            threshold (int): Number of derived alleles
                above which polymorphism is counted, e.g.,
                threshold=1 excludes singletons.
            output (tuple or str): Whether to output number of
                polymorphic sites or index positions of polymorphic sites,
                or both. Possible values are "num" returning number of sites,
                "which" returning indices,
                or a tuple of both (default) returning a dict of both.
        """
        valid_outputs = ("which", "num")
        snp_array = np.zeros((self.npop, self.num_replicates), dtype=int)
        which = []
        for repidx, rep in enumerate(
            self.num_mutants(populations=self.populations)
        ):
            snp_array[:, repidx] = np.count_nonzero(rep > threshold, axis=1)
            # np.nonzero returns an array of *coordinates*.
            # Transpose for ordered pairs on rows.
            snp_which = np.nonzero(rep > threshold)
            which.append(snp_which)
        results = {"which": tuple(which), "num": snp_array}
        if type(output) == tuple and len(
            set(output).intersection(set(valid_outputs))
        ) == len(output):
            return results
        elif output in valid_outputs:
            return results[output]
        else:
            raise ValueError(
                "Invalid output, {output} specified."
                "Specify 'num' or 'which'.".format(output=output)
            )

    def segsites(self):
        out = np.zeros(len(self.popdata), dtype=int)
        for repidx, replicate in enumerate(self.popdata):
            if self.type == "TreeSequence":
                out[repidx] = replicate.num_sites
            else:
                out[repidx] = replicate.shape[1]
        return out[0] if out.size == 1 else out

    def theta_w(self, by_population=False, threshold=0):
        """
        Calculate the Watterson estimator.

        Args:
            by_population (bool): Whether to compute theta_w per-population.
            threshold (int): Sites with threshold or fewer derived alleles will
                not be considered as SNPs, e.g., threshold=1 excludes
                singletons.

        Returns:
            If by_population: npop X num_replicates np.ndarray
            If not by_population: 1 X num_replicates np.ndarray
        """
        # Check if multiple populations are provided or desired
        populations = (
            self.populations
            if by_population
            else np.zeros((self.nchrom,), dtype=int)
        )
        # populations for portability to MetaSample
        nchrom = np.bincount(populations)
        harmonic_num = np.apply_along_axis(
            lambda x: np.sum(1 / np.arange(1, x)), 1, nchrom.reshape((-1, 1))
        )
        num_polymorphic = self.polymorphic(output="num", threshold=threshold)
        return num_polymorphic / harmonic_num.reshape((-1, 1))


class MetaSample(Sample):

    """

    Class representing a metapopulation sample and associated methods.

    Input argument should be a nchrom X segsites np.ndarray with an
    array listing to which population each chromosome belongs,
    or an msprime.TreeSequence object.

    Attributes:
        npop (int): The number of populations in the sample.
        pop_sample_sizes (np.ndarray): The number of individuals sampled from
            each population.
        populations (np.ndarray): A 1-dimensional np.ndarray of ints
            specifying to which population each sample belongs.

    """

    def __init__(self, popdata, populations, force_meta=False):
        """
        Args:
            popdata (np.ndarray OR msprime.TreeSequence): A 2D np.ndarray
                with individual chromosomes
                represented by rows and snp positions represented by columns.
                Alternatively, an object of class "TreeSequence" can be
                provided and the relevant attributes will be inferred.
                Note that this it the transpose of
                msprime.TreeSequence.genotype_matrix(). This accomodates
                generators output by msprime.simulate() num_replicates
                argument and accepts such an iterable  while returning
                a tuple of "TreeSequence" or "np.ndarray"
                objects.
            populations (np.ndarray): A 1D np.ndarray of ints specifying to
                which population each sample belongs.
            force_meta (bool): Whether to force a single population to become
                a metapopulation rather than coercion to Population class.
        """
        super(MetaSample, self).__init__(popdata)
        if len(set(populations)) == 1 or (
            self.type == "TreeSequence"
            and self.popdata[0].num_populations == 1
            and not force_meta
        ):
            raise Exception(
                "Only 1 population provided. "
                "Use force_meta=True for MetaSample or use Sample."
            )
        else:
            self.npop = (
                self.popdata[0].num_populations
                if self.type == "TreeSequence"
                else len(set(populations))
            )
        self.pop_sample_sizes = np.array(
            [
                [
                    np.count_nonzero(np.full(self.nchrom, x) == populations)
                    for x in set(populations)
                ]
            ]
        )
        self.populations = populations

    def fst(
        self,
        fst_method="gst",
        summary="mean",
        average_reps=False,
        average_sites=True,
        h_opts={},
    ):
        """
        Returns specified fst statistic.
        Args:
            fst_method (str): Only "gst" is supported right now. This returns
            the classic (ht - hs) / ht statistic.
            average_sites (bool): Whether to average the heterozygosities
                across sites when calculating. If false, will return a
                num_replicates list of self.segsites()-long arrays.
            summary (str or tuple): The summary statistics returned for
                replicates. Can take arguments "mean" or "sd" for standard
                deviation. Returns a dictionary of the supplied statistics.
                Redundant if not average_sites.
            average_reps (bool): Whether to average final fst values. If true,
                returns 1 fst value, otherwise 1 value for each replicate in an
                array. Redundant if not average_sites.
            h_opts (dict): Extra arguments for Sample.h(), in the form of a
                kwargs dictionary.
        """
        if isinstance(summary, str):
            summary = (summary,)
        if fst_method == "gst":
            ind = np.where(self.segsites() != 0)[0]
            h_by_site = tuple(
                self.h(by_population=True, **h_opts)[i] for i in ind
            )
            hs = tuple(
                np.average(x, axis=0, weights=self.pop_sample_sizes[0])
                for x in h_by_site
            )
            ht = tuple(x[0] for x in tuple(self.h(**h_opts)[i] for i in ind))
            fst = tuple((1 - np.true_divide(x, y)) for x, y in zip(hs, ht))
            if average_sites:
                stats = []
                if "mean" in summary:
                    if self.segsites().any():
                        stats.append([np.average(x) for x in fst])
                    else:
                        stats.append(0.0)
                if "sd" in summary:
                    if self.segsites().any():
                        stats.append([np.std(x) for x in fst])
                    else:
                        stats.append(0.0)
                if average_reps:
                    try:
                        stats = [
                            np.average(x, weights=self.segsites()[ind])
                            for x in stats
                        ]
                    except Exception:
                        stats = np.array([0.0 for _ in stats])
                return dict(zip(summary, stats))
            else:
                return fst
        else:
            raise Exception("invalid method {}".format(fst_method))


def fst(Nm, tau, rho):
    """
    Theoretical Fst from Nm, tau, and rho.

    Args:
        Nm (float): The migration parameter Ne * m.
        tau (float): The rate of vertical transmission.
        rho (float): The proportion of the population that is female.
    """

    A = tau ** 2 * (3 - 2 * tau) * (1 - rho)
    B = 2 * rho * (1 - rho) * (A + rho)

    return B / (Nm + B)


def ms_simulate(
    nchrom,
    num_populations,
    host_theta,
    host_Nm,
    num_simulations,
    stats=("fst_mean", "fst_sd", "pi_h"),
    prior_params={"eta": (0, 0.1), "tau": (1, 1), "rho": (1, 1)},
    nsamp_populations=None,
    num_replicates=1,
    num_cores="auto",
    theta_source="mt",
    prior_seed=None,
    average_reps=True,
    progress_bar=False,
    h_opts={},
    **kwargs
):
    """
    Generate random sample summary using msprime for the specified prior
    distributions of tau (vertical transmission rate) and rho (sex ratio).

    From a supplied dict of prior (hyper)parameters, ms_simulate generates a
    num_simulations-tall array of parameters with which to estimate the
    posterior distributions of tau and rho using abc methods. It then draws
    num_replicates coalescent samples for each parameter combination and
    outputs a summary table consisting of mean fst, fst standard deviation, pi,
    and the original simulated parameter values for each metasimulation.

    Args:
        nchrom (int): The number of chromosomes to sample from each population
        num_populations (int): The number of populations to include in the
            migration matrix.
        host_theta (float): The host's haploid theta (2 * Ne * mu * L)
            estimated from mitochondrial or nuclear data.
        host_Nm (float): The symmetric migration parameter (2 * Ne * m),
            estimated from host mitochondrial or nuclear fst.
        num_simulations (int): The number of tau-rho pairs of parameters
            to draw from their priors, and hence the number of metasimulations
            to include in the output.
        stats (tuple): The statistics to be returned by the simulation.
            May take values "fst_mean" for mean locus Fst, "fst_sd" for locus
            standard deviation, or "pi_h", "pi_nei", or "pi_tajima". See
            Sample.pi() documentation for details.
        prior_params (dict): A dict containing tuples specifiying the prior
            distribution parameters for eta, tau, and rho. That is, the
            mutation rate multiplier, vertical transmission frequency, and
            sex ratio. Optionally one may provide a scalar value for eta to
            fix the mutation rate multiplier.
        num_replicates (int): Number of msprime replicates to run for each
            simulated parameter pair and the number of simulations in each
            metasimulation.
        average_reps (bool): Whether to average replicates. False will return
            raw simulations.
        progress_bar (bool): Display a progress bar for prior simulations.
            Redundant if num_cores is set to None.
        num_cores (int or str): The number of cores to use for computation.
            "auto" will automatically detect using multiprocessing.cpu_count().
            None will use a single thread not routed through
            multiprocessing.Pool, primarily for debugging and profiling.
            An int value will specify the number of cores to use.
        theta_source (str): What is theta estimated from? Takes "mt" or "nuc".
        prior_seed (int): The seed used to draw samples for tau and rho.
            Setting a seed will allow repeatability of results.
        h_opts (dict): Extra options for Sample.h() in the form of a kwargs
            dictionary.
        **kwargs (): Extra arguments for ms.simulate(), Sample.pi(), and
            Sample.fst().
    """

    # Number of output statistics plus parameters eta, tau, and rho.

    populations = np.repeat(np.arange(num_populations), nchrom)
    population_config = tuple(
        ms.PopulationConfiguration(nchrom) for _ in np.arange(num_populations)
    )
    nsamp_populations = (
        num_populations if not nsamp_populations else nsamp_populations
    )
    if prior_seed:
        np.random.seed(prior_seed)
    if isinstance(prior_params["eta"], float):
        eta = np.full((num_simulations,), prior_params["eta"])
    elif isinstance(prior_params["eta"], tuple):
        eta = np.random.normal(
            prior_params["eta"][0], prior_params["eta"][1], num_simulations
        )
    else:
        raise Exception("eta must be tuple or float")
    tau = np.random.beta(
        prior_params["tau"][0], prior_params["tau"][1], size=num_simulations
    )
    rho = np.random.beta(
        prior_params["rho"][0], prior_params["rho"][1], size=num_simulations
    )
    params = np.array([eta, tau, rho]).T
    simpartial = functools.partial(
        sim,
        host_theta=host_theta,
        host_Nm=host_Nm,
        population_config=population_config,
        num_replicates=num_replicates,
        populations=populations,
        theta_source=theta_source,
        average_reps=True,
        stats=stats,
        h_opts=h_opts,
        **kwargs
    )
    structure = {
        "names": stats + tuple(prior_params.keys()),
        "formats": tuple(np.repeat("f8", len(stats) + len(prior_params))),
    }
    if num_cores:
        # for multiprocessing, None automatically detects number of cores.
        # Switching here allows autodetection.
        if num_cores == "auto":
            num_cores = cpu_count()
        pool = Pool(processes=num_cores)
        if progress_bar:
            out = np.array(
                list(tqdm(pool.imap(simpartial, params), total=len(params)))
            )
        else:
            out = np.array(list(pool.imap(simpartial, params)))
    else:
        out = np.apply_along_axis(simpartial, 1, params)
    out = np.core.records.fromarrays(out.T, dtype=structure)
    return out


def sim(
    params,
    host_theta,
    host_Nm,
    population_config,
    populations,
    stats,
    num_replicates,
    theta_source="mt",
    average_reps=True,
    h_opts={},
    **kwargs
):
    """
    Runs actual simulation with ms. Intended as helper for ms_simulate().

    At top level for picklability (for multiprocessing).

    Args:
        params (tuple): eta, tau, rho for simulation.
        host_theta (float): Estimate of host theta (2*Ne*mu*L) for host.
        host_Nm (float): Estimate of host migration parameter (Ne*m).
        population_config (list): List of population configurations for
            msprime.
        populations (np.ndarray): A nchrom np.ndarray indicating to which
            population each chromosome belongs.
        stats (tuple): The requested statistics to be calculated. May contain
            any of "fst_mean", "fst_sd", "pi_h", "pi_nei", "pi_tajima",
            "theta_w", or "num_sites".
        theta_source (str): What is theta estimated from? Takes "mt" or "nuc".
        average_reps (bool): Whether to return averaged replicates. False will
            return raw summaries.
        num_replicates (int): Number of msprime replicates to run for each
            simulated parameter pair and the number of simulations in each
            metasimulation.
        h_opts (dict): Extra arguments for Sample.h(), formatted as kwargs
            dictionary.
        **kwargs (): Extra arguments for msprime.simulate().
    """

    eta, tau, rho = params
    if theta_source == "mt":
        a = rho
    elif theta_source == "nuc":
        a = 2.0
    else:
        raise ValueError("theta_source must be 'mt' or 'nuc'")
    A = tau ** 2 * (3 - 2 * tau) * (1 - rho)
    B = 2 * rho * (1 - rho) * (A + rho)
    symbiont_Nm = np.true_divide(host_Nm, 2 * B)
    symbiont_theta = np.true_divide(10 ** eta * host_theta, a * 2 * B)
    num_populations = len(population_config)
    migration = np.full(
        (num_populations, num_populations),
        np.true_divide(
            # num_populations - 1 is multiplied by 2 to preserve the value of
            # 2*Nm during the simulation as ms does.
            symbiont_Nm,
            ((num_populations - 1) * 2),
        ),
    )
    np.fill_diagonal(migration, 0)
    tree = ms.simulate(
        Ne=0.5,  # again, factor of 1/2 to preserve ms behavior
        num_replicates=num_replicates,
        migration_matrix=migration,
        population_configurations=population_config,
        mutation_rate=symbiont_theta / 2,  # factor of 1/2 to preserve ms beh.
        **kwargs
    )
    treesample = MetaSample(tree, populations)
    out = (
        np.zeros((num_replicates, len(stats) + len(params)))
        if not average_reps
        else np.zeros((1, len(stats) + len(params)))
    )
    if len(set(("fst_mean", "fst_sd")).intersection(set(stats))) > 0:
        fst_summ = treesample.fst(
            average_sites=True,
            average_reps=average_reps,
            summary=("mean", "sd"),
            h_opts=h_opts,
        )
    for statidx, stat in enumerate(stats):
        if stat == "pi_h":
            out[:, statidx] = (
                treesample.pi(pi_method="h", h_opts=h_opts, **kwargs)
                if not average_reps
                else np.mean(
                    treesample.pi(pi_method="h", h_opts=h_opts, **kwargs)
                )
            )
        elif stat == "pi_nei":
            out[:, statidx] = (
                treesample.pi(pi_method="nei", **kwargs)
                if not average_reps
                else np.mean(treesample.pi(pi_method="nei", **kwargs))
            )
        elif stat == "pi_tajima":
            out[:, statidx] = (
                treesample.pi(pi_method="tajima", **kwargs)
                if not average_reps
                else np.mean(treesample.pi(pi_method="tajima", **kwargs))
            )
        elif stat == "num_sites":
            out[:, statidx] = (
                treesample.segsites()
                if not average_reps
                else np.mean(treesample.segsites())
            )
        elif stat == "theta_w":
            out[:, statidx] = (
                treesample.theta_w()
                if not average_reps
                else np.mean(treesample.theta_w())
            )
        elif stat == "fst_mean":
            out[:, statidx] = fst_summ["mean"]
        elif stat == "fst_sd":
            out[:, statidx] = fst_summ["sd"]
    out[:, -3] = eta
    out[:, -2] = tau
    out[:, -1] = rho
    return out if not average_reps else out[0]


def main():
    return 0


if __name__ == "__main__":
    main()
