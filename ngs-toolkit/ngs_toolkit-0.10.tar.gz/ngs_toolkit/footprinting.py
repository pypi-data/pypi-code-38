#!/usr/bin/env python

import re
from scipy.stats import mannwhitneyu
from statsmodels.sandbox.stats.multicomp import multipletests


def piq_prepare_motifs(
    motifs_file="data/external/jaspar_human_motifs.txt",
    output_dir="footprinting",
    piq_source_dir="/home/arendeiro/workspace/piq-single/",
    motif_numbers=None,
):
    """
    Prepare motifs for footprinting with PIQ.
    This is typically done only once per genome.

    Parameters
    ----------
    motifs_file : :obj:`str`
        A JASPAR-format file with PWMs of motifs.

    output_dir : :obj:`str`
        A root directory to use for the output of a footprint analys

    piq_source_dir : :obj:`str`
        The root directory of the PIQ code.

    motif_numbers : :obj:`str`
        A range of integers enumerating the TF motifs from
    """
    import textwrap
    from pypiper import NGSTk

    tk = NGSTk()

    output_dir = os.path.abspath(output_dir)
    motifs_dir = os.path.join(output_dir, "motifs")
    jobs_dir = os.path.join(motifs_dir, "jobs")

    for path in [output_dir, motifs_dir, jobs_dir]:
        if not os.path.exists(path):
            os.makedirs(path)

    if motif_numbers is None:
        n_motifs = open(motifs_file, "r").read().count(">")
        motif_numbers = range(1, n_motifs + 1)

    for motif in motif_numbers:
        # skip if exists
        a = os.path.exists(os.path.join(motifs_dir, "{}.pwmout.RData".format(motif)))
        b = os.path.exists(os.path.join(motifs_dir, "{}.pwmout.rc.RData".format(motif)))
        if a and b:
            continue

        # prepare job
        log_file = os.path.join(
            jobs_dir, "piq_preparemotifs.motif{}.slurm.log".format(motif)
        )
        job_file = os.path.join(
            jobs_dir, "piq_preparemotifs.motif{}.slurm.sh".format(motif)
        )
        cmd = tk.slurm_header(
            "piq_preparemotifs.{}".format(motif),
            log_file,
            cpus_per_task=1,
            queue="shortq",
            mem_per_cpu=8000,
        )

        # change to PIQ dir (required in PIQ because of hard-coded links in code)
        cmd += """cd {}\n\t\t""".format(piq_source_dir)

        # Actual PIQ command
        cmd += """Rscript {}/pwmmatch.exact.r""".format(piq_source_dir)
        cmd += " {}/common.r".format(piq_source_dir)
        cmd += " {}".format(os.path.abspath(motifs_file))
        cmd += " " + str(motif)
        cmd += """ {}\n""".format(motifs_dir)

        # write job to file
        with open(job_file, "w") as handle:
            handle.writelines(textwrap.dedent(cmd))

        tk.slurm_submit_job(job_file)


