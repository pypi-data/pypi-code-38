"""Functions to process the ortholog groups and generate staticts."""
import os
import sys
import numpy as np
from shutil import move
import multiprocessing as mp
from scipy import stats as scpy_stats
from typing import Dict, List, Deque, Any, Tuple
from collections import OrderedDict, deque
from sonicparanoid import sys_tools as systools
from subprocess import Popen, PIPE
import pickle

#### IMPORT TO GENERATE PyPi package
from sonicparanoid import sys_tools as systools
from sonicparanoid import seq_tools as seqtools
from sonicparanoid import workers
from sonicparanoid import inpyranoid_c



__module_name__ = 'Orthogroups'
__source__ = 'orthogroups.py'
__author__ = 'Salvatore Cosentino'
__license__ = 'GPLv3'
__version__ = '0.7'
__maintainer__ = 'Cosentino Salvatore'
__email__ = 'salvo981@gmail.com'



#root path for files
pySrcDir = os.path.dirname(os.path.abspath(__file__))
pySrcDir += '/'
multiparanoidSrcDir = '%squick_multi_paranoid/'%pySrcDir



### FUNCTIONS ####
def info() -> None:
    """Functions ot group orthologs and generate statistics on groups."""
    print('MODULE NAME:\t%s'%__module_name__)
    print('SOURCE FILE NAME:\t%s'%__source__)
    print('MODULE VERSION:\t%s'%__version__)
    print('LICENSE:\t%s'%__license__)
    print('AUTHOR:\t%s'%__author__)
    print('EMAIL:\t%s'%__email__)



#### Worker Functions ####

def consume_write_sql_c(jobs_queue, results_queue, outDir):
    while True:
        current_table = jobs_queue.get(True, 1)
        if current_table is None:
            break
        # extract input paths
        # create temporary directory name

        # it MUST use 1 CPU
        outSql = inpyranoid_c.write_sql_c(current_table, outDir, debug=False)
        # exit if the SQL file does not exists
        if not os.path.isfile(outSql):
            sys.stderr.write('\nERROR: the SQL table could not be generated.\n')
            sys.exit(-2)
        # store the path of the SQL file in the queue
        results_queue.put(outSql)



#### Parallel Functions ####

def create_sql_tables(orthoDbDir: str, outSqlDir: str, pairsList: List[str] = [], threads: int = 4,  debug: bool=False) -> int:
    """Create a SQL table from each ortholog table."""
    if debug:
        print("\ncreate_sql_tables :: START")
        print("Directory with ortholog tables: {:s}".format(orthoDbDir))
        print("Output directory: {:s}".format(outSqlDir))
        print("Tables to be processed:\t{:d}".format(len(pairsList)))
        print("Threads:\t{:d}".format(threads))

    # create the queue and start adding
    ortho2sql_queue = mp.Queue(maxsize=len(pairsList) + threads)

    # fill the queue with the pairs
    for pair in pairsList:
        sys.stdout.flush()
        spA, spB = pair.split("-", 1)
        tmpPath = os.path.join(orthoDbDir, "{:s}/table.{:s}".format(pair, pair))
        ortho2sql_queue.put(tmpPath)

    # add flags for completed jobs
    for i in range(0, threads):
        sys.stdout.flush()
        ortho2sql_queue.put(None)
    # Queue to contain the execution time
    results_queue = mp.Queue(maxsize=len(pairsList))

    # call the method inside workers
    print("\nCreating SQL tables...")
    runningJobs = [mp.Process(target=consume_write_sql_c, args=(ortho2sql_queue, results_queue, outSqlDir)) for i_ in range(threads)]

    for proc in runningJobs:
        proc.start()

    # counter for created tables
    sqlCnt: int = 0

    while True:
        try:
            outSqlPath: str = results_queue.get(False, 0.01)
            if debug:
              sys.stdout.write("\nSQL table\n{:s}\ncreated\n".format(outSqlPath))
            sqlCnt += 1
        except:
            pass
        allExited = True
        for t in runningJobs:
            if t.exitcode is None:
                allExited = False
                break
        if allExited & results_queue.empty():
            break

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()

    # SQL tables creation completed
    if debug:
        print("{:d} SQL tables created.".format(sqlCnt))
    return sqlCnt



#### Other Functions ####


def write_binning(outPath, mtx, rowNames: List[str], firstCol: str, debug: bool=False) -> None:
    """Count bins and write it in the output file."""
    if debug:
        print('\nwrite_binning :: START')
        print('Output path: {:s}'.format(outPath))
        print('Rows: {:s}'.format(','.join(rowNames)))
        print('First column: {:s}'.format(firstCol))

    # generate the bin intervals
    chunk1: List[int] = deque(range(0, 27, 1))
    # create the other ranges of bins
    chunk2: Deque[int] = deque(range(51, 102, 25)) # up to 100
    chunk3: Deque[int] = deque(range(151, 252, 50)) # up to 250
    chunk4: Deque[int] = deque(range(501, 1002, 250)) # up to 1001
    # concatenate the lists
    allBins: Deque[int] = chunk1 + chunk2 + chunk3 + chunk4
    # add last bin counts >1000
    allBins.append(10001)
    # delete not required bins
    del chunk1, chunk2, chunk3, chunk4

    # create string for the bin columns
    binStrList: List[str] = []
    tmpEdge: str
    for idx, edge in enumerate(list(allBins)[:-1]):
        tmpEdge = str(edge)
        if edge < 26:
            binStrList.append(tmpEdge)
        else: # create a string reprenting the histogram bin
            try:
                if allBins[idx + 1]: # if next element exists
                    binStrList.append('{:s}-{:s}'.format(str(edge), str(allBins[idx + 1] - 1)))
            except IndexError:
                #do what needs to be done in this case.
                pass

    # open the output file
    ofd = open(outPath, 'w')
    ofd.write('{:s}\t{:s}\n'.format(firstCol, '\t'.join(binStrList)))

    for i, col in enumerate(rowNames):
        histCnts, outBins = np.histogram(mtx[i], bins=allBins)
        ofd.write('{:s}\t'.format(col))
        histCnts.tofile(ofd, sep="\t", format="%d")
        ofd.write('\n')
    ofd.close()



