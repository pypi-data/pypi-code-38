#!/usr/bin/env python 3
from olctools.accessoryFunctions.accessoryFunctions import make_path
from genemethods.sipprCommon.bowtie import Bowtie2CommandLine, Bowtie2BuildCommandLine
from sipprverse.sippr.method import Method
from Bio.Sequencing.Applications import SamtoolsFaidxCommandline, SamtoolsIndexCommandline, \
    SamtoolsSortCommandline, SamtoolsViewCommandline
from Bio.Blast.Applications import NcbiblastnCommandline
from argparse import ArgumentParser
from subprocess import call
import multiprocessing
from time import time
import psutil
import shutil
import sys
import os

mem = psutil.virtual_memory()
testpath = os.path.abspath(os.path.dirname(__file__))
scriptpath = os.path.join(testpath, '..')
sys.path.append(scriptpath)

__author__ = 'adamkoziol'


def variables():
    v = ArgumentParser()
    v.outputpath = os.path.join(testpath, 'testdata', 'results')
    v.referencefilepath = os.path.join(testpath, 'testdata', 'targets')
    v.miseqpath = os.path.join(testpath, 'testdata')
    v.miseqfolder = 'flowcell'
    v.readlengthforward = '1'
    v.readlengthreverse = '0'
    v.customsamplesheet = os.path.join(v.miseqpath, v.miseqfolder, 'SampleSheet.csv')
    v.copy = True
    v.debug = True
    v.demultiplex = True
    return v


def method_init():
    global var
    var = variables()
    method_obj = Method(var, '', time(), scriptpath)
    return method_obj


method = method_init()


def test_bcl2fastq():
    method.createobjects()
    assert os.path.isfile(os.path.join(var.outputpath, var.miseqfolder, '1_0',
                                       'Undetermined_S0_L001_R1_001.fastq.gz'))


def metadata_update(analysistype):
    """

    :param analysistype:
    :return:
    """
    method.sequencepath = os.path.join(testpath, 'testdata', 'sequences', analysistype)
    method.reportpath = os.path.join(testpath, 'testdata', 'results', 'reports')
    for sample in method.runmetadata.samples:
        sample.name = 'unit_test'
        sample.general.outputdirectory = method.sequencepath
        sample.run.outputdirectory = method.sequencepath
        sample.general.fastqfiles = [os.path.join(method.sequencepath, 'reads.fastq.gz')]
        sample.general.trimmedcorrectedfastqfiles = sample.general.fastqfiles
        sample.general.logout = os.path.join(method.sequencepath, 'logout')
        sample.general.logerr = os.path.join(method.sequencepath, 'logerr')


def test_fastq_bait():
    outfile = os.path.join(var.outputpath, 'bait', 'baited.fastq')
    targetpath = os.path.join(var.referencefilepath, 'bait')
    baitcall = 'bbduk.sh ref={ref} -Xmx5G in={input} threads={cpus} outm={out}'.format(
        ref=os.path.join(targetpath, 'combinedtargets.fasta'),
        input=os.path.join(targetpath, 'genesippr.fastq.gz'),
        cpus=multiprocessing.cpu_count(),
        out=os.path.join(outfile)
    )
    call(baitcall, shell=True)
    size = os.stat(outfile)
    assert size.st_size > 0


def test_reverse_bait():
    outfile = os.path.join(var.outputpath, 'reverse_bait', 'baited_targets.fasta')
    targetpath = os.path.join(var.referencefilepath, 'bait')
    baitcall = 'bbduk.sh -Xmx5G ref={ref} in={input} threads={cpus} outm={out}'.format(
        ref=os.path.join(targetpath, 'genesippr.fastq.gz'),
        input=os.path.join(targetpath, 'combinedtargets.fasta'),
        cpus=multiprocessing.cpu_count(),
        out=os.path.join(outfile)
    )
    call(baitcall, shell=True)
    size = os.stat(outfile)
    assert size.st_size > 0


def test_bowtie2_build():
    # Use bowtie2 wrapper to create index the target file
    targetpath = os.path.join(var.referencefilepath, 'bait')
    bowtie2build = Bowtie2BuildCommandLine(reference=os.path.join(targetpath, 'baitedtargets.fa'),
                                           bt2=os.path.join(targetpath, 'baitedtargets'))

    bowtie2build()
    size = os.stat(os.path.join(targetpath, 'baitedtargets.1.bt2'))
    assert size.st_size > 0


