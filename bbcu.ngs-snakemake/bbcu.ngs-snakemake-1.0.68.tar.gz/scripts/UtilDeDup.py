#!/usr/bin/env python

import pysam

'''
A collection of functions for dealing with sam records
'''


# Get the n'th bit of a sam flag
def get_sam_flag(rec, n):
    return rec.flag % (2 ** (n + 1)) / (2 ** n)


# Get the strand
def get_strand(rec):
    return (-1) ** get_sam_flag(rec, 4)


def get_unclipped_start(rec):
    start = rec.pos
    # rec.cigar has the form [(4, 3), (0, 101), (4, 11)] where each tuple corressponds to a cigar operator.
    #  The first element is a code for the type, and the second is a the size of the operator.
    cig_op_type = rec.cigar[0][0]
    cig_op_size = rec.cigar[0][1]
    if cig_op_type in [4, 5]:  # 4 is th code for soft clip, 5 for hard clip
        return start - cig_op_size
    else:
        return start


def get_unclipped_end(rec):
    return get_unclipped_start(rec) + get_unclip_align_offset(rec.cigar)


# The offset between the pos of the first unclipped base on the ref and the last
# (a seq of length 1 would have offset = 0)
# e.g., the cigar string 3S50M10I20M4H has offset 3+50+20+4-1=76
def get_unclip_align_offset(cigartuples):
    """
    :type cigartuples: list[(int,int)]
    :rtype: int
    """
    # A map operatorCode -> shift on reference
    d = {0: 1, 1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1}
    return sum([d[op] * l for (op, l) in cigartuples]) - 1


def is_properly_mapped(rec):
    res = not rec.is_unmapped
    res &= (rec.mapping_quality > 0)
    res &= not rec.is_supplementary
    res &= not rec.is_secondary
    return res


###########################
# Scoring alignment records
##########################
def score(rec, scoring_strategy):
    if scoring_strategy == 'none':
        return 0
    elif scoring_strategy == 'baseQual':
        return qual_sum(rec)
    elif scoring_strategy == 'numMapped':
        return num_mapped_bases(rec)


# Return the sum of qualities of all bases with qual >= 15
def qual_sum(rec):
    score = 0
    for q in rec.query_qualities:
        if q >= 15:
            score += q
    return score


# Return the number of bases mapped to the reference (size of the M operators in the cigar)
def num_mapped_bases(rec): return rec.alen


###########################
# Read pair seq agreement
##########################

# Test whether the seqs of two reads agree on their overlap (true if there is no overlap)
def get_overlap(rec1, rec2):
    """
    :type rec1: pysam.AlignedSegment
    :type rec2: pysam.AlignedSegment
    :rtype: (str, str)
    """
    # test the rec's are a pair
    if rec1.query_name != rec2.query_name:
        raise ValueError("Reads are not a pair: " + rec1.query_name + ", " +
                         rec2.query_name)
    if rec1.is_unmapped or rec2.is_unmapped:
        raise ValueError("Read not aligned.")
    (fst, snd) = sorted((rec1, rec2), key=lambda rec: rec.reference_start)
    # Case: no overlap between reads.
    if fst.reference_end <= snd.reference_start:
        return "", ""

    # find "anchors" to align both rec's to each other: (anchor1, anchor2) are a pair of indices
    # in rec1 and rec2 which align to the same position
    snd_pos = [pos for (index, pos) in snd.get_aligned_pairs()]
    anchor1 = anchor2 = None
    for index, pos in fst.get_aligned_pairs(matches_only=True):
        if pos in snd_pos:
            anchor1 = index
            anchor2 = snd_pos.index(pos)
            break
    # If fst and snd have no bases aligned to the same position (this is a strange phenomenon when
    # fst.reference_end <= snd.reference_start, but possible if there is a translocation.
    if (anchor1 == anchor2 == None):
        return "", ""
    else:
        return rec1.seq[anchor1 - anchor2:], rec2.seq[:len(rec1.seq) - anchor1 + anchor2]


# Test whether the seqs of two reads agree on their overlap (true if there is no overlap)
def is_overlap_concordant(rec1, rec2):
    """
    :type rec1: pysam.AlignedSegment
    :type rec2: pysam.AlignedSegment
    :rtype: bool
    """
    seq1, seq2 = get_overlap(rec1, rec2)
    return seq1 == seq2


# The number of mismatches in the overlap of a read pair
def num_overlap_mismatches(rec1, rec2):
    """
    :type rec1: pysam.AlignedSegment
    :type rec2: pysam.AlignedSegment
    :rtype: int
    """
    seq1, seq2 = get_overlap(rec1, rec2)
    return hamming_dist(seq1, seq2)


###########################
# String Utilities
##########################

def hamming_dist(s1, s2):
    """Return the Hamming distance between equal-length sequences. Shamelessly copied from Wikipedia..."""
    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length")
    return sum(bool(ord(ch1) - ord(ch2)) for ch1, ch2 in zip(s1, s2))

######
# Write a histogram to a text file
######
def write_hist(hist, hist_file_name):
    """
    :type hist: dict{str, int}
    :type hist_file_name: str
    """
    with open(hist_file_name, 'w') as histWriter:
        for key in sorted(hist.keys()):
            histWriter.write(str(key) + ",%d\n" % hist[key])
