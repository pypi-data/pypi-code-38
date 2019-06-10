
import click
import pandas as pd

from .pji import identify_pji_taxa


@click.group('pji')
def pji():
    pass


@pji.command('find')
@click.argument('longform_taxa')
@click.argument('outfile', type=click.File('w'))
def cli_find_contams(longform_taxa, outfile):
    compression = 'gzip' if '.gz' in longform_taxa else None
    longtaxa = pd.read_csv(longform_taxa, compression=compression)
    longtaxa.columns = [
        'sample_name', 'taxa_name', 'taxa_id', 'rank', 'mpa',
        'cov', 'dup', 'kmers', 'percent', 'reads', 'tax_reads'
    ]
    longtaxa = longtaxa.query('kmers > 256')
    identified = identify_pji_taxa(longtaxa)
    identified.to_csv(outfile)


if __name__ == '__main__':
    pji()
