#!/usr/bin/python3

"""
moiety_modeling.analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides several classes to analyze the optimization results, select the optimal model, and visualize the
results. The :class:`~moiety_modeling.analysis.ResultAnalysis` class is responsible for generating general statistics
from the optimization results. The :class:`~moiety_modeling.analysis.ModelRank` class selects the model that best
reflects the observed isotopologue profile. The :class:`~moiety_modeling.analysis.ComparisonTable` class compares
the optimal model selected under different optimization settings. The :class:`~moiety_modeling.analysis.PlotMoietyDistribution`
class plots the distribution of moiety value of the moiety model. The :class:`~moiety_modeling.analysis.PlotIsotopologueIntensity`
class plots comparison of the observed and the calculated isotopologue intensity.

"""


import jsonpickle
import math
import functools
import operator
import statistics as sta
import os
import collections
import csv
import sys
import numpy as np
import matplotlib.pyplot as plt


class ResultsAnalysis:

    """ResultsAnalysis class performs the analysis of moiety model optimization results."""

    def __init__(self, filename, path=None):
        """ResultsAnalysis initializer.

        :param str filename: the filenames of optimization results file.
        :param str path: the path to store the analysis results.
        """
        self.path = path if path is not None else os.path.dirname(filename) + '/'
        with open(filename) as file:
            data = jsonpickle.decode(file.read(), keys=True)
        self.model = data['model']
        self.datasets = data['datasets']
        self.bestGuesses = data['bestGuesses']
        self.optimizationSetting = data['optimizationSetting']
        self.energyFunction = data['energyFunction']
        self.jsonfilePath = None

    def analyze(self):
        """Analyze the optimization results for each model.

        :return dict: the analysis results.
        """
        #calculate the energies.
        energy = [ bestGuess.energy for bestGuess in self.bestGuesses ]

        # calculate the moiety values from best guess.
        moietyValues = []
        # the moietyValues is a list of dictionary. Each dictionary contains the moiety value of a guess, which is also a dictionary. eg[ {datasetName: {}, }, ....]
        for bestGuess in self.bestGuesses:
            moietyValue = {}
            for i in range(len(self.datasets)):
                subVector = [bestGuess.elements[i] for i in range(i* self.model.parameterNum, (i+1) * self.model.parameterNum)]
                moietyValue[self.datasets[i].datasetName] = self.model.calculateMoietyState(subVector)
            moietyValues.append(moietyValue)
        # print(moietyValues[0])

        RSS = []  # this stores the sum of diff square for each optimization result.
        calculatedMolecules = collections.defaultdict(list) # this is a list of calculated molecules for each guess.
        for moietyValue in moietyValues:
            rss = collections.defaultdict(lambda: 0)
            for ds in range(len(self.datasets)):
                dataset = self.datasets[ds]
                dsResidual = 0
                for molecule in self.model.molecules:
                    calculatedMolecule = self._calculateMolecule(molecule, moietyValue[dataset.datasetName])
                    residuals = self._calculateResiduals(molecule, dataset, calculatedMolecule)
                    name = 'DS{0}.{1}'.format(dataset.datasetName, molecule.name)
                    dsResidual += self._calculateRSS(residuals)
                    calculatedMolecules[name].append(calculatedMolecule)
                rss[dataset.datasetName] = dsResidual
            RSS.append(rss)  # one rss for each set of moietyValues separate by the dataset name.

        moietyStats = self._calcualteMoietyStats(moietyValues)

        RSS_AIC = []
        RSS_AICc = []
        BIC = []
        paramsNum = self.model.parameterNum * len(self.datasets)
        dataNum = 0
        for dataset in self.datasets:
            for moleculeName in dataset.keys():
                dataNum += len(dataset[moleculeName])
        for rss in RSS:
            rssSum = sum([rss[key] for key in rss])
            RSS_AIC.append(self._calculateAIC(rssSum, paramsNum, dataNum))
            RSS_AICc.append(self._calculateAICc(rssSum, paramsNum, dataNum))
            BIC.append(self._calculateBIC(rssSum, paramsNum, dataNum))

        optimizeParams = {'AIC': self._calculateMeanStdMaxMin(RSS_AIC), 'AICc': self._calculateMeanStdMaxMin(RSS_AICc), 'BIC': self._calculateMeanStdMaxMin(BIC), 'energy': self._calculateMeanStdMaxMin(energy)}

        # write the descriptive stats results for readability.
        scriptFile = open('{0}{1}_{2}_{3}_Descriptive_Stats.txt'.format(self.path, self.model.name, self.optimizationSetting, self.energyFunction), 'w')
        scriptFile.write("Descriptive Statistics of {0} using {1} and {2} energy function \n\n".format(self.model.name, self.optimizationSetting, self.energyFunction))
        scriptFile.write("Moiety States Statistical Results: \n")

        for dataset in moietyStats:
            scriptFile.write(" Datasets: {0}\n".format(dataset))
            for moietyState in moietyStats[dataset]:
                scriptFile.write("     {0}: {1}\n".format(moietyState, moietyStats[dataset][moietyState]))

        scriptFile.write("\nCalculated Molecule Statistical Results: \n")
        calculatedMoleculesStats = {molecule: {} for molecule in calculatedMolecules.keys()}

        for molecule in calculatedMolecules.keys():
            scriptFile.write(" Calculated {0}:\n".format(molecule))
            # calculateMolecules[molecule] is a list containing results of each optimization. Each item in the list is a dictionary containing all the isotopologues of this molecule.
            for isotopologue in calculatedMolecules[molecule][0].keys():
                isotopologueList = [thisMolecule[isotopologue] for thisMolecule in calculatedMolecules[molecule]]
                stats = self._calculateMeanStdMaxMin(isotopologueList)
                calculatedMoleculesStats[molecule][isotopologue] = stats
                scriptFile.write("     Calculated {0}[{1}]: {2}\n".format(molecule, isotopologue, stats))

        scriptFile.write("\nAverage RSS, RSS_AIC, RSS_AICc, and BIC.\n")
        for key in optimizeParams:
            scriptFile.write(" {0}: {1}\n".format(key, optimizeParams[key]))
        scriptFile.close()

        # write the analysis results into JSON file for reusability.
        self.jsonfilePath = '{0}{1}_{2}_{3}_Stats.json'.format(self.path, self.model.name, self.optimizationSetting, self.energyFunction)
        with open(self.jsonfilePath, 'w') as outJSONfile:
            outJSONfile.write(jsonpickle.encode({'model': self.model.name, 'optimizeParams': optimizeParams, 'moietyValues': moietyValues, 'calculatedMolecules': calculatedMoleculesStats, 'datasets': self.datasets, "optimizationSetting": self.optimizationSetting, 'energyFunction': self.energyFunction}))

        return {'optimizeParams': optimizeParams, 'moietyValues': moietyValues, 'calculatedMolecules': calculatedMoleculesStats}

    def _calculateMolecule(self, molecule, moietyStateValue):

        """To calculate of the energy of the model.

        :param moietyStateValue: the list of value of the moietyStates.
        :return: the energy of the model.
        """

        calculated = collections.defaultdict(lambda: 0)
        for isotopologue in molecule.standardStates:
            calculated[isotopologue] = sum(functools.reduce(operator.mul, [moietyStateValue[i] for i in isotopomer]) for isotopomer in molecule.standardStates[isotopologue])
        return calculated

    def _calculateResiduals(self, molecule, dataset, calculatedMolecules):

        """
        To calculate the residuals of the molecule based on the observed value and observed value.
        :param molecule: the molecule that is checked.
        :param dataset: the dataset that contain the observed value of the molecule.
        :param calculatedMolecules: the calculated values of the molecule.
        :return: the residuals.
        """

        residuals = {}
        observed = dataset[molecule.name] # this is a list
        for isotopologue in observed:
            residuals[isotopologue['labelingIsotopes']] = isotopologue['height'] - calculatedMolecules[isotopologue['labelingIsotopes']]
        return residuals

    def _calculateRSS(self, residuals):

        """
        To calculate the rss of the residuals.
        :param residuals: the residuals
        :return: rss
        """

        return sum([residuals[key] ** 2 for key in residuals.keys()])

    def _calcualteMoietyStats(self, moietyValues):

        """
        To calculate the stats of the moieties for each dataset.
        :param moietyValues: the list of moiety values. [{datasetName: {a[0]: 0.01}, }, {}, ]
        :return: the dictionary of moiety value.
        """

        averagedParams = {dataset.datasetName: {} for dataset in self.datasets}
        for dataset in self.datasets:
            for moiety in moietyValues[0][dataset.datasetName].keys():
                moietyValueList= [moietyValue[dataset.datasetName][moiety] for moietyValue in moietyValues]
                averagedParams[dataset.datasetName][moiety] = self._calculateMeanStdMaxMin(moietyValueList)
        return averagedParams

    def _calculateMeanStdMaxMin(self, list):

        """
        To calculate the mean, std, max and min of the list.
        :param list: a list of value.
        :return: dictionary of count, mean, std, max and min.
        """

        count = len(list)
        mean = sum(list)/count
        std = sta.stdev(list)
        maxValue = max(list)
        minValue = min(list)
        stat = {'count': count, 'mean': mean, 'std': std, 'max': maxValue, 'min': minValue}
        return stat

    def _calculateAIC(self, rss, paramsNum, dataNum):

        """
        To calculate the Akaike Information Criterion.
        :param rss: residual sum of squares.
        :param paramsNum: number of parameters (degrees of freedom).
        :param dataNum: number of data points.
        :return: the AIC value.
        """

        return 2 * paramsNum + dataNum * math.log(rss/dataNum)

    def _calculateAICc(self, rss, paramsNum, dataNum):

        """
        Calculate the corrected Akaike Information Criterion. AICc is useful when dataNum is not many times more than paramsNum^2.
        :param rss: residual sum of squares.
        :param paramsNum: number of parameters (degrees of freedom).
        :param dataNum: number of data points.
        :return: the AICc value.
        """

        return self._calculateAIC(rss, paramsNum, dataNum) + (2 * paramsNum * (paramsNum + 1)) / (dataNum - paramsNum -1)

    def _calculateBIC(self, rss, paramsNum, dataNum):

        """
        To calculate the Bayesian Information Criterion.
        :param rss: residual sum of square.
        :param paramsNum: number of parameters (degrees of freedom).
        :param dataNum: number of data points.
        :return: the BIC value.
        """

        return dataNum * math.log(rss/dataNum) + paramsNum * math.log(dataNum)