def compute_groups_stats(inTbl: str, outDir: str, outNameSuffix: str, seqCnts: Dict[str, int], proteomeSizes: Dict[str, int], debug: bool=False) -> Dict[str, str]:
    """Extract different stats about the ortholog groups."""
    if debug:
        print('\ncompute_groups_stats :: START')
        print('Input clusters:{:s}'.format(inTbl))
        print('Output directory:{:s}'.format(outDir))
        print('Output suffix:{:s}'.format(outNameSuffix))
        print('Sequence counts dictionary:{:d}'.format(len(seqCnts)))
        print('Proteome size dictionary:{:d}'.format(len(proteomeSizes)))
    # keep count of the conflict types
    conflictDict: Dict[str, int] = {'no':0, 'nr':0, 'nm':0}
    if outDir[-1] != '/':
        outDir = '{:s}/'.format(outDir)

    ifd = open(inTbl, 'r')
    # extract the species names
    hdrFldsRx: str = ifd.readline().rstrip('\n').split('\t', 4)[-1]
    spStatsHdr: List[str] = []
    # contains different counts about the clustered genes per species
    spStatsDict: Dict[str, Dict[str, Any]] = {}
    totProteins: int = 0
    totInputSize: int = 0
    # compute the number of required splits (e.g., (#proteomes * 2 + extra_columns) - 1)
    tblCols: int = (len(seqCnts) * 2) + 5

    for i, col in enumerate(hdrFldsRx.split('\t', tblCols-1)[:-1]):
        if i % 2 == 0:
            spStatsHdr.append(col)
            proteinCnt: int = seqCnts[col]
            genomeSize: int = proteomeSizes[col]
            totProteins += proteinCnt
            totInputSize += genomeSize
            spStatsDict[col] = {'ortho_cnt':0, 'inpara_cnt':0, 'seed_pct':0., 'avg_confidence':0., 'protein_count':proteinCnt, 'proteome_size':genomeSize, 'ortho_pct':0., 'grp_cnt':0}

    # add the column with the totals
    spStatsDict['total'] = {'ortho_cnt':0, 'inpara_cnt':0, 'seed_pct':0., 'avg_confidence':0., 'protein_count':totProteins, 'proteome_size':totInputSize, 'ortho_pct':0., 'grp_cnt':0}
    del totProteins
    del totInputSize

    # define the output per species and open it
    outPaths: Dict[str, str] = {}
    outPaths["counts"] = os.path.join(outDir, 'ortholog_counts_per_species.{:s}.tsv'.format(outNameSuffix))
    # now the files with the groups per species sizes (bins)
    # for example, #groups with x genes from species sp
    outPaths["bins"] = os.path.join(outDir, 'species_coverages_in_groups.{:s}.tsv'.format(outNameSuffix))
    outPaths["overall"] = os.path.join(outDir, 'overall.{:s}.tsv'.format(outNameSuffix))
    outFds: List[Any] = []
    outFds.append(open(outPaths["counts"], 'w'))
    outFds[0].write('Group_ID\t{:s}\ttotal\n'.format('\t'.join(spStatsHdr)))

    # temporary variables
    tmpGrpId: str
    tmpGrpSize: int
    tmpSpInGrp: int
    tmpSeedCnt: int
    tblCols = len(seqCnts) * 2
    loopCnt: int = 0
    for ln in ifd:
        tmpGrpId, tmpGrpSize, tmpSpInGrp, tmpSeedCnt, grpsRaw = ln.rstrip('\n').split('\t', 4)
        grpFlds = grpsRaw.split('\t', tblCols)
        conflictDict[grpFlds[-1]] += 1 # increment the count for conflicts
        totCnt: int = 0
        totAvg: float = 0.
        geneCntArr, inparaCntArr, spAvgConfArr, seedRatioArr = compute_single_clstr_stats_numpy(grpFlds[:-1], debug=debug)
        # Write the output files
        # gene counts
        outFds[0].write('{:s}\t'.format(tmpGrpId))
        geneCntArr.tofile(outFds[0], sep="\t", format="%d")
        outFds[0].write('\n')
        # stop the loop
        loopCnt += 1
        if debug:
            if loopCnt % 1000 == 0:
                print('Cluster\t{:d}'.format(loopCnt))
    ifd.close()

    # close the output files
    for fd in outFds:
        fd.close()

    # column names
    colNames: List[str] = list(spStatsDict.keys())
    # do the binning for orthologs (the column with Totals is omitted)
    mtx = np.genfromtxt(outPaths["counts"], dtype=np.uint32, skip_header=1, delimiter="\t", names=None, missing_values=None, filling_values=None, usecols=tuple(range(1, len(colNames) + 1, 1)), excludelist=None, deletechars=None, replace_space='_', unpack=True, usemask=False, loose=True, invalid_raise=True)
    write_binning(outPaths["bins"], mtx[:-1], rowNames=colNames[:-1], firstCol="species/#orthologs_from_species_in_group", debug=debug)

    # count the total number of groups
    totGrps: int = 0
    # calculate the total orthologs for each species
    for i, col in enumerate(colNames):
        # count the total number of groups
        if totGrps == 0:
            totGrps = len(mtx[i])
        spStatsDict[col]['ortho_cnt'] = np.sum(mtx[i])
        inpCnt: int = spStatsDict[col]['ortho_cnt']
        spStatsDict[col]['ortho_pct'] = round(float(inpCnt/spStatsDict[col]['protein_count']) * 100., 3)
        # count in how many groups the species is found
        spStatsDict[col]['grp_cnt'] = np.count_nonzero(mtx[i])
        #print('Groups:\t{:d}'.format(spStatsDict[col]['grp_cnt']))

    # open the file with the overall stats
    ofdStats = open(outPaths["overall"], 'w')
    # dictionary to contain the lines that will be printed out
    printDict: Dict[str, List[Any]] = {}
    # inialize the line names
    printDict['Proteome sizes'] = []
    printDict['Input proteins'] = []
    printDict['Orthologs'] = []
    printDict['Assigned (%)'] = []
    printDict['No orthologs'] = []
    printDict['Groups'] = []
    printDict['Groups (%)'] = []

    # write the hdr with all the column names
    ofdStats.write('info/species\t{:s}\n'.format('\t'.join(colNames)))
    # define some temporary variables
    tmpProtCnt: int = 0
    tmpGenSize: int = 0
    tmpGrpCnt: int = 0
    tmpOrthoCnt: int = 0
    tmpInparaCnt: int = 0
    tmpGrpCnt: int = 0
    tmpTotGrpCnt: int = 0

    for sp, vals in spStatsDict.items():
        # now stats filling the lists with values
        tmpProtCnt = vals['protein_count']
        tmpGenSize = vals['proteome_size']
        tmpOrthoCnt = vals['ortho_cnt']
        tmpInparaCnt = vals['inpara_cnt']
        tmpGrpCnt = vals['grp_cnt']
        # add the values to the lists
        printDict['Input proteins'].append(str(tmpProtCnt))
        printDict['Proteome sizes'].append(str(tmpGenSize))
        printDict['Orthologs'].append(str(tmpOrthoCnt))
        printDict['Assigned (%)'].append(str(round(float(tmpOrthoCnt/tmpProtCnt) * 100., 2)))
        printDict['No orthologs'].append(str(tmpProtCnt-tmpOrthoCnt))
        printDict['Groups'].append(str(tmpGrpCnt))
        printDict['Groups (%)'].append(str(round(float(tmpGrpCnt/totGrps) * 100., 2)))

    # now write the output files
    for row, vals in printDict.items():
        ofdStats.write('{:s}\t{:s}\n'.format(row, '\t'.join(vals)))
    ofdStats.close()
    # return dictionary with the paths
    return outPaths



