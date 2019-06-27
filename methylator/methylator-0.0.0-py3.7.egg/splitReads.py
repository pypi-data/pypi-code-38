## Title: Group reads based on heterozygous SNPs locations. Each group of reads will be placed in a separate BAM file
## Author: I. Moustakas, i.moustakas@lumc.nl

import click
import pysam
import re
import os
import pandas as pd
from pathlib import Path

from typing import List
from dataclasses import dataclass
from .methylationPattern import methylPatterns

@click.command()
@click.option('--inputpath', type=click.Path(exists=True, readable=True), required=True, help='Directory with CpG and alignment files files')
@click.option('--thr', type=click.FLOAT, required=True, help='Threshold for allele frequency bellow which an allele is ignored')
@click.option('--outpath', type=click.Path(writable=True), required=True, help='Path to place the output')
# @click.option('--cpgfile', required=True, help="CpG file from bismark (CpG_OB_*)")
@click.option('--ampltable', required=True, help="Tab separated file with amplicon locations") ##TODO: specify table format
def topLevel(inputpath, thr, outpath, ampltable):
    inPath = Path(inputpath)
    alignmentFiles = list(inPath.glob("*bam"))

    # Loop over samples, put the per sample output in a dict according to the amplicon
    amplToDF = {}
    for file in alignmentFiles:
        sampleID = sampleName(str(file))
        cpgFile = inputpath + "/CpG_OB_" + sampleID + "_bismark_bt2.sorted.txt.gz"
        df = perSample(file, thr, outpath, cpgFile, ampltable, sampleID)
        for ampl, d in df.items():
            if ampl not in amplToDF:
                amplToDF[ampl] = [d]
            else:
                amplToDF[ampl].append(d)
    # One table per amplicon
    for ampl, d in amplToDF.items():
        pd.concat(d).to_csv("{0}/{1}.tsv".format(outpath, ampl), sep ="\t", header=True)
        pd.concat(d).to_excel("{0}/{1}.xls".format(outpath, ampl))
    # Create an empty file to signal the end of script for snakemake
    Path(outpath + '/methylator.txt').touch()

def perSample(samfile, thr, outpath, cpgfile, ampltable, sampleID):
    """
    Accepts an alignment file, a methylation call file and list of amplicons
    For each amplicon, calculate a table with methylation pattern counts
    :param samfiles:
    :param location:
    :param thr:
    :param outpath:
    :param cpgfile:
    :param ampltable:
    :return: {amplicon => methylation counts DF}
    """

    # Create output directory
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    # Load methylation call data. Forward and reverse strand are in two separate files (OB and OT).
    # Combine them in one df. If file does not exist, create empty DF
    if os.path.isfile(cpgfile):
        methylationOB = pd.read_csv(cpgfile, sep="\t", skiprows=1, header=None, names=["Read", "MethylStatus", "Chr", "Pos", "Zz"])
    else:
        methylationOB = pd.DataFrame(columns=["Read", "MethylStatus", "Chr", "Pos", "Zz"])
    cpgfileOT = cpgfile.replace("CpG_OB_", "CpG_OT_")
    if os.path.isfile(cpgfileOT):
        methylationOT = pd.read_csv(cpgfileOT, sep="\t", skiprows=1, header=None, names=["Read", "MethylStatus", "Chr", "Pos", "Zz"])
        methylation = pd.concat([methylationOB, methylationOT])
    else:
        methylation = methylationOB

    # Read alignment file, create a dict of allele to records list
    samFile = pysam.AlignmentFile(samfile, 'rb')

    amplList = readAmplicon(ampltable)

    ampliconToDF = {}

    # Loop over the list of amplicons
    for amplicon in amplList:
        start = amplicon.start
        end = amplicon.end
        methylationThr = amplicon.methylThr
        ampliconName = amplicon.name
        chrom = amplicon.chrom
        numberCGs = amplicon.nr_cg
        snpCoords = amplicon.snps_coord.split(";")

        # Extract the methylation table that concerns this amplicon region
        ampliconMeth = methylation.loc[(methylation["Chr"] == chrom) & (methylation["Pos"] >= start) & (methylation["Pos"] <= end)]

        index = []
        listSeries = []
        # Each amplicon region might have more than one SNPs
        for snpCoord in snpCoords:
            snpCoord = int(snpCoord)-1  # pysam uses zero-based indexing
            # Create a dict of allele to records list from the alignment file
            alleleToReadRecord = baseToReads(samFile, chrom, snpCoord)
            # returns a flattened list
            allRecords = [record for listRecords in alleleToReadRecord.values() for record in listRecords]
            allRecordCounts = len(allRecords)

            # Remove alleles with read count below threshold
            recordsToKeep = {}
            for allele, records in alleleToReadRecord.items():
                if len(records) > float(thr) * allRecordCounts:
                    recordsToKeep[allele] = records

            # Add All Alleles with allRecords to dict
            recordsToKeep["Total"] = allRecords

            counts = phaseReads(recordsToKeep, ampliconMeth, outpath, methylationThr, numberCGs, sampleID, chrom, snpCoord)
            for allele, series in counts.items():
                index.append((sampleID, ampliconName, "{0}:{1}".format(chrom, snpCoord+1), allele))
                listSeries.append(series)
        index = pd.MultiIndex.from_tuples(index, names=["Sample", "Amplicon", "SNP_coord", "Allele"])
        df = pd.DataFrame(listSeries, index = index)
        ampliconToDF[ampliconName] = df
    return(ampliconToDF)


