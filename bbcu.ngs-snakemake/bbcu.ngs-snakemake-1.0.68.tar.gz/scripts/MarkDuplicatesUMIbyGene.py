#!/usr/bin/env python

import sys
import HTSeq
import pysam
from UtilDeDup import *
import collections
import Queue
import os
import argparse
import logging
import re

__author__ = 'pmbarlev'

'''
Overview: Mark duplicates in a bam file with appropriate UMI tags. Two reads are duplicates if both have the same UMI-barcode (in a bam tag of the form RX:Z:[barcode]) and both map to the same gene (as recorded in a tag of the form XF:Z:[gene]). This is tailored to Mars-seq libraries, in which the UMI-barcodes are added and some PCR cycles are performed BEFORE fragmentation, so reads from PCR-duplicate transcripts may not map identically. For other library prepation protocols, in which PCR-duplicate reads do map identically, it is recommended to use Picard MarkDuplicates (with the 'BARCODE_TAG' option).
 Within each UMI duplication equivalence class, one read is chosen as representative, and the rest are marked as
  duplicates.

Input: A position sorted bam file containing barcode related read tags:
    a. barcode tag  - RX:Z:<barcode>
    b. barcode qual tag - QX:Z:<barcode quals>
    c. feature tag - XF:Z:<feature name>
    Typically, such a bam is created using the workflow described in readme.md.

Output: A bam file with the following:
    a. The duplicate bit in the sam flag set for UMI duplicates
    b. A tag containing the read name of the representative read (self, if it is the rep) rp:Z:<rep read name>
    c. For each representative, a tag containing the number of read pairs in the equivalence class: nd:i:<number of
     dups>

Arguments:
    --bamIn: path to the input bam file.
    --bamOut: path of the output bam file to be created.
    --gtf: gtf file.
    --bcLength: expected UMI barcode length.
    --scoringStrategy: strategry used for choosing a representative read amongst all duplicates. Options: 'none',
     'baseQual', 'numMapped'. Default = 'baseQual', the sum of base qualities >= 15.
    --outputMetricsDir': Where histogram and metrics files will be written.
    --logFile: Name of a logfile to be written. Default = stderr


Remarks: This program loads all essential data from the bam into memory, so it is appropriate for "small" bams, as
 expected from single cell experiments.

Typical Usage:
python MarkDuplicatesUMI.py \
--inputBam myBam.bam' \
--outputBam myBam.deDup.bam \
--gtf my.gtf \
--bcLength 8 \
--outputMetricsDir metricsDir \
--outputPrefix myBam


Algorithm overview:
    This is a single pass algorithm. First the gtf is indexed to determine the end position of each gene. The bam is traversed, the alignments are buffered in memory with their feature recorded (as it appears in the XF tag). When the end-position of a gene is passed, all the buffered alignments associated with that feature are partitioned by UMI-barcode, a representative is chosen from each partition, and the duplicate bit flag is set in all the other alignments.

Generated metrics files:
    1.  `*.metrics.csv`. A summary of read metrics. E.g.,
        sample,totReads,unmapped,notProperlyMapped,duplicates,failMotif,passFilter
        mySample,1578160,7383,159914,1488847,110821,47246

    2. `*.dupHistogram.csv`. Duplication level histogram. E.g.,
        duplication-level, number-of-fragments
        1,11915
        2,4509
        3,2356
        4,1629

    References and credits:
    The treatment of UMI-barcode sequencing reads follows the recommendations in a blog by Tom Smith in:
    https://cgatoxford.wordpress.com/2015/08/14/unique-molecular-identifiers-the-problem-the-solution-and-the-proof/
    In particular, the adoption the "adjacency graph" clustering approach.
'''