def compute_groups_stats_no_conflict(inTbl: str, outDir: str, outNameSuffix: str, seqCnts: Dict[str, int], proteomeSizes: Dict[str, int], debug: bool=False) -> Dict[str, str]:
    """Extract different stats about the ortholog groups."""
    if debug:
        print('\ncompute_groups_stats_no_conflict :: START')
        print('Input clusters:{:s}'.format(inTbl))
        print('Output directory:{:s}'.format(outDir))
        print('Output suffix:{:s}'.format(outNameSuffix))
        print('Sequence counts dictionary:{:d}'.format(len(seqCnts)))
        print('Proteome size dictionary:{:d}'.format(len(proteomeSizes)))

    ifd = open(inTbl, 'r')
    # extract the species names and columns with average scores
    hdrFldsRx: str = ifd.readline()[:-1].split('\t', 4)[-1]
    spStatsHdr: List[str] = []
    # contains different counts about the clustered genes per species
    spStatsDict: Dict[str, Dict[str, Any]] = {}
    totProteins: int = 0
    totInputSize: int = 0
    # compute the number of required splits (e.g., (#proteomes * 2 + extra_columns) - 1)
    tblCols: int = (len(seqCnts) * 2) + 3
    for i, col in enumerate(hdrFldsRx.split('\t', tblCols-1)[:-1]):
        if i % 2 == 0:
            spStatsHdr.append(col)
            proteinCnt: int = seqCnts[col]
            genomeSize: int = proteomeSizes[col]
            totProteins += proteinCnt
            totInputSize += genomeSize
            spStatsDict[col] = {'ortho_cnt':0, 'inpara_cnt':0, 'seed_pct':0., 'avg_confidence':0., 'protein_count':proteinCnt, 'proteome_size':genomeSize, 'ortho_pct':0., 'grp_cnt':0}

    # add the column with the totals
    spStatsDict['total'] = {'ortho_cnt':0, 'inpara_cnt':0, 'seed_pct':0., 'avg_confidence':0., 'protein_count':totProteins, 'proteome_size':totInputSize, 'ortho_pct':0., 'grp_cnt':0}
    del totProteins
    del totInputSize
    # define the output per species and open it
    outPathsDict: Dict[str, str] = {}
    outPathsDict["counts"] = os.path.join(outDir, 'ortholog_counts_per_species.{:s}.tsv'.format(outNameSuffix))
    # now the files with the groups per species sizes (bins)
    # for example, #groups with x genes from species sp
    outPathsDict["bins"] = os.path.join(outDir, 'species_coverages_in_groups.{:s}.tsv'.format(outNameSuffix))
    outPathsDict["overall"] = os.path.join(outDir, 'overall.{:s}.tsv'.format(outNameSuffix))
    outFds: List[Any] = []
    outFds.append(open(outPathsDict["counts"], 'wt'))
    outFds[0].write('Group_ID\t{:s}\ttotal\n'.format('\t'.join(spStatsHdr)))
    # temporary variables
    tmpGrpId: str
    tmpGrpSize: int
    tmpSpInGrp: int
    tmpSeedCnt: int
    tblCols = (len(seqCnts) * 2) - 1
    loopCnt: int = 0

    for ln in ifd:
        tmpGrpId, tmpGrpSize, tmpSpInGrp, tmpSeedCnt, grpsRaw = ln.rstrip('\n').split('\t', 4)
        grpFlds = grpsRaw.split('\t', tblCols)
        totCnt: int = 0
        totAvg: float = 0.
        geneCntArr, inparaCntArr, spAvgConfArr, seedRatioArr = compute_single_clstr_stats_numpy(grpFlds, debug=False)
        # Write the output files
        # gene counts
        outFds[0].write('{:s}\t'.format(tmpGrpId))
        geneCntArr.tofile(outFds[0], sep="\t", format="%d")
        outFds[0].write('\n')
        # stop the loop
        loopCnt += 1
        if debug:
            if loopCnt % 1000 == 0:
                print('Processed groups:\t{:d}'.format(loopCnt))
                #sys.exit("DEBUG")
    ifd.close()
    # close the output files
    for fd in outFds:
        fd.close()
    # column names
    colNames: List[str] = list(spStatsDict.keys())
    # do the binning for orthologs (the column with Totals is omitted)
    # mtx contains 1 numpy array for each species with the paralogs counts
    # plus one ndarray for the total counts
    mtx = np.genfromtxt(outPathsDict["counts"], dtype=np.uint32, skip_header=1, delimiter="\t", names=None, missing_values=None, filling_values=None, usecols=tuple(range(1, len(colNames) + 1, 1)), excludelist=None, deletechars=None, replace_space='_', unpack=True, usemask=False, loose=True, invalid_raise=True)
    write_binning(outPathsDict["bins"], mtx[:-1], rowNames=colNames[:-1], firstCol="species/#orthologs_from_species_in_group", debug=debug)

    # count the total number of groups
    totGrps: int = 0
    # calculate the total orthologs for each species
    for i, col in enumerate(colNames):
        # count the total number of groups
        if totGrps == 0:
            totGrps = len(mtx[i])
        spStatsDict[col]['ortho_cnt'] = np.sum(mtx[i])
        paraCnt: int = spStatsDict[col]['ortho_cnt']
        spStatsDict[col]['ortho_pct'] = round(float(paraCnt/spStatsDict[col]['protein_count']) * 100., 3)
        # count in how many groups the species is found
        spStatsDict[col]['grp_cnt'] = np.count_nonzero(mtx[i])

    # open the file with the overall stats
    ofdStats = open(outPathsDict["overall"], 'w')
    # dictionary to contain the lines that will be printed out
    printDict: Dict[str, List[Any]] = {}
    # inialize the line names
    printDict['Proteome sizes'] = []
    printDict['Input proteins'] = []
    printDict['Orthologs'] = []
    printDict['Assigned (%)'] = []
    printDict['No orthologs'] = []
    printDict['Groups'] = []
    printDict['Groups (%)'] = []

    # write the hdr with all the column names
    ofdStats.write('info/species\t{:s}\n'.format('\t'.join(colNames)))
    # define some temporary variables
    tmpProtCnt: int = 0
    tmpGenSize: int = 0
    tmpGrpCnt: int = 0
    tmpOrthoCnt: int = 0
    tmpInparaCnt: int = 0
    tmpGrpCnt: int = 0
    tmpTotGrpCnt: int = 0

    for sp, vals in spStatsDict.items():
        # now stats filling the lists with values
        tmpProtCnt = vals['protein_count']
        tmpGenSize = vals['proteome_size']
        tmpOrthoCnt = vals['ortho_cnt']
        #tmpInparaCnt = vals['inpara_cnt']
        tmpGrpCnt = vals['grp_cnt']
        # add the values to the lists
        printDict['Input proteins'].append(str(tmpProtCnt))
        printDict['Proteome sizes'].append(str(tmpGenSize))
        printDict['Orthologs'].append(str(tmpOrthoCnt))
        printDict['Assigned (%)'].append(str(round(float(tmpOrthoCnt/tmpProtCnt) * 100., 2)))
        printDict['No orthologs'].append(str(tmpProtCnt-tmpOrthoCnt))
        printDict['Groups'].append(str(tmpGrpCnt))
        printDict['Groups (%)'].append(str(round(float(tmpGrpCnt/totGrps) * 100., 2)))

    # now write the output files
    for row, vals in printDict.items():
        ofdStats.write('{:s}\t{:s}\n'.format(row, '\t'.join(vals)))
    ofdStats.close()
    # return dictionary with the paths
    return outPathsDict