class ModelRank:

    """ModelRank class ranks the models according to the selection criteria."""

    def __init__(self, pathFile, path, selectionCriterion):
        """ModelRank initializer.

        :param str pathFile: the txt file containing paths to the model analysis results.
        :param str path: the path to store the model rank results.
        :param str selectionCriterion: the selection criteria (eg: AIC, BIC, BICc).
        """
        self.selectionCriterion = selectionCriterion
        self.path = path if path is not None else '{0}/model_rank_{1}/'.format(os.path.dirname(pathFile), self.selectionCriterion)
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.pathFile = pathFile

    def rank(self):
        """To rank the models according to the selection criteria.

        :return list: the rank results.
        """

        dataCollection = {}
        energyFunction = None
        optimizationSetting = None

        with open(self.pathFile) as pathFile:
            for filename in pathFile:
                filename = filename.replace("\n", "")
                with open(filename) as file:
                    data = jsonpickle.decode(file.read())
                    # keys are the AIC, AICc, BIC and energy.
                    dataCollection[data['model']] = data['optimizeParams'][self.selectionCriterion]['mean']
                    if energyFunction is None:
                        energyFunction = data['energyFunction']
                    else:
                        if energyFunction != data['energyFunction']:
                            sys.exit("Models cannot be compared with different energyFunction!")
                    if optimizationSetting is None:
                        optimizationSetting = data['optimizationSetting']
                    else:
                        if optimizationSetting != data['optimizationSetting']:
                            sys.exit("Models cannot be compared with different optimizationSetting!")

        # the sorted function return the ordered items in the dictionary, each item is a set of key and value, like (key, value).
        rankedData = sorted(dataCollection.items(), key=operator.itemgetter(1))

        with open('{0}Model_rank_on_{1}.json'.format(self.path, self.selectionCriterion), 'w') as outFile:
            outFile.write(jsonpickle.encode({'rank': rankedData, 'selectionCriteria': self.selectionCriterion, 'optimizationSetting': optimizationSetting, 'energyFunction': energyFunction}))

        with open('{0}Model_rank_on_{1}.txt'.format(self.path, self.selectionCriterion), 'w') as outFile:
            outFile.write("Model rank of {0} based on model selection criteria.\n".format(self.selectionCriterion))
            for data in rankedData:
                outFile.write('{0}: optimizeParams: {1} \n'.format(data[0], data[1]))

        return rankedData


