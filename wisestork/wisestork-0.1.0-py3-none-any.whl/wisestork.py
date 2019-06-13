#    Copyright (C) 2016-2019  Sander Bollen
#
#    This file is part of wisestork
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see {http://www.gnu.org/licenses/}.

"""
wisestork.wisestork
~~~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2016-2019 Sander Bollen
:license: GPL-3.0
"""

import click

from .count import count
from .gc_correct import gc_correct
from .newref import newref
from .ztest import ztest
from . import version as wiseguy_version

shared_options = [
    click.option("--binsize", "-B", type=click.IntRange(0, None),
                 default=50000,
                 help="Bin size to use. Default = 50000"),
    click.option("--reference", "-R", type=click.Path(exists=True),
                 required=True,
                 help="Path to reference fasta"),
    click.option('--bin-file', '-L', type=click.Path(exists=True),
                 required=False,
                 help="Optional path to region BED file"),
    click.version_option(version=wiseguy_version())
]


def generic_option(options):
    """
    Decorator to add generic options to Click CLI's
    The group parent should NOT be decorated with this decorator
    :param options: list of click.option
    :return: decorated function
    """
    def __generic_option(func):
        for option in reversed(options):
            func = option(func)
        return func
    return __generic_option


@click.command(short_help="Count coverages")
@generic_option(shared_options)
@click.option("--output", "-O", type=click.Path(), required=True,
              help="Path to output BED file")
@click.option("--input", "-I", type=click.Path(exists=True), required=True,
              help="Path to input BAM file")
def count_cli(**kwargs):
    """
    Take a BAM file, and calculate the number of reads per bin.
    It will output a BED file (with 0-based positions) of regions and
    associated number of reads per bin.

    \b
    Your BAM file _must_ be indexed and _must_ contain chromosome
    lengths and names in the header.
    """
    input = kwargs.get("input", None)
    output = kwargs.get("output", None)
    binsize = kwargs.get("binsize", 50000)
    reference = kwargs.get("reference", None)
    regions = kwargs.get("bin_file", None)
    count(input=input, output=output, binsize=binsize, reference=reference,
          binfile=regions)


@click.command(short_help="GC correct")
@generic_option(shared_options)
@click.option("--output", "-O", type=click.Path(), required=True,
              help="Path to output BED file")
@click.option("--input", "-I", type=click.Path(exists=True), required=True,
              help="Path to input BED file")
@click.option("--frac-n", "-n", type=click.FLOAT, default=0.1,
              help="Maximum fraction of N-bases per bin. Default = 0.1")
@click.option("--frac-r", "-r", type=click.FLOAT, default=0.0001,
              help="Minimum fraction of reads per bin. Default = 0.0001")
@click.option("--iter", "-t", type=click.INT, default=3,
              help="Number of iterations for LOWESS function. Default = 3")
@click.option("--frac-lowess", "-l", type=click.FLOAT, default=0.1,
              help="Fraction of data to use for LOWESS function. "
                   "Default = 0.1")
def gcc_cli(**kwargs):
    """
    GC-correct a BED file containing counts per region
    """
    input_path = kwargs.get("input", None)
    output = kwargs.get("output", None)
    reference = kwargs.get("reference", None)
    frac_n = kwargs.get("frac_n", 0.1)
    frac_r = kwargs.get("frac_r", 0.0001)
    iter = kwargs.get("iter", 3)
    frac_lowess = kwargs.get("frac_lowess", 0.1)
    gc_correct(input=input_path, output=output, reference=reference,
               frac_r=frac_r, frac_n=frac_n, iter=iter,
               frac_lowess=frac_lowess)


@click.command(short_help="Calculate Z-scores")
@generic_option(shared_options)
@click.option("--input", "-I", type=click.Path(exists=True), required=True,
              help="Path to input BED file")
@click.option("--output", "-O", type=click.Path(), required=True,
              help="Path to output BED file")
@click.option("--dictionary-file", "-D", type=click.Path(), required=True,
              help="Path to dictionary BED file")
def zscore_cli(**kwargs):
    """
    Calculate Z-scores from GC-corrected BED files.

    \b
    You must supply a "reference dictionary" BED file
    containing locations of reference bins.
    This reference dictionary must be gzipped and
    indexed with tabix.

    \b
    Your query BED file should also be gzipped and
    indexed with tabix
    """
    input_path = kwargs.get("input", None)
    output_path = kwargs.get("output", None)
    database = kwargs.get("dictionary_file", None)
    ztest(input_path=input_path, output_path=output_path,
          database_path=database)


@click.command(short_help="Create new reference")
@generic_option(shared_options)
@click.option("--input", "-I", type=click.Path(exists=True), required=True,
              multiple=True, help="Path(s) to input BEDs")
@click.option("--output", "-O", type=click.Path(), required=True,
              help="Path to output BED file")
@click.option("--n-bins", "-n", type=click.INT, default=250,
              help="Amount of neighbours bins to consider per bin")
def newref_cli(**kwargs):
    """
    Create a new reference dictionary BED file.

    \b
    This tool takes multiple input BED files.
    For each bin, it will then find a set of neighbour bins
    that behave most similar to one another.

    \b
    You must short and then tabix the output after running this tool.
    """
    input_path = kwargs.get("input", None)
    output_path = kwargs.get("output", None)
    reference_fasta = kwargs.get("reference", None)
    binsize = kwargs.get("binsize", 50000)
    n_bins = kwargs.get("n_bins", 250)
    regions = kwargs.get("bin_file", None)
    newref(input_paths=input_path, output_path=output_path,
           reference=reference_fasta,
           binsize=binsize, n_bins=n_bins, binfile=regions)


@click.group()
@click.version_option()
def cli(**kwargs):
    """
    Discover CNVs from BAM files.

    \b
    A typical workflow first extracts regions from a BAM file
    The resulting BED tracks must then be GC-corrected.
    Using a reference track of region similarity,
    One can then calculate Z-scores for every region.

    \b
    The following sub-commands are supported:
     - count: count coverage per bin
     - gc-correct: GC-correct bins
     - zscore: calculate Z-scores
     - newref: Generate a new reference dictionary of bin similarities

    """
    pass


def main():
    cli.add_command(count_cli, "count")
    cli.add_command(gcc_cli, "gc-correct")
    cli.add_command(zscore_cli, "zscore")
    cli.add_command(newref_cli, "newref")
    cli()


if __name__ == '__main__':
    main()
