"""
Simple wrappers around swalign package to help tie assemblies to biograph.Reference and convert
the results into a vcf
"""
from __future__ import print_function

from io import BytesIO

import swalign

def aligner(reference, assembly, s_anchor, e_anchor, match=2, mismatch=-1, gap_penalty=-2, gap_extension_decay=0.5):
    """
    Given two anchor reference ranges map a query sequence align  using swalign
    returns the alignment
    """
    positions = [s_anchor.start, s_anchor.end, e_anchor.start, e_anchor.end]
    start = min(positions)
    end = max(positions)
    # We're assuming non tloc
    chrom = s_anchor.chromosome
    scoring = swalign.NucleotideScoringMatrix(match, mismatch)
    sw = swalign.LocalAlignment(scoring, gap_penalty=gap_penalty, gap_extension_decay=gap_extension_decay)
    aln = sw.align(str(reference.make_range(chrom, start, end).sequence), str(assembly))
    return aln

def aln_to_vcf(anchor, aln, header=True):
    """
    Turns an swalign into a vcf written to a StringIO
    this can be parsed by pyvcf directly or written to a file
    It currently has no INFO and a fake FORMAT of GT=0/1
    if header is true, turn write a vcf header
    """
    ret = BytesIO()
    if header:
        ret.write(('##INFO=<ID=NS,Number=1,Type=Integer,Description="Number of smaples">\n'
                   '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n'
                   '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE\n'))
    tovcf = lambda chrom, pos, ref, alt: ret.write("{chrom}\t{pos}\t.\t{ref}\t{alt}\t.\tPASS\tNS=1\tGT\t0/1\n".format(
        chrom=chrom, pos=pos, ref=ref, alt=alt))

    # Position in the ref/query sequence
    # this will be off if the assembly maps to a sub-sequence of the anchor region
    base_position = anchor.start + 1
    rpos = 0
    qpos = 0
    chrom = anchor.chromosome
    query = aln.query
    reference = aln.ref
    for size, code in aln.cigar:
        if code == "M":
            for _ in range(size):
                if query[qpos] != reference[rpos]:
                    # SNP. Can't handle MNPs yet
                    tovcf(chrom, base_position, reference[rpos], query[qpos])
                rpos += 1
                qpos += 1
                base_position += 1
        elif code == 'I':  # ins
            tovcf(chrom, base_position - 1, reference[rpos - 1], reference[rpos - 1] + query[qpos:qpos + size])
            qpos += size
        elif code == 'D':  # del
            tovcf(chrom, base_position - 1, reference[rpos - 1:rpos + size], reference[rpos - 1])
            rpos += size
            base_position += size
    ret.seek(0)
    return ret