def test_bowtie2_align():
    outpath = os.path.join(var.outputpath, 'bait')
    outfile = os.path.join(outpath, 'map_test_sorted.bam')
    targetpath = os.path.join(var.referencefilepath, 'bait')
    # Use samtools wrapper to set up the bam sorting command
    samsort = SamtoolsSortCommandline(input=outfile,
                                      o=True,
                                      out_prefix="-")
    samtools = [
        # When bowtie2 maps reads to all possible locations rather than choosing a 'best' placement, the
        # SAM header for that read is set to 'secondary alignment', or 256. Please see:
        # http://davetang.org/muse/2014/03/06/understanding-bam-flags/ The script below reads in the stdin
        # and subtracts 256 from headers which include 256
        'python3 {}'.format(scriptpath),
        # Use samtools wrapper to set up the samtools view
        SamtoolsViewCommandline(b=True,
                                S=True,
                                h=True,
                                input_file="-"),
        samsort]
    # Add custom parameters to a dictionary to be used in the bowtie2 alignment wrapper
    indict = {'--very-sensitive-local': True,
              '-U': os.path.join(targetpath, 'genesippr.fastq.gz'),
              '-a': True,
              '--threads': multiprocessing.cpu_count(),
              '--local': True}
    # Create the bowtie2 reference mapping command
    bowtie2align = Bowtie2CommandLine(bt2=os.path.join(targetpath, 'baitedtargets'),
                                      threads=multiprocessing.cpu_count(),
                                      samtools=samtools,
                                      **indict)
    bowtie2align(cwd=outpath)
    size = os.stat(outfile)
    assert size.st_size > 0


def test_index_target():
    targetpath = os.path.join(var.referencefilepath, 'bait')
    target_index = SamtoolsFaidxCommandline(reference=os.path.join(targetpath, 'baitedtargets.fa'))
    target_index()
    size = os.stat(os.path.join(targetpath, 'baitedtargets.fa.fai'))
    assert size.st_size > 0


def test_index_bam():
    targetpath = os.path.join(var.referencefilepath, 'bait')
    bam_index = SamtoolsIndexCommandline(input=os.path.join(targetpath, 'genesippr_sorted.bam'))
    bam_index()
    size = os.stat(os.path.join(targetpath, 'genesippr_sorted.bam.bai'))
    assert size.st_size > 0


def test_subsample():
    targetpath = os.path.join(var.referencefilepath, 'blast')
    outpath = os.path.join(var.outputpath, 'blast')
    make_path(outpath)
    outfile = os.path.join(outpath, 'subsampled_reads.fastq.gz')
    cmd = 'reformat.sh in={input} out={output} samplebasestarget=100000'.format(
        input=os.path.join(targetpath, 'reads.fastq.gz'),
        output=os.path.join(outfile))
    call(cmd, shell=True)
    size = os.stat(outfile)
    assert size.st_size > 0


def test_downsample():
    outpath = os.path.join(var.outputpath, 'blast')
    outfile = os.path.join(outpath, 'subsampled_reads.fastq')
    cmd = 'seqtk sample {input} 1000 > {output}' .format(
        input=os.path.join(outpath, 'subsampled_reads.fastq.gz'),
        output=outfile)
    call(cmd, shell=True)
    size = os.stat(outfile)
    assert size.st_size > 0


def test_fastq_to_fasta():
    outfile = os.path.join(var.outputpath, 'blast', 'subsampled_reads.fasta')
    cmd = 'reformat.sh in={input} out={output}' \
        .format(input=os.path.join(os.path.join(var.outputpath, 'blast', 'subsampled_reads.fastq')),
                output=outfile)
    call(cmd, shell=True)
    size = os.stat(outfile)
    assert size.st_size > 0


def test_make_blastdb():
    targetpath = os.path.join(var.referencefilepath, 'blast')
    command = 'makeblastdb -in {targets} -parse_seqids -max_file_sz 2GB -dbtype nucl -out {output}'.format(
        targets=os.path.join(targetpath, 'baitedtargets.fa'),
        output=os.path.join(targetpath, 'baitedtargets'))
    call(command, shell=True)
    outfile = os.path.join(targetpath, 'baitedtargets.nsi')
    size = os.stat(outfile)
    assert size.st_size > 0


def test_blast():
    targetpath = os.path.join(var.referencefilepath, 'blast')
    outpath = os.path.join(var.outputpath, 'blast')
    outfile = os.path.join(outpath, 'blast_results.csv')
    # Use the NCBI BLASTn command line wrapper module from BioPython to set the parameters of the search
    blastn = NcbiblastnCommandline(query=os.path.join(outpath, 'subsampled_reads.fasta'),
                                   db=os.path.join(targetpath, 'baitedtargets'),
                                   max_target_seqs=1,
                                   num_threads=multiprocessing.cpu_count(),
                                   outfmt="'6 qseqid sseqid positive mismatch gaps "
                                          "evalue bitscore slen length qstart qend qseq sstart send sseq'",
                                   out=outfile)
    blastn()
    size = os.stat(outfile)
    assert size.st_size > 0