def piq_prepare_bams(
    bam_files,
    group_name,
    output_dir="footprinting",
    piq_source_dir="/home/arendeiro/workspace/piq-single/",
):
    """
    Prepare single or group of BAM files for footprinting.

    `bam_files` is a string path to a BAM file or a list of the same.
    `group_name` is a label matching the one given to `piq_prepare_bams`.
    `output_dir` is a root directory to use for the output of a footprint analysis.
    `piq_source_dir` is the root directory of the PIQ code.

    This will launch jobs for each motif.
    """
    import textwrap
    from pypiper import NGSTk

    tk = NGSTk()

    if isinstance(bam_files, str):
        bam_files = [bam_files]

    output_dir = os.path.abspath(output_dir)
    cache_dir = os.path.join(output_dir, "piq_cache")
    jobs_dir = os.path.join(cache_dir, "jobs")

    for path in [output_dir, cache_dir, jobs_dir]:
        if not os.path.exists(path):
            os.makedirs(path)

    merged_bam = os.path.join(cache_dir, "{}.merged.bam".format(group_name))
    merged_cache = os.path.join(cache_dir, "{}.merged.RData".format(group_name))
    log_file = os.path.join(jobs_dir, "piq_preparebams.{}.slurm.log".format(group_name))
    job_file = os.path.join(jobs_dir, "piq_preparebams.{}.slurm.sh".format(group_name))

    # Build job
    cmd = tk.slurm_header(
        "piq_preparebams.{}".format(group_name),
        log_file,
        cpus_per_task=4,
        queue="mediumq",
        time="11:00:00",
        mem_per_cpu=8000,
    )

    # merge all bam files
    if not os.path.exists(merged_bam):
        cmd += """sambamba merge -t 12 {0} {1}\n\t\t""".format(
            merged_bam, " ".join(bam_files)
        )

    # change to PIQ dir (required in PIQ because of hard-coded links in code)
    cmd += """cd {}\n""".format(piq_source_dir)

    # Actual PIQ command
    cmd += """\t\tRscript {0}/bam2rdata.r {0}/common.r {1} {2}\n""".format(
        piq_source_dir, merged_cache, merged_bam
    )

    # slurm footer
    cmd += tk.slurm_footer()

    # write job to file
    with open(job_file, "w") as handle:
        handle.writelines(textwrap.dedent(cmd))

    tk.slurm_submit_job(job_file)


def footprint(
    group_name,
    motif_numbers,
    output_dir="footprinting",
    piq_source_dir="/home/arendeiro/workspace/piq-single/",
    total_job_limit=250,
    min_time_between_jobs=5,
    refresh_time=10,
):
    """
    Perform TF footprinting with PIQ.

    `group_name` is a label matching the one given to `piq_prepare_bams`.
    `motif_numbers` is a range of integers enumerating the TF motifs from
    the motif file given to `piq_prepare_motifs` to footprint.
    `output_dir` is a root directory to use for the input/output of a footprint analysis.
    `piq_source_dir` is the root directory of the PIQ code.

    This will launch jobs in `min_time_between_jobs` (seconds) intervals
    until the whole job queue has `total_job_limit` jobs
    and retry after `refresh_time` (seconds).
    """
    import subprocess
    import time
    import textwrap
    from pypiper import NGSTk

    tk = NGSTk()

    output_dir = os.path.abspath(output_dir)
    motifs_dir = os.path.join(output_dir, "motifs/")  # slash is important - PIQ reasons
    cache_dir = os.path.join(output_dir, "piq_cache")
    foots_dir = os.path.join(output_dir, "footprint_calls")
    tmp_dir = os.path.join(foots_dir, "tmp_output")
    jobs_dir = os.path.join(foots_dir, "jobs")
    merged_cache = os.path.join(cache_dir, "{}.merged.RData".format(group_name))

    for path in [output_dir, motifs_dir, cache_dir, foots_dir, tmp_dir, jobs_dir]:
        if not os.path.exists(path):
            os.makedirs(path)

    for motif_number in motif_numbers:
        if not os.path.exists(
            os.path.join(motifs_dir, "{}.pwmout.RData".format(motif_number))
        ):
            _LOGGER.warning("PIQ file for motif {} does not exist".format(motif_number))
            continue

        t_dir = os.path.join(tmp_dir, group_name)
        o_dir = os.path.join(foots_dir, group_name)
        for path in [t_dir, o_dir]:
            if not os.path.exists(path):
                os.mkdir(path)
        log_file = os.path.join(
            jobs_dir,
            "piq_footprinting.{}.motif{}.slurm.log".format(group_name, motif_number),
        )
        job_file = os.path.join(
            jobs_dir,
            "piq_footprinting.{}.motif{}.slurm.sh".format(group_name, motif_number),
        )

        # prepare slurm job header
        cmd = tk.slurm_header(
            "piq_footprinting.{}.motif{}".format(group_name, motif_number),
            log_file,
            cpus_per_task=1,
            queue="shortq",
            mem_per_cpu=8000,
        )

        # change to PIQ dir (required in PIQ because of hard-coded links in code)
        cmd += """cd {}\n""".format(piq_source_dir)

        # Actual PIQ command
        # footprint
        cmd += """\t\tRscript {0}/pertf.r {0}/common.r {1} {2} {3} {4} {5}\n""".format(
            piq_source_dir, motifs_dir, t_dir, o_dir, merged_cache, motif_number
        )

        # slurm footer
        cmd += tk.slurm_footer()

        # write job to file
        with open(job_file, "w") as handle:
            handle.writelines(textwrap.dedent(cmd))

        # submit jobs slowly and keeping total numbe of jobs below a certain ammount
        submit = (
            len(subprocess.check_output("squeue").split("\n")) - 1
        ) < total_job_limit
        while not submit:
            time.sleep(refresh_time)
            _LOGGER.info("Waited {}. Checking again...".format(refresh_time))
            submit = (
                len(subprocess.check_output("squeue").split("\n")) - 1
            ) < total_job_limit

        tk.slurm_submit_job(job_file)
        _LOGGER.info(
            "Submitted job of group {}, motif {}.".format(group_name, motif_number)
        )
        time.sleep(min_time_between_jobs)


