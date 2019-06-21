from __future__ import print_function
import argparse
import os
import re
import sys
import textwrap

import basic_data_analysis
import report


VFDB_PATH=os.path.join(sys.path[0], "VFDB_setA_nt.v2.fas")

# ---- 2a Nanopore-only Assembly ----

# Step1: Canu assembly
def canu_assembly(fq_file, genome_size, outdir, prefix='canu_assembly', corrected_error_rate=0.144, minReadLength=1000, minOverlapLength=500):
    try:
        shell_path = os.path.join(outdir, '2-1.canu_assembly.sh')
        outdir = os.path.join(outdir, 'canu_assembly')
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

        with open(shell_path, 'w') as f:
            f.write('canu -p {} -d {} genomesize={} correctedErrorRate={} useGrid=false -nanopore-raw {} minReadLength={} minOverlapLength={}\n'.format(prefix, outdir, genome_size, corrected_error_rate, fq_file, minReadLength, minOverlapLength))

        print('\n---- (2) Start Nanopore-only Assembly ----\n\n---- Step2-1: Canu assembly ----')
        os.system('sh {}'.format(shell_path))
    except Exception as e:
        raise e


# Step2b: Polishing (Racon)
def polish_racon(fa_file, fq_file, outdir, thread=16):
    try:
        shell_path = os.path.join(outdir, '2-2.polish_racon.sh')
        old_outdir = outdir
        outdir = os.path.join(outdir, 'racon_result')
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        with open(shell_path, 'w') as f:
            # bwa
            bam_path = os.path.join(outdir, 'reads.sorted.bam')
            sam_path = re.sub('.bam', '.sam', bam_path)
            tmp_fa_path = os.path.join(outdir, 'racon_tmp.fa')
            final_Fa_path = os.path.join(outdir, 'racon_polished.fa')

            f.write('bwa index {}\n'.format(fa_file))
            f.write('bwa mem -x ont2d -t {} {} {} | samtools sort -o {} -T reads.tmp -\n'.format(thread, fa_file, fq_file, bam_path))
            f.write('samtools view -h {} > {}\n'.format(bam_path, sam_path))

            # racon consensus
            f.write('racon {} {} {} -t {} > {} \n'.format(fq_file, sam_path, fa_file, thread, tmp_fa_path))
            f.write('grep -v "racon" {} | dos2unix > {}\n'.format(tmp_fa_path, final_Fa_path))
            f.write('cp {} {}/assembly.fasta\n'.format(final_Fa_path, old_outdir))
            f.write('rm {}\n'.format(tmp_fa_path))

        print('---- Step2-2: Polishing using Racon ----')
        os.system('sh {}'.format(shell_path))
    except Exception as e:
        raise e

# ---- 2b Hybrid Assembly ----

# Step1: Hybrid assembly (Unicycler)
def unicycler_hybrid_assembly(fq_file, short_r1, short_r2, outdir, mode='normal'):
    try:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        shell_path = os.path.join(outdir, '2-1.unicycler_hybrid_assembly.sh')
        with open(shell_path, 'w') as f:
            f.write('unicycler -1 {} -2 {} -l {} --mode {} -o {}\n'.format(short_r1, short_r2, fq_file, mode, outdir))

        print('\n---- (2) Start Nanopore-NGS Hybrid Assembly ----\n\n---- Step2-1: Unicycler Hybrid Assembly ----')
        os.system('sh {}'.format(shell_path))
    except Exception as e:
        raise e


def assembly_one(nanopore_fq_file, strain_info, outdir, thread=16, genomesize=None, minReadLength=1000, minOverlapLength=500):
    for key in strain_info.keys():
        if len(strain_info[key]) == 2:
            if genomesize is None:
                print('Error: parameter "genomesize" is required when using canu software for long-read-only assembly.\n')
                sys.exit(-1)

            canu_assembly_dir = os.path.join(outdir, strain_info[key][1])
            canu_assembly(nanopore_fq_file, genomesize, outdir=canu_assembly_dir, minReadLength=minReadLength, minOverlapLength=minOverlapLength)

            polish_racon(fa_file='{}/*.contigs.fasta'.format(canu_assembly_dir), fq_file=nanopore_fq_file, outdir=outdir, thread=thread)
        elif len(strain_info[key]) == 4:
            if os.path.exists(strain_info[key][2]) and os.path.exists(strain_info[key][3]):
                unicycler_hybrid_assembly(nanopore_fq_file, strain_info[key][2], strain_info[key][3], outdir)
            else:
                print('Error: please check the Illuminia fastq path: {} or {}'.format(strain_info[key][2], strain_info[key][3]))
                sys.exit(-1)