def compute_single_clstr_stats_numpy(clstrValues: List[str], debug: bool=False) -> Tuple[Any, Any, Any, Any]:
    """
    Returns the counts of genes per species (seeds and in-paralogs) for the input cluster,
    and average confidence.
    """
    if debug:
        print('\ncompute_single_clstr_stats_numpy :: START')
        print("Raw input cluster fileds: %s"% str(clstrValues))
    # make sure that the number of elements in the verctor is correct
    if len(clstrValues) % 2 != 0:
        sys.exit('ERROR: the number of elements must be a multiple of 2!')
    # start processing
    #tmpAllConfArr = np.zeros((1, int(len(clstrValues)/2)+1) , dtype=np.uint32)
    seedRatioList: List[float] = []
    meanConfList: List[float] = []
    meanInparaConfList: List[float] = []
    # length of main putput arrays
    mainArrayLen = int(len(clstrValues)/2)+1
    # create one dimensional array
    geneCntArr = np.zeros((mainArrayLen,), dtype=np.uint32)
    # inparalog count
    inparaCntArr = np.zeros((mainArrayLen,), dtype=np.uint32)
    # Array with the avergae confidence per species
    spAvgConfArr = np.zeros((mainArrayLen,), dtype=np.float64)
    tmpAllCnt: int = 0
    tmpNotSeedCnt: int = 0
    tmpSeedRatio: float = 0.
    for i, spParalogs in enumerate(clstrValues):
        if i % 2 == 0: # then is the part containing the genes
            paralogs: List[str] = spParalogs.split(',')
            tmpAllCnt: int = len(paralogs)
            # add the gene count to the corresponding array
            arrIdx = int(i/2)
            tmpAllConfArr = np.zeros((tmpAllCnt,) , dtype=np.float64)
            # now extract the confince from all the orthologs
            tmpNotSeedCnt: int = spParalogs.count(':')
            tmpInparaCnt: int = 0
            tmpAllCnt = 0 # reuse to count the seeds
            for j, gene in enumerate(paralogs):
                geneParts = gene.rsplit(':', 1)
                if len(geneParts) > 1: # it is an inparalog
                    tmpAllConfArr[j] = float(geneParts[-1])
                    tmpInparaCnt += 1
                else:
                    if gene[0] == '*':
                        tmpAllConfArr[j] = 0.
                    else:
                        tmpAllCnt += 1
                        tmpAllConfArr[j] = 1.
            # add the average confidence to the output array
            spAvgConfArr[arrIdx] = np.mean(tmpAllConfArr)
            inparaCntArr[arrIdx] = tmpInparaCnt
            # set the count of seeds
            geneCntArr[arrIdx] = tmpAllCnt + tmpInparaCnt

    # compute the totals
    geneCntArr[-1] = np.sum(geneCntArr[:-1])
    inparaCntArr[-1] = np.sum(inparaCntArr[:-1])
    spAvgConfArr[-1] = scpy_stats.tmean(spAvgConfArr[:-1], (0.01, np.max(spAvgConfArr[:-1])))
    # compute the array with the seed ratios
    # the calculation is computed only if the number of inparalogs is > 0
    #seedRatioArr = np.where(geneCntArr > 0, (geneCntArr - inparaCntArr)/geneCntArr, geneCntArr)
    seedRatioArr = (geneCntArr - inparaCntArr)/geneCntArr
    if debug:
        print('Final genes counts:\t{:s}'.format(str(geneCntArr)))
        print('Final InParalog counts:\t{:s}'.format(str(inparaCntArr)))
        print('Final average conf per species:\t{:s}'.format(str(spAvgConfArr)))
        print('Final seed ratio per species:\t{:s}'.format(str(seedRatioArr)))
    # return the arrays
    return (geneCntArr, inparaCntArr, spAvgConfArr, seedRatioArr)