def tfbs_to_gene(
    bed_file,
    tss_file="data/external/ensembl.tss.bed",
    promoter_and_genesbody_file="data/external/ensembl.promoter_and_genesbody.bed",
):
    """
    Assign a TF binding site (output of PIQ footprinting) to a gene.
    TFBS are assigned to a gene if they overlap with their promoter or genebody,
    else to the nearest TSS (regardless of the distance).
    This distance can be used later to weight the interaction e.g. in combination
    with the confidence measures of the footprint (binding).

    `bed_file` is a PIQ output 8-column BED file:
    chrom, start, end, pwm, shape, strand, score, purity.

    `tss_file` and `promoter_and_genesbody_file` are 6-column BED files:
    chrom, start, end, gene_id, transcript_id, strand.

    Returns TFBS-gene assignment matrix.
    """
    # read in gene body + promoter info
    promoter_and_genesbody = pybedtools.BedTool(promoter_and_genesbody_file)
    # read in TSS info
    tss = pybedtools.BedTool(tss_file)
    # columns
    columns = [
        "chrom",
        "start",
        "end",
        "pwm",
        "shape",
        "strand",
        "score",
        "purity",
        "chrom_gene",
        "start_gene",
        "end_gene",
        "gene",
        "transcript",
        "strand_gene",
    ]

    # Assign TFBS to gene if they overlap with gene body or promoter (5kb around TSS -> 2.5kb upstream)
    gene_assignments = (
        pybedtools.BedTool(os.path.join(bed_file))
        .intersect(promoter_and_genesbody, wa=True, wb=True)
        .to_dataframe(names=columns)
    )

    # For the remaining TFBSs, assign TFBS to closest TSS regardless of distance
    # (distance is not so important for assignment because distance is a penalyzing effect during TF-gene interaction score calculation)
    # 1. get genes not assigned previously
    all_ = pybedtools.BedTool(os.path.join(bed_file)).to_dataframe(names=columns[:8])

    merged = pd.merge(all_, gene_assignments, how="left")
    remaining = merged[merged["gene"].isnull()]

    # 2. assign to nearest
    closest_tss = (
        pybedtools.BedTool(
            remaining.iloc[:, range(all_.shape[1])]
            .to_string(index=False, header=False)
            .replace(" ", "\t"),
            from_string=True,
        )
        .closest(tss, d=True)
        .to_dataframe(names=columns + ["distance"])
    )

    # put the two together
    gene_assignments = pd.concat([gene_assignments, closest_tss])

    # set overlapping distance to 0
    gene_assignments.loc[gene_assignments["distance"].isnull(), "distance"] = 0

    return gene_assignments


