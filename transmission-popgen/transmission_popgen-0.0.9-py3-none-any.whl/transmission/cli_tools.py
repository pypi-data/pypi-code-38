# #!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# transmission: A tool for inferring endosymbiont biology from metagenome data.
# Copyright (C) 31/12/2018 Mark Juers

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

import ast
import pickle

import click

from transmission import ms_simulate


@click.command()
@click.option(
    "-n",
    "--nchrom",
    required=True,
    type=int,
    help="The number of chromosomes to sample from *each*" " population.",
    show_default=True,
)
@click.option(
    "-d",
    "--demes",
    "num_populations",
    required=True,
    type=int,
    help="The number of subpopulations.",
    show_default=True,
)
@click.option(
    "-M",
    "--Nm",
    "host_Nm",
    required=True,
    type=float,
    help="The host's Nm, calculated from mitochondrial or nuclear" " Fst",
    show_default=True,
)
@click.option(
    "-t",
    "--theta",
    "host_theta",
    required=True,
    type=float,
    help="The host's haploid theta estimated using pi or the" " Watterson estimator.",
    show_default=True,
)
@click.option(
    "-s",
    "--numsim",
    "num_simulations",
    default=10,
    type=int,
    help="The number of independent transmission parameters to" " simulate.",
    show_default=True,
)
@click.option(
    "-r",
    "--replicates",
    "num_replicates",
    default=10,
    type=int,
    help="The number of replicates for each simulation.",
    show_default=True,
)
@click.option(
    "-p",
    "--params",
    "prior_params",
    default='{"eta": (0, 0.1), "tau": (1, 1), "rho": (1, 1)}',
    type=str,
    help="A dict formatted as a string containing"
    " hyperparameters for distributions of eta, tau, and rho"
    " The distribution of eta is normal (mean, sd),"
    " while tau and rho are beta with pararmeters (a, b). rho uses"
    " a nonstandard beta distribution with support (0, 2).",
    show_default=True,
)
@click.option(
    "--nc",
    "num_cores",
    default="auto",
    type=str,
    help="The number of processing cores to use. For now,"
    ' integers must be quoted. "auto" will detect available procs.',
    show_default=True,
)
@click.option(
    "--ps",
    "prior_seed",
    type=int,
    help="The seed value for reproducible prior parameters",
    show_default=True,
)
@click.option(
    "--rs",
    "random_seed",
    type=int,
    help="The seed value for reproducible trees.",
    show_default=True,
)
@click.option(
    "--noprog",
    "progress_bar",
    default=True,
    is_flag=True,
    help="Do not display a progress bar.",
)
@click.option(
    "--h_opts",
    default="{}",
    type=str,
    help="options for transmission.Sample.h(), given as a sting"
    " representation of a dictionary.",
    show_default=True,
)
@click.argument("outfile", type=click.File("wb"))
def simulate_prior_stats(
    nchrom,
    num_populations,
    host_Nm,
    host_theta,
    num_simulations,
    num_replicates,
    prior_params,
    num_cores,
    prior_seed,
    random_seed,
    h_opts,
    progress_bar,
    outfile,
):
    """
    Generate pickled structured array of prior statistics with parameters
    generated from given hyper-priors.
    """

    try:
        num_cores = int(num_cores)
    except ValueError:
        if num_cores == "auto":
            pass
        else:
            raise ValueError("num_cores must be 'auto' or int")

    simulation_data = ms_simulate(
        nchrom=nchrom,
        num_populations=num_populations,
        host_theta=host_theta,
        host_Nm=host_Nm,
        num_simulations=num_simulations,
        num_replicates=num_replicates,
        prior_params=ast.literal_eval(prior_params),
        num_cores=num_cores,
        prior_seed=prior_seed,
        random_seed=random_seed,
        average_reps=True,
        h_opts=ast.literal_eval(h_opts),
        progress_bar=progress_bar,
    )
    pickle.dump(simulation_data, outfile)
