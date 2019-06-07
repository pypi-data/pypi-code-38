"""This module contains functions for the detection of orthologs using software like inparanoid."""
import sys
import os
import time
import subprocess
import itertools
from collections import OrderedDict
from collections import deque
import shutil
import multiprocessing as mp
import numpy as np
from scipy.sparse import dok_matrix, csr_matrix, triu, save_npz

# Internal modules
from sonicparanoid import sys_tools as systools
from sonicparanoid import seq_tools as seqtools
# import the module for orthology prediction
from sonicparanoid import inpyranoid
from sonicparanoid import workers
from sonicparanoid import hdr_mapping as idmapper
from sonicparanoid import graph_c as graph
from sonicparanoid import mcl_c as mcl
from sonicparanoid import orthogroups



__module_name__ = 'Ortholog detection'
__source__ = 'ortholog_detection.py'
__author__ = 'Salvatore Cosentino'
#__copyright__ = ''
__license__ = 'GPL'
__version__ = '2.3'
__maintainer__ = 'Cosentino Salvatore'
__email__ = 'salvo981@gmail.com'


#root path for files
pySrcDir = os.path.dirname(os.path.abspath(__file__))
pySrcDir += '/'
blast_parser = '%sparser.py'%pySrcDir

# Config file paths
cfgPath = os.path.join(pySrcDir, 'config.json')
# directory in which the mmseqs binaries are located
mmseqsPath = 'mmseqs'



def info():
    """This module contains functions for the detection of orthologs."""
    print('MODULE NAME:\t%s'%__module_name__)
    print('SOURCE FILE NAME:\t%s'%__source__)
    print('MODULE VERSION:\t%s'%__version__)
    print('LICENSE:\t%s'%__license__)
    print('AUTHOR:\t%s'%__author__)
    print('EMAIL:\t%s'%__email__)



def check_hsp_overlap(hsp1, hsp2, debug=True):
    """Check if there is overlap among the 2 hsp."""
    if debug:
        print('\ncheck_hsp_overlap :: START')
        print('hsp1:\t%s'%str(hsp1))
        print('hsp2:\t%s'%str(hsp2))
    #print('Current HSP:\t%d\t%d'%(qstart, qend))
    if hsp1[0] == hsp2[0]: #then there is an overlap for sure
        #print('Overlap found SAME START!')
        #print('hsp1:\t%s'%str(hsp1))
        #print('hsp2:\t%s'%str(hsp2))
        return True
    #position the 2 hsp first
    lxHsp = dxHsp = None
    if hsp1[0] < hsp2[0]:
        lxHsp = (hsp1[0], hsp1[1])
        dxHsp = (hsp2[0], hsp2[1])
    else: #tmpS < qstart
        lxHsp = (hsp2[0], hsp2[1])
        dxHsp = (hsp1[0], hsp1[1])
    lenLxHsp = lxHsp[1] - lxHsp[0] + 1
    lenDxHsp = dxHsp[1] - dxHsp[0] + 1
    #find the shortest HSP
    shortestHsp = min(lenLxHsp, lenDxHsp)
    #calculate the overlap
    overlap = round((dxHsp[0] - lxHsp[1] - 1.) / float(shortestHsp), 4)
    #print('Overlap score:\t%s\n'%str(overlap))
    if overlap <= -0.05:
        #print('Overlap found!')
        return True
    return False



def check_2species_run(rootDir, sp1, sp2, sharedDir, debug=False):
    """Check the integrity of a 2-species ortholog search."""
    if debug:
        print('check_2species_run :: START')
        print('Root directory:\t%s'%rootDir)
        print('Species A:\t%s'%sp1)
        print('Species B:\t%s'%sp2)
        print('Shared directory:\t%s'%sharedDir)
    #path to run doirectory
    pair = '%s-%s'%(sp1, sp2)
    runDir = '%s%s/'%(rootDir, pair)
    if not os.path.isdir(runDir):
        sys.stderr.write('ERROR: the directory containing the run\n%s\n does not exist.\n'%runDir)
        sys.exit(-2)
    #output variables
    runOk = False
    missingComp = []
    #calculate all the possible combinations
    rawComb = itertools.combinations_with_replacement([sp1, sp2], 2)
    comparisonPaths = []
    for tpl in rawComb:
        comparisonPaths.append('%s%s-%s'%(runDir, tpl[0], tpl[-1]))
    # add the pair BA
    comparisonPaths.append('%s%s-%s'%(runDir, sp2, sp1))
    #check if the files exists
    for path in comparisonPaths:
        if os.path.isfile(path):
            s1, s2 = os.path.basename(path).split('-')
            if s1 == s2: #check if it is a within species
                sharedFile = '%s%s-%s'%(sharedDir, s1, s2)
                #sys.exit('debug')
                if not os.path.isfile(sharedFile):
                    systools.copy(path, sharedDir, debug=debug)
        else:
            missingComp.append(os.path.basename(path))
    #check if the sql directory table exists
    tblFile = '%stable.%s'%(runDir, pair)
    sqlFile = '%ssqltable.%s'%(runDir, pair)
    if (os.path.isfile(tblFile)) and (os.path.isfile(sqlFile)):
        runOk = True
    if debug:
        print('Missing comparisons:\n')
        print(missingComp)
    return(runOk, missingComp)



