from collections import defaultdict
import gzip


def load_ncbi_gene(godb, gene_info_file, gene2go_file, tax_id=None):
    """
    Load NCBI gene data to the GODB structure
    :param godb: GODB data structure
    :param gene_info_file: NCBI gene info file
               (ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz)
    :param gene2go_file: NCBI goenrichment file
               (ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/goenrichment.gz)
    :return: GODB data structure
    """
    gname = {}
    with gzip.open(gene_info_file, 'rb') as f:
        for l in f:
            line = l.decode().strip()
            if not line.startswith('#'):
                f = line.split('\t')
                if not tax_id or f[0] == tax_id:
                    gname[f[1]] = f[2]
    print('Processing gene2go')
    data = defaultdict(set)
    with gzip.open(gene2go_file, 'rb') as f:
        for l in f:
            line = l.decode().strip()
            if not line.startswith('!') and not line.startswith('#'):
                r = line.split('\t')
                if (not tax_id or r[0] == tax_id) and r[1] in gname:
                    alt_id = godb['alt_id'][godb['alt_id']['alt_id'] == r[2]]
                    if not alt_id.empty:
                        r[2] = alt_id.iloc[0]['term']
                    data.setdefault(r[2], set()).add(gname[r[1]])
    return data


def load_uniprot_goa_gene(godb, uniprot_goa_file, tax_id=None):
    """
    Load Uniprot GOA genes into the GODB data structure
    :param godb: GODB data structure
    :param uniprot_goa_file: Uniprot GOA file
           (ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/UNIPROT/goa_uniprot_all.gaf.gz)
    :param tax_id: Tax id to extract
    :return: GODB data structure
    """
    data = defaultdict(set)
    with gzip.open(uniprot_goa_file, 'rb') as f:
        for l in f:
            line = l.decode().strip()
            if not line.startswith('!') and not line.startswith('#'):
                r = line.split('\t')
                if not tax_id or r[12].split(':')[1] == tax_id:
                    alt_id = godb['alt_id'][godb['alt_id']['alt_id'] == r[4]]
                    if not alt_id.empty:
                        r[4] = alt_id.iloc[0]['term']
                    data.setdefault(r[4], set()).add(r[2])
    return data


def load_tsv_gene(godb, tsv_go_file):
    """
    Load TSV file created with parameters:
    Gene name       GO term accession
    :param godb: GODB data structure
    :param tsv_go_file: TSV input file
    :return: GODB data structure
    """
    data = defaultdict(set)
    with gzip.open(tsv_go_file, 'rb') as f:
        for l in f:
            line = l.decode().strip()
            if not line.startswith('#'):
                f = line.split('\t')
                if len(f) > 2 and 'GO:' in f[1]:
                    alt_id = godb['alt_id'][godb['alt_id']['alt_id'] == f[1]]
                    if not alt_id.empty:
                        f[1] = alt_id.iloc[0]['term']
                    data.setdefault(f[1], set()).add(f[0])
    return data