def piq_to_network(
    group_name, motif_numbers, peak_universe_file, output_dir="footprinting"
):
    """
    Parse PIQ output, filter footprints and score TF-gene interactions.
    Returns matrix with score of each TF regulating each gene.

    `group_name` is a label matching the one given to `piq_prepare_bams`.
    `motif_numbers` is a range of integers enumerating the TF motifs from
    the motif file given to `piq_prepare_motifs` to footprint.
    `peak_universe_file` is a 3-column BED file with high confidence genomic locations
    to filter interactions for (generally a peak set).
    `output_dir` is a root directory to use for the input/output of a footprint analysis.

    Records in `peak_universe_file` are recommended to be enlarged (e.g. up to 500bp in each direction).
    """
    output_dir = os.path.abspath(output_dir)
    foots_dir = os.path.join(output_dir, "footprint_calls")
    group_foot_dir = os.path.join(foots_dir, group_name)

    for path in [output_dir, foots_dir, group_foot_dir]:
        if not os.path.exists(path):
            os.makedirs(path)

    # list results_dir
    files = os.listdir(group_foot_dir)

    if len(files) == 0:
        _LOGGER.warning(
            "There are not footprint calls for group '{}' in '{}'".format(
                group_name, group_foot_dir
            )
        )

    # use universe set of ATAC-seq peaks to filter data
    all_peaks = pybedtools.BedTool(peak_universe_file)

    # dataframe to store TFBS assignment to genes
    assignments = pd.DataFrame()

    # dataframe to store TF->gene interactions
    interactions = pd.DataFrame()

    # dataframe to store stats about the TFBS and the interactions
    stats = pd.DataFrame()

    # loop through motifs/TFs, filter and establish relationship between TF and gene
    for motif in motif_numbers:
        _LOGGER.info(
            "Gathering footprint calls of motif '{}' for group '{}'".format(
                motif, group_name
            )
        )
        # get both forward and reverse complement PIQ output files
        result_files = list()
        for f in files:
            m = re.match(r"%i-.*-calls\.csv$" % motif, f)
            if hasattr(m, "string"):
                result_files.append(m.string)

        # make bed file from it
        # concatenate files (forward and reverse complement are treated differently by PIQ)
        for i, result_file in enumerate(result_files):
            df = pd.read_csv(os.path.join(group_foot_dir, result_file), index_col=0)
            df.rename(columns={"coord": "start"}, inplace=True)
            # fix coordinates
            if "RC-calls.csv" not in result_file:
                df["end"] = df["start"] + 1
                df["strand"] = "+"
            else:
                df["end"] = df["start"]
                df["start"] = df["start"] - 1
                df["strand"] = "-"
            # concatenate
            if i == 0:
                df2 = df
            else:
                df2 = pd.concat([df, df2])

        # add total TFBS to stats
        stats.loc[motif, "TFBS"] = len(df2)
        stats.loc[motif, "TFBS_+"] = len(df2[df2["strand"] == "+"])
        stats.loc[motif, "TFBS_-"] = len(df2[df2["strand"] == "-"])

        # Filter for purity
        footprints = df2[df2["purity"] > 0.7]
        stats.loc[motif, "pur0.7"] = len(footprints)

        # If less than 500 significant interactions, ignore TF
        if footprints.shape[0] < 500:
            continue

        # filter for motifs overlapping CLL peaks
        footprints = (
            pybedtools.BedTool(
                (
                    footprints[
                        [
                            "chr",
                            "start",
                            "end",
                            "pwm",
                            "shape",
                            "strand",
                            "score",
                            "purity",
                        ]
                    ]
                    .to_string(header=None, index=False)
                    .replace(" ", "\t")
                ),
                from_string=True,
            )
            .intersect(all_peaks, wa=True)
            .to_dataframe()
        )
        footprints.columns = [
            "chr",
            "start",
            "end",
            "pwm",
            "shape",
            "strand",
            "score",
            "purity",
        ]
        footprints.to_csv(os.path.join("tmp.bed"), sep="\t", index=False, header=False)
        stats.loc[motif, "overlap_universe"] = footprints.shape[0]

        # assign TFBS to gene
        gene_assignments = tfbs_to_gene(os.path.join("tmp.bed"))
        gene_assignments.loc[:, "TF"] = motif
        stats.loc[motif, "gene_overlap_count"] = len(
            gene_assignments[gene_assignments["distance"] == 0]
        )
        stats.loc[motif, "dist_gene_mean"] = gene_assignments["distance"].mean()
        stats.loc[motif, "dist_gene_median"] = gene_assignments["distance"].median()
        stats.loc[motif, "dist_gene_std"] = gene_assignments["distance"].std()

        # Get weighted values
        # weigh with footprint purity and distance to tss
        gene_assignments["interaction_score"] = gene_assignments.apply(
            lambda x: 2 * (x["purity"] - 0.5) * 10 ** -(x["distance"] / 1000000.0),
            axis=1,
        )
        # sum scores for each gene
        scores = (
            gene_assignments.groupby(["gene"])["interaction_score"]
            .apply(sum)
            .reset_index()
        )
        scores.loc[:, "TF"] = motif

        # filter out potentially not assigned bindings
        scores = scores[scores["gene"] != "."]

        # add mean score for each gene
        stats.loc[motif, "score_gene_mean"] = scores["interaction_score"].mean()
        stats.loc[motif, "score_gene_std"] = scores["interaction_score"].std()
        stats.loc[motif, "TF"] = motif

        # save
        scores.to_csv(
            os.path.join(group_foot_dir, "scores.motif{}.csv".format(motif)),
            index=False,
        )
        gene_assignments.to_csv(
            os.path.join(group_foot_dir, "gene_assignments.motif{}.csv".format(motif)),
            index=False,
        )

        # add to dataframe with all TF-gene interactions
        interactions = interactions.append(scores, ignore_index=True)
        assignments = assignments.append(gene_assignments, ignore_index=True)

    # save
    assignments.to_csv(
        os.path.join(group_foot_dir, "assignments.all_motifs.csv"), index=False
    )
    interactions.to_csv(
        os.path.join(group_foot_dir, "interactions.all_motifs.csv"), index=False
    )
    stats.to_csv(os.path.join(group_foot_dir, "stats.all_motifs.csv"), index=False)

    return (assignments, interactions, stats)


