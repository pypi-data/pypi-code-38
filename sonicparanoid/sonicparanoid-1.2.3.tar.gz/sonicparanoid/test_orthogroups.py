#run the main test functions in the group_stats.py module
import orthogroups
from typing import Dict, List
import os
import pickle



def test_compute_groups_stats_no_conflict(debug: bool=True):
    """Test compuation of stats for orthogroups without the conflict column"""
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, "test/")
    outGrpDir: str = os.path.join(testRoot, "output_grp_stats/")
    seqLenDir: str = os.path.join(testRoot, "len_files/")
    grpFile: str = os.path.join(testRoot, "input_groups/ortholog_groups_mcl.tsv")
    # load protein counts
    protCntDict = pickle.load(open(os.path.join(seqLenDir, "protein_counts.pckl"), "rb"))
    # load proteome sizes
    genomeSizesDict = pickle.load(open(os.path.join(seqLenDir, "proteome_sizes.pckl"), "rb"))
    # extract stats
    statFiles = orthogroups.compute_groups_stats_no_conflict(inTbl=grpFile, outDir=outGrpDir, outNameSuffix="mcl_stats_test", seqCnts=protCntDict, proteomeSizes=genomeSizesDict, debug=debug)



def test_create_sql_tables(debug: bool=True):
    """Create SQL tables from ortholog tables"""
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, "test/")
    outDir: str = os.path.join(testRoot, "output/")
    tblsDir: str = os.path.join(testRoot, "input_tables/")
    pairsFile: str = os.path.join(tblsDir, "species_pairs.tsv")
    # Load pairs
    pairsList: List[str]
    with open(pairsFile, "rt") as ifd:
        pairsList = [ln[:-1] for ln in ifd]
    # create the SQL tables
    orthogroups.create_sql_tables(tblsDir, outDir, pairsList, threads=1, debug=debug)



def main() -> int:
    debug: bool = False

    # print module info
    if debug:
        orthogroups.info()

    # compute stats on table without conflict column
    #test_compute_groups_stats_no_conflict(debug=debug)

    # create SQL tables
    test_create_sql_tables(debug=debug)

    return 0

if __name__ == "__main__":
    main()