class MarkUmiDuplicates(object):
    def __init__(self, bam_in, bam_out, bc_length, scoring_strategy='baseQual',
                 gtf=None,
                 com_line="", num_mismatches=0):
        """
        :type bam_in: str
        :type bam_out:str
        :type bc_length:int
        :type read_length:int
        :type scoring_strategy:str
        :type com_line:str
        """

        self.bc_length = bc_length
        self.scoring_strategy = scoring_strategy
        self.gtf = gtf
        self.gtf_index = dict() # A map gene_name -> end position
        self.num_mismatches = num_mismatches
        self.bam_in = bam_in
        self.bam_out = bam_out
        self.com_line = com_line

        ###
        self.gene_tag = "XF"
        self.no_feature_regex = "^__"

        # Setup the bam writer
        # Set up bamwriter and reader
        with pysam.AlignmentFile(self.bam_in, "rb") as bam_reader:
            if bam_reader.header['HD']['SO'] != "coordinate":
                raise ValueError("Bam is not sorted by coordinate")
            # Add command line to the bam header
            pg_header_line = {'CL': self.com_line, 'ID': 'MarkDuplicatesUMIbyGene', 'PN': 'MarkDuplicatesUMIbyGene'}
            header = bam_reader.header
            header.get('PG', []).append(pg_header_line)
            self.bam_writer = pysam.AlignmentFile(self.bam_out, "wb", header=header)

        # The number of records read from the bam
        self.num_recs = 0

        # The number of positions with reads starting at them
        self.num_occupied_pos = 0

        # the number of reads skipped because they are unmapped, not primary alignments, or failed motif filter
        self.num_rec_skipped = 0

        # Metric collection
        # Duplication level histogram. a map int -> number of reads with that duplication level
        self.dup_hist = collections.Counter()

        # single read metrics collection
        self.unmapped = 0
        self.dup = 0
        self.not_properly_mapped = 0
        self.pass_filter = 0

        self.ready = 'ready'  # ready to be written
        self.pending = 'pending'  # waiting to be deDupped

        # A named-tuple type and factory for self.gene_q entries
        self.Gene = collections.namedtuple('Rec', ['end', 'name'])

        # Bam traversal status data
        ## A buffer for the sam records waiting to be processed and written
        self.rec_buffer = collections.deque()

        ## A map from gene_name -> list[records]
        ## We will encode that a gene has been process using the key,value gene_name, ["processed"]
        self.rec_index = collections.defaultdict(list)
        """ :type : dict[str, list[pysam.AlignedSegment]]"""

        self.gene_q = Queue.PriorityQueue()
        """:type : Queue.PriorityQueue"""

    def __call__(self):
        self.index_gtf()
        self.traverse_bam_by_gene()

    ### deDup by gene ###

    def traverse_bam_by_gene(self):

        logging.info("Starting bam traversal. Marking duplicates by UMI + Gene.")

        bam_reader = pysam.AlignmentFile(self.bam_in, "rb")
        """ :type : pysam.AlignmentFile"""

        # Keep track of contig
        curr_contig=None

        curr_rec_index = 0

        for rec in bam_reader:
            curr_rec_index += 1
            """ :type rec: pysam.AlignedSegment"""
            if rec.rname != curr_contig:
                # Clear the buffer, reset the current pos and contig
                self.process_genes()
                while self.rec_buffer:
                    self.write_rec(self.rec_buffer.popleft())
                curr_contig = rec.rname

            self.add_rec_to_buffer(rec)

            # If we have advanced the position, process genes
            if not self.gene_q.empty() and rec.pos > self.gene_q.queue[0].end:
                self.process_genes(rec.pos)
                # Write "ready" records
                while self.rec_buffer and self.rec_buffer[0].status is self.ready:
                    self.write_rec(self.rec_buffer.popleft())

            # log progress
            if curr_rec_index > 0 and curr_rec_index % 1e6 == 0:
                logging.debug("Start data extracted from %d single reads so far" % curr_rec_index)


        # At the end of the bam, process remaining reads
        self.process_genes()
        while self.rec_buffer:
            self.write_rec(self.rec_buffer.popleft())

        self.bam_writer.close()
        # log stats
        logging.debug("%d genes with reads." % self.num_occupied_pos)
        logging.info("%d single reads processed." % (curr_rec_index))
        logging.info("%d reads are unmapped, not primary alignments, or supplementary alignments."
                     % self.num_rec_skipped)

    # Processes a record: add to the buffer, update gene_q
    def add_rec_to_buffer(self, rec):
        # Records missing a gene tag (XF:Z...)
        try:
            gene_name = rec.get_tag(self.gene_tag)
        except KeyError:
            self.rec_buffer.append(Rec(rec, self.ready))
        # Records with a "no proper gene" gene tag, or not properly mapped
        if re.match(self.no_feature_regex, gene_name) or \
                rec.is_secondary or \
                rec.is_unmapped or \
                rec.is_supplementary:
            self.rec_buffer.append(Rec(rec, self.ready))
            self.num_rec_skipped += 1

        # Records with a "proper" gene tag
        else:
            rec_status = Rec(rec, self.pending)
            self.rec_buffer.append(rec_status)
            self.add_gene(gene_name)  # this will throw an exception if the gene is not in the gtf
            self.rec_index[gene_name].append(rec_status)

    # Query the gtf for the end of a gene, and add to gene_q
    def add_gene(self, gene_name):
        if gene_name not in self.rec_index.keys():
            try:
                gene_end = self.gtf_index[gene_name]
            except KeyError:
                raise ValueError("Gene name %s not found in gtf." %gene_name)
            self.gene_q.put(self.Gene(gene_end, gene_name))
            self.num_occupied_pos += 1

    # Process all genes in gene_q, and all records in the buffer up to pos (unless pos is None)
    def process_genes(self, pos = None):
        while not self.gene_q.empty() and (self.gene_q.queue[0].end < pos or not pos ):
            gene = self.gene_q.get().name
            rec_list = self.rec_index.pop(gene)
            self.mark_dup_by_bc([rec_status.rec for rec_status in rec_list])
            for rec in rec_list:
                rec.status = self.ready


    # write record to bam, and collect metrics.
    def write_rec(self, rec_status):
        if rec_status.status is not self.ready:
            raise ValueError("Error processing read: %s" % rec_status.rec)
        self.bam_writer.write(rec_status.rec)
        self.collect_metrics(rec_status.rec)

    def index_gtf(self):
        logging.info("Indexing gtf...")
        gtf_reader = HTSeq.GFF_Reader(self.gtf, end_included=True)
        num_featured_processed = 0
        num_genes = 0
        for feature in gtf_reader:
            if feature.type in {"gene", "exon"}:
                gene_name = feature.attr['gene_name']
                iv = feature.iv
                if gene_name in self.gtf_index:
                    self.gtf_index[gene_name] = max(self.gtf_index[gene_name], iv.end)
                else:
                    self.gtf_index[gene_name] = iv.end
                    num_genes += 1

            # progress logging
            num_featured_processed += 1
            if num_featured_processed >0 and num_featured_processed % 1e5  == 0:
                logging.debug("%d features processed, %d genes indexed" %(num_featured_processed, num_genes))
        logging.info("Done indexing gtf. %d genes indexed" %num_genes)

    ######

    # Mark duplicates in a list of reads based on UMI data only.
    # It is assumed that the reads have the same position data.
    # No return value - it modifies the records given.
    def mark_dup_by_bc(self, read_list):
        '''
        :type read_list: list[pysam.calignedsegment.AlignedSegment]
        '''
        # index the reads by bc
        bc_index = collections.defaultdict(list)
        for rec in read_list:
            bc_index[rec.get_tag('RX')].append(rec)
        # Construct a list of bc's in the list of reads.
        bc_list = map(lambda bc: UMIBarcode(bc, len(bc_index[bc])), bc_index.keys())
        
        # Bypass clustering if no mismatches are permitted
        if (self.num_mismatches == 0):
            clusters = map(lambda bc: [bc], bc_list)

        else:
            clusterer = BCClusters(bc_list, self.num_mismatches)
            clusters = clusterer.get_clusters()
            """
            :type clusters: list[list[UMIBarcode]]
            """
        for cluster in clusters:
            ranked_recs = self.rank_recs(cluster, bc_index)
            representative = ranked_recs[0]
            rep_name = representative.query_name
            num_copies = len(ranked_recs)
            for rec in ranked_recs:
                try:
                    rec.get_tag('rp')
                except KeyError:
                    rec.set_tag('rp', rep_name, value_type="Z")
                try:  # make sure the 'nd' numCopies tag has not been set for this read
                    rec.get_tag('nd')
                except KeyError:
                    rec.set_tag('nd', num_copies, value_type="i")
                if (rep_name != rec.query_name) & (not rec.is_duplicate):
                    # set duplicate bit
                    rec.flag += 1024
            #metric collection
            self.dup_hist[num_copies] += 1

    # choose representative with the following priorities:
    # 1) Complete barcode with no N's
    # 2) High barcode score
    # 3) High read score
    # Returns a priotized list of pysam records (best first)
    def rank_recs(self, bc_cluster, bc_index):
        """
        :type cluster: list[UMIBarcode]
        :type bc_index: dict[str, list[pysam.calignedsegment.AlignedSegment]]
        :rtype:
        """
        # Build a list[(bc, fragdata)] for all reads in the duplication class
        l = []
        for bc in bc_cluster:
            l0 = map(lambda rec: ReadWithScores(rec, bc, self.bc_length, self.scoring_strategy), bc_index[bc.bc])
            l.extend(l0)
        # sort l appropriately

        return map(lambda read_with_score: read_with_score.rec, l)

    ###### Metrics and Summary ######

    def collect_metrics(self, rec):
        """
        :type rec: pysam.calignedsegment.AlignedSegment
        """
        self.num_recs += 1

        pass_filter = True
        if rec.is_unmapped:
            self.unmapped += 1
            pass_filter = False

        if not is_properly_mapped(rec):
            self.not_properly_mapped += 1
            pass_filter = False

        if rec.is_duplicate:
            self.dup += 1
            pass_filter = False

        if pass_filter:
            self.pass_filter += 1

    def write_summary(self, file_name, sample_name):
        writer = open(file_name, 'w')
        # Write header
        writer.write("sample,numPos,numAlignments,unmapped,notProperlyMapped,duplicates,passFilter\n")
        # write stats
        writer.write(",".join(
            [sample_name, str(self.num_occupied_pos), str(self.num_recs), str(self.unmapped), str(self.not_properly_mapped),
             str(self.dup), str(self.pass_filter)]) + "\n")

    def write_metrics(self, output_dir, output_prefix):
        #write_hist(self.bc_class_count, os.path.join(output_dir, output_prefix + ".bcClassCount.csv"))
        write_hist(self.dup_hist, os.path.join(output_dir, output_prefix + ".dupHistogram.csv"))
        self.write_summary(os.path.join(output_dir, output_prefix + ".metrics.csv"), output_prefix)
        logging.info("Metrics written in " + output_dir)