def extract_inparanoid_scores(hspDict, qid, sid, debug=False):
    """Extract the scores for an inparanoid graph-node.

    Also the overlaps are calculated
    Return a tab-separated similar to the following:
    63363_O67184 63363_O66911 75.5 564 926 214 303 133 136 q:324-380 h:578-634	q:462-537 h:802-880
    """
    if debug:
        print('\nextract_inparanoid_scores :: START')
        print('Query:\t%s'%qid)
        print('Subject:\t%s'%sid)
        print('Number of HSP:\t%d'%len(hspDict))
    # the meaning of the fileds are the following
    #col1: query
    #col2: subject
    #col3: sum( hsp_i.bitscore )
    #col4: query length [qlen]
    #col5: subject length [slen]
    #col6: max([hsp_1.qend, hsp_2.qend, ... hsp_N.qend]) - min([hsp_1.qstart, hsp_2.qstart, ... hsp_N.qstart] + 1)
    #col7: max([hsp_1.send, hsp_2.send, ... hsp_N.send]) - min([hsp_1.sstart, hsp_2.sstart, ... hsp_N.sstart] + 1)
    #col8: for i=[1, N], sum([hsp_i.qend - hsp_i.qstart] + 1)
    #col9: for i=[1, N], sum([hsp_i.send - hsp_i.sstart] + 1)
    #col10: tab-separated list of all hsp start and end of query subject, in ascending order of the qstart value
    # example of value in col10: q:324-380 h:578-634	q:462-537 h:802-880
    #each entry in the dictionary has qstart for the hsp as key
    #and the following information as values: qlen, slen, qstart, qend, sstart, send, bitscore
    #calculate score in the simple case in which there is only one HSP
    qFragmentList = [] #contain tuples with start and end positions of hsp on query
    hFragmentList = [] #contain tuples with start and end positions of hsp on hit
    tmpDict = {} # will have the qstart as keys and strings like (q:324-380 h:578-634	q:462-537 h:802-880) as values
    if len(hspDict) == 1:
        qlen, slen, qstart, qend, sstart, send, bitscore = list(hspDict.values())[0]
        #return(qid, sid, str(bitscore), str(qlen), str(slen), str(qend - qstart + 1), str(send - sstart + 1), str(qend - qstart + 1), str(send - sstart + 1), ['q:%d-%d h:%d-%d'%(qstart, qend, sstart, send)])
        return(qid, sid, str(bitscore), str(qlen), str(slen), str(qend - qstart + 1), str(send - sstart + 1), str(qend - qstart + 1), str(send - sstart + 1), ['q:%d-%d h:%d-%d'%(qstart, qend, sstart, send)])
    else:
        fBitscore = 0.
        fQlen = fSlen = fCol6 = fCol7 = fCol8 = fCol9 = 0
        #these will be used to calculate the overlap
        #and represent the: rightmost end of hsp on query, rightmost end on hsp on hit, leftmost start on hsp on query,  leftmost start on hsp on hit
        dxQuery = dxHit = lxQuery = lxHit = None
        i = 0
        for hsp in hspDict:
            i += 1
            qlen, slen, qstart, qend, sstart, send, bitscore = list(hspDict[hsp])
            if len(qFragmentList) == 0: #then it is the first hsp and must be included in the count
                qFragmentList.append((qstart, qend))
                hFragmentList.append((sstart, send))
                fQlen = qlen
                fSlen = slen
                dxQuery = qend
                lxQuery = qstart
                dxHit = send
                lxHit = sstart
                fBitscore += bitscore
                tmpDict['%d:%d'%(qstart, qend)] = 'q:%d-%d h:%d-%d'%(qstart, qend, sstart, send)
            else:
                overlapFound = False #used to decide if the current hsp should be included in the final score or not
                #check if there is any overlap on the query
                for interval in qFragmentList:
                    overlapFound = check_hsp_overlap((qstart, qend), interval, debug)
                    if overlapFound:
                        #print('Overlap found:\tQUERY')
                        break
                #check if there is any overlap on the hit
                if not overlapFound:
                    for interval in hFragmentList:
                        overlapFound = check_hsp_overlap((sstart, send), interval, debug)
                        if overlapFound:
                            #print('Overlap found:\tSUBJECT')
                            break
                #if the overlap was found just skip the hsp
                if overlapFound:
                    continue
                #otherwise include the current hsp
                qFragmentList.append((qstart, qend))
                hFragmentList.append((sstart, send))
                fBitscore += bitscore
                tmpDict['%d:%d'%(qstart, qend)] = 'q:%d-%d h:%d-%d'%(qstart, qend, sstart, send)
        #finalize the output record
        fBitscore = round(fBitscore, 2)
        #dictionary for strings in col10
        col10Dict = {}
        #insert values in the col10Dict with the qstart as key value (tmpDict dict should not contain same values)
        for k in tmpDict:
            tmpStart = k.split(':')[0]
            col10Dict[int(tmpStart)] = tmpDict[k]
        del tmpDict
        #sort the values for col10
        sorted_list = sorted(col10Dict.items(), key=lambda x: x[0])
        col10List = []
        for el in sorted_list:
            col10List.append(el[1])
        #calculate values for column 6, 7, 8, 9
        #load required values for hsp in queries
        tmpStart = []
        tmpEnd = []
        #col8: for i=[1, N], sum([hsp_i.qend - hsp_i.qstart] + 1)
        for el in qFragmentList:
            tmpStart.append(el[0])
            tmpEnd.append(el[1])
            fCol8 += el[1] - el[0] + 1
        #col6: max([hsp_1.qend, hsp_2.qend, ... hsp_N.qend]) - min([hsp_1.qstart, hsp_2.qstart, ... hsp_N.qstart]) + 1
        fCol6 = max(tmpEnd) - min(tmpStart) + 1
        #load required values for hsp in subjects
        tmpStart.clear()
        tmpEnd.clear()
        #col9: for i=[1, N], sum([hsp_i.send - hsp_i.sstart] + 1)
        for el in hFragmentList:
            tmpStart.append(el[0])
            tmpEnd.append(el[1])
            fCol9 += el[1] - el[0] + 1
        #col7: max([hsp_1.send, hsp_2.send, ... hsp_N.send]) - min([hsp_1.sstart, hsp_2.sstart, ... hsp_N.sstart] + 1)
        fCol7 = max(tmpEnd) - min(tmpStart) + 1
    #return the required values
    return(qid, sid, str(fBitscore), str(qlen), str(slen), str(fCol6), str(fCol7), str(fCol8), str(fCol9), col10List)