def assembly_all(nanopore_fq_path, strain_info, outdir, thread=16, genomesize=None, minReadLength=1000, minOverlapLength=500):
    for key in strain_info.keys():
        nanopore_fq_file = os.path.join(nanopore_fq_path, 'filtered_trimmed_{}.fastq.gz'.format(strain_info[key][1]))
        if len(strain_info[key]) == 2:
            if genomesize is None:
                print('Error: parameter "genomesize" is required when using canu software for long-read-only assembly.\n')
                sys.exit(-1)

            canu_assembly_dir = os.path.join(outdir, strain_info[key][1])
            canu_assembly(nanopore_fq_file, genomesize, outdir=canu_assembly_dir, minReadLength=minReadLength, minOverlapLength=minOverlapLength)

            polish_racon(fa_file='{}/*.contigs.fasta'.format(os.path.join(canu_assembly_dir, 'canu_assembly')), fq_file=nanopore_fq_file, outdir=canu_assembly_dir, thread=thread)
        elif len(strain_info[key]) == 4:
            if os.path.exists(strain_info[key][2]) and os.path.exists(strain_info[key][3]):
                unicycler_hybrid_assembly(nanopore_fq_file, strain_info[key][2], strain_info[key][3], os.path.join(outdir, strain_info[key][1]))
            else:
                print('Error: please check the Illuminia fastq path: {} or {}'.format(strain_info[key][2], strain_info[key][3]))
                sys.exit(-1)


# ---- 3 Data Analysis after assembly ----

# Step1: Genomic Anotation
def prokka_annotation(fasta_file, prefix, outdir):
    outdir = os.path.join(outdir, '03.Prokka', prefix)
    shell_path = os.path.join(outdir, '3-1.prokka.sh')
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    with open(shell_path, 'w') as f:
        f.write('prokka --force -outdir {} --prefix {} {}\n'.format(outdir, prefix, fasta_file))
    os.system('sh {}'.format(shell_path))


# Step2: Circlator Analysis and plot

# Step3: AMR gene Identification
def card_annotation(fasta_file, prefix, outdir):
    outdir = os.path.join(outdir, '04.Resistance_genes', prefix)
    shell_path = os.path.join(outdir, '4-1.rgi.sh')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    with open(shell_path, 'w') as f:
        f.write('rgi main -i {} -o {}/{} --clean'.format(fasta_file, outdir, prefix))
    os.system('sh {}'.format(shell_path))


# Step4: Virulence Factors Identification
def vfdb_annotation(fasta_file, prefix, outdir):
    outdir = os.path.join(outdir, '05.Virulence_genes', prefix)
    shell_path = os.path.join(outdir, '5-1.vfdb.sh')

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    with open(shell_path, 'w') as f:
        f.write('blastn -query {} -db {} -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore staxids stitle qcovs qcovhsp" -out {}/{}.vfdb.m6.out\n'.format(fasta_file, VFDB_PATH, outdir, prefix))
    os.system('sh {}'.format(shell_path))

    # filter vfdb blast result: identity >= 90%, hit_len/total_gene_len >= 90% and qcovs >= 90% 
    out = open('{}/{}.vfdb.xls'.format(outdir, prefix), 'w')
    with open('{}/{}.vfdb.m6.out'.format(outdir, prefix)) as f:
        out.write('Contig\tStart\tEnd\tVFDB ID\tGene Name\tVirulence Factor\tGene Function\tSpecies\tIdentity\tHit Length\n')
        for line in f.readlines():
            t = line.strip().split('\t')
            s = t[-3].split('|')
            sub_len = int((s[3].split('-'))[-1])
            if (float(t[3]) / sub_len >= 0.9) and (float(t[2]) >= 90):
                s[4] = re.sub('ARO:', '', s[4])
                out.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(t[0],t[6],t[7],s[4],s[5],s[6],s[8],s[7],t[2],t[3]))
    out.close()


def annotation(strain_info, outdir):
    for key in strain_info.keys():
        prefix = strain_info[key][1]
        fasta_file = os.path.join(outdir, '02.Assembly', prefix, 'assembly.fasta')

        prokka_annotation(fasta_file, prefix, outdir)
        card_annotation(fasta_file, prefix, outdir)
        vfdb_annotation(fasta_file, prefix, outdir)