def differential_interactions(
    group_name1,
    group_name2,
    output_dir="footprinting",
    motifs_mapping="data/external/jaspar_human_motifs.id_mapping.txt",
):
    """
    Compare TF-gene interactions between two sets of groups (e.g. KO and WT)
    and visualize differences.
    """

    def add_xy_line(axis):
        lims = [
            np.min([axis.get_xlim(), axis.get_ylim()]),
            np.max([axis.get_xlim(), axis.get_ylim()]),
        ]
        axis.plot(lims, lims, "--", alpha=0.5, zorder=0)
        axis.set_aspect("equal")
        axis.set_xlim(lims)
        axis.set_ylim(lims)

    if group_name1 == group_name2:
        _LOGGER.warning("The two groups are the same! Skipping...")
        return

    comparison_name = "{}-{}".format(group_name1, group_name2)

    output_dir = os.path.abspath(output_dir)
    foots_dir = os.path.join(output_dir, "footprint_calls")
    diff_dir = os.path.join(output_dir, "differential_calls")

    for path in [output_dir, foots_dir, diff_dir]:
        if not os.path.exists(path):
            os.makedirs(path)

    f1 = pd.read_csv(
        os.path.join(foots_dir, group_name1, "interactions.all_motifs.csv")
    )
    f2 = pd.read_csv(
        os.path.join(foots_dir, group_name2, "interactions.all_motifs.csv")
    )

    # Global changes in TFs
    # are the TFs binding differently globally on average?
    tf_stats = f1.groupby("TF")["interaction_score"].mean().to_frame(name=group_name1)
    tf_stats = tf_stats.join(
        f2.groupby("TF")["interaction_score"]
        .mean()
        .to_frame(name=group_name2)
        .squeeze(),
        how="outer",
    )

    # calculate some tf_stats
    for tf in tf_stats.index:
        a = f1.loc[f1["TF"] == tf, "interaction_score"]
        b = f2.loc[f2["TF"] == tf, "interaction_score"]
        tf_stats.loc[tf, "group1_log_interactions"] = np.log(
            (a.shape[0] / float(f1.shape[0])) * 1e3
        )
        tf_stats.loc[tf, "group2_log_interactions"] = np.log(
            (b.shape[0] / float(f2.shape[0])) * 1e3
        )
        tf_stats.loc[tf, "p_value"] = mannwhitneyu(a, b)[1]
    tf_stats.loc[:, "q_value"] = multipletests(
        tf_stats.loc[:, "p_value"], method="fdr_bh"
    )[1]
    tf_stats.loc[:, "log_fold_change"] = np.log2(
        tf_stats.loc[:, group_name1] / tf_stats.loc[:, group_name2]
    )
    tf_stats.loc[:, "a"] = (1 / 2.0) * np.log2(
        tf_stats.loc[:, group_name1] * tf_stats.loc[:, group_name2]
    )

    # annotate TF ids with names
    annot = pd.read_csv(
        motifs_mapping, sep="\t", header=None, names=["tf", "jaspar_id", "tf_name"]
    ).set_index("tf")
    tf_stats = tf_stats.join(annot).set_index("tf_name")

    # save summary
    tf_stats.to_csv(
        os.path.join(diff_dir, "tf_differential_binding.{}.csv".format(comparison_name))
    )

    # Scatter
    fig, axis = plt.subplots(1, figsize=(4, 4))
    axis.scatter(
        tf_stats.loc[:, "group1_log_interactions"],
        tf_stats.loc[:, "group2_log_interactions"],
        alpha=0.5,
        rasterized=True,
    )
    add_xy_line(axis)
    axis.set_xlabel("{} interactions (log)".format(group_name1))
    axis.set_ylabel("{} interactions (log)".format(group_name2))
    sns.despine(fig)
    fig.savefig(
        os.path.join(
            diff_dir,
            "tf_differential_binding.{}.scatter.log_interactions.svg".format(
                comparison_name
            ),
        ),
        bbox_inches="tight",
        dpi=300,
    )

    fig, axis = plt.subplots(1, figsize=(4, 4))
    axis.scatter(
        tf_stats.loc[:, group_name1],
        tf_stats.loc[:, group_name2],
        alpha=0.5,
        rasterized=True,
    )
    add_xy_line(axis)
    axis.set_xlabel("{} interactions mean".format(group_name1))
    axis.set_ylabel("{} interactions mean".format(group_name2))
    sns.despine(fig)
    fig.savefig(
        os.path.join(
            diff_dir,
            "tf_differential_binding.{}.scatter.mean_interactions.svg".format(
                comparison_name
            ),
        ),
        bbox_inches="tight",
        dpi=300,
    )

    # MA
    fig, axis = plt.subplots(1, figsize=(4, 4))
    axis.scatter(
        tf_stats.loc[:, "a"],
        tf_stats.loc[:, "log_fold_change"],
        alpha=0.5,
        rasterized=True,
    )
    axis.axhline(0, linestyle="--", alpha=0.5, zorder=0)
    axis.set_xlabel("Intensity (A)")
    axis.set_ylabel("Log2 fold change ({} / {})".format(group_name1, group_name2))
    sns.despine(fig)
    fig.savefig(
        os.path.join(
            diff_dir, "tf_differential_binding.{}.ma.svg".format(comparison_name)
        ),
        bbox_inches="tight",
        dpi=300,
    )

    # Volcano
    fig, axis = plt.subplots(1, figsize=(4, 4))
    axis.scatter(
        tf_stats.loc[:, "log_fold_change"],
        -np.log(tf_stats.loc[:, "p_value"]),
        alpha=0.5,
        rasterized=True,
    )
    axis.axvline(0, linestyle="--", alpha=0.5, zorder=0)
    axis.set_xlabel("Log2 fold change ({} / {})".format(group_name1, group_name2))
    axis.set_ylabel("-log p-value")
    sns.despine(fig)
    fig.savefig(
        os.path.join(
            diff_dir, "tf_differential_binding.{}.volcano.svg".format(comparison_name)
        ),
        bbox_inches="tight",
        dpi=300,
    )
