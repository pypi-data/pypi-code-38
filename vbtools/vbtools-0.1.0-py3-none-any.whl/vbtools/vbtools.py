import os
import sys
import argparse
import subprocess as sp
import pandas as pd
import re
from funpipe.utils import run


class snp_share:
    """ SNP counts in categories

    To do: add missing categories in this module
    Description
    -----------
        Of all discovered SNPs for a paticular pipeline, which shared SNP category
        does it belongs to. It inputs a

    Example
    -------
    >>> pipe_dos =  [0,  1, 0, 0, 1, 1, 1]
    >>> np_called = [9, 10, 8, 8, 7, 7, 6]   # number of pipelines called
    >>> pipe = snp_share(pipe_dos, np_called)

    >>> pipe.hit_cates
    >>> pipe.miss_cates

    """
    def __init__(self, var_series):
        var_series = var_series[var_series!=0]
        self.counts = var_series.value_counts()
        self.counts.index = self.counts.index.astype('int32')

        self.total = len(var_series)
        self.private = len(var_series[var_series==1])
        self.share = len(var_series[var_series>10])
        if self.total != 0:
            self.pct_private = round(self.private / self.total * 100, 2)
            self.pct_share = round(self.share / self.total * 100, 2)
        else:
            self.pct_private = np.nan
            self.pct_share = np.nan

    def plt(self, log=False):
        if log:
            lg_count_table = self.counts.apply(math.log)
            lg_count_table.sort_index().plot.bar()
        else:
            self.counts.sort_index().plot.bar()


def _get_sample_names(vcf):
    """ get VCF sample names """
    samples = (sp.check_output("bcftools query -l "+vcf, shell=True).decode()
               .strip().split('\n'))
    return samples


def _sample_check(vcf1, vcf2):
    """ check if input sample names are the same
        sample names are required to be sorted lexilogically.
    """
    if not _get_sample_names(vcf1) == _get_sample_names(vcf2):
        raise ValueError((
            "Input sample names are not consistent with benchmark names."
        ))


def _contig_name(contig_header):
    """ parse contig name from contig header line

    Example
    -------

    >>> _contig_name('##contig=<ID=1>')
    'test'

    >>> _contig_name('##contig=<ID=test,URL=test>)
    'test'

    """
    m = re.search(r'<ID=([^,]+?)[,>]', contig_header)
    if m:
        return m.group(1)
    else:
        raise ValueError("Contig names not in the header.")


def _contig_names(vcf):
    """ parse contig names from header """
    contig_headers = sp.check_output(
        'bcftools view -h '+vcf+"| grep \'##contig\' ", shell=True,
        ).decode().strip().split("\n")

    return [_contig_name(i) for i in contig_headers]


def _contig_check(vcf, bench):
    """ check if input VCF has same contig names with benchmark VCF """
    if not _contig_names(vcf) == _contig_names(bench):
        raise ValueError((
            "Contig names or order are not consistent between input and "
            "benchmark VCF."))


def format_check(vcf, bench):
    """ """
    print(("\n+ Check contig and sample name consistency between input and"
           " benchmark VCFs"))
    _contig_check(vcf, bench)
    _sample_check(vcf, bench)


def preprocess_vcf(vcf, prefix):
    """ preprocess input VCF

    Description
    -----------
        Remove sites with asterisk marks, missing ref alleles, monomorphic
        sites, low quality sites (non-PASS in filter columns).
        If haploid, will remove sites with heterozygous calls.

    """
    print(" + Preprocess input VCF.\n")
    out = prefix+'.snps.no_mono.no_star.mini.vcf.gz'
    cmd = ' | '.join([
        # remove unused alleles
        'bcftools view --trim-alt-alleles -f .,PASS ' + vcf,
        # remove monomorphic, non-PASS, heterozygous and non-SNP sites
        'bcftools filter -e {} '.format('\' N_ALT==0 || TYPE!="SNP" || GT="het"\' '),
        # remove sites with asterisk marks
        'grep -v \'*\'',
        # diploid to haploid
        'sed \"s/\([0-9\.]\)\/[^\t]\+/\\1/g\"',
        # minimize VCF
        'bcftools annotate -x INFO,QUAL',
        # compress
        'bgzip > ' + out
    ])
     # index
    cmd += ' && tabix '+out
    run(cmd)
    return out


def get_var_ids(vcf, prefix):
    """ Get variant IDs from a VCF """
    site_id = prefix+'.site_id.txt'
    var_id = prefix+'.var_id.txt'
    run('bcftools query -f \'%CHROM:%POS:%REF:%ALT\n\' '+vcf+' > '+ site_id)

    with open(site_id) as fh, open(var_id, 'w') as ofh:
        ofh.write("varid\t"+prefix+'\n')
        for line in fh:
            chr, pos, ref, alt = line.strip().split(':')
            alts = alt.split(',')
            for i in alts:
                if i != '*':
                    ofh.write('-'.join([chr, pos, ref, i])+'\t1\n')
    return var_id


def get_variant_table(varid1, varid2):
    """ merge variant IDs from each callset into a single table """
    varf = [varid1, varid2]
    allvar = pd.read_csv(varf[0], sep='\t',header=0)
    allvar = allvar.merge(pd.read_csv(varf[1], sep='\t', header=0), how='outer')
    allvar = allvar.fillna(0)
    allvar = allvar.set_index('varid')
    allvar['n_called'] = allvar.sum(axis=1)
    return allvar
