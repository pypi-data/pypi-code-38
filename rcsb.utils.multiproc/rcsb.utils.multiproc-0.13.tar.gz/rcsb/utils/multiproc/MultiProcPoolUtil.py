##
# File:    MultiProcPoolUtil.py
# Author:  J. Westbrook
# Date:    20-Dec-2018
# Version: 0.001
#
# Updates:
#  23-Mar-2019 jdw handle nonhashable data lists
##
"""
Multiprocessing execution wrapper using process pools supporting tasks with list of inputs and a variable
number of output lists.

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import contextlib
import logging
import multiprocessing
from functools import partial

logger = logging.getLogger(__name__)


class MultiProcPoolUtil(object):
    def __init__(self, verbose=True):
        self.__verbose = verbose
        self.__workerFunc = None
        self.__optionsD = {}
        self.__workingDir = "."
        self.__loggingMP = True
        self.__sentinel = None

    def setOptions(self, optionsD):
        """ A dictionary of options that is passed as an argument to the worker function
        """
        self.__optionsD = optionsD

    def setWorkingDir(self, workingDir):
        """ A working directory option that is passed as an argument to the worker function.
        """
        self.__workingDir = workingDir

    def set(self, workerObj=None, workerMethod=None):
        """  WorkerObject is the instance of object with method named workerMethod()

             Worker method must support the following prototype -

             sucessList,resultList,diagList=workerFunc(runList=nextList, procName, optionsD, workingDir)
        """
        try:
            self.__workerFunc = getattr(workerObj, workerMethod)
            return True
        except AttributeError:
            logger.error("Object/attribute error")
            return False

    ##
    def runMulti(self, dataList=None, numProc=0, numResults=1, chunkSize=0):
        """ Start  a pool of 'numProc' worker methods consuming the input dataList -

            Divide the dataList into sublists/chunks of size 'chunkSize'
            if chunkSize <= 0 use chunkSize = numProc

            sucessList,resultList,diagList=workerFunc(runList=nextList, procName, optionsD, workingDir)

            Returns,   successFlag true|false
                       failList (data from the inut list that was not successfully processed)
                       resultLists[numResults] --  numResults result lists
                       diagList --  unique list of diagnostics --

        """
        #
        retLists = []
        successList = []
        diagList = []
        try:
            procName = "temp"
            if numProc < 1:
                numProc = multiprocessing.cpu_count() * 2

            lenData = len(dataList)
            numProc = min(numProc, lenData)
            chunkSize = min(lenData, chunkSize)
            #
            if chunkSize <= 0:
                numLists = numProc
            else:
                numLists = int(lenData / int(chunkSize))
            #
            subLists = [dataList[i::numLists] for i in range(numLists)]
            #
            if subLists is not None and subLists:
                logger.info("Running with numProc %d subtask count %d subtask length ~ %d", numProc, len(subLists), len(subLists[0]))
            #
            #
            pFunc = partial(self.__workerFunc, procName=procName, optionsD=self.__optionsD, workingDir=self.__workingDir)
            #
            # start numProc worker processes
            with contextlib.closing(multiprocessing.Pool(processes=numProc)) as pool:
                retTupList = pool.map(pFunc, subLists)  # pylint: disable=no-member
                logger.info("Map completed result length %d %r", len(retTupList), type(retTupList))

            #
            logger.debug("rTup is %r", retTupList)
            #
            retLists = [[] for ii in range(numResults)]
            for retTup in retTupList:
                successList.extend(retTup[0])
                for ii in range(numResults):
                    retLists[ii].extend(retTup[ii + 1])
                diagList.extend(retTup[-1])
            #

            logger.info("Input task length %d success length %d retLists len %d diagList len %d ", len(dataList), len(successList), len(retLists), len(diagList))
            #

            if len(dataList) == len(successList):
                logger.info("Complete run  - input task length %d success length %d", len(dataList), len(successList))
                return True, [], retLists, diagList
            else:
                # logger.debug("data list %r", dataList[:4])
                # logger.debug("successlist %r", successList[:4])
                failList = list(set(dataList) - set(successList))
                logger.info("Incomplete run  - input task length %d success length %d fail list %d", len(dataList), len(successList), len(failList))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False, failList, retLists, diagList

    def runMultiAsync(self, dataList=None, numProc=0, numResults=1, chunkSize=1):
        """ Start  a pool of 'numProc' worker methods consuming the input dataList -

            Divide the dataList into sublists/chunks of size 'chunkSize'
            if chunkSize <= 0 use chunkSize = numProc

            sucessList,resultList,diagList=workerFunc(runList=nextList, procName, optionsD, workingDir)

            Returns,   successFlag true|false
                       failList (data from the inut list that was not successfully processed)
                       resultLists[numResults] --  numResults result lists
                       diagList --  unique list of diagnostics --

        """
        #
        retLists = []
        successList = []
        diagList = []
        failList = []
        try:
            procName = "temp"
            if numProc < 1:
                numProc = multiprocessing.cpu_count() * 2

            lenData = len(dataList)
            numProc = min(numProc, lenData)

            #
            pFunc = partial(self.__workerFunc, procName=procName, optionsD=self.__optionsD, workingDir=self.__workingDir)
            #
            # start numProc worker processes
            with contextlib.closing(multiprocessing.Pool(processes=numProc)) as pool:
                aSyncMapResult = pool.map_async(pFunc, dataList, chunksize=chunkSize)  # pylint: disable=no-member
                retTupList = aSyncMapResult.get()

            #
            logger.debug("rTup is %r", retTupList)
            #
            retLists = [[] for ii in range(numResults)]
            for retTup in retTupList:
                successList.extend(retTup[0])
                for ii in range(numResults):
                    retLists[ii].extend(retTup[ii + 1])
                diagList.extend(retTup[-1])
            #

            logger.info("Input task length %d success length %d retLists len %d diagList len %d ", len(dataList), len(successList), len(retLists), len(diagList))

            #
            if len(dataList) == len(successList):
                logger.info("Complete run  - input task length %d success length %d", len(dataList), len(successList))
                return True, [], retLists, diagList
            else:
                # logger.debug("data list %r " % dataList[:4])
                # logger.debug("successlist %r " % successList[:4])
                # failList = list(set(dataList) - set(successList))
                failList = self.__diffList(dataList, successList)
                logger.info("Incomplete run  - input task length %d success length %d fail list %d", len(dataList), len(successList), len(failList))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False, failList, retLists, diagList

    def __diffList(self, l1, l2):
        """ List difference -  elements in l1 not in l2
        """
        try:
            return list(set(l1) - set(l2))
        except TypeError:
            try:
                idD1 = {id(t): ii for ii, t in enumerate(l1)}
                idD2 = {id(t): ii for ii, t in enumerate(l2)}
                idDifL = list(set(idD1.keys()) - set(idD2.keys()))
                return [l1[idD1[ind]] for ind in idDifL]
            except Exception as e:
                logger.exception("Failing with %s", str(e))
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return []