def baseToReads(samFile, chr, pos):
    """
    For all possible alleles in a genomic position, return a dictionary {allele => [Read IDs with this allele]}
    :param samFile:
    :param chr:
    :param pos:
    :return: dictionary {allele => [Read IDs with this allele]}
    """
    pileups = samFile.pileup(chr, pos, max_depth=30000)

    baseToReadRecord = {}
    for pileupCol in pileups:
        for pileupRead in pileupCol.pileups:
            if not pileupRead.is_del and not pileupRead.is_refskip and pileupCol.pos == pos:
                aln = pileupRead.alignment
                base = aln.query_sequence[pileupRead.query_position]
                if base not in baseToReadRecord:
                    baseToReadRecord[base] = [aln.query_name]
                else:
                    baseToReadRecord[base].append(aln.query_name)
    return(baseToReadRecord)


# A class to hold info about an amplicon

@dataclass
class Amplicon:
    name: str
    chrom: str
    start: int
    end: int
    strand: str
    nr_cg: int
    methylThr: int
    snps_coord: str

def readAmplicon(ampltable) -> List[Amplicon]:
    """
    Read amplicon table and get list of amplicon objects
    :param ampltable:
    :param methylation:
    :return:
    """
    ## Load the amplicon table
    amplicons = pd.read_csv(ampltable, sep="\t")

    amplList = []
    for index, row in amplicons.iterrows():
        name = row["Name"]
        chrom = row["Chr"]
        start = row["start"]
        end = row["end"]
        strand = row["strand"]
        nr_cg = row["nr_CG"]
        methylThr = row["methylThr"]
        snp_coord = str(row["snps_coord"])
        # row: List[things]
        # amplication = Amplicon(*row)  <- Amplicon(row[0], row[1] .... )
        # row: Dict[str, things]
        # amplicon = Amplicon(**row) <- Amplicon(key=row[key], key2=row[key2]...)
        amplicon = Amplicon(name, chrom, start, end, strand, nr_cg, methylThr, snp_coord)
        amplList.append(amplicon)
    return amplList

def phaseReads(recordsToKeep, methylation, outpath, methylThr, numberCGs, sampleID, chrom, snpCoord):
    """
    Provided a heterozygous SNP is present, phase reads according to SNP.
    Apply methylPatterns on split dataset
    :param outpath:
    :param cpgfile:
    :return: {allele => countsDF}
    """

    alleleToCounts = {}
    ## Loop over alleles, phase reads
    for allele, records in recordsToKeep.items():
        methylationPhased = methylation[methylation["Read"].isin(records)]
        countsPerClass = methylPatterns(methylationPhased, outpath, methylThr, numberCGs, sampleID, allele, chrom, snpCoord)
        alleleToCounts[allele] = countsPerClass

    return alleleToCounts

def sampleName(file):
    """
    Get sample name out of the bismark file name.
    Expects full path of a CpG file created by bismark
    """
    # str_search = re.search('.+/CpG_OB_(.+)_bismark.+', file)
    str_search = re.search('.+/(.+)_bismark_bt2\.sorted\.bam', file)
    sampleName = str_search.group(1)
    return sampleName

if __name__ == '__main__':
    topLevel()


## pd.concat([list(a.values())[0], list(b.values())[0]])