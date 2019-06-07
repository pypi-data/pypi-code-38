"""
Module for parsing .bed files containing gene track information.
"""

import gzip


def load_genes(bedfile):
    """
    Loads information for genes from a .bed file into dicts and returns them.

    Parameters
    ----------
    bedfile : str
        String reference to location of .bed file to load genes from.

    Returns
    -------
    dict of lists of dicts
        The keys are chromosome names. The values are lists of genes for that
        chromosome. The genes are represented as dicts with the following
        structure::

            {
                'start' : int,
                'end'   : int,
                'name'  : str,
                'strand': '+' or '-',
                'blocks': list of dicts
            }

        Blocks typically represent exons and are represented as dicts with the
        following structure::

            {
                'start': int,
                'end'  : int
            }

    """
    # dict to store genes
    genes = {}

    # parse bedfile
    with open(bedfile, 'r') as handle:
        for line in handle:
            # skip comments and track line
            if line.startswith('#') or line.startswith('track'):
                continue

            # split line
            pieces = line.strip().split('\t')

            # parse chromosome
            chromosome = pieces[0]

            # add chromosome to dict if this is a new one
            if chromosome not in genes:
                genes[chromosome] = []

            # parse gene information
            start = int(pieces[1])
            end = int(pieces[2])
            name = pieces[3]
            strand = pieces[5]
            thick_start, thick_end = None, None
            if len(pieces) > 6:
                thick_start = int(pieces[6])
                thick_end = int(pieces[7])
                block_sizes = [int(piece)
                               for piece in pieces[10].strip(',').split(',')]
                block_starts = [int(piece)
                                for piece in pieces[11].strip(',').split(',')]

            # compute block information
            blocks = []
            if thick_start and thick_end and not thick_start == thick_end:
                for i in range(len(block_starts)):
                    block = {}
                    block['start'] = max(start + block_starts[i], thick_start)
                    block['end'] = min(start + block_starts[i] + block_sizes[i],
                                       thick_end)
                    if block['end'] > block['start']:
                        blocks.append(block)

            # add this gene to the list
            genes[chromosome].append({'chrom' : chromosome,
                                      'start' : start,
                                      'end'   : end,
                                      'name'  : name,
                                      'strand': strand,
                                      'blocks': blocks})
        for chrom in genes:
            genes[chrom].sort(key=lambda x: x['start'])

    return genes


def load_gene_table(tablefile):
    """
    Similar to ``load_genes()``, but reads in a gzipped UCSC table file instead.

    The main advantage of this approach is that genes parsed this way include
    human-readable gene symbols.

    Parameters
    ----------
    tablefile : str
        String reference to location of the gzipped table file to read.

    Returns
    -------
    dict of lists of dicts
        The keys are chromosome names. The values are lists of genes for that
        chromosome. The genes are represented as dicts with the following
        structure::

            {
                'start' : int,
                'end'   : int,
                'name'  : str,
                'id': str,
                'strand': '+' or '-',
                'blocks': list of dicts
            }

        Blocks typically represent exons and are represented as dicts with the
        following structure::

            {
                'start': int,
                'end'  : int
            }
    """
    # dict to store genes
    genes = {}

    # parse bedfile
    with gzip.open(tablefile, 'rb') as handle:
        for line in handle:
            # skip header
            if line.startswith('#'):
                continue

            # split line
            pieces = line.split('\t')

            # parse chromosome
            chromosome = pieces[2].strip()

            # add chromosome to dict if this is a new one
            if chromosome not in genes:
                genes[chromosome] = []

            # parse gene information
            start = int(pieces[4])
            end = int(pieces[5])
            id = pieces[1].strip()
            name = pieces[12]
            strand = pieces[3]

            # parse block information if applicable
            blocks = []
            cds_start = int(pieces[6])
            cds_end = int(pieces[7])
            if cds_start != cds_end:
                block_starts = [int(piece)
                                for piece in pieces[9].strip(',').split(',')]
                block_ends = [int(piece)
                              for piece in pieces[10].strip(',').split(',')]
                for i in range(len(block_starts)):
                    block = {'start': max(block_starts[i], cds_start),
                             'end': min(block_ends[i], cds_end)}
                    if block['end'] > block['start']:
                        blocks.append(block)

            # add this gene to the list
            genes[chromosome].append({'chrom' : chromosome,
                                      'start' : start,
                                      'end'   : end,
                                      'name'  : name,
                                      'id'    : id,
                                      'strand': strand,
                                      'blocks': blocks})
        for chrom in genes:
            genes[chrom].sort(key=lambda x: x['start'])

    return genes


# test client
def main():
    genes = load_genes('test/genes.bed')['chr3']
    print(len(genes))
    print(genes[0])


if __name__ == "__main__":
    main()