def extract_ortholog_pairs(rootDir=os.getcwd(), outDir=os.getcwd(), outName=None, pairsFile=None, coreOnly=False, singleDir=False, tblPrefix='table', splitMode=False, debug=False):
    """Create file containing all generated ortholog pairs."""
    if debug:
        print('extract_ortholog_pairs :: START')
        print('Root directory:\t%s'%rootDir)
        print('Output directory:\t%s'%outDir)
        print('Output file name:\t%s'%outName)
        print('Species pairs file:\t%s'%pairsFile)
        print('Core only:\t%s'%coreOnly)
        print('All tables in same directory:\t{:s}'.format(str(singleDir)))
        print('Table file prefix:\t{:s}'.format(tblPrefix))
        # keep only first part of the gene id after splitting on the '_' character (if any)
        print('Split mode:\t%s'%splitMode)
    #fetch result files tables
    tblList = fetch_inparanoid_tables(rootDir=rootDir, outDir=outDir, pairsFile=pairsFile, tblPrefix=tblPrefix, singleDir=singleDir, debug=debug)
    totRead = totWrite = tblCnt = 0
    coreClstrMissCnt = 0
    #extract the project name from the root
    projName = ''
    # NOTE: rtemove this since it not required
    if rootDir[-1] == '/':
        projName = rootDir.rsplit('/', 2)[-2]
    else:
        projName = rootDir.rsplit('/', 2)[-1]
    if outName is None:
        if coreOnly:
            outName = '%s_core_relations.tsv'%projName
        else:
            outName = '%s_all_relations.tsv'%projName
    #create output directory if required
    systools.makedir(outDir)
    #output file
    outTbl = os.path.join(outDir, outName)
    # this dictionary is to avoid repetition among the non-core pairs
    repeatTrap = {}
    print('Creating file with homolog pairs...')
    #create output file
    ofd = open(outTbl, 'w')
    for path in tblList:
        if os.path.isfile(path):
            if debug:
                print(path)
            if os.path.basename(path).startswith(tblPrefix) or singleDir:
                tblCnt += 1
                for clstr in open(path):
                    if clstr[0] == 'O':
                        continue
                    totRead += 1
                    clusterID, score, orto1, orto2 = clstr.rstrip().split('\t')
                    #count the cases
                    ortho1All = orto1.rstrip().split(' ')
                    ortho2All = orto2.rstrip().split(' ')
                    #will associate scores to ortholog genes
                    orthoScoresDict = OrderedDict()
                    for i, gene in enumerate(ortho1All):
                        if i % 2 == 0:
                            if splitMode:
                                orthoScoresDict[gene.split('_', 1)[1]] = round(float(ortho1All[i + 1]), 2)
                            else:
                                orthoScoresDict[gene] = round(float(ortho1All[i + 1]), 2)
                    #now the second part of the cluster...
                    for i, gene in enumerate(ortho2All):
                        if i % 2 == 0:
                            if splitMode:
                                orthoScoresDict[gene.split('_', 1)[1]] = round(float(ortho2All[i + 1]), 2)
                            else:
                                orthoScoresDict[gene] = round(float(ortho2All[i + 1]), 2)
                    #make lists with gene ids
                    ortho1list = []
                    #extract genes for ortho1
                    for i, gene in enumerate(ortho1All):
                        if i % 2 == 0:
                            if splitMode:
                                ortho1list.append(gene.split('_', 1)[1])
                            else:
                                ortho1list.append(gene)
                    ortho1AllLen = len(ortho1list)
                    #extract genes for ortho2
                    ortho2list = []
                    #extract genes for ortho1
                    for i, gene in enumerate(ortho2All):
                        if i % 2 == 0:
                            if splitMode:
                                ortho2list.append(gene.split('_', 1)[1])
                            else:
                                ortho2list.append(gene)
                    ortho2AllLen = len(ortho2list)
                    #write the pairs in the output file
                    if coreOnly: #add only the ortholog relation with 1.0 as score
                        #check the the score is 1.0
                        pairFound = False
                        coreCnt = 0
                        for orto1gene in ortho1list:
                            if orthoScoresDict[orto1gene] == 1.0:
                                for orto2gene in ortho2list:
                                    #count the core relations written
                                    if orthoScoresDict[orto2gene] == 1.0:
                                        ofd.write('%s\t%s\n'%(orto1gene, orto2gene))
                                        totWrite += 1
                                        coreCnt += 1
                                    pairFound = True
                        if not pairFound:
                            if debug:
                                print('WARNING: the CORE pair was not found:\n%s'%clstr)
                            coreClstrMissCnt += 1
                    else: #write all the ortholog relations
                        for orto1gene in ortho1list:
                            for orto2gene in ortho2list:
                                tmpPair = '%s-%s'%(orto1gene, orto2gene)
                                if not tmpPair in repeatTrap:
                                    repeatTrap[tmpPair] = None
                                    ofd.write('%s\t%s\n'%(orto1gene, orto2gene))
                                totWrite += 1
    ofd.close()
    # sort the output file alphabetically
    from sh import sort
    tmpSortPath = os.path.join(outDir, 'tmp_sorted_orthologs.tsv')
    # sort using sh
    print('Sorting homolog pairs...')
    sort(outTbl, '-o', tmpSortPath)
    # remove the original ortholog pairs file
    os.remove(outTbl)
    # rename the sorted file to the original output name
    os.rename(tmpSortPath, outTbl)
    if debug:
        print('Total clusters read:\t%d'%totRead)
        if coreOnly:
            print('Total CORE clusters read:\t%d'%(totRead - coreClstrMissCnt))
    # write the number of ortholog relations in created
    from io import StringIO
    from sh import wc
    buf = StringIO()
    wc('-l', outTbl, _out=buf)
    pairsCnt = buf.getvalue().strip().split(' ', 1)[0]
    print("Total orthologous relations\t{:s}".format(pairsCnt))