def copy_quickparanoid_files(srcDir, outDir=os.getcwd(), debug=False):
    """Copy the source and binary files for quickparanoid in the output directory."""
    if debug:
        print('copy_quickparanoid_files :: START')
        print('Source directory:\t%s'%srcDir)
        print('QuickParanoid output directory:\t%s'%outDir)
    if os.path.realpath(srcDir) == os.path.realpath(outDir):
        if debug:
            sys.stderr.write('\nINFO: output and source directory are same, no file will be copied.\n')
    else: # copy the files
        # traverse the directory
        for dirPath, dirNames, fNames in os.walk(srcDir):
            # create the output directory if required
            systools.makedir(outDir)
            # copy files
            for f in fNames:
                tmpPath = os.path.join(srcDir, f)
                systools.copy(tmpPath, outDir)



def count_clusters_no_pandas(inTbl, debug=False):
    """Count the clusters with orthologs."""
    from collections import Counter
    tmpDict = {} #will contain the ids
    cnt = Counter()
    #open and read the table file
    for line in open(inTbl):
        if line.startswith('#cl') or line.startswith('clusterID'):
            continue
        line = line.rstrip()
        flds = line.split('\t')
        clstrId = flds[0]
        if not clstrId in tmpDict:
            tmpDict[clstrId] = None
            cnt.update([flds[-1]]) #count the type of conflict
    no_conflict = cnt['No']
    diff_names = cnt['diff. names']
    diff_numbers = cnt['diff. numbers']
    tot_conflicts = diff_names + diff_numbers
    clstrCnt = tot_conflicts + no_conflict
    if debug:
        print('Clusters:\t%d'%clstrCnt)
        print('No conflict:\t%d'%no_conflict)
        print('diff.names conflict:\t%d'%diff_names)
        print('diff.numbers conflict:\t%d'%diff_numbers)
        print('Total conflicts:\t%d'%tot_conflicts)
    #return the main numbers
    return(clstrCnt, no_conflict, diff_names, diff_numbers)



