"""
Handle generation of GRAAL-compatible contact maps from fastq files.
cmdoret, 20190322
"""
import os, time, csv, sys, re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import shutil as st
import itertools
import logging
from os.path import join
import subprocess as sp
from Bio import SeqIO
import pandas as pd
import numpy as np
import pysam as ps
import hicstuff.digest as hcd
import hicstuff.iteralign as hci
import hicstuff.filter as hcf
import hicstuff.io as hio
import hicstuff.distance_law as hcdl
import matplotlib
from hicstuff.version import __version__
import hicstuff.log as hcl
from hicstuff.log import logger


def align_reads(
    reads,
    genome,
    out_sam,
    tmp_dir=None,
    threads=1,
    aligner="bowtie2",
    iterative=False,
    min_qual=30,
):
    """
    Select and call correct alignment method and generate logs accordingly.
    Alignments are filtered so that there at most one alignment per read.

    Parameters
    ----------
    reads : str
        Path to the fastq file with Hi-C reads.
    genome : str
        Path to the genome bowtie2 index prefix if using bowtie2 or to the 
        fasta if using minimap2.
    out_sam : str
        Path to the output SAM file containing mapped Hi-C reads.
    tmp_dir : str
        Path where temporary files are stored.
    threads : int
        Number of threads to run alignments in parallel.
    aligner : bool
        Use minimap2 instead of bowtie2.
    iterative : bool
        Wether to use the iterative mapping procedure (truncating reads and
        extending iteratively)
    min_qual : int
        Minimum mapping quality required to keep an alignment during iterative
        mapping.
    """
    if tmp_dir is None:
        tmp_dir = os.getcwd()
    index = None
    tmp_sam = out_sam + ".tmp"

    if iterative:
        iter_tmp_dir = hio.generate_temp_dir(tmp_dir)
        hci.iterative_align(
            reads,
            tmp_dir=iter_tmp_dir,
            ref=genome,
            n_cpu=threads,
            sam_out=tmp_sam,
            min_qual=min_qual,
            aligner=aligner,
        )
        st.rmtree(iter_tmp_dir)
    else:
        if aligner == "minimap2":
            map_cmd = "minimap2 -2 -t {threads} -ax sr {fasta} {fastq} > {sam}"
        else:
            index = hci.check_bt2_index(genome)
            map_cmd = "bowtie2 --very-sensitive-local -p {threads} -x {index} -U {fastq} > {sam}"
        map_args = {
            "threads": threads,
            "sam": tmp_sam,
            "fastq": reads,
            "fasta": genome,
            "index": index,
        }
        sp.call(map_cmd.format(**map_args), shell=True)

    # Remove supplementary alignments
    # TODO: replace sp.call with ps.view command. It currently has a bug
    # preventing output redirection.
    sp.call(
        "samtools view -F 2048 -h -@ {threads} -o {out} {tmp}".format(
            tmp=tmp_sam, threads=threads, out=out_sam
        ),
        shell=True,
    )
    os.remove(tmp_sam)