###### Barcode clustering class #######
###### Currently not in use ######

# Breadth first search in a graph(a util method)
def bfs(adj_lists, node):
    """
    :type adj_lists: dict[umiBarcode, list[UMIBarcodes]]
    :type node: UMIBarcode
    :rtype: list[UMIBarcode]
    """
    res = [node]
    queue = [node]
    seen = {node}
    while queue:
        curr_node = queue.pop(0)
        new_nodes = set(adj_lists[curr_node]).difference(seen)  # get only new neighbors
        res.extend(new_nodes)
        queue.extend(new_nodes)
        seen.update(new_nodes)
    return res


class BCClusters(object):
    def __init__(self, barcodes=[], edge_dist=1, score_ratio=0.5):
        """
        :type barcodes: list[umiBarcode]
        """
        self.adj_lists = {}
        self.edge_dist = edge_dist
        self.score_ratio = score_ratio
        for bc in barcodes:
            self.add(bc)

    def add(self, bc):
        """
        :type bc: UMIBarcode
        """
        if bc in self.adj_lists:
            raise ValueError("Barcode %s is already in the graph." %bc)

        neighbors = []
        for bc_other in self.adj_lists.keys():
            if self.has_edge(bc, bc_other):
                neighbors.append(bc_other)
            if self.has_edge(bc_other, bc):
                self.adj_lists[bc_other].append(bc)
        self.adj_lists[bc] = neighbors

    # The implemention of this method defines how the graph constructed.
    # Currently implements directed adjacency: there is an edge from barcode x to barcode y if:
    # 1. dist(x, y) <= self.edge_dist
    # 2. bc.score >= self.score_ratio * bcOther.score
    # Currently, bc.score is the number of fragments at the mapping position which have the given barcode.
    def has_edge(self, bc, bc_other):
        """
        :type bc: UMIBarcode
        :type bc_other: UMIBarcode
        :rtype: bool
        """
        return bc.dist(bc_other) <= self.edge_dist and bc.score >= self.score_ratio * bc_other.score

    # Cluster barcodes - greedy algorithm: start bfs with the unclaimed node of highest score, and claim all nodes reachable along the directed graph. Repeat until there are no unclaimed nodes.
    # Return each cluster  ordered by score (highest first)
    def get_clusters(self):
        """
        :rtype: list[list[UMIBarcode]]
        """
        clusters = []
        """ :type : dict[umiBarcode, list[umiBarcode]"""
        bc_sorted = sorted(self.adj_lists.keys(), key=lambda bc0: bc0.score, reverse=True)
        while bc_sorted:
            bc = bc_sorted[0]
            # Keep only bc's which haven't been claimed - i.e., are in bc_sorted
            in_cluster = [bc0 for bc0 in bfs(self.adj_lists, bc) if bc0 in bc_sorted]
            in_cluster = sorted(in_cluster, key=lambda bc0: bc0.score, reverse=True)
            clusters.append(in_cluster)
            # remove in_cluster from bc_sorted
            bc_sorted = [bc0 for bc0 in bc_sorted if bc0 not in in_cluster ]
        return clusters