def fetch_sql_files(rootDir=os.getcwd(), outDir=os.getcwd(), pairsFile=None, coreOnly=False, debug=False):
    """Find result SQL tables and copy it to the output directory."""
    import fnmatch
    if debug:
        print('fetch_sql_paths :: START')
        print('Root directory:\t%s'%rootDir)
        print('Output directory:\t%s'%outDir)
        print('Core only:\t%s'%coreOnly)
        print('Species pairs file:\t%s'%pairsFile)
    #check that the input directory is valid
    if not os.path.isdir(rootDir):
        sys.stderr.write('ERROR: the directory containing the inparanoid output files\n%s\n does not exist.\n'%rootDir)
        sys.exit(-2)
    if not os.path.isfile(pairsFile):
        sys.stderr.write('ERROR: you must provide a valid file containing all the species pairs.\n')
        sys.exit(-2)
    # create the output directory if does not exist yet
    if outDir[-1] != '/':
        outDir += '/'
    systools.makedir(outDir)
    # load the species names
    pairs = OrderedDict()
    foundPairs = OrderedDict()
    species = OrderedDict()
    # enter the root directory
    prevDir = os.getcwd()
    os.chdir(rootDir)
    #find the sql files
    fileList = []
    for pair in open(pairsFile):
        pair = pair.rstrip()
        pairs[pair] = None
        sp1, sp2 = pair.split('-')
        species[sp1] = None
        species[sp2] = None
        #make the file paths
        runPath = '%s%s/'%(rootDir, pair)
        sqlName = 'sqltable.%s'%pair
        if os.path.isdir(runPath):
            sqlPath = '%s%s'%(runPath, sqlName)
            if os.path.isfile(sqlPath):
                fileList.append(sqlPath)
                if debug:
                    print(sqlPath)
                foundPairs[pair] = None
    #check that the found tables and the species-pairs count are same
    if len(foundPairs) != len(pairs):
        sys.stderr.write('ERROR: the number found SQL table files (%d) and the number of species pairs (%d) must be the same.\n'%(len(fileList), len(pairs)))
        print('\nMissing SQL tables for pairs:')
        # check which pair is missing
        tmpList = []
        for p in pairs:
            if p not in foundPairs:
                tmpList.append(p)
        print(' '.join(tmpList))
        sys.exit(-2)
    # minimum confidence
    minConf = 0.05
    for el in fileList:
        # filter using the threshold if required
        if minConf > 0.05:
            filter_sql_tbl_by_confidence(el, os.path.join(outDir, os.path.basename(el)), confThr=minConf, debug=debug)
        else:
            systools.copy(el, outDir, metaData=False, debug=debug)
    #reset the current directory to the previous one
    os.chdir(prevDir)
    #return the final list
    return fileList



def filter_sql_tbl_by_confidence(inTbl, outTbl, confThr=0.3, debug=False):
    """Filter sql table to include only homologs above a given threshols."""
    if debug:
        print('filter_sql_tbl_by_confidence :: START')
        print('Input SQL table:\t{:s}'.format(inTbl))
        print('Output SQL table:\t{:s}'.format(outTbl))
        print('Minimum confidence:\t%s'%(str(confThr)))
    if not os.path.isfile(inTbl):
        sys.stderr.write('ERROR: the file with the SQL table \n%s\n does not exist.\n'%inTbl)
        sys.exit(-2)
    if inTbl == outTbl:
        sys.stderr.write('ERROR: the input and output table must be different.\n')
        sys.exit(-5)
    #example of line in sql table
    #1 3993 jcm_1507 1.000 jcm_1507_scaffold_3_gene4130 100%
    ofd = open(outTbl, 'w')
    wCnt = rCnt = 0
    #start reading the input table
    for ln in open(inTbl):
        rCnt += 1
        #ln = ln.rstrip()
        d1, confidence, d2 = ln.rsplit('\t', 2)
        confidence = float(confidence)
        if confidence >= confThr: #core ortholog
            ofd.write('%s\n'%ln)
            wCnt += 1
    if debug:
        print('Read entries:\t%d'%rCnt)
        print('Wrote entries:\t%d'%wCnt)
    ofd.close()



def get_quick_multiparanoid_src_dir():
    """Return the directory in which the binaries and source of quiclparanoid are stored."""
    return multiparanoidSrcDir