def sam2pairs(sam1, sam2, out_pairs, info_contigs, min_qual=30):
    """
    Make a .pairs file from two Hi-C sam files sorted by read names.
    The Hi-C mates are matched by read identifier. Pairs where at least one
    reads maps with MAPQ below  min_qual threshold are discarded. Pairs are
    sorted by readID and stored in upper triangle (first pair higher).

    Parameters
    ----------
    sam1 : str
        Path to the name-sorted SAM file with aligned Hi-C forward reads.
    sam2 : str
        Path to the name-sorted SAM file with aligned Hi-C reverse reads.
    out_pairs : str
        Path to the output space-separated .pairs file with columns 
        readID, chr1 pos1 chr2 pos2 strand1 strand2
    info_contigs : str
        Path to the info contigs file, to get info on chromosome sizes and order.
    min_qual : int
        Minimum mapping quality required to keep a Hi=C pair.
    """
    forward = ps.AlignmentFile(sam1)
    reverse = ps.AlignmentFile(sam2)

    # Generate header lines
    format_version = "## pairs format v1.0\n"
    sorting = "#sorted: readID\n"
    cols = "#columns: readID chr1 pos1 chr2 pos2 strand1 strand2\n"
    # Chromosome order will be identical in info_contigs and pair files
    chroms = pd.read_csv(info_contigs, sep="\t").apply(
        lambda x: "#chromsize: %s %d\n" % (x.contig, x.length), axis=1
    )
    with open(out_pairs, "w") as pairs:
        pairs.writelines([format_version, sorting, cols] + chroms.tolist())
        pairs_writer = csv.writer(pairs, delimiter="\t")
        n_reads = {"total": 0, "mapped": 0}
        # Remember if some read IDs were missing from either file
        unmatched_reads = 0
        # Remember if all reads in one sam file have been read
        exhausted = [False, False]
        # Iterate on both SAM simultaneously
        for end1, end2 in itertools.zip_longest(forward, reverse):
            # Both file still have reads
            # Check if reads pass filter
            try:
                end1_passed = end1.mapping_quality >= min_qual
            # Happens if end1 sam file has been exhausted
            except AttributeError:
                exhausted[0] = True
                end1_passed = False
            try:
                end2_passed = end2.mapping_quality >= min_qual
            # Happens if end2 sam file has been exhausted
            except AttributeError:
                exhausted[1] = True
                end2_passed = False
            # Skip read if mate is not present until they match or reads
            # have been exhausted
            while sum(exhausted) == 0 and end1.query_name != end2.query_name:
                # Get next read and check filters again
                # Count single-read iteration
                unmatched_reads += 1
                n_reads["total"] += 1
                if end1.query_name < end2.query_name:
                    try:
                        end1 = next(forward)
                        end1_passed = end1.mapping_quality >= min_qual
                    # If EOF is reached in SAM 1
                    except (StopIteration, AttributeError):
                        exhausted[0] = True
                        end1_passed = False
                    n_reads["mapped"] += end1_passed
                elif end1.query_name > end2.query_name:
                    try:
                        end2 = next(reverse)
                        end2_passed = end2.mapping_quality >= min_qual
                    # If EOF is reached in SAM 2
                    except (StopIteration, AttributeError):
                        exhausted[1] = True
                        end2_passed = False
                    n_reads["mapped"] += end2_passed

            # 2 reads processed per iteration, unless one file is exhausted
            n_reads["total"] += 2 - sum(exhausted)
            n_reads["mapped"] += sum([end1_passed, end2_passed])
            # Keep only pairs where both reads have good quality
            if end1_passed and end2_passed:

                # Flipping to get upper triangle
                if (
                    end1.reference_id == end2.reference_id
                    and end1.reference_start > end2.reference_start
                ) or end1.reference_id > end2.reference_id:
                    end1, end2 = end2, end1
                pairs_writer.writerow(
                    [
                        end1.query_name,
                        end1.reference_name,
                        end1.reference_start + 1,
                        end2.reference_name,
                        end2.reference_start + 1,
                        "-" if end1.is_reverse else "+",
                        "-" if end2.is_reverse else "+",
                    ]
                )
    pairs.close()
    if unmatched_reads > 0:
        logger.warning(
            "%d reads were only present in one SAM file.", unmatched_reads
        )
    logger.info(
        "{perc_map}% reads (single ends) mapped with Q >= {qual} ({mapped}/{total})".format(
            total=n_reads["total"],
            mapped=n_reads["mapped"],
            perc_map=round(100 * n_reads["mapped"] / n_reads["total"]),
            qual=min_qual,
        )
    )


