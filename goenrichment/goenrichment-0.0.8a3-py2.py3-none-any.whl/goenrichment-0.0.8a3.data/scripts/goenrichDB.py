#!python
import sys
import pickle
import argparse

from goenrichment.go import create_go_graph, update_go_graph
from goenrichment.parsers import load_ncbi_gene, load_tsv_gene, load_uniprot_goa_gene

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Creates pickle data structure used by "goenrich.py"')
    parser.add_argument('--gene_info', help='NCBI gene_info file', required=False)
    parser.add_argument('--gene2go', help='NCBI gene2go file', required=False)
    parser.add_argument('--tsv', help='TSV file with at least two columns: Gene_name<tab>GO terms', required=False)
    parser.add_argument('--goenrichDB', help='Previous created goenrich pickle file. '
                                   'The new genes will be added to this database', required=False)
    parser.add_argument('--goa_uniprot', help='Uniprot GOA file GAF format', required=False)
    parser.add_argument('--gobo', help='UGO Obo file from Gene Ontology', required=False)
    parser.add_argument('--taxid', help='Process genes for tax id if it is possible', required=False)
    parser.add_argument('-o', help='Pickle output file name', required=True)

    args = parser.parse_args()
    pickle_file = args.o
    tax_id = None
    if args.taxid:
        tax_id = args.taxid

    geneGoDB = None
    if args.gobo:
        print('Creating geneGODB data structure')
        geneGoDB = create_go_graph(args.gobo)

    if args.goenrichDB:
        print('Loading pickle file')
        geneGoDB = pickle.load(open(args.goenrichDB, "rb"))

    if not geneGoDB:
        print('Should use one of the options --gobo or --goenrichDB')
        sys.exit(-1)

    print('There are %d alternative ids' % (len(geneGoDB['alt_id'])))
    print('There are %d GO terms' % (len(geneGoDB['graph'].node)))

    if args.gene_info:
        gene_info_file = args.gene_info
    else:
        gene_info_file = None

    if args.gene2go:
        gene2go_file = args.gene2go
    else:
        gene2go_file = None

    if gene_info_file and gene2go_file:
        print('Loaging NCBI gene data')
        values = load_ncbi_gene(geneGoDB, gene_info_file, gene2go_file, tax_id)
        geneGoDB = update_go_graph(geneGoDB, values, 'genes')
        print('There are %d genes' % (geneGoDB['M']))

    if args.tsv:
        print('Loaging TSV gene data')
        values = load_tsv_gene(geneGoDB, args.tsv)
        geneGoDB = update_go_graph(geneGoDB, values, 'genes')
        print('There are %d genes' % (geneGoDB['M']))

    if args.goa_uniprot:
        print('Loaging Uniprot gene data')
        values = load_uniprot_goa_gene(geneGoDB, args.goa_uniprot, tax_id)
        geneGoDB = update_go_graph(geneGoDB, values, 'genes')
        print('There are %d genes' % (geneGoDB['M']))

    print('There are %d alternative ids' % (len(geneGoDB['alt_id'])))
    print('There are %d GO terms' % (len(geneGoDB['graph'].node)))
    print('There are %d genes' % (geneGoDB['M']))
    pickle.dump(geneGoDB, open(pickle_file, "wb"))