def prettify_multispecies_output(inTbl, outDir=os.getcwd(), sharedDir=os.getcwd(), refSpeciesList=[], minScore=0.05, maxGenePerSp=10, debug=False):
    """Prettify the output from quickparanoid and make it more readable."""
    #the origninal input table contains these information:
    #clusterID species gene is_seed_ortholog confidence_score species_in_cluster tree_conflict
    #species_in_cluster and tree_conflict are the same for each entry pf the same clstr
    if debug:
        print('prettify_multispecies_output :: START')
        print('Input table:%s'%inTbl)
        print('Outdir:%s'%outDir)
        print('Directory with shared information (e.g., proteome sizes):\t{:s}'.format(sharedDir))
        print('Species:\t%d'%len(refSpeciesList))
        print('Minimum homolog score:\t%s'%str(minScore))
        print('Maximum number of genes per species:\t{:d}'.format(maxGenePerSp))
    outDict = OrderedDict()
    refSpeciesList.sort()
    if outDir[-1] != '/':
        outDir = '%s/'%outDir
    #start extracting the information
    for ln in open(inTbl):
        if (ln[0] == '#') or (ln[0] == 'c'):
            continue
        ln = ln.rstrip('\n')
        clstrId, sp, gene, isSeedOrtho, score, speciesList, conflict = ln.split('\t', 6)
        clstrId = int(clstrId)
        score = float(score)
        speciesList = speciesList.split('-')
        isSeedOrtho = int(isSeedOrtho)
        if conflict[-2:] == 'rs':
            conflict = 'nr'
        elif conflict[-2:] == 'es':
            conflict = 'nm'
        else:
            conflict = 'no'
        #create the entry in the dictionary
        if not clstrId in outDict:
            #contains: number of species, number of seed orthologs, avg clstr score, dict with genes for each score, conflict type
            outDict[clstrId] = [len(speciesList), 1, score, score, isSeedOrtho, OrderedDict([(sp, OrderedDict([(gene, score)]))]), conflict]
        else:
            # skip entries with score lower than the threshold
            if score < minScore:
                continue
            #update the dictionary with the species and associated genes
            if sp in outDict[clstrId][5]:
                # if the number of genes per species is too high, just skip it
                if len(outDict[clstrId][5][sp]) >= maxGenePerSp:
                    continue
                if not gene in outDict[clstrId][5][sp]: #if the gene is not present already
                    outDict[clstrId][5][sp][gene] = score
                else:
                    sys.stderr.write('\nERROR: attemp of multiple entry for gene %s for species %s\n'%(gene, sp))
            else: #add the new species to the species dictionary
                outDict[clstrId][5][sp] = OrderedDict([(gene, score)])
            # update the other fields
            outDict[clstrId][1] += 1 #increment the entries
            outDict[clstrId][2] += score #increment the total confidence
            outDict[clstrId][3] = (outDict[clstrId][2])/float(outDict[clstrId][1]) #update average score
            outDict[clstrId][4] += isSeedOrtho #incrememnt the seed orthologs count

    # load species ids in dictionary
    notGroupedProteinsDict: Dict[str, List[str]] = {}
    if debug:
        print('Loading pickles with protein IDs...')
    for sp in refSpeciesList:
        pathToPckl = os.path.join(sharedDir, '{:s}.ids.pckl'.format(sp))
        notGroupedProteinsDict[sp] = pickle.load(open(pathToPckl, 'rb'))

    # create datapoints file with the count for each cluster size (number of species in clstr)
    bsName = os.path.basename(inTbl)
    bsName = bsName.rsplit('.')[0]
    mainOutPath = '{:s}tmp_{:s}.tsv'.format(outDir, bsName)
    # this file contains 1 cluster per line without scores
    flatNoScoreOutPath = '{:s}flat.{:s}.tsv'.format(outDir, bsName)
    # write the main output table
    ofd = open(mainOutPath, 'w')
    spNamesInHdr = ['%s\tavg_score_sp%d'%(x, i+1) for i, x in enumerate(refSpeciesList)]
    ofd.write('group_id\tgroup_size\tsp_in_grp\tseed_ortholog_cnt\t%s\tconflict\n'%('\t'.join(spNamesInHdr)))
    del spNamesInHdr
    # open the second output file and write the header
    ofd2 = open(flatNoScoreOutPath, 'w')
    ofd2.write('group_id\t{:s}\n'.format('\t'.join(refSpeciesList)))
    #sort the tmpDict by size
    for k in outDict:
        size = outDict[k][0]
        entries = outDict[k][1]
        avg_score = str(round(outDict[k][3], 3))
        #sort the dictionary of each species by score
        spGenesDict = outDict[k][5]
        # will contain the elements for the final string
        tmpGenesPerSpecies = []
        # will contain orthologs without scores for the flat output
        tmpGenesNoScores = []
        #generate the string with genes and scores per species
        for spName in refSpeciesList:
            if not spName in spGenesDict:
                # create and empty string
                tmpGenesPerSpecies.append('*\t0')
                tmpGenesNoScores.append('*')
            else: #add the informations
                avgScoreVal = '1'
                confValues = list(spGenesDict[spName].values())
                geneNames = list(spGenesDict[spName].keys())
                if len(spGenesDict[spName]) > 1:
                    #calculate the average score
                    confValues = list(spGenesDict[spName].values())
                    avgScoreVal = round(np.mean(confValues), 3)
                    if avgScoreVal == 1:
                        avgScoreVal = "1"
                    else:
                        avgScoreVal = str(avgScoreVal)
                #create the substring with the info about specis spName
                tmpSubStrList = []
                tmpSubStrNoScores = []
                for i, gname in enumerate(geneNames):
                    tmpSubStrNoScores.append(gname)
                    # remove the gene from the list with grouped genes
                    notGroupedProteinsDict[spName].remove(gname)
                    if confValues[i] == 1.:
                        tmpSubStrList.append(gname)
                    else:
                        tmpSubStrList.append('%s:%s'%(gname, str(confValues[i])))
                #join the substring
                joinedSubstr = ','.join(tmpSubStrList)
                tmpGenesPerSpecies.append('{:s}\t{:s}'.format(joinedSubstr, avgScoreVal))
                tmpGenesNoScores.append('{:s}'.format(','.join(tmpSubStrNoScores)))
        # extract the variables that will be printed
        seedCnt = outDict[k][4]
        conflict = outDict[k][6]
        # write the main output
        ofd.write('%d\t%d\t%d\t%d\t%s\t%s\n'%(k, entries, len(spGenesDict), seedCnt, '\t'.join(tmpGenesPerSpecies), conflict))
        # write on the flat file
        ofd2.write('{:d}\t{:s}\n'.format(k, '\t'.join(tmpGenesNoScores)))
    ofd.close()
    ofd2.close()

    # open and write the file with proteins that could not be grouped
    ofd = open('{:s}not_assigned_genes.{:s}.tsv'.format(outDir, bsName), 'w')
    # print the number of not grouped proteins
    for sp, gList in notGroupedProteinsDict.items():
        # write the species name
        ofd.write('#{:s}\n'.format(sp))
        for unassigned in gList:
            ofd.write('{:s}\n'.format(unassigned))
        ofd.write('\n')
    ofd.close()
    # print final information
    if debug:
        print('Total clstrs:\t%d'%(len(outDict)))
        print('Output file:\t%s'%(mainOutPath))
    return mainOutPath