def fetch_inparanoid_tables(rootDir=os.getcwd(), outDir=os.getcwd(), pairsFile=None, tblPrefix='table', singleDir=False, debug=False):
    """Find result inparanoid table files for each proteome pair."""
    import fnmatch
    if debug:
        print('fetch_inparanoid_tables :: START')
        print('Root directory:\t%s'%rootDir)
        print('Output directory:\t%s'%outDir)
        print('Species pairs file:\t%s'%pairsFile)
        print('Table prefix:\t%s'%tblPrefix)
        print('Pairwise table are stored all in the same directory:\t{:s}'.format(str(singleDir)))
        # the output table prefix can be 'table' for ortholog tables, or 'Output' for tables with bitscores
    #check that the input directory is valid
    if not os.path.isdir(rootDir):
        sys.stderr.write('ERROR: the directory containing the table files\n%s\n does not exist.\n'%rootDir)
        sys.exit(-2)
    if not os.path.isfile(pairsFile):
        sys.stderr.write('ERROR: you must provide a valid file containing all the species pairs\n')
        sys.exit(-2)
    #create the output directory if does not exist yet
    if outDir[-1] != '/':
        outDir += '/'
    systools.makedir(outDir)
    #load the species names
    pairs = OrderedDict()
    foundPairs = OrderedDict()
    species = OrderedDict()
    #enter the root directory
    prevDir = os.getcwd()
    os.chdir(rootDir)
    #find the inparanoid table files
    fileList = []
    for pair in open(pairsFile):
        pair = pair.rstrip('\n')
        pairs[pair] = None
        sp1, sp2 = pair.split('-')
        species[sp1] = None
        species[sp2] = None
        #make the file paths
        runPath = ""
        tblName = ""
        if singleDir:
            runPath = rootDir
        else:
            runPath = os.path.join(rootDir, pair)
        #runPath = '%s%s/'%(rootDir, pair)
        # set the table name
        if len(tblPrefix) == 0:
            tblName = pair
        else:
            tblName = "{:s}.{:s}".format(tblPrefix, pair)
        #tblName = '%s.%s'%(tblPrefix, pair)
        if os.path.isdir(runPath):
            tblPath = os.path.join(runPath, tblName)
            if os.path.isfile(tblPath):
                fileList.append(tblPath)
                if debug:
                    print(tblPath)
                foundPairs[pair] = None
    #check that the found tables and the species-pairs count are same
    if len(foundPairs) != len(pairs):
        sys.stderr.write('ERROR: the number of ortholog tables found (%d) and the number of species pairs (%d) must be the same.\n'%(len(foundPairs), len(pairs)))
        print('\nMissing ortholog tables for pairs:')
        # check which pair is missing
        tmpList = []
        for p in pairs:
            if p not in foundPairs:
                tmpList.append(p)
        print(' '.join(tmpList))
        sys.exit(-4)
    #reset the current directory to the previous one
    os.chdir(prevDir)
    if debug:
        print('Found tables:\t%d'%len(fileList))
    #return the final list
    return fileList