class ComparisonTable:

    """
    ComparisonTable class collects the best and second best models under different optimization settings.
    """

    def __init__(self, pathFile, path):
        """ComparisonTable initializer.

        :param str pathFile: the filenames of model rank at different situations.
        :param str path: the path to directory that stores the result.
        """

        self.path = path if path is not None else os.path.dirname(pathFile) + '/'
        self.pathFile = pathFile

    def makeTable(self):

        """To make the comparison table under different optimization settings.

        :return: None
        :rtype: :py:obj:`None`
        """

        dataCollection = {}
        energyFunction = None
        selectionCriteria = None

        with open(self.pathFile) as pathFile:
            for filename in pathFile:
                filename = filename.replace("\n", "")
                with open(filename) as file:
                    data = jsonpickle.decode(file.read())
                    dataCollection[data['optimizationSetting']] = [data['rank'][i] for i in range(2)]
                    if energyFunction is None:
                        energyFunction = data['energyFunction']
                    else:
                        if energyFunction != data['energyFunction']:
                            sys.exit("The analysis results have different energy function!")
                    if selectionCriteria is None:
                        selectionCriteria = data['selectionCriteria']
                    else:
                        if selectionCriteria != data['selectionCriteria']:
                            sys.exit("The analysis results have different selection criteria!")

        with open('{0}Comparison_table_of_optimization_parameter_based_on_{1}_with_{2}_energy_function.csv'.format(self.path, selectionCriteria, energyFunction), 'w') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=',')
            csvWriter.writerow('Energy function: {0}'.format(energyFunction))
            csvWriter.writerow('Selection criteria: {0}'.format(selectionCriteria))
            csvWriter.writerow(['optimizationParameter', '1st model', selectionCriteria, '2nd model', selectionCriteria, 'abs_diff', 'relative_diff'])
            for rank in dataCollection:
                firstModel = dataCollection[rank][0][0]
                secondModel = dataCollection[rank][1][0]
                diff = abs(dataCollection[rank][0][1] - dataCollection[rank][1][1])
                relativeDiff = diff / abs(dataCollection[rank][1][1])
                csvWriter.writerow([rank, firstModel, dataCollection[rank][0][1], secondModel, dataCollection[rank][1][1], diff, relativeDiff])