def run_quickparanoid(sqlTblDir=os.getcwd(), outDir=os.getcwd(), sharedDir=os.getcwd(), srcDir=None, outName=None, maxGenePerSp=20, debug=False):
    """Prepare configuration file for quickparanoid and execute it."""
    if debug:
        print("\nrun_quickparanoid :: START")
        print("Input SQL tables directory:\t%s"%sqlTblDir)
        print("QuickParanoid output directory:\t%s"%outDir)
        print("Directory with input sizes and species info:\t{:s}".format(sharedDir))
        print("Directory with binaries for quick MultiParanoid:\t%s"%srcDir)
        print("Output cluster name:\t%s"%outName)

    # set path to the species file
    speciesFile = os.path.join(sharedDir, "species.tsv")
    # check that quickparanoid binaries are available
    if srcDir is None:
        sys.stderr.write("ERROR: you must provide the path to the directory containing quick multiparanoid files\n")
        sys.exit(-5)
    #check that the input directory is valid
    if not os.path.isdir(sqlTblDir):
        sys.stderr.write("ERROR: the directory containing the ortholog tables \n%s\n does not exist.\n"%sqlTblDir)
        sys.exit(-2)
    if not os.path.isfile(speciesFile):
        sys.stderr.write("ERROR: you must provide a file containing all the species names\n")
        sys.exit(-2)
    #load the species names
    species = []
    for ln in open(speciesFile, "rt"):
        species.append(ln.split("\t", 1)[0])
    #check that the species list not empty
    if len(species) < 2:
        sys.stderr.write("ERROR: the list with species names must contain at least 2 species names.\n")
        sys.exit(-4)
    #create the output directory if does not exist yet
    if outDir[-1] != "/":
        outDir += "/"
    systools.makedir(outDir)
    # copy the files
    copy_quickparanoid_files(srcDir=srcDir, outDir=outDir, debug=debug)
    #change the mode foe the main executable file qp, qa1 and qa2
    qp = "%sqp"%outDir
    config = "%sconfig"%outDir
    #write the species names in the config file
    ofd = open(config, "w")
    for el in species:
        ofd.write("%s\n"%el)
    ofd.close()
    #enter the root directory
    prevDir = os.getcwd()
    os.chdir(outDir)
    # Run quickparanoid
    # EXAMPLE: ./qp
    print("\nCreating multi-species ortholog groups...")
    #process = subprocess.Popen(qp, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    process = Popen(qp, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    if debug:
        if stdout_val is not None:
            print("\nQuickparanoid compile script STDOUT:\n%s"%str(stdout_val.decode()))
        if stderr_val is not None:
            print("\nQuickparanoid compile script STDERR:\n%s"%str(stderr_val.decode()))
    process.wait()
    #now generate the clusters
    qpBin = "%stest"%outDir
    outClstrPath = outDir
    if outName is None:
        outName = "ortholog_groups.tsv"
    outClstrPath = "%s%s"%(outDir, outName)
    cmd = "%s"%(qpBin)
    if debug:
        print(cmd)
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    # open the output file and write the clusters in it
    tmpOfd = open(outClstrPath, "w")
    tmpOfd.write(stdout_val.decode())
    tmpOfd.close()
    if debug:
        if stdout_val is not None:
            print("\nQuickparanoid clustering STDOUT:\n%s"%str(stdout_val.decode()))
        if stderr_val is not None:
            print("\nQuickparanoid clustering STDERR:\n%s"%str(stderr_val.decode()))
    process.wait()
    #fix the hdr in quickparanoid output
    tmpClstr = "%stmp_cstrs.txt"%outDir
    ofd = open(tmpClstr, "w")
    for ln in open(outClstrPath):
        if ln[0] == "#": # this is the hdr
            ln = ln.rstrip()
            ofd.write("%s\n"%ln[1:])
        else:
            ofd.write(ln)
    ofd.close()
    systools.move(tmpClstr, outClstrPath, debug=debug)
    #remove the sql tables, and other not required files
    reduntand_files = ["qa1", "qa2","qp", "dump", "Makefile", "Makefile.in"]
    reduntand_files.append("test")
    reduntand_files.append("tests")
    reduntand_files.append("gen_header")
    for fname in os.listdir(outDir):
        if fname.startswith("sqltable.") or fname in reduntand_files:
            os.remove(os.path.join(outDir, fname))
    # reset working directory
    os.chdir(prevDir)
    # prettify the output
    prettyOutPath = prettify_multispecies_output(outClstrPath, outDir=outDir, sharedDir=sharedDir, refSpeciesList=species, minScore=0.05, maxGenePerSp=maxGenePerSp, debug=debug)
    # remove the old file and rename the pretty output
    os.remove(outClstrPath)
    move(prettyOutPath, outClstrPath)
    # load the pickle with input sizes
    genomeSizesDict = pickle.load(open(os.path.join(sharedDir, "proteome_sizes.pckl"), "rb"))
    seqCntsDict = pickle.load(open(os.path.join(sharedDir, "protein_counts.pckl"), "rb"))
    # extract stats
    statPaths = compute_groups_stats(inTbl=outClstrPath, outDir=outDir, outNameSuffix="groups", seqCnts=seqCntsDict, proteomeSizes=genomeSizesDict, debug=debug)
    return (outClstrPath, statPaths)