def load_input_sequences(inSeq, debug=False):
    """Load input sequences in dictionary."""
    if debug:
        print('load_input_sequences :: START')
        print('Input file:\t%s'%inSeq)
    outDict = OrderedDict()
    #Use biopython
    from Bio import SeqIO
    cnt = wcnt = 0
    for record in SeqIO.parse(open(inSeq), 'fasta'): #python2.7, 3
        cnt += 1
        seq = str(record.seq)
        #seqId = record.id
        seqId = record.id.split(' ', 1)[0]
        #add sequecens to the dictionary
        outDict[seqId] = seq.lower()
    if debug:
        print('%d fasta sequences loaded in dictionary.'%len(outDict))
    return outDict



def run_sonicparanoid2_multiproc(inPaths, outDir=os.getcwd(), tblDir=os.getcwd(), threads=4, alignDir=None, mmseqsDbDir=None, create_idx=True, sensitivity=4.0, cutoff=40, confCutoff=0.05, lenDiffThr=0.5, overwrite_all=False, overwrite_tbls=False, update_run=False, keepAlign=False, debug=False):
    """Execute sonicparanoid, using MMseqs2 if required for all the proteomes in the input directory."""
    import copy
    if debug:
        print('\nrun_sonicparanoid2_multiproc :: START')
        print('Input paths:\t{:d}'.format(len(inPaths)))
        print('Run root directory:%s'%outDir)
        print('Pairwise-ortholog directory:%s'%tblDir)
        print('CPUs:\t%d'%threads)
        print('Alignment directory:\t%s'%alignDir)
        print('MMseqs2 database directory:\t%s'%mmseqsDbDir)
        print('Inxes MMseqs2 databases:\t{:s}'.format(str(create_idx)))
        print('MMseqs2 sensitivity (-s):\t%s'%str(sensitivity))
        print('Cutoff:\t%d'%cutoff)
        print('Confidence cutoff for paralogs:\t%s'%str(confCutoff))
        print('Length difference filtering threshold:\t%s'%str(lenDiffThr))
        print('Overwrite existing ortholog tables:\t%s'%overwrite_tbls)
        print('Overwrite everything:\t%s'%overwrite_all)
        print('Update an existing run:\t%s'%update_run)
        print('Keep raw MMseqs2 alignments:\t{:s}'.format(str(keepAlign)))

    # directory with the input files
    inDir = os.path.dirname(inPaths[0])

    #check cutoff and woed size
    if cutoff < 40:
        cutoff = 40

    # check that file with info on input file exists
    spFile = os.path.join(outDir, "species.tsv")
    if not os.path.isfile(spFile):
        sys.stderr.write("\nERROR: the species file ({:s}) could not be found.".format(os.path.basename(spFile)))
        sys.stderr.write("\nMake sure the species file is created before proceeding.\n")
        sys.exit(-2)
    # load proteomes sizes
    spSizeDict = {}
    for el in open(spFile, "r"):
        spId, spName, digest, protSize = el[:-1].split('\t', 3)
        if not spId in spSizeDict:
            spSizeDict[spId] = int(protSize)
    spList = list(spSizeDict.keys())

    #generate file with the combinations
    spPairsFile = os.path.join(outDir, "species_pairs.tsv")
    spPairs = list(itertools.combinations(spList, r=2))

    # create a matrix that contains the combinations
    # this will be used as a control to decide if the master matrix can be created
    spListInt = [int(x) for x in spList] # convert the strings to integers
    maxSp = max(spListInt)
    M = dok_matrix((maxSp, maxSp), dtype=np.int8)
    # fill the matrix (the species idx will decreased by 1)
    for tplInt in itertools.combinations(spListInt, r=2):
        M[tplInt[0]-1, tplInt[1]-1] = 1
    # store to a npz file
    M = M.tocsr()
    #M = triu(M, k=0, format="csr")
    combMtxPath = os.path.join(outDir, "combination_mtx.npz")
    save_npz(combMtxPath, M, compressed=True)
    del M
    del spListInt

    #check that the file with genome pairs has not been created yet
    if os.path.isfile(spPairsFile) and not overwrite_all and not update_run:
        pass
    else:
        ofd = open(spPairsFile, 'w')
        [ofd.write('%s-%s\n'%(tpl[0], tpl[1])) for tpl in spPairs]
        ofd.close()

    #give some information about the combinations
    dashedPairs = ['%s-%s'%(tpl[0], tpl[1]) for tpl in spPairs]
    print('\nFor the %d input species %d combinations are possible.'%(len(spList), len(spPairs)))
    # pair for which the ortholog table is missing
    requiredPairsDict = {}
    requiredSpDict = {} # species for which computations are required
    # create dictionary with both within- and between-proteome alignment names
    alignDict = {}
    requiredAlignDict = {} # will contain the required alignments
    alignFlist = [] # contains files in the alignment directory

    # generate all possible pairs
    for sp in spList:
        alignDict['{:s}-{:s}'.format(sp, sp)] = spSizeDict[sp]
    for pair in dashedPairs:
        sp1, sp2 = pair.split('-', 1)
        # calculate the genome size for the pair
        avgGenSize = float(spSizeDict[sp2] + spSizeDict[sp1]) / 2.
        alignDict[pair] = avgGenSize
        alignDict['{:s}-{:s}'.format(sp2, sp1)] = avgGenSize
    # fill the dictionaries with required alignments and ortholog tables
    if overwrite_all:
        # set all the overwite flags to true if overwrite_all
        overwrite_tbls = True
        #sys.exit('DEBUG :: overwrite_all')
        # it will be the same
        requiredAlignDict = copy.deepcopy(alignDict)
        for sp in spList:
            requiredSpDict[sp] = None
        requiredPairsDict = copy.deepcopy(dashedPairs)
        # remove all files in the shared directory
        alignFlist = os.listdir(alignDir)
        for f in alignFlist:
            os.remove(os.path.join(alignDir, f))
        #sys.exit("DEBUG :: run_sonicparanoid2_multiproc :: overwrite_all")
    # predict all ortholog tables but reuse alignments
    elif overwrite_tbls and not overwrite_all:
        # ortholog tables will be predicted for all pairs:
        for sp in spList:
            requiredSpDict[sp] = None
        requiredPairsDict = copy.deepcopy(dashedPairs)
        # alignments can be reused where possible
        for pair in alignDict:
            sp1, sp2 = pair.split('-', 1)
            # get the genome sizes
            sizeSp1 = spSizeDict[sp1]
            sizeSp2 = genSize = 0
            if sp1 == sp2:
                genSize = 2 * sizeSp1
            else:
                sizeSp2 = spSizeDict[sp2]
                genSize = sizeSp1 + sizeSp2
            # check alignment
            alignPath = os.path.join(alignDir, '{:s}-{:s}'.format(sp1, sp2))
            if not os.path.isfile(alignPath) and not os.path.isfile('{:s}.gz'.format(alignPath)):
                requiredAlignDict['{:s}-{:s}'.format(sp1, sp2)] = genSize
        #sys.exit("DEBUG :: run_sonicparanoid2_multiproc :: overwrite_tbls")
    # no overwrite, hence both ortholog tables
    # and alignments can be reused
    else:
        for pair in dashedPairs:
            tmpDir = os.path.join(tblDir, pair)
            tblName = 'table.{:s}'.format(pair)
            sqlName = 'sqltable.{:s}'.format(pair)
            tmpTblPath = os.path.join(tmpDir, tblName)
            tmpSqlPath = os.path.join(tmpDir, sqlName)
            # if one of the tables does not exist
            if (not os.path.isfile(tmpTblPath)) or (not os.path.isfile(tmpSqlPath)):
                requiredPairsDict[pair] = None
                sp1, sp2 = pair.split('-', 1)
                # get the genome sizes
                sizeSp1 = spSizeDict[sp1]
                sizeSp2 = spSizeDict[sp2]
                # calculate the average genome sizes per pair
                avgSizeSp11 = sizeSp1
                avgSizeSp22 = sizeSp2
                avgSizeBtw = float(sizeSp1 + sizeSp2) / 2.
                # check alignment AB
                alignPathAB = os.path.join(alignDir, '{:s}-{:s}'.format(sp1, sp2))
                if not os.path.isfile(alignPathAB) and not os.path.isfile('{:s}.gz'.format(alignPathAB)):
                    requiredAlignDict['{:s}-{:s}'.format(sp1, sp2)] = avgSizeBtw
                # check alignment BA
                alignPathBA = os.path.join(alignDir, '{:s}-{:s}'.format(sp2, sp1))
                if not os.path.isfile(alignPathBA) and not os.path.isfile('{:s}.gz'.format(alignPathBA)):
                    requiredAlignDict['{:s}-{:s}'.format(sp2, sp1)] = avgSizeBtw
                # check alignment AA
                alignPathAA = os.path.join(alignDir, '{:s}-{:s}'.format(sp1, sp1))
                if not os.path.isfile(alignPathAA) and not os.path.isfile('{:s}.gz'.format(alignPathAA)):
                    requiredAlignDict['{:s}-{:s}'.format(sp1, sp1)] = sizeSp1
                # check alignment BB
                alignPathBB = os.path.join(alignDir, '{:s}-{:s}'.format(sp2, sp2))
                if not os.path.isfile(alignPathBB) and not os.path.isfile('{:s}.gz'.format(alignPathBB)):
                    requiredAlignDict['{:s}-{:s}'.format(sp2, sp2)] = sizeSp2
        # fill the dict with required species
        for pair in requiredAlignDict:
            sp1, sp2 = pair.split('-', 1)
            if not sp1 in requiredSpDict:
                requiredSpDict[sp1] = spSizeDict[sp1]
            if not sp2 in requiredSpDict:
                requiredSpDict[sp2] = spSizeDict[sp2]
            # if all the possible species are already include exit loop
            if len(requiredSpDict) == len(spList):
                break
    # check which if alignments are already available
    totAlign = len(alignDict)
    print('\nTotal possible alignments:\t{:d}'.format(totAlign))
    print('Required alignments:\t{:d}'.format(len(requiredAlignDict)))
    print('Required ortholog table predictions:\t{:d}'.format(len(requiredPairsDict)))

    if len(requiredAlignDict) > 0:
        #NOTE: Restore if the new version is not better
        #'''
        # sort the alignments so that the biggest ones are performed first
        s = [(k, requiredAlignDict[k]) for k in sorted(requiredAlignDict, key=requiredAlignDict.get, reverse=True)]
        # empty the dictionary and fill it again with the size-sorted one
        requiredAlignDict.clear()
        requiredAlignDict = {key: value for (key, value) in s}
        del s
        #'''
        dqAlign = deque()

        for p, size in requiredAlignDict.items():
            tpl = (p, size)
            dqAlign.append(tpl)

        #'''
        pairsCnt = len(requiredAlignDict)
        jobCnt = 0
        n = 1
        chunkList = [] # will contain the size of chunks that will fill the job queue
        # now create a list with the chunk sizes
        while jobCnt < pairsCnt:
            n += 1
            triangularNum = int((n * (n + 1)) / 2.)
            jobCnt += triangularNum
            chunkList.append(triangularNum)
        # sort the list of chunks in inverted order
        chunkList.sort(reverse=True)
        # remove the biggest chunk
        chunkList.pop(0)
        # make a copy with the chunks and invert it
        chunkListInv = []
        for el in chunkList:
            chunkListInv.append(el)
        chunkListInv.sort()
        # set the step to half of the cpus
        heavyChunkSize = int(threads / 2.)
        if heavyChunkSize == 0:
            heavyChunkSize = 1
        # update the alignments dictionary
        requiredAlignDict.clear()
        remainingJobs = len(dqAlign)
        while remainingJobs > 0:
            # add the chunk of jobs that require a lot of memory
            for i in range(0, heavyChunkSize):
                if len(dqAlign) > 0:
                    p, fSize = dqAlign.popleft()
                    requiredAlignDict[p] = fSize
                    remainingJobs -= 1 # decrement
                else: # no more elements to be added
                    break
            # add a chunk of small jobs
            if len(chunkList) > 0:
                if len(dqAlign) > 0:
                    cSize = chunkList.pop(0)
                    for i in range(0, cSize):
                        if len(dqAlign) > 0:
                            p, fSize = dqAlign.pop()
                            requiredAlignDict[p] = fSize
                            remainingJobs -= 1 # decrement
                        else: # no more elements to be added
                            break
            # add chunks of growing size
            elif len(chunkListInv) > 0:
                if len(dqAlign) > 0:
                    cSize = chunkListInv.pop(0)
                    for i in range(0, cSize):
                        if len(dqAlign) > 0:
                            p, fSize = dqAlign.pop()
                            requiredAlignDict[p] = fSize
                            remainingJobs -= 1 # decrement
                        else: # no more elements to be added
                            break
        # perform the alignments
        workers.perform_mmseqs_multiproc_alignments(required_align=requiredAlignDict, inDir=inDir, outDir=alignDir, dbDir=mmseqsDbDir, create_idx=create_idx, sensitivity=sensitivity, cutoff=cutoff, threads=threads, keepAlign=keepAlign, debug=debug)

    # perform the orthology inference for the required pairs
    if len(requiredPairsDict) > 0:
        #'''
        # sort the the species dictionary by size
        s = [(k, spSizeDict[k]) for k in sorted(spSizeDict, key=spSizeDict.get, reverse=True)]
        # empty the dictionary and fill it again with the size-sorted one
        spSizeDict.clear()
        spSizeDict = {key: value for (key, value) in s}
        del s

        # add counters for the within alignments to be loaded
        withinAlignDict = copy.deepcopy(spSizeDict)
        del spSizeDict

        # Prepare the dictionary that will contain the withinalignment scores
        # set the counters to 0
        for sp in withinAlignDict:
            withinAlignDict[sp] = [0, None, None]
        # fill the dict with required species
        for pair in requiredPairsDict:
            sp1, sp2 = pair.split('-', 1)
            # increment the counters
            withinAlignDict[sp1][0] += 1
            withinAlignDict[sp2][0] += 1

        sys.stdout.write('\nPredicting {:d} ortholog tables...'.format(len(requiredPairsDict)))
        # calculate cpu-time for orthology inference
        orthology_start = time.perf_counter()

        #'''##### USE PREPROCESSING ####
        #### ORIGINAL ####
        # segOverlapCutoff: float = 0.5
        ##################
        segOverlapCutoff: float = 0.25
        # The actual matching segments must cover this of this match of the matched sequence
        # For example for a matched sequence 70 bps long, segments 1-15 and 50-70 gives a total coverage of 35, which is 50% of total.
        segCoverageCutoff: float = 0.25
        # load the required within alignments in parallel
        inpyranoid.preprocess_within_alignments_parallel(withinAlignDict, alignDir=alignDir, threads=threads, covCoff=segCoverageCutoff, overlapCoff=segOverlapCutoff, debug=debug)
        workers.perform_parallel_orthology_inference_shared_dict(requiredPairsDict, inDir, outDir=tblDir, sharedDir=alignDir, sharedWithinDict=withinAlignDict, cutoff=cutoff, confCutoff=confCutoff, lenDiffThr=lenDiffThr, threads=threads, debug=debug)

        ###################################
        #'''

        '''
        #### DO NOT USE PREPROCESSING ####
        workers.perform_parallel_orthology_inference(requiredPairsDict, inDir, outDir=outDir, sharedDir=sharedDir, cutoff=cutoff, confCutoff=confCutoff, lenDiffThr=lenDiffThr, threads=threads, debug=debug)
        ###################################
        '''

        sys.stdout.write('\nOrtholog tables creation elapsed time (seconds):\t{:s}\n'.format(str(round(time.perf_counter() - orthology_start, 3))))

    # return the paths for species and pairs files
    return (spFile, spPairsFile, requiredPairsDict)



