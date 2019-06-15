#!/bin/python

from ruffus import *
import os
import argparse
import pandas as pd

import linkageMapper
import subprocess

from Bio.Align.Applications import ClustalwCommandline

from linkageMapper.logo import logo


class Options():
    def __init__(self, options):
        self.__dict__.update(options)


@active_if(lambda: options.DoAmplicon)
@subdivide(lambda: options.PrimerFile, formatter(), "*.fasta")
def find_primers(primerFile, outputPath):

    finderOptions = {
        "primerFile": primerFile,
        "outputPath": outputPath,
        "WantedLoci": ""
    }

    return linkageMapper.primerFinder.Execute(Options(finderOptions))


@active_if(lambda: options.DoAlignment)
def run_alignment(filePrefix):
    infile = filePrefix + ".fasta"
    outfile = filePrefix + ".aln"

    aln_cmd = ClustalwCommandline("clustalw2", infile=infile, outfile=outfile)
    stdout, stderr = aln_cmd()

    print(stdout)

    infile = filePrefix + ".aln"
    tree_cmd = ClustalwCommandline("clustalw2", infile=infile, tree=True)
    tree_cmd()


def draw_tree(filePrefix):
    infile = filePrefix + ".ph"
    outfile = filePrefix + "pdf"

    treeOptions = Options({
        "InputFile": infile,
        "OutputFile": outfile
    })

    linkageMapper.DrawGraphics.drawTree.Execute(treeOptions)


def run_meshclust(filePrefix):
    subprocess.run(["meshclust",
                    filePrefix + ".fasta",
                    "--output",
                    filePrefix + ".clst",
                    "--id", "0.999",
                    "--align"])


def detect_mutations(filePrefix):
    infile = filePrefix + ".aln"

    mutationsOptions = Options({
        "InputFile": infile,
        "PlotSubtitle": ""
    })

    linkageMapper.detectMutations.Execute(mutationsOptions)


def matrix_analysis(WorkingDirectory):
    analysisOptions = Options({
        "InputDirectory": WorkingDirectory,
        "updateOnly": False
    })

    linkageMapper.compareHeatmap.Execute(analysisOptions)
    return linkageMapper.matrixAnalysis.Execute(analysisOptions)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", dest="PrimerFile")

    parser.add_argument("--noamplicon", dest="DoAmplicon",
                        action="store_false", default=True)

    parser.add_argument("--noalign", dest="DoAlignment",
                        action="store_false", default=True)

    parser.add_argument("--alnmode", dest="AlignmentMode",
                        default="clustal")

    parser.add_argument("--dir", dest="WorkingDirectory")
    options = parser.parse_args()

    return options


def main():
    options = parse_arguments()

    # -- SELECT WORKING DIRECTORY;
    if options.WorkingDirectory:
        WorkingDirectory = options.WorkingDirectory

    else:
        AnalysisCode = os.path.splitext(options.PrimerFile)[0]
        AnalysisCode = os.path.basename(AnalysisCode)

        WorkingDirectoryBase = "analysisResults"
        if not os.path.isdir(WorkingDirectoryBase):
            os.mkdir(WorkingDirectoryBase)
        WorkingDirectory = os.path.join(WorkingDirectoryBase,
                                        AnalysisCode)

    # -- TEST CLUSTALW2 SETUP;
    try:
        # this is giving problems.. maybe ask on Biopython issues.
        if False:
            test_clustal = ClustalwCommandline("clustalw2")
            stdout, stderr = test_clustal()
            print(stdout)
            print(stderr)
    except Exception as e:
        print(e)
        print("Clustalw2 not found! Aborting...")
        exit(1)

    if not os.path.isdir(WorkingDirectory):
        Path = os.path.split(WorkingDirectory)
        for d, Directory in enumerate(Path):
            subDirectoryPath = os.path.join(*Path[:d+1])
            print(subDirectoryPath)
            if not os.path.isdir(subDirectoryPath):
                print("Creating directory %s." % subDirectoryPath)
                os.mkdir(subDirectoryPath)

    # SHOW BEAUTIFUL ASCII ART;
    print(logo)

    # pipeline using ruffus is wip;
    ruffusMode = False

    # RUN NORMALLY;
    if not ruffusMode:
        if options.DoAmplicon:
            result = find_primers(options.PrimerFile, WorkingDirectory)
            if not result:
                print("Failure to find primers.")
                exit(1)

        AllowedAlignModes = ["clustal"]
        if options.AlignmentMode not in AllowedAlignModes:
            print("Unknown alignment mode %s." % (options.AlignmentMode))
            exit(1)

        MatchedPrimersPath = os.path.join(WorkingDirectory, "MatchedRegions.csv")
        SucessfulLoci = pd.read_csv(MatchedPrimersPath)["LocusName"]

        if options.DoAlignment:
            for locusName in SucessfulLoci:
                filePrefix = os.path.join(WorkingDirectory, "LOCI_" + locusName)
                print("Running alignment for %s..." % locusName)
                run_alignment(filePrefix)
                # draw_tree(filePrefix)
                detect_mutations(filePrefix)
                run_meshclust(filePrefix)

        if matrix_analysis(WorkingDirectory):
            print("Analysis sucesfull.")

    # RUN BY RUFFUS;
    else:
        pipeline_run()


if __name__ == "__main__":
    main()