class PlotMoietyDistribution:

    """
    PlotMoietyDistribution class plots the moiety state distribution of the optimization results.
    """

    def __init__(self, filename, path):
        """PlotMoietyDistribution initializer.

        :param str filename: the json file of model analysis results.
        :param str path: the path to store the plot results.
        """
        self.filename = filename
        self.path = path

    def plotMoiety(self):
        """To plot the distribution of moiety states.

        :return: None
        :rtype: :py:obj:`None`
        """
        with open(self.filename) as file:
            data = jsonpickle.decode(file.read())
            model = data['model']
            optimizationSetting = data['optimizationSetting']
            energyFunction = data['energyFunction']
            moietyValues = data['moietyValues']
            moietyCollections = {}
            for dataset in moietyValues[0].keys():
                for moietyState in moietyValues[0][dataset].keys():
                    moietyValueList = [moietyValue[dataset][moietyState] for moietyValue in moietyValues]
                    moietyCollections['DS{0}.{1}'.format(dataset, moietyState)] = moietyValueList
            nPlots = len(moietyCollections)
            labels = sorted(moietyCollections.keys())
            for i in range(nPlots):
                value = moietyCollections[labels[i]]
                plt.subplot(int(nPlots/5)+1, 5, i+1)
                plt.hist(value, 30, range=[0,1], align='mid', alpha=0.5, density=True)
                plt.xlabel("Moiety Value")
                plt.ylabel("Counts")
                plt.title("{0}".format(labels[i]), fontsize=10)
            plt.suptitle('Moiety value histogram of model {0} with {1} optimization setting and {2} energy function'.format(model, optimizationSetting, energyFunction))
            plt.tight_layout()
            plt.show()


