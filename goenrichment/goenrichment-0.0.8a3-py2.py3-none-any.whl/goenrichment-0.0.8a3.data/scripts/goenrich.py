#!python
import pickle
import argparse

from goenrichment.enrichment import calculate
from goenrichment.go import load_goenrichdb

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Calculate GO enrichment from a list of genes. Default database organism: human')

    parser.add_argument('-i', help='Input list of gene names', required=True)
    parser.add_argument('-o', help='TSV file with all results', required=True)
    parser.add_argument('--goenrichDB', help='Gene2GO pickle file created with '
                                             '"goenrichDB.py". If not provided '
                                             'the database is loaded from:'
                                             '', required=False)
    parser.add_argument('--min_category_depth', help='Min GO term graph depth '
                                                     'to include in the report. '
                                                     'Default: 4', required=False)
    parser.add_argument('--min_category_size', help='Min number of gene in a GO '
                                                    'term to include in the report. '
                                                    'Default: 3', required=False)
    parser.add_argument('--max_category_size', help='Max number of gene in a GO '
                                                    ''
                                                    'term to include in the report. Default: 500', required=False)
    parser.add_argument('--alpha', help='Alpha value for p-value correction. '
                                        'Default: 0.05', required=False)

    args = parser.parse_args()

    output = args.o
    input = args.i

    goenrichDB = "ftp://ftp.ncbi.nlm.nih.gov/pub/goenrichment/goenrichDB_human.pickle"
    if args.goenrichDB:
        goenrichDB = args.goenrichDB

    godb = load_goenrichdb(goenrichDB)

    alpha = 0.05
    if args.alpha:
        alpha = float(args.alpha)

    min_category_depth = 4
    if args.min_category_depth:
        min_category_depth = int(args.min_category_depth)

    min_category_size = 3
    if args.min_category_size:
        min_category_size = int(args.min_category_size)

    max_category_size = 500
    if args.max_category_size:
        max_category_size = int(args.max_category_size)

    query = set()
    with open(input) as fin:
        for l in fin:
            query.add(l.strip())

    print('There are %d alternative ids in database' % (len(godb['alt_id'])))
    print('There are %d GO terms' % (len(godb['graph'].node)))
    print('There are %d genes in database' % (godb['M']))
    print('Query size: %d genes' % len(query))

    df = calculate(godb, query, alpha, min_category_depth, min_category_size, max_category_size)
    print('GO terms with q less than %.2f: %d' % (alpha, len(df[df['q'] <= alpha])))
    df.to_csv(output, sep='\t', index=None)
