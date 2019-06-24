import factory

from decimal import Decimal

from metagenomi.tasks.mapping import Mapping


class MappingFactory(factory.Factory):
    class Meta:
        model = Mapping
    mgid = "PROJ_001_X"
    cmd_run = "snap-aligner paired /scratch/626331aa-094e-4eaf-82e9-b7c9e1abbf11/snap /scratch/626331aa-094e-4eaf-82"
    job_id = factory.Faker('pyint')
    updated = "2018-12-13 05:12:17"
    aligned_mapq_greaterequal_10 = factory.Faker('pyint')
    aligned_mapq_less_10 = factory.Faker('pyint')
    percent_pairs = Decimal(35.97)
    reads_mapped = {
        "fwd": "s3://metagenomi/projects/rey/reads/qc/PREY_SS07_USA_MGQ-read_trim_clean.1.fastq.gz",
        "rev": "s3://metagenomi/projects/rey/reads/qc/PREY_SS07_USA_MGQ-read_trim_clean.2.fastq.gz"
    }
    reads_per_sec = factory.Faker('pyint')
    ref = "s3://metagenomi/projects/rey/assembly/PREY_SS07_USA_MGQ-assm/PREY_SS07_USA_MGQ-assm_contigs_min1000.fa"
    seed_size = factory.Faker('pyint')
    time_in_aligner_seconds = factory.Faker('pyint')
    too_short_or_too_many_NNs = factory.Faker('pyint')
    total_bases = factory.Faker('pyint')
    total_reads = factory.Faker('pyint')
    unaligned = factory.Faker('pyint')