def clean_folder(analysistype):
    """

    :param analysistype: the name of the current typing analysis
    """
    try:
        shutil.rmtree(os.path.join(method.sequencepath, analysistype))
    except FileNotFoundError:
        pass
    try:
        os.remove(os.path.join(method.sequencepath, 'logout'))
    except FileNotFoundError:
        pass
    try:
        os.remove(os.path.join(method.sequencepath, 'logerr'))
    except FileNotFoundError:
        pass
    try:
        os.remove(os.path.join(method.sequencepath, 'unit_test_metadata.json'))
    except FileNotFoundError:
        pass


def test_confindr():
    analysistype = 'ConFindr'
    metadata_update(analysistype)
    method.contamination_detection()
    shutil.rmtree(os.path.join(method.sequencepath, 'confindr'))
    for sample in method.runmetadata.samples:
        assert sample.confindr.num_contaminated_snvs == 0


def test_genesippr():
    analysistype = 'genesippr'
    metadata_update(analysistype)
    method.run_genesippr()
    outfile = os.path.join(method.reportpath, '{}.csv'.format(analysistype))
    size = os.stat(outfile)
    clean_folder(analysistype)
    assert size.st_size > 0


def test_sixteens():
    analysistype = 'sixteens_full'
    metadata_update(analysistype)
    method.run_sixteens()
    outfile = os.path.join(method.reportpath, '{}.csv'.format(analysistype))
    size = os.stat(outfile)
    clean_folder(analysistype)
    assert size.st_size > 0


def test_mash():
    analysistype = 'mash'
    metadata_update(analysistype)
    method.run_mash()
    outfile = os.path.join(method.reportpath, '{}.csv'.format(analysistype))
    size = os.stat(outfile)
    clean_folder(analysistype)
    assert size.st_size > 0


def test_gdcs():
    analysistype = 'GDCS'
    metadata_update(analysistype)
    method.run_gdcs()
    outfile = os.path.join(method.reportpath, '{}.csv'.format(analysistype))
    size = os.stat(outfile)
    assert size.st_size > 0
    clean_folder(analysistype)


def test_clear_results():
    shutil.rmtree(var.outputpath)


def test_clear_targets():
    targetpath = os.path.join(var.referencefilepath, 'bait')
    os.remove(os.path.join(targetpath, 'baitedtargets.1.bt2'))
    os.remove(os.path.join(targetpath, 'baitedtargets.2.bt2'))
    os.remove(os.path.join(targetpath, 'baitedtargets.3.bt2'))
    os.remove(os.path.join(targetpath, 'baitedtargets.4.bt2'))
    os.remove(os.path.join(targetpath, 'baitedtargets.rev.1.bt2'))
    os.remove(os.path.join(targetpath, 'baitedtargets.rev.2.bt2'))
    os.remove(os.path.join(targetpath, 'baitedtargets.fa.fai'))
    os.remove(os.path.join(targetpath, 'genesippr_sorted.bam.bai'))


def test_clear_blast():
    targetpath = os.path.join(var.referencefilepath, 'blast')
    os.remove(os.path.join(targetpath, 'baitedtargets.nsq'))
    os.remove(os.path.join(targetpath, 'baitedtargets.nsi'))
    os.remove(os.path.join(targetpath, 'baitedtargets.nsd'))
    os.remove(os.path.join(targetpath, 'baitedtargets.nog'))
    os.remove(os.path.join(targetpath, 'baitedtargets.nni'))
    os.remove(os.path.join(targetpath, 'baitedtargets.nnd'))
    os.remove(os.path.join(targetpath, 'baitedtargets.nin'))
    os.remove(os.path.join(targetpath, 'baitedtargets.nhr'))


def test_clear_kma():
    targetpath = os.path.join(var.referencefilepath, 'ConFindr', 'databases')
    os.remove(os.path.join(targetpath, 'rMLST_combined_kma.index.b'))
    os.remove(os.path.join(targetpath, 'rMLST_combined_kma.length.b'))
    os.remove(os.path.join(targetpath, 'rMLST_combined_kma.name'))
    os.remove(os.path.join(targetpath, 'rMLST_combined_kma.seq.b'))


def test_clear_logs():
    # Use os.walk to find all log files in the subfolders within the reference file path
    for root, folders, files in os.walk(var.referencefilepath):
        for sub_file in files:
            # Only target log files
            if '.log' in sub_file:
                # Remove the file
                os.remove(os.path.join(root, sub_file))