def set_mmseqs_path(newPath):
    global mmseqsPath
    """Set path of the directory in which MMseqs2 binaries are stored."""
    mmseqsPath = os.path.normpath(newPath)



def test_extract_ortholog_pairs(debug=True):
    """Extract ortholog pairs."""
    rootDir = '/home/salvocos/projects/pyinparanoid/benchmark/runs/qfo2011_fungi_pyparanoid/'
    pairsFile = '%sspecies_pairs.txt'%rootDir
    outDir = '/home/salvocos/projects/pyinparanoid/benchmark/runs/qfo2011_fungi_pyparanoid/ortholog_pairs/'
    coreOnly = False
    splitHdr = True
    #extract pairs
    extract_ortholog_pairs(rootDir=rootDir, outDir=outDir, outName=None, pairsFile=pairsFile, coreOnly=coreOnly, splitMode=splitHdr, debug=debug)



def test_fetch_inparanoid_tables(debug=True):
    """Find ortholog relation tables."""
    rootDir = '/home/salvocos/projects/pyinparanoid/benchmark/runs/qfo2011_fungi_pyparanoid/'
    pairsFile = '%sspecies_pairs.txt'%rootDir
    outDir = '/home/salvocos/projects/pyinparanoid/benchmark/runs/fungi_2011/to_be_removed/'
    prefix = 'Output'
    #prefix = 'table'
    tblList = fetch_inparanoid_tables(rootDir=rootDir, outDir=outDir, pairsFile=pairsFile, tblPrefix=prefix, debug=debug)