class PlotIsotopologueIntensity:

    """
    PlotIsotopologueIntensity class plots the comparison of calculated and observed isotoplogue intensity.
    """

    def __init__(self, filename, path):
        """PlotIsotopologueIntensity initializer.

        :param str filename: The json file of model analysis results.
        :param str path: the path to store the plot results.
        """
        self.filename = filename
        self.path = path

    def plotIsotopologue(self):
        """To plot the comparison of observed and calculated isotoplogue intensities.

        :return: None
        :rtype: :py:obj:`None`
        """
        with open(self.filename) as file:
            data = jsonpickle.decode(file.read())
            calculatedMolecules = data['calculatedMolecules']
            observedMolecules = data['datasets']
        molecules = calculatedMolecules.keys()
        calValue = {molecule :{} for molecule in molecules}
        calStd = {molecule: {} for molecule in molecules}
        obsValue = {molecule: {} for molecule in molecules}
        obsStd = {molecule: {} for molecule in molecules}
        for molecule in molecules:
            for isotopologue in calculatedMolecules[molecule].keys():
                calValue[molecule][isotopologue] = calculatedMolecules[molecule][isotopologue]['mean']
                calStd[molecule][isotopologue] = calculatedMolecules[molecule][isotopologue]['std']

        for dataset in observedMolecules:

            for molecule in dataset:
                name = 'DS{0}.{1}'.format(dataset.datasetName, molecule)
                if name in molecules:
                    for isotopologue in dataset[molecule]:
                        obsValue[name][isotopologue['labelingIsotopes']] = isotopologue['height']
                        obsStd[name][isotopologue['labelingIsotopes']] = isotopologue['heightSE']

        for molecule in molecules:
            labels = sorted(calValue[molecule].keys())
            calPerformance = [calValue[molecule][label] for label in labels]
            calMoleculeSta = [calStd[molecule][label] for label in labels]
            obsPerformance = [obsValue[molecule][label] for label in labels]
            obsMoleculeSta = [obsStd[molecule][label] for label in labels]
            fig, ax = plt.subplots()
            index = np.arange(len(labels))
            barWidth = 0.2
            opacity = 0.4
            errorConfig = {"ecolor": '0.3'}
            rects1 = plt.bar(index, calPerformance, barWidth, alpha=opacity, color='b', yerr=calMoleculeSta, error_kw=errorConfig, label='calculated' )
            rects2 = plt.bar(index+barWidth, obsPerformance, barWidth, alpha=opacity, color='r', yerr=obsMoleculeSta, error_kw=errorConfig, label='observed' )
            plt.xlabel('Isotopologues of {0}'.format(molecule))
            plt.ylabel('Normalized Intensity')
            plt.xticks(index+barWidth/2, labels)
            plt.legend()
            plt.tight_layout()
            plt.show()










