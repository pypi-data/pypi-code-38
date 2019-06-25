
import os


def sra_id2geo_id(sra_ids):
    """Query SRA ID from GEO ID"""
    import subprocess

    cmd = "esearch -db sra -query {}"
    cmd += " | efetch -format docsum"
    cmd += " | xtract -pattern DocumentSummary -element Runs"
    cmd += """ |  perl -ne '@mt = ($_ =~ /SRR\\d+/g); print "@mt"'"""

    geo_ids = list()
    for id_ in sra_ids:
        geo_ids.append(subprocess.call(cmd.format(id_).split(" ")).read())
    return


def sra2fastq(input_sra, output_dir):
    cmd = """
\t\tfastq-dump --split-3 --outdir {} {}
    """.format(
        output_dir, input_sra
    )

    return cmd


def fastq2bam(input_fastq, output_bam, sample_name, input_fastq2=None):
    cmd = """
\t\tjava -Xmx4g -jar /cm/shared/apps/picard-tools/1.118/FastqToSam.jar"""
    cmd += " FASTQ={0}".format(input_fastq)
    cmd += " SAMPLE_NAME={0}".format(sample_name)
    if input_fastq2 is not None:
        cmd += " FASTQ2={0}".format(input_fastq2)
    cmd += """ OUTPUT={0}""".format(output_bam)

    return cmd


def download_cram(link, output_dir):
    cmd = """
    cd {}
    wget '{}'
    cd -
    """.format(
        output_dir, link
    )

    return cmd


def cram2bam(input_cram, output_bam):
    cmd = """
    samtools view -b -o {} {}
    """.format(
        output_bam, input_cram
    )

    return cmd


def download_sra(link, output_dir):
    cmd = """
    cd {}
    wget '{}'
    cd -
    """.format(
        output_dir, link
    )

    return cmd


def sra2bam_job(sra_id, base_path):
    import textwrap

    from pypiper import NGSTk

    tk = NGSTk()

    # Slurm header
    job_file = os.path.join(base_path, "%s_sra2bam.sh" % sra_id)
    log_file = os.path.join(base_path, "%s_sra2bam.log" % sra_id)

    cmd = tk.slurm_header("-".join(["sra2bam", sra_id]), log_file, cpus_per_task=2)

    # SRA to FASTQ
    cmd += sra2fastq(os.path.join(base_path, sra_id + ".sra"), base_path)

    # FASTQ to BAM
    cmd += fastq2bam(
        os.path.join(base_path, sra_id + "_1.fastq"),
        os.path.join(base_path, sra_id + ".bam"),
        sra_id,
        os.path.join(base_path, sra_id + "_2.fastq"),
    )

    # Slurm footer
    cmd += tk.slurm_footer() + "\n"

    # Write job to file

    with open(job_file, "w") as handle:
        handle.write(textwrap.dedent(cmd))

    # Submit
    tk.slurm_submit_job(job_file)


def link2bam_job(sample_name, link, base_path):
    import textwrap

    from pypiper import NGSTk

    tk = NGSTk()

    # Slurm header
    job_file = os.path.join(base_path, "%s_link2bam.sh" % sample_name)
    log_file = os.path.join(base_path, "%s_link2bam.log" % sample_name)

    cmd = tk.slurm_header(
        "-".join(["link2bam", sample_name]), log_file, cpus_per_task=2
    )

    # Download CRAM
    cmd += download_cram(link, base_path)

    # CRAM to BAM
    cmd += cram2bam(
        os.path.join(base_path, sample_name + ".cram"),
        os.path.join(base_path, sample_name + ".bam"),
    )

    # Slurm footer
    cmd += tk.slurm_footer() + "\n"

    # Write job to file

    with open(job_file, "w") as handle:
        handle.write(textwrap.dedent(cmd))

    # Submit
    tk.slurm_submit_job(job_file)


def sralink2bam_job(sra_id, base_path):
    import textwrap

    from pypiper import NGSTk
    from ngs_toolkit import _LOGGER

    tk = NGSTk()

    # Slurm header
    job_file = os.path.join(base_path, "%s_sra2bam.sh" % sra_id)
    log_file = os.path.join(base_path, "%s_sra2bam.log" % sra_id)

    cmd = tk.slurm_header("-".join(["sra2bam", sra_id]), log_file, cpus_per_task=2)

    # SRA to FASTQ
    cmd += sra2fastq(sra_id, base_path)

    # FASTQ to BAM
    cmd += fastq2bam(
        os.path.join(base_path, sra_id + "_1.fastq"),
        os.path.join(base_path, sra_id + ".bam"),
        sra_id,
        os.path.join(base_path, sra_id + "_2.fastq"),
    )

    # Slurm footer
    cmd += tk.slurm_footer() + "\n"

    # Write job to file

    with open(job_file, "w") as handle:
        handle.write(textwrap.dedent(cmd))

    # Submit
    tk.slurm_submit_job(job_file)
    _LOGGER.info(job_file)