def generate_log_header(log_path, input1, input2, genome, enzyme):
    hcl.set_file_handler(log_path, formatter=logging.Formatter(""))
    logger.info("## hicstuff: v%s log file", __version__)
    logger.info("## date: %s", time.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("## enzyme: %s", str(enzyme))
    logger.info("## input1: %s ", input1)
    logger.info("## input2: %s", input2)
    logger.info("## ref: %s", genome)
    logger.info("---")
    hcl.set_file_handler(log_path, formatter=hcl.logfile_formatter)


def filter_pcr_dup(pairs_idx_file, filtered_file):
    """
    Filter out PCR duplicates from a coordinate-sorted pairs file using
    overrrepresented exact coordinates. If multiple fragments have two reads
    with the exact same coordinates, only one of those fragments is kept.
    Parameters
    ----------
    pairs_idx_file : str
        Path to an indexed pairs file containing the Hi-C reads.
    filtered_file : str
        Path to the output pairs file after removing duplicates.
    """
    # Keep count of how many reads are filtered
    filter_count = 0
    reads_count = 0
    # Store header lines
    header = hio.get_pairs_header(pairs_idx_file)
    with open(pairs_idx_file, "r") as pairs, open(
        filtered_file, "w"
    ) as filtered:
        # Copy header lines to filtered file
        for head_line in header:
            filtered.write(head_line + "\n")
            next(pairs)

        # Use csv methods to easily access columns
        paircols = [
            "readID",
            "chr1",
            "pos1",
            "chr2",
            "pos2",
            "strand1",
            "strand2",
            "frag1",
            "frag2",
        ]
        # Columns used for comparison of coordinates
        coord_cols = [col for col in paircols if col != "readID"]
        pair_reader = csv.DictReader(
            pairs, delimiter="\t", fieldnames=paircols
        )
        filt_writer = csv.DictWriter(
            filtered, delimiter="\t", fieldnames=paircols
        )

        # Initialise a variable to store coordinates of reads in previous pair
        prev = {k: 0 for k in paircols}
        for pair in pair_reader:
            reads_count += 1
            # If coordinates are the same as before, skip pair
            if all(
                pair[pair_var] == prev[pair_var] for pair_var in coord_cols
            ):
                filter_count += 1
                continue
            # Else write pair and store new coordinates as previous
            else:
                filt_writer.writerow(pair)
                prev = pair
        logger.info(
            "%d%% PCR duplicates have been filtered out (%d / %d pairs) "
            % (
                100 * round(filter_count / reads_count, 3),
                filter_count,
                reads_count,
            )
        )


def pairs2matrix(
    pairs_file, mat_file, fragments_file, mat_fmt="GRAAL", threads=1
):
    """Generate the matrix by counting the number of occurences of each
    combination of restriction fragments in a pairs file.

    Parameters
    ----------
    pairs_file : str
        Path to a Hi-C pairs file, with frag1 and frag2 columns added.
    mat_file : str
        Path where the matrix will be written.
    fragments_file : str
        Path to the fragments_list.txt file. Used to know total
        matrix size in case some observations are not observed at the end.
    mat_fmt : str
        The format to use when writing the matrix. Can be GRAAL or bg2 format.
    threads : int
        Number of threads to use in parallel.
    """
    # Number of fragments is N lines in frag list - 1 for the header
    n_frags = sum(1 for line in open(fragments_file, "r")) - 1
    frags = pd.read_csv(fragments_file, delimiter="\t")

    def write_mat_entry(frag1, frag2, contacts):
        """Write a single sparse matrix entry in either GRAAL or bg2 format"""
        if mat_fmt == "GRAAL":
            mat.write(
                "\t".join(map(str, [prev_pair[0], prev_pair[1], n_occ])) + "\n"
            )
        elif mat_fmt == "bg2":
            frag1, frag2 = int(frag1), int(frag2)
            mat.write(
                "\t".join(
                    map(
                        str,
                        [
                            frags.chrom[frag1],
                            frags.start_pos[frag1],
                            frags.end_pos[frag1],
                            frags.chrom[frag2],
                            frags.start_pos[frag2],
                            frags.end_pos[frag2],
                            contacts,
                        ],
                    )
                )
                + "\n"
            )

    pre_mat_file = mat_file + ".pre.pairs"
    hio.sort_pairs(
        pairs_file, pre_mat_file, keys=["frag1", "frag2"], threads=threads
    )
    header_size = len(hio.get_pairs_header(pre_mat_file))
    with open(pre_mat_file, "r") as pairs, open(mat_file, "w") as mat:
        # Skip header lines
        for _ in range(header_size):
            next(pairs)
        prev_pair = ["0", "0"]  # Pairs identified by [frag1, frag2]
        n_occ = 0  # Number of occurences of each frag combination
        n_nonzero = 0  # Total number of nonzero matrix entries
        n_pairs = 0  # Total number of pairs entered in the matrix
        pairs_reader = csv.reader(pairs, delimiter="\t")
        # First line contains nrows, ncols and number of nonzero entries.
        # Number of nonzero entries is unknown for now
        if mat_fmt == "GRAAL":
            mat.write("\t".join(map(str, [n_frags, n_frags, "-"])) + "\n")
        for pair in pairs_reader:
            # Fragment ids are field 8 and 9
            curr_pair = [pair[7], pair[8]]
            # Increment number of occurences for fragment pair
            if prev_pair == curr_pair:
                n_occ += 1
            # Write previous pair and start a new one
            else:
                if n_occ > 0:
                    write_mat_entry(prev_pair[0], prev_pair[1], n_occ)
                prev_pair = curr_pair
                n_pairs += n_occ
                n_occ = 1
                n_nonzero += 1
        # Write the last value
        write_mat_entry(curr_pair[0], curr_pair[1], n_occ)
        n_nonzero += 1
        n_pairs += 1

    # Edit header line to fill number of nonzero entries inplace in GRAAL header
    if mat_fmt == "GRAAL":
        with open(mat_file) as mat, open(pre_mat_file, "w") as tmp_mat:
            header = mat.readline()
            header = header.replace("-", str(n_nonzero))
            tmp_mat.write(header)
            st.copyfileobj(mat, tmp_mat)
        # Replace the matrix file with the one with corrected header
        os.rename(pre_mat_file, mat_file)
    else:
        os.remove(pre_mat_file)

    logger.info(
        "%d pairs used to build a contact map of %d bins with %d nonzero entries.",
        n_pairs,
        n_frags,
        n_nonzero,
    )


def full_pipeline(
    genome,
    input1,
    input2=None,
    enzyme=5000,
    circular=False,
    out_dir=None,
    tmp_dir=None,
    plot=False,
    min_qual=30,
    min_size=0,
    threads=1,
    no_cleanup=False,
    iterative=False,
    filter_events=False,
    prefix=None,
    start_stage="fastq",
    mat_fmt="GRAAL",
    aligner="bowtie2",
    pcr_duplicates=False,
    distance_law=False,
    centromeres=None,
):
    """
    Run the whole hicstuff pipeline. Starting from fastq files and a genome to
    obtain a contact matrix.
    
    Parameters
    ----------
    genome : str
        Path to the bowtie2 index prefix if using bowtie2 or to the genome in
        fasta format if using minimap2.
    input1 : str
        Path to the Hi-C reads in fastq format (forward), the aligned Hi-C reads
        in SAM format, or the pairs file, depending on the value of start_stage.
    input2 : str
        Path to the Hi-C reads in fastq format (forward), the aligned Hi-C reads
        in SAM format, or None, depending on the value of start_stage.
    enzyme : int or str
        Name of the enzyme used for the digestion (e.g "DpnII"). If an integer
        is used instead, the fragment attribution will be done directly using a
        fixed chunk size.
    circular : bool
        Use if the genome is circular.
    out_dir : str or None
        Path where output files should be written. Current directory by default.
    tmp_dir : str or None
        Path where temporary files will be written. Creates a "tmp" folder in
        out_dir by default.
    plot : bool
        Whether plots should be generated at different steps of the pipeline.
        Plots are saved in a "plots" directory inside out_dir.
    min_qual : int
        Minimum mapping quality required to keep a pair of Hi-C reads.
    min_size : int
        Minimum contig size required to keep it.
    threads : int
        Number of threads to use for parallel operations.
    no_cleanup : bool
        Whether temporary files should be deleted at the end of the pipeline.
    iterative : bool
        Use iterative mapping. Truncates and extends reads until unambiguous
        alignment.
    filter_events : bool
        Filter spurious or uninformative 3C events. Requires a restriction enzyme.
    prefix : str or None
        Choose a common name for output files instead of default GRAAL names.
    start_stage : str
        Step at which the pipeline should start. Can be "fastq", "sam", "pairs"
        or "pairs_idx". With starting from sam allows to skip alignment and start 
        from named-sorted sam files. With
        "pairs", a single pairs file is given as input, and with "pairs_idx", the
        pairs in the input must already be attributed to fragments and fragment
        attribution is skipped.
    mat_fmt : str
        Select the output matrix format. Can be either "bg2" for the 
        cooler-compatible bedgraph2 format, or GRAAL format.
    aligner : str
        Read alignment software to use. Can be either "minimap2" or "bowtie2".
    pcr_duplicates : bool
        If True, PCR duplicates will be filtered based on genomic positions.
        Pairs where both reads have exactly the same coordinates are considered
        duplicates and only one of those will be conserved.
    distance_law : bool
        If True, generates a distance law file with the values of the probabilities 
        to have a contact between two distances for each chromosomes or arms if the
        file with the positions has been given. The values are not normalized, or 
        averaged.
    centromers : None or str
        If not None, path of file with Positions of the centromeres separated by a
        space and in the same order than the chromosomes. 
    """
    # Pipeline can start from 3 input types
    start_time = datetime.now()
    stages = {"fastq": 0, "sam": 1, "pairs": 2, "pairs_idx": 3}
    start_stage = stages[start_stage]
    # sanitize enzyme
    enzyme = str(enzyme)
    # Remember whether fragments_file has been generated during this run
    fragments_updated = False

    if out_dir is None:
        out_dir = os.getcwd()

    if tmp_dir is None:
        tmp_dir = join(out_dir, "tmp")

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)

    # Define figures output paths
    if plot:
        fig_dir = join(out_dir, "plots")
        os.makedirs(fig_dir, exist_ok=True)
        frag_plot = join(fig_dir, "frags_hist.pdf")
        dist_plot = join(fig_dir, "event_distance.pdf")
        pie_plot = join(fig_dir, "event_distribution.pdf")
        distance_law_plot = join(fig_dir, "distance_law.pdf")
        matplotlib.use("Agg")
    else:
        fig_dir = None
        dist_plot = pie_plot = frag_plot = None

    # Use current time for logging and to identify files
    now = time.strftime("%Y%m%d%H%M%S")

    def _tmp_file(fname):
        if prefix:
            fname = prefix + "." + fname
        return join(tmp_dir, fname)

    def _out_file(fname):
        if prefix:
            fname = prefix + "." + fname
        return join(out_dir, fname)

    # Define temporary file names
    log_file = _out_file("hicstuff_" + now + ".log")
    tmp_genome = _tmp_file("genome.fasta")
    sam1 = _tmp_file("for.sam")
    sam2 = _tmp_file("rev.sam")
    pairs = _tmp_file("valid.pairs")
    pairs_idx = _tmp_file("valid_idx.pairs")
    pairs_filtered = _tmp_file("valid_idx_filtered.pairs")
    pairs_pcr = _tmp_file("valid_idx_pcrfree.pairs")

    # If the user chose bowtie2 and supplied an index, extract fasta from it
    # For later steps of the pipeline (digestion / frag attribution)
    if aligner == "bowtie2":
        bt2fa = sp.Popen(
            ["bowtie2-inspect", genome],
            stdout=open(tmp_genome, "w"),
            stderr=sp.PIPE,
        )
        _, bt2err = bt2fa.communicate()
        # bowtie2-inspect still has return code 0 when crashing, need to
        # actively look for error in stderr
        fasta = tmp_genome
        if re.search(r"[Ee]rror", bt2err.decode()):
            logger.error(bt2err)
            logger.error(
                "bowtie2-inspect has failed, make sure you provided "
                "the path to the bowtie2 index without the extension."
            )
            sys.exit(1)
    else:
        fasta = genome

    # If the user chose bowtie2 and supplied an index, extract fasta from it
    if aligner == "bowtie2":
        fasta = _tmp_file("genome.fasta")
        with open(fasta, "w") as temp_genome:
            bt2fa = sp.Popen(
                ["bowtie2-inspect", genome], stdout=temp_genome, stderr=sp.PIPE
            )
        _, bt2err = bt2fa.communicate()
        # bowtie2-inspect still has return code 0 when crashing, need to
        # actively look for error in stderr
        if re.search(r"[Ee]rror", bt2err.decode()):
            logger.error(bt2err)
            logger.error(
                "bowtie2-inspect has failed, make sure you provided "
                "the path to the bowtie2 index without the extension."
            )
            sys.exit(1)
    else:
        fasta = genome

    # Enable file logging
    hcl.set_file_handler(log_file)
    generate_log_header(log_file, input1, input2, genome, enzyme)

    # Define output file names
    if prefix:
        fragments_list = _out_file("frags.tsv")
        info_contigs = _out_file("chr.tsv")
        mat = _out_file("mat.tsv")
    else:
        # Default GRAAL file names
        fragments_list = _out_file("fragments_list.txt")
        info_contigs = _out_file("info_contigs.txt")
        mat = _out_file("abs_fragments_contacts_weighted.txt")

    # Define what input files are given
    if start_stage == 0:
        reads1, reads2 = input1, input2
    elif start_stage == 1:
        sam1, sam2 = input1, input2
    elif start_stage == 2:
        pairs = input1
    elif start_stage == 3:
        pairs_idx = input1

    # Detect if multiple enzymes are given
    if re.search(",", enzyme):
        enzyme = enzyme.split(",")
    # Perform genome alignment
    if start_stage == 0:
        align_reads(
            reads1,
            genome,
            sam1,
            tmp_dir=tmp_dir,
            threads=threads,
            aligner=aligner,
            iterative=iterative,
            min_qual=min_qual,
        )
        align_reads(
            reads2,
            genome,
            sam2,
            tmp_dir=tmp_dir,
            threads=threads,
            aligner=aligner,
            iterative=iterative,
            min_qual=min_qual,
        )
        # Sort alignments by read name
        ps.sort(
            "-@", str(threads), "-n", "-O", "SAM", "-o", sam1 + ".sorted", sam1
        )
        st.move(sam1 + ".sorted", sam1)
        ps.sort(
            "-@", str(threads), "-n", "-O", "SAM", "-o", sam2 + ".sorted", sam2
        )
        st.move(sam2 + ".sorted", sam2)

    # Starting from sam files
    if start_stage <= 1:

        fragments_updated = True
        # Generate info_contigs and fragments_list output files
        hcd.write_frag_info(
            fasta,
            enzyme,
            min_size=min_size,
            circular=circular,
            output_contigs=info_contigs,
            output_frags=fragments_list,
        )

        # Log fragment size distribution
        hcd.frag_len(
            frags_file_name=fragments_list, plot=plot, fig_path=frag_plot
        )

        # Make pairs file (readID, chr1, chr2, pos1, pos2, strand1, strand2)
        sam2pairs(sam1, sam2, pairs, info_contigs, min_qual=min_qual)

    # Starting from pairs file
    if start_stage <= 2:
        restrict_table = {}
        for record in SeqIO.parse(fasta, "fasta"):
            # Get chromosome restriction table
            restrict_table[record.id] = hcd.get_restriction_table(
                record.seq, enzyme, circular=circular
            )

        # Add fragment index to pairs (readID, chr1, pos1, chr2,
        # pos2, strand1, strand2, frag1, frag2)
        hcd.attribute_fragments(pairs, pairs_idx, restrict_table)

    # Sort pairs file by coordinates for next steps
    hio.sort_pairs(
        pairs_idx,
        pairs_idx + ".sorted",
        keys=["chr1", "pos1", "chr2", "pos2"],
        threads=threads,
    )
    os.rename(pairs_idx + ".sorted", pairs_idx)

    if filter_events:
        uncut_thr, loop_thr = hcf.get_thresholds(
            pairs_idx, plot_events=plot, fig_path=dist_plot, prefix=prefix
        )
        hcf.filter_events(
            pairs_idx,
            pairs_filtered,
            uncut_thr,
            loop_thr,
            plot_events=plot,
            fig_path=pie_plot,
            prefix=prefix,
        )
        use_pairs = pairs_filtered
    else:
        use_pairs = pairs_idx

    # Generate fragments file if it has not been already
    if not fragments_updated:
        hcd.write_frag_info(
            fasta,
            enzyme,
            min_size=min_size,
            circular=circular,
            output_contigs=info_contigs,
            output_frags=fragments_list,
        )

    # Generate distance law table if enabled
    if distance_law:
        out_distance_law = _out_file("distance_law.txt")
        x_s, p_s, names_distance_law = hcdl.get_distance_law(
            pairs_idx,
            fragments_list,
            centro_file=centromeres,
            base=1.1,
            out_file=out_distance_law,
            circular=circular,
        )
        # Generate distance law figure is plots are enabled
        if plot:
            # Retrieve chrom labels from distance law file
            _, _, chr_labels = hcdl.import_distance_law(out_distance_law)
            chr_labels = [lab[0] for lab in chr_labels]
            chr_labels_idx = np.unique(chr_labels, return_index=True)[1]
            chr_labels = [
                chr_labels[index] for index in sorted(chr_labels_idx)
            ]
            p_s = hcdl.normalize_distance_law(x_s, p_s)
            hcdl.plot_ps_slope(
                x_s, p_s, labels=chr_labels, fig_path=distance_law_plot
            )

    # Filter out PCR duplicates if requested
    if pcr_duplicates:
        filter_pcr_dup(use_pairs, pairs_pcr)
        use_pairs = pairs_pcr

    # Build matrix from pairs.
    pairs2matrix(
        use_pairs, mat, fragments_list, mat_fmt=mat_fmt, threads=threads
    )

    # Clean temporary files
    if not no_cleanup:
        tempfiles = [
            pairs,
            pairs_idx,
            pairs_filtered,
            sam1,
            sam2,
            pairs_pcr,
            tmp_genome,
        ]
        # Do not delete files that were given as input
        try:
            tempfiles.remove(input1)
            tempfiles.remove(input2)
        except ValueError:
            pass
        for file in tempfiles:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

    end_time = datetime.now()
    duration = relativedelta(end_time, start_time)
    logger.info(
        "Contact map generated after {h}h {m}m {s}s".format(
            h=duration.hours, m=duration.minutes, s=duration.seconds
        )
    )