###### UMIBarcode ######
'''
Barcode object for a read.
If a read has no barcode, then the corressponding field has "no_bc".
'''
class UMIBarcode(object):
    NO_BC = "no_bc"
    def __init__(self, bc, score):
        self.bc = bc
        self.score = score  # Typically, how many fragments have this umiBarcode

    # This distance is a measure of the number of "events" needed for self to mutate into other. We allow 1) tag
    #  dropout 2) char dropout 3) char changes but no additions
    # The number infin(ity) should be the largest possible distance and means that self cannot mutate into other
    def dist(self, other, infin=100):
        """
        :type other: UMIBarcode
        :rtype: int
        """
        return self.tag_dist(self.bc, other.bc, infin)

    # TODO: treat N's in the barcode
    def tag_dist(self, tag_self, tag_other, infin=100):
        if tag_other is None:
            return 0
        elif tag_self is None:
            return infin

        # If both tags exist
        i = len(tag_self) - len(tag_other)
        if i < 0:
            return infin

        return hamming_dist(tag_self[i:], tag_other)


    # check if the barcode contains N's and has the expected length
    def is_proper(self, expected_length=None):
        return ('n' not in self.bc.lower()) & (expected_length is None or len(self.bc) == expected_length)

    def __repr__(self):
        return self.bc if self.bc else "No BC"

    def __hash__(self):
        return self.bc.__hash__()

    def __eq__(self, other):
        return self.bc == other.bc