def test_run_sonicparanoid2_multiproc(debug=False):
    """Test a complete sonicparanoid run."""
    local = False

    root = '/home/salvocos/tmp/test_ortholog_detection/'
    #inDir = os.path.join(root, 'input_bigger/')
    #inDir = os.path.join(root, 'input_much_bigger/')
    inDir = '/home/salvocos/projects/pyinparanoid/benchmark/input/qfo_2011/'
    #inDir = '/home/salvocos/projects/pyinparanoid/benchmark/input/eukaryote_2011/'
    #rootOut = os.path.join(root, 'test_run_multiproc/')
    #rootOut = '/tmp/sonicpara_qfo_se4_8x1cpu_parser-fix-minscore30/'
    rootOut = '/tmp/sonicpara_qfo_se4_8x1cpu_parser-fix/'
    cpus = 8
    sens = 2
    coff = 40
    sharedDir = '%sshared_output/'%rootOut
    dbDirectory = '%smmseqs2_databases/'%rootOut
    ov_all = False
    ov_tbls = False

    # set different paths and setting when running locally
    if local:
        root = '/Users/salvocos/Desktop/test_queues_sonicpara/'
        inDir = os.path.join(root, 'input/')
        rootOut = os.path.join(root, 'test_run/')
        cpus = 4
        sens = 4
        coff = 40
        sharedDir = '%sshared_output/'%rootOut
        dbDirectory = '%smmseqs2_databases/'%rootOut
        ov_all = False
        ov_tbls = False

    run_sonicparanoid2_multiproc(inDir, outDir=rootOut, threads=cpus, sharedDir=None, mmseqsDbDir=dbDirectory, sensitivity=sens, cutoff=coff, confCutoff=0.05, lenDiffThr=0.5, noMmseqs=False, overwrite_all=ov_all, overwrite_tbls=ov_tbls, debug=debug)
