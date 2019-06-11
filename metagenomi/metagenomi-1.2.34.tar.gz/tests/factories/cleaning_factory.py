import factory

from metagenomi.tasks.cleaning import (
    Cleaning, AdapterRemoval, ContaminantRemoval, QualityTrimming
)
import tests.factories.providers.models.sequencing_provider
import tests.factories.providers.misc

def bbmap_adapter_removal_cmd():
    in1 = '/scratch/a827/SS_13_DNA_Q.1.fastq.gz'
    out1 = '/scratch/a827/SS_13_DNA_Q.1.fastq.g_trim.fastq.gz'
    in2 = '/scratch/a827/SS_13_DNA_Q.2.fastq.gz'
    out2 = '/scratch/a827/SS_13_DNA_Q.2.fastq.g_trim.fastq.gz'
    ref = '/tmp/bbmap/resources/adapters.fa'
    cmd = f'/tmp/bbmap/bbduk.sh ref={ref} \
        k=23 mink=11 hdist=1 tbo tpe ktrim=r ftm=5 \
        -in1={in1} -out1={out1} -in2={in2} -out2={out2} t=16'
    return(cmd)


def bbmap_contaminant_removal_cmd():
    refa = '/tmp/bbmap/resources/phix174_ill.ref.fa.gz'
    refb = '/tmp/bbmap/resources/sequencing_artifacts.fa.gz'
    in1 = '/scratch/a827/SS_13_DNA_Q.1.fastq.g_trim.fastq.gz'
    out1 = '/scratch/a827/SS_13_DNA_Q.1.fastq.g_trim.fastq.g_trim_clean.fastq.gz'
    in2 = '/scratch/a827/SS_13_DNA_Q.2.fastq.g_trim.fastq.gz'
    out2 = '/scratch/a827/SS_13_DNA_Q.2.fastq.g_trim.fastq.g_trim_clean.fastq.gz'
    cmd = f'/tmp/bbmap/bbduk.sh ref={refa},{refb} k=31 hdist=1 \
        -in1={in1} -out1={out1} -in2={in2} -out2={out2} t=16'
    return(cmd)


def bbmap_quality_trimming_cmd():
    in1 = '/scratch/a827/SS_13_DNA_Q.1.fastq.g_trim.fastq.g_trim_clean.fastq.gz'
    out1 = '/scratch/a827/SS_13_DNA_Q.1.fastq.g_trim.fastq.g_trim_clean.fastq.g_trim_clean_qual.fastq.gz'
    in2 = '/scratch/a827/SS_13_DNA_Q.2.fastq.g_trim.fastq.g_trim_clean.fastq.gz'
    out2 = '/scratch/a827/SS_13_DNA_Q.2.fastq.g_trim.fastq.g_trim_clean.fastq.g_trim_clean_qual.fastq.gz'
    cmd = f'/tmp/bbmap/bbduk.sh qtrim=f trimq=6 \
        -in1={in1} -out1={out1} -in2={in2} -out2={out2} t=16'
    return(cmd)


class AdapterRemovalFactory(factory.Factory):
    class Meta:
        model = AdapterRemoval
    cmd_run = bbmap_adapter_removal_cmd()
    ftrimmed_reads = factory.Faker('pyint')
    ktrimmed_reads = factory.Faker('pyint')
    total_bases = factory.Faker('pyint')
    total_reads = factory.Faker('pyint')
    total_removed_reads = factory.Faker('pyint')
    trimmed_by_overlap_reads = factory.Faker('pyint')

class ContaminantRemovalFactory(factory.Factory):
    class Meta:
        model = ContaminantRemoval
    cmd_run = bbmap_contaminant_removal_cmd()
    contaminants = factory.Faker('pyint')
    total_removed_reads = factory.Faker('pyint')

class QualityTrimmingFactory(factory.Factory):
    class Meta:
        model = QualityTrimming
    cmd_run = bbmap_quality_trimming_cmd()
    total_removed_reads = factory.Faker('pyint')

class CleaningFactory(factory.Factory):
    class Meta:
        model = Cleaning
    mgid = 'CODE_NUM_CNTY'
    cmd_run = 'adapter_removal,contaminant_removal,quality_trimmin'
    job_id = factory.Faker('pyint')
    total_bases = factory.Faker('pyint')
    total_reads = factory.Faker('pyint')
    adapter_removal = factory.SubFactory(AdapterRemovalFactory)
    contaminant_removal = factory.SubFactory(ContaminantRemovalFactory)
    quality_trimming = factory.SubFactory(QualityTrimmingFactory)
