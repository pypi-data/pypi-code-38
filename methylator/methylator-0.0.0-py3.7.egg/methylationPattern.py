import pandas as pd
from pathlib import Path


def methylPatterns(methylation, outpath, methylThr, numberCGs, sampleID, allele, chrom, snpCoord):
    """
    Separate reads in three categories: Methylated , unmethylated, partially methylated according to the number
    of CpGs that are methyalted
    :param methylation: pandas df with columns "Read", "MethylStatus", "Chr", "Pos", "Zz". This is the output of bismark_methylation_extractor
    :param outpath: path to save the table with the methylation patterns
    :param methylThr: an integer to separate a
    :return: A pandas.Series with read counts and percentages for the three methylation categories
    """

    # if records for amplicon
    if len(methylation.index)>0:

        # Get all methylation positions in the amplicon
        methPosCounts = methylation["Pos"].value_counts()
        readPosMethyl = methylation[["Read", "Pos", "MethylStatus"]]
        readCount = len(readPosMethyl["Read"].unique())

        # Keep only meth posistions with counts in at least 1% of all reads in amplicon
        posToKeep = methPosCounts[methPosCounts > readCount*0.01].index
        # posToKeepCount = len(posToKeep)
        readPosMethyl = readPosMethyl[readPosMethyl["Pos"].isin(posToKeep)]

        # reshape the DF
        readPosMethyl.set_index(["Read", "Pos"], inplace=True)
        methylPattern = readPosMethyl.unstack()
        methylPattern.reset_index(inplace=True)
        methylPattern = methylPattern.drop(labels = "Read", axis = 1)
        methylPattern.columns = methylPattern.columns.droplevel()

        # Fill in NaN with asteriscs (NaN in the case methylation site not on all reads)
        methylPattern = methylPattern.fillna("*")
        # Collapses identical methylation patterns together and adds  column with the count for each pattern
        collapsedCountedPatterns = methylPattern.groupby(methylPattern.columns.tolist()).size().reset_index().rename(columns={0:'counts'})
        # totalMethPos = methylPattern.shape[1]

        # Count the per read methylation states and save in a separate column
        collapsedCountedPatterns["methStatesCount"] = countStates(collapsedCountedPatterns, "+")
        collapsedCountedPatterns["unmethStatesCount"] = countStates(collapsedCountedPatterns, "-")
        collapsedCountedPatterns["notApplCount"] = countStates(collapsedCountedPatterns, "*")

        # Save in table
        p = Path(outpath + "/perSample/")
        p.mkdir( exist_ok=True)
        collapsedCountedPatterns.to_csv("{0}/perSample/{1}_{2}_{3}.{4}.tsv".format(outpath, sampleID, chrom, snpCoord, allele), sep ="\t", header=True)

        # Splits the methylation patterns in 3 categories:
        # Mostly methylated (meth >= totalMethPos-methylThr)
        # Mostly unMethylated (meth <= methylThr)
        # Else patriallyMeth
        # Count reads in each category
        # Returns a Series
        methylated = sum(collapsedCountedPatterns[collapsedCountedPatterns["methStatesCount"] >= (numberCGs - methylThr)]["counts"])
        unmethylated = sum(collapsedCountedPatterns[collapsedCountedPatterns["methStatesCount"] <= methylThr]["counts"])
        patriallyMeth = readCount - methylated - unmethylated
        methylPcnt = methylated / readCount
        unmethylPcnt = unmethylated / readCount
        partialPcnt = patriallyMeth / readCount
        countMethClass = pd.Series(
            [readCount, methylated, methylPcnt, unmethylated, unmethylPcnt, patriallyMeth, partialPcnt],
            index=["totalReads",
                   "methylated_reads(mGCs>={})".format(numberCGs - methylThr),
                   "methylPcnt",
                   "unmethylated_reads(mGCs<={})".format(methylThr),
                   "unmethylPcnt",
                   "patriallyMeth_reads",
                   "partialPcnt"])
    else:
        countMethClass = pd.Series(
            [0, 0, 0, 0, 0, 0, 0],
            index=["totalReads",
                   "methylated_reads(mGCs>={})".format(numberCGs - methylThr),
                   "methylPcnt",
                   "unmethylated_reads(mGCs<={})".format(methylThr),
                   "unmethylPcnt",
                   "patriallyMeth_reads",
                   "partialPcnt"])

    return countMethClass

def countStates(methMatrix, methState):
    """
    Count the occurence of strings (denoting methylations states) in the table per pattern (row):
    Returns a Series with length equal to matrix rows
    """
    patterns = methMatrix.drop(labels="counts", axis=1)
    counts = patterns.apply(func = lambda x: sum(x == methState), axis = 1)
    return counts