###### ReadWithScores ######
'''
A data type containing a read, a read score, and a barcode score for a read with a read socre
'''
class ReadWithScores(object):
    def __init__(self, rec, umi_data, expected_bc_length, scoring_strategy):
        """
        :type rec: pysam.calignedsegment.AlignedSegment
        :type umi_data: UMIBarcode
        """
        self.rec = rec
        self.bc_score = umi_data.score
        self.read_score = score(rec, scoring_strategy)
        self.has_proper_bc = umi_data.is_proper(expected_bc_length)

# a datatype for bam records and their status (ready or pending)
class Rec(object):
    __slots__ = ('rec', 'status')

    def __init__(self, rec, status):
        self.rec = rec
        self.status = status

###### Main method and arg parsing ######

def parse_args():
    help_txt = "Mark UMI duplicates in a bam file"
    parser = argparse.ArgumentParser(description=help_txt)
    parser.add_argument('--inputBam', help='Input .bam file', required=True)
    parser.add_argument('--outputBam', help='Output .bam file', required=True)
    parser.add_argument('--bcLength', help='UMI barcode length', type=int, required=True)
    parser.add_argument('--scoringStrategy',
                        help='Scoring strategy for selecting representative reads amongst duplicates. Options: none,'
                             ' baseQual,numMapped',
                        default='baseQual', required=False)
    parser.add_argument('--numMismatches', help='The number of mismatches allowed in Barcodes', type=int, default=0,
                        required=False)
    parser.add_argument('--gtf', help='A gtf file. Necessary when posResolution == gene',
                        default=None, required=True)
    parser.add_argument('--logFile', help='Log File', required=False)
    parser.add_argument('--outputMetricsDir',
                        help='Where histogram and metrics files will be written. If no dir is given, metrics will not'
                             ' be written',
                        required=False)
    parser.add_argument('--outputPrefix', help='prefix for output file names', default="sample", required=False)
    return parser.parse_args()


if __name__ == "__main__":
    # The command line executed, for adding to the bam header
    CL = " ".join(sys.argv)
    args = parse_args()
    logging_args = {
        "level": logging.DEBUG,
        "filemode": 'w',
        "format": '%(asctime)s %(message)s',
        "datefmt": '%m/%d/%Y %H:%M:%S'
    }
    # set up log file
    if args.logFile is not None:
        logging_args["filename"] = args.logFile
    logging.basicConfig(**logging_args)

    logging.info('Program started')
    dup_marker = MarkUmiDuplicates(
        args.inputBam, args.outputBam, args.bcLength,
        scoring_strategy=args.scoringStrategy, num_mismatches=args.numMismatches, com_line=CL,
        gtf=args.gtf
    )
    dup_marker()
    # Write histogram metrics
    if args.outputMetricsDir:
        dup_marker.write_metrics(args.outputMetricsDir, args.outputPrefix)
    logging.info('Program finished')
