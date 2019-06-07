"""Run the test functions for the graph.py module."""
import graph
from typing import Dict, List
import os
import sys
import numpy as np
# import Cython module for graph and matrixes creation
from sonicparanoid import graph_c



def test_compute_offsets(debug: bool=True):
    """Test calculation of offsets for indexes in matrixes"""
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir = os.path.join(testRoot, "output/")
    outDir = os.path.join(testRoot, "output/")
    protCntPcklPath = os.path.join(inDir, "protein_counts.pckl")
    # compute the offsets
    offSetDict, sizesDict = graph_c.compute_offsets(protCntPcklPath, debug=debug)



def test_dump_ortho_adjacency(debug: bool=True):
    """Test the creation of adjacency dictionary for ortholog relations"""
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir = os.path.join(testRoot, "output/")
    outDir = os.path.join(testRoot, "output/")
    #inTbl = os.path.join(inDir, "3-4.npz")
    inTbl = os.path.join(inDir, "2-3.npz")

    # compute the adjacency dictionary from the matrix
    graph_c.dump_ortho_adjacency(mtxPath=inTbl, outDir=outDir, dumpGraph=True, debug=debug)



def test_pairwise_tbl2tpl_dict(debug=False) -> None:
    """Test the remapping of FASTA headers."""
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir = os.path.join(testRoot, "ortholog_tables/")
    outDir = os.path.join(testRoot, "output/")

    #inTbl = os.path.join(inDir, "table.1-2") # ~970 clusters [bacteria]
    #inTbl = os.path.join(inDir, "table.1-3") # ~690 clusters [bacteria]
    #inTbl = os.path.join(inDir, "table.2-3") # ~700 clusters [bacteria]

    #inTbl = os.path.join(inDir, "table.1-2") # >3000 clusters
    #inTbl = os.path.join(inDir, "table.1-3") # ~1600 clusters
    inTbl = os.path.join(inDir, "table.2-3") # >1500 clusters

    # dictionary with sizes for big genomes test
    sizesBig = {1:28394, 2:33502, 3:50189}
    sizesSmall = {1:3085, 2:4406, 3:1852}
    # get the sizes based on the species names
    # extract the species names
    small: bool = False
    spA, spB = os.path.basename(inTbl).split(".", 1)[-1].split("-", 1)
    spA = int(spA)
    spB = int(spB)

    ''' extract the matrices
    if small:
        #graph_c.create_matrix_from_orthotbl(inTbl, outDir, aSize=sizesSmall[spA], bSize=sizesSmall[spB], storeDgraph=False, debug=debug)
        #graph_c.pairwise_tbl2tpl_dict(inTbl, outDir, aSize=sizesSmall[spA], bSize=sizesSmall[spB], debug=debug)
    else:
        #graph_c.create_matrix_from_orthotbl(inTbl, outDir, aSize=sizesBig[spA], bSize=sizesBig[spB], storeDgraph=False, debug=debug)
        #graph_c.pairwise_tbl2tpl_dict(inTbl, outDir, aSize=sizesBig[spA], bSize=sizesBig[spB], debug=debug)
    '''

    # extract the combinations for a given species
    combMtxPath = os.path.join(outDir, "combination_mtx.npz")
    graph_c.merge_inparalog_matrixes(1, outDir=outDir, combMtxPath=combMtxPath, debug=debug)
    graph_c.merge_inparalog_matrixes(2, outDir=outDir, combMtxPath=combMtxPath, debug=debug)
    graph_c.merge_inparalog_matrixes(3, outDir=outDir, combMtxPath=combMtxPath, debug=debug)
    graph_c.merge_inparalog_matrixes(4, outDir=outDir, combMtxPath=combMtxPath, debug=debug)



def test_write_per_species_mcl_graph(debug: bool=True):
    """Test the creation of MCL graph related to a single species"""
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir = os.path.join(testRoot, "output/")
    outDir = os.path.join(testRoot, "output/")
    mtxPath = os.path.join(inDir, "combination_mtx.npz")
    protCntPcklPath = os.path.join(inDir, "protein_counts.pckl")

    # write the MCL graph for a given species
    graph_c.write_per_species_mcl_graph(sp=1, protCntPckl=protCntPcklPath, runDir=inDir, outDir=outDir, combMtxPath=mtxPath, debug=debug)
    graph_c.write_per_species_mcl_graph(sp=2, protCntPckl=protCntPcklPath, runDir=inDir, outDir=outDir, combMtxPath=mtxPath, debug=debug)
    graph_c.write_per_species_mcl_graph(sp=3, protCntPckl=protCntPcklPath, runDir=inDir, outDir=outDir, combMtxPath=mtxPath, debug=debug)
    graph_c.write_per_species_mcl_graph(sp=4, protCntPckl=protCntPcklPath, runDir=inDir, outDir=outDir, combMtxPath=mtxPath, debug=debug)



def test_write_per_species_mcl_graph_parallel(debug: bool=True):
    """Test parallel creation of MCL sub-graphs"""
    # get dir with test data
    threads: int = 4
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir = os.path.join(testRoot, "output/")
    outDir = os.path.join(testRoot, "output/")
    protCntPcklPath = os.path.join(inDir, "protein_counts.pckl")
    # compute the offsets
    mclSpGraphDict = graph_c.write_per_species_mcl_graph_parallel(np.arange(start=1, stop=5, step=1, dtype=np.uint16), runDir=inDir, outDir=outDir, threads=4, debug=debug)
    if debug:
        for sp, mclPath in mclSpGraphDict.items():
            print(sp, mclPath)



def main() -> int:
    debug: bool = True
    threads: int = 1
    # print module info
    graph_c.info()

    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir: str = os.path.join(testRoot, 'ortholog_tables/')
    outDir: str = os.path.join(testRoot, 'output/')

    if debug:
        print('Test directory:\t{:s}'.format(testRoot))
        print('Test input dir:\t{:s}'.format(inDir))
        print('Test output dir:\t{:s}'.format(outDir))

    # compute offsets
    #test_compute_offsets(debug=debug)

    # remap a single pair
    #test_pairwise_tbl2tpl_dict(debug=debug)

    # compute adjacency from orthology matrix
    #test_dump_ortho_adjacency(debug=debug)
    # write MCL graph for a given species
    #test_write_per_species_mcl_graph(debug=debug)
    # write MCL graph for a given species in parallel
    #test_write_per_species_mcl_graph_parallel(debug=debug)


    return 0

if __name__ == "__main__":
    main()
