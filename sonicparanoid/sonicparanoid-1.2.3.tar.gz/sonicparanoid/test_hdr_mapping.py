"""Run the test functions for the hdr_mapping.py module."""
import hdr_mapping as idmapper
from typing import Dict, List
import os
import sys
import pickle
# import Cython module for remapping headers
from sonicparanoid import remap_tables_c as remap



def test_remap_pairwise_relations(debug=False) -> None:
    """Test the remapping of FASTA headers."""
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/remap_test')
    print(testRoot)
    inTbl = os.path.join(testRoot, "table.1-2")
    outTbl = os.path.join(testRoot, "output/1-2")

    # load hdr mapping dictionary
    mappingPicklPath1 = os.path.join(testRoot, "hdr_1.pckl")
    with open(mappingPicklPath1, "rb") as fd:
        old2NewHdrDictA = pickle.load(fd)

    mappingPicklPath2 = os.path.join(testRoot, "hdr_2.pckl")
    with open(mappingPicklPath2, "rb") as fd:
        old2NewHdrDictB = pickle.load(fd)

    remap.remap_pairwise_relations(inTbl, outTbl, old2NewHdrDictA, old2NewHdrDictB, debug=debug)



def test_remap_pairwise_relations_parallel(debug=False) -> None:
    """Test the remapping of FASTA headers for pairwise relations."""
    # cpus to be used
    threads: int = 3
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/remap_test')
    # directory with mapped input files
    inDir: str = os.path.join(testRoot, 'tables_to_be_mapped')
    runDir: str = testRoot
    # perform the remapping
    remap.remap_pairwise_relations_parallel(inDir, runDir=testRoot, threads=threads, debug=debug)



def main() -> int:
    debug: bool = False
    threads: int = 1
    updateNames: bool = True
    # remove tables and alignments for obsolete species
    removeOld: bool = False

    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    inDir: str = os.path.join(testRoot, 'input/')
    inDirMod: str = os.path.join(testRoot, 'input_mod/')
    outDir: str = os.path.join(testRoot, 'output/')
    outUpd: str = os.path.join(testRoot, 'update/')

    if debug:
        print('Test directory:\t{:s}'.format(testRoot))
        print('Test input dir:\t{:s}'.format(inDir))
        print('Test output dir:\t{:s}'.format(outDir))
        print('Test output dir for update:\t{:s}'.format(outUpd))

    '''
    # test the parallel computation of digests
    digestDict, repeatedFiles = idmapper.compute_hash_parallel(inPaths, algo='sha256', bits=256, threads=threads, debug=debug)
    if len(repeatedFiles) > 0:
        print(repeatedFiles)
        sys.stderr.write("\nERROR: the following files are repeated:")
        for tpl in repeatedFiles:
            sys.stderr.write("\n{:s}\t{:s}\n".format(tpl[0], tpl[1]))
        sys.stderr.write("\nPlease remove the repeated files before proceeding.\n")
        sys.exit(-2)

    # write output file with the digests
    digestPath = os.path.join(outDir, "digests.tsv")
    with open(digestPath, "w") as ofd:
        for digest, f in digestDict.items():
            ofd.write("{:s}\t{:s}\n".format(f, digest))

    #for k, v in digestDict.items():
    #    print(k, v)

    # perform the mapping for a single FASTA
    #idmapper.map_hdrs(inFasta=inPaths[2], spId=1, outDir=outDir, debug=debug)
    # perform the mapping FASTA input in parallel
    idmapper.map_hdrs_parallel(inPaths, outDir=outDir, digestDict=digestDict, idMapDict={}, threads=threads, debug=debug)
    #'''

    '''
    # compare digests
    #oldDigestFile = os.path.join(outDir, "digests.tsv")
    oldDigestFile = os.path.join(outDir, "species.tsv")

    toRemove, obsolete, toKeep, toAdd, toReuse, newDigestDict = idmapper.compare_digests(inPaths, oldDigestFile=oldDigestFile, algo='sha256', bits=256, threads=threads, updateNames=updateNames, removeOld=removeOld, debug=debug)

    print("toRemove:\t", toRemove)
    print("obsolete:\t", obsolete)
    print("toKeep:\t", toKeep)
    print("toAdd:\t", toAdd)
    print("toReuse:\t", toReuse)

    oldSpFile = os.path.join(outDir, "species.tsv")

    idmapper.update_run_info(toAdd, toReuse, toKeep, inDir=inDir, outDir=outUpd, digestDict=newDigestDict, oldSpFile=oldSpFile, threads=threads, debug=debug)
    '''

    '''
    oldSpFile = os.path.join(outDir, "species.tsv")

    idmapper.update_run_info(inDir=inDirMod, outDir=outUpd, oldSpFile=oldSpFile, algo='sha256', bits=256, threads=threads, updateNames=updateNames, removeOld=removeOld, debug=debug)
    #'''

    # remap a single pair
    #test_remap_pairwise_relations(debug=debug)
    # remap a set of predictions in parallel
    test_remap_pairwise_relations_parallel(debug=debug)


    return 0

if __name__ == "__main__":
    main()
