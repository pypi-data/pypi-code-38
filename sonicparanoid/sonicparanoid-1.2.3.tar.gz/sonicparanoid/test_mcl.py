"""Run the test functions for the mcl.py module."""
from typing import Dict, List
import os
import sys
import numpy as np
# import Cython module for remapping headers
from sonicparanoid import mcl_c



def test_concatenate_files(debug: bool=True):
    """Test calculation of offsets for indexes in matrixes"""
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir = os.path.join(testRoot, "output/")
    outDir = os.path.join(testRoot, "output/")
    f1 = os.path.join(inDir, "g1.txt")
    f2 = os.path.join(inDir, "g2.txt")
    f3 = os.path.join(inDir, "g3.txt")
    f4 = os.path.join(inDir, "g4.txt")
    # compute the offsets
    mcl_c.concatenate_files([f1, f2, f3, f4], outPath=outDir, removeProcessed=False, chunkSize=10, debug=debug)



def test_remap_mcl_groups(debug: bool=True):
    """Test mapping of MCL to SonicParanoid groups"""
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    outDir = os.path.join(testRoot, "output/")
    inDir = os.path.join(outDir, "mcl_graphs/")
    threads: int = 2
    mclRawClstrs = os.path.join(inDir, "mcl_groups_raw.txt")
    outPath = os.path.join(inDir, "remapped_groups.tsv")
    #sys.exit("DEBUG :: test_run_mcl")
    mcl_c.remap_mcl_groups(mclGrps=mclRawClstrs, outPath=outPath, runDir=outDir, debug=debug)



def test_run_mcl(debug: bool=True):
    """Test creation of MCL matrix"""
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    outDir = os.path.join(testRoot, "output/")
    inDir = os.path.join(outDir, "mcl_graphs/")
    threads: int = 2
    mclGraphPath = os.path.join(inDir, "mcl_graph.txt")
    mclOutPath = os.path.join(inDir, "mcl_graph_out.txt")
    #sys.exit("DEBUG :: test_run_mcl")
    mcl_c.run_mcl(mclGraph=mclGraphPath, outPath=mclOutPath, threads=threads, removeInput=False, debug=debug)



def test_write_mcl_matrix(debug: bool=True):
    """Test execution of MCL"""
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir = os.path.join(testRoot, "output/")
    outDir = os.path.join(testRoot, "output/")
    threads: int = 1
    spArray = np.array(np.arange(start=1, stop=5, step=1), dtype=np.uint16)
    emptyArray = np.array(np.arange(start=1, stop=1, step=1), dtype=np.uint16)
    removeProcessed = True
    #sys.exit("DEBUG :: test_write_mcl_matrix")
    mcl_c.write_mcl_matrix(spArray, spSkipArray=emptyArray, runDir=outDir, mtxDir=outDir, threads=threads, removeProcessed=removeProcessed, debug=debug)



def main() -> int:
    debug: bool = False
    # print module info
    mcl_c.info()

    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir: str = os.path.join(testRoot, 'ortholog_tables/')
    outDir: str = os.path.join(testRoot, 'output/')

    if debug:
        print('Test directory:\t{:s}'.format(testRoot))
        print('Test input dir:\t{:s}'.format(inDir))
        print('Test output dir:\t{:s}'.format(outDir))

    # concatenate files
    #test_concatenate_files(debug=debug)
    # test creation of MCL graph
    #test_write_mcl_matrix(debug=debug)
    # test mcl run
    #test_run_mcl(debug=debug)
    # test remap MCL clusters
    test_remap_mcl_groups(debug=debug)


    return 0

if __name__ == "__main__":
    main()
