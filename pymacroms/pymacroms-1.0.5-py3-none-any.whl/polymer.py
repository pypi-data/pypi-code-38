# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Kevin De Bruycker and Tim Krappitz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import absolute_import
from collections import Counter
import itertools
import pymacroms
import matplotlib.pyplot as plt
from operator import itemgetter, attrgetter
import re
import sys

class Polymer:

    def __init__(self,
                 endgroupPairs,
                 monomers,
                 adductIon = "H+",
                 charge = 1,
                 minRelAbundance = 0.01,
                 minRepeatingUnits = None,
                 maxRepeatingUnits = None,
                 mzRange = None,
                 customEndgroupsDatabase = None,
                 customMonomersDatabase = None,
                 firstMonomerMajor: bool = False,
                 comonomersToFirstMaxRatio: float = 1,
                 lastMonomerMinor: bool = False):
        """

        :type endgroupPairs: list
        :type monomers: list
        :type adductIon: str
        :type charge: int
        :type minRelAbundance: float
        :type minRepeatingUnits: int or list
        :type maxRepeatingUnits: int or list
        :type mzRange: list
        :type customEndgroupsDatabase: dict
        :type customMonomersDatabase: dict
        """

        # Internal formulas of endgroups and monomers should be (lists of) Counters for processing
        # Their self.attr counterpart is then the counter printed as str for easy external readout.
        #todo Maybe allow to enter chemical formulas directly, but then the code should first check whether the string is found in the database and if not transform it using the getCounterFromFormula function. Not urgent

        # input processing
        if customEndgroupsDatabase is not None:
            self.customEndgroupsDatabase = customEndgroupsDatabase
        else:
            self.customEndgroupsDatabase = dict()
        if customMonomersDatabase is not None:
            self.customMonomersDatabase = customMonomersDatabase
        else:
            self.customMonomersDatabase = dict()

        print("Simulating polymer...")
        if type(endgroupPairs) != list:
            endgroupPairs = [endgroupPairs]
        self.endgroupPairs = []
        for index, endgroupPair in enumerate(endgroupPairs):
            if type(endgroupPair) == str: # lookup the entry in the endgroups list in the database
                self.endgroupPairs.append(endgroupPair)
                if endgroupPair in self.customEndgroupsDatabase:
                    endgroupPairs[index] = self.customEndgroupsDatabase[endgroupPair][0] + self.customEndgroupsDatabase[endgroupPair][1]
                elif endgroupPair in pymacroms.database.endgroups:
                    endgroupPairs[index] = pymacroms.database.endgroups[endgroupPair][0] + pymacroms.database.endgroups[endgroupPair][1]
                else:
                    sys.exit("endgroupPair " + endgroupPair + " not found in either custom or built-in database!")
            elif type(endgroupPair) == list: # entry in the endgroups list is a list --> both endgroups are separate so should be combined first
                endgroupPairs[index] = endgroupPair[0] + endgroupPair[1]
                self.endgroupPairs.append(pymacroms.getFormulaStrFromCounter(endgroupPairs[index]))
            else: # entry is a counter, 1 counter for the 2 endgroups of the polymer
                self.endgroupPairs.append(pymacroms.getFormulaStrFromCounter(endgroupPair))
        if type(monomers) != list:
            monomers = [monomers]
        self.monomers = []
        for index, monomer in enumerate(monomers):
            if type(monomer) == str:
                self.monomers.append(monomer)
                if monomer in self.customMonomersDatabase:
                    monomers[index] = self.customMonomersDatabase[monomer]
                elif monomer in pymacroms.database.monomers:
                    monomers[index] = pymacroms.database.monomers[monomer]
                else:
                    sys.exit("Monomer " + monomer + " not found in either custom or built-in database!")
            else:
                self.monomers.append(pymacroms.getFormulaStrFromCounter(monomer))

        self.adductIon = adductIon
        self.charge = charge
        try:
            adductIon = pymacroms.database.ionising_species[adductIon]  # [formula: Counter, charge: int, mass_correction: float]
        except:
            sys.exit("adductIon not found in database!")
        self.amountAdductIons = abs(int(charge / adductIon[1]))
        # macromolecules will be generated with a defined minimum and maximum (total) number of repeating units
        # These boundaries can be given as arguments, but can also be estimated from an mzRange and
        # the molecular weights of the smallest (maxRU) and biggest (minRU) monomer:
        if mzRange is None and maxRepeatingUnits is None:
            # it will be impossible to estimate the range of repeating units
            sys.exit("I'm struggling to build a matrix of possible combinations of monomers based on \nthe provided combination of mzRange, minRepeatingUnits and maxRepeatingUnits.\nPlease check the parameters.")
        elif maxRepeatingUnits is None:
            if minRepeatingUnits is None:
                minRepeatingUnits = max(int((mzRange[0] * abs(charge) - max(list(pymacroms.getMonoIsotopicMass(endgroupPair) for endgroupPair in endgroupPairs)) - abs(int(charge / adductIon[1])) * pymacroms.getMonoIsotopicMass(adductIon[0])) / max(list(pymacroms.getMonoIsotopicMass(monomer) for monomer in monomers))), 0)
                print("--> minimum sum of repeating units: %i (estimated based on the provided mzRange and the masses of the components)" % minRepeatingUnits)
            maxRepeatingUnits = int((mzRange[1] * abs(charge) - min(list(pymacroms.getMonoIsotopicMass(endgroupPair) for endgroupPair in endgroupPairs)) - abs(int(charge / adductIon[1])) * pymacroms.getMonoIsotopicMass(adductIon[0])) / min(list(pymacroms.getMonoIsotopicMass(monomer) for monomer in monomers))) + 1
            print("--> maximum sum of repeating units: %i (estimated based on the provided mzRange and the masses of the components)" % maxRepeatingUnits)
        elif minRepeatingUnits is None:
            if mzRange is not None:
                minRepeatingUnits = max(int((mzRange[0] * abs(charge) - max(list(pymacroms.getMonoIsotopicMass(endgroupPair) for endgroupPair in endgroupPairs)) - abs(int(charge / adductIon[1])) * pymacroms.getMonoIsotopicMass(adductIon[0])) / max(list(pymacroms.getMonoIsotopicMass(monomer) for monomer in monomers))), 0)
                print("--> minimum sum of repeating units: %i (estimated based on the provided mzRange and the masses of the components)" % minRepeatingUnits)
            else:
                minRepeatingUnits = 0
                print("--> minimum sum of repeating units set to 0 since it cannot be estimated")
        # Now build all the combinations of repeating units within the limits of the given (or estimated) parameters
        if type(minRepeatingUnits) == int:
            # in this case, only a global minimum is given, so all combinations have to be made from 0
            # the ones with a sum smaller than minRepeatingUnits will be filtered later
            if type(maxRepeatingUnits) == int:
                # most simple case: every monomer from 0 to the same maxRepeatingUnits
                # combinations with a too high sum will be filtered later
                RUCombinations = list(itertools.product(range(maxRepeatingUnits + 1), repeat=len(monomers)))
            elif type(maxRepeatingUnits) == list:
                # first check that the length of the list is valid
                if len(maxRepeatingUnits) != len(monomers):
                    sys.exit("The length of maxRepeatingUnits does not match the amount of monomers!\nEither provide a max for each monomer or 1 global max for the sum of the repeating units")
                # similar as before but instead of the same range repeated for "amount of monomer times", here different ranges are used
                RUCombinations = list(itertools.product(*(range(max + 1) for max in maxRepeatingUnits)))
                maxRepeatingUnits = sum(maxRepeatingUnits)
            else:
                sys.exit("Something went wrong when interpreting maxRepeatingUnits\nCheck your input")
        elif type(minRepeatingUnits) == list:
            # first check that the length of the list is valid
            if len(minRepeatingUnits) != len(monomers):
                sys.exit("The length of minRepeatingUnits does not match the amount of monomers!\nEither provide a min for each monomer or 1 global min for the sum of the repeating units")
            if type(maxRepeatingUnits) == int:
                # the same formula as earlier can be used, but now the list comprehension will be over the minimum with a constant maximum
                # again, the combinations with a too high sum will be filtered later
                RUCombinations = list(itertools.product(*(range(min, maxRepeatingUnits + 1) for min in minRepeatingUnits)))
            elif type(maxRepeatingUnits) == list:
                # first check that the length of the list is valid
                if len(maxRepeatingUnits) != len(monomers):
                    sys.exit("The length of maxRepeatingUnits does not match the amount of monomers!\nEither provide a max for each monomer or 1 global max for the sum of the repeating units")
                # now both the minima and maxima are fixed, both min and max lists are combined using zip
                RUCombinations = list(itertools.product(*(range(min, max + 1) for min, max in list(zip(minRepeatingUnits, maxRepeatingUnits)))))
                maxRepeatingUnits = sum(maxRepeatingUnits)
            else:
                sys.exit("Something went wrong when interpreting maxRepeatingUnits\nCheck your input")
            minRepeatingUnits = sum(minRepeatingUnits)
        else:
            sys.exit("Something went wrong when interpreting minRepeatingUnits\nCheck your input")
        if minRepeatingUnits > maxRepeatingUnits:
            sys.exit("With the current parameters, minRepeatingUnits is higher than maxRepeatingUnits, this can't be correct...")
        # Finally, combine the combinations of repeating units with the different indices of the different end groups
        compositions = list(itertools.product(range(len(endgroupPairs)), RUCombinations))
        print("--> Possible combinations of repeating units/end groups based on given parameters: " + str(len(compositions)))
        print("--> Filtering and calculating the isotopic patterns...")

        formulaDatabase = [[],[]]
        macromolecules = []
        isobaricSpecies = False
        for EGPairIndex, RUCombination in compositions:
            if sum(RUCombination) < minRepeatingUnits or sum(RUCombination) > maxRepeatingUnits: # kick out the monomer combinations that result in a total amount of repeating units outside the defined range
                continue
            if firstMonomerMajor and RUCombination[0] < (sum(RUCombination) - RUCombination[0])/comonomersToFirstMaxRatio:
                continue
            if lastMonomerMinor and len(RUCombination) > 2 and RUCombination[len(RUCombination)-1] > sum(RUCombination) - RUCombination[0] - RUCombination[len(RUCombination)-1]: #
                # only makes sense when there are 3 or more different monomers
                # will still include the combination that has the same amount of last monomer as the sum of others
                # RUCombination[len(RUCombination)-1] > min(RUCombination) is bad plan
                continue
            formulaCounter = Counter()
            for index, numberRU in enumerate(RUCombination):
                formulaCounter += Counter({element:amount*numberRU for element,amount in monomers[index].items()})
            formulaCounter = endgroupPairs[EGPairIndex] + formulaCounter
            tempMolecule = pymacroms.Molecule(formulaCounter, self.adductIon, charge, minRelAbundance)
            # kick out the molecule if it's outside the defined mass range
            if mzRange is not None:
                if not tempMolecule.inMassRange(mzRange, False):
                    continue
            if formulaCounter in formulaDatabase[0]:
                formulaDatabase[1][formulaDatabase[0].index(formulaCounter)].append([RUCombination, EGPairIndex])
                isobaricSpecies = True
            else:
                formulaDatabase[0].append(formulaCounter)
                formulaDatabase[1].append([[RUCombination, EGPairIndex]])
                macromolecules.append({"repUnitsTotal": sum(RUCombination), "repUnitsCombination": RUCombination, "endgroupPairIndex": EGPairIndex, "moleculeData": tempMolecule})
        if isobaricSpecies:
            self.isobaricSpecies = []
            for index, [counter, data] in enumerate(zip(formulaDatabase[0], formulaDatabase[1])):
                if len(data) > 1:
                    self.isobaricSpecies.append({"repUnitsCombinations": list(zip(*data))[0], "endgroupPairIndices": list(zip(*data))[1], "moleculeData": macromolecules[index]["moleculeData"]})
        else:
            self.isobaricSpecies = None
        print("--> Number of (non-isobaric) macromolecules retained based on restrictions: " + str(len(macromolecules)))
        self.macromolecules = sorted(macromolecules, key=itemgetter("repUnitsTotal"))
        self.isotopicDist = self.getIsotopicDist()
        self.mzRange = [self.isotopicDist[0][0], self.isotopicDist[len(self.isotopicDist) - 1][0]]
        print("--> Done\n")

    def getIsotopicDist(self, resolution: float = None):
        isotopicDist = []
        for macromolecule in self.macromolecules:
            if resolution is None:
                for mass, normAbund in macromolecule["moleculeData"].isotopicDist:
                    isotopicDist.append([mass, normAbund])
            else:
                if not hasattr(macromolecule["moleculeData"], "resolution"):
                    macromolecule["moleculeData"].resolution = resolution
                    macromolecule["moleculeData"].isotopicDist_resolution = pymacroms.combineIsotopes(macromolecule["moleculeData"].isotopicDist, resolution)
                    macromolecule["moleculeData"].massMostAbundant = sorted(macromolecule["moleculeData"].isotopicDist_resolution, key=itemgetter(1), reverse=True)[0][0]
                elif macromolecule["moleculeData"].resolution != resolution:
                    macromolecule["moleculeData"].resolution = resolution
                    macromolecule["moleculeData"].isotopicDist_resolution = pymacroms.combineIsotopes(macromolecule["moleculeData"].isotopicDist, resolution)
                    macromolecule["moleculeData"].massMostAbundant = sorted(macromolecule["moleculeData"].isotopicDist_resolution, key=itemgetter(1), reverse=True)[0][0]
                for mass, normAbund in macromolecule["moleculeData"].isotopicDist_resolution:
                    isotopicDist.append([mass, normAbund])
        return sorted(isotopicDist)

    def getMoleculeList(self, experimentalMass: float = None, ppmDev: float = 5, resolution: float = None):
        isotopesNearMass = None
        moleculeList = []
        for index, macromolecule in enumerate(self.macromolecules):
            if experimentalMass is not None:
                isotopesNearMass = macromolecule["moleculeData"].getIsotopesNearMass(experimentalMass, ppmDev, resolution)
                if isotopesNearMass is None:
                    continue
            moleculeList.append([index, list(macromolecule["repUnitsCombination"]), isotopesNearMass])
        # return sorted(moleculeList, key=itemgetter(2))
        if len(moleculeList) > 0:
            return sorted(moleculeList, key=itemgetter(1))
        else:
            return None

    # def printMoleculeList(self, experimentalMass: float = None, ppmDev: float = 5):
    #     print("Monomer combination\tFormula (ion)\tMost abundant mass")
    #     # print("\t" + str(self.monomers))
    #     for macromoleculeIndex, repUnitsCombination, formula_ion, massMostAbundant in self.getMoleculeList(experimentalMass, ppmDev):
    #         print(str(repUnitsCombination) + "\t" + formula_ion + "\t" + str(massMostAbundant))

    def printMoleculeList(self, experimentalMass: float = None, ppmDev: float = 5, resolution: float = None):
        moleculeList = self.getMoleculeList(experimentalMass, ppmDev, resolution)
        if moleculeList is not None:
            print("Experimental mass: " + str(experimentalMass))
            print("Monomer combination\tEnd-groups\tFormula (ion)\tMost abundant mass\tMatched isotope(s) (m/z, dev. (ppm))")
            # print(str(self.monomers) + "\t\t\t(m/z, norm. abundance, dev (ppm))")
            for macromoleculeIndex, repUnitsCombination, isotopesNearMass in moleculeList:
                if isotopesNearMass is not None:
                    print(str(repUnitsCombination) + "\t" + self.endgroupPairs[self.macromolecules[macromoleculeIndex]["endgroupPairIndex"]] + "\t" + self.macromolecules[macromoleculeIndex]["moleculeData"].formula_ion + "\t" + str(self.macromolecules[macromoleculeIndex]["moleculeData"].massMostAbundant) + "\t" + str(list((mz, round(dev, 2)) for mz, normAbund, dev in isotopesNearMass)))
                else:
                    print(str(repUnitsCombination) + "\t" + self.endgroupPairs[
                        self.macromolecules[macromoleculeIndex]["endgroupPairIndex"]] + "\t" +
                          self.macromolecules[macromoleculeIndex]["moleculeData"].formula_ion + "\t" + str(
                        self.macromolecules[macromoleculeIndex]["moleculeData"].massMostAbundant) + "\tN/A")
        else:
            print("No matching molecules found...")

    def printFullInfo(self):
        print("Total number of repeating units\tMonomer combination\tEnd-groups\tFormula (ion)\tm/z\tRel. Abundance")
        print("\t" + str(self.monomers))
        for macromolecule in self.macromolecules:
            i = 1
            for mass, relAbund in pymacroms.toRelativeAbundance(macromolecule["moleculeData"].isotopicDist):
                if i == 1:
                    print(str(macromolecule["repUnitsTotal"]) + "\t" + str(list(macromolecule["repUnitsCombination"])) + "\t" + self.endgroupPairs[macromolecule["endgroupPairIndex"]] + "\t" + macromolecule["moleculeData"].formula_ion + "\t" + str(mass) + "\t" + str(relAbund))
                else:
                    print("\t\t\t\t" + str(mass) + "\t" + str(relAbund))
                i += 1

    def printIsotopicDist(self, resolution: float = None):
        print("Mass\tRel. Abundance")
        print("\t" + str(self.monomers))
        if resolution is not None:
            if not hasattr(self, "isotopicDist_resolution"):
                self.isotopicDist_resolution = self.getIsotopicDist(resolution)
            isotopicDist_rel = pymacroms.toRelativeAbundance(self.isotopicDist_resolution)
        else:
            isotopicDist_rel = pymacroms.toRelativeAbundance(self.isotopicDist)
        for mass, relAbund in isotopicDist_rel:
            print(str(mass) + "\t" + str(relAbund))

    def plotIsotopicDist(self, color = "black", mzRange: list = None):
        mz_axis = []
        relAbund_axis = []
        for mz, relAbund in pymacroms.toRelativeAbundance(self.isotopicDist):
            mz_axis += list([mz - 1e-10, mz, mz + 1e-10])
            relAbund_axis += list([-0.1, relAbund, -0.1])
        plt.plot(mz_axis, relAbund_axis, color=color)
        plt.title(r"Isotopic distribution ({}{} adducts) of a (co)polymer of".format(self.amountAdductIons, re.sub("([0-9]+)", "$_{\\1}$", re.sub("([+-]+)", "$^{\\1}$", self.adductIon))) + "\n" +
                  "{} with end-group(s): {}".format(re.sub("([0-9]+)", "$_{\\1}$", str(self.monomers)), re.sub("([0-9]+)", "$_{\\1}$", str(self.endgroupPairs))))
        plt.xlabel("m/z")
        plt.ylabel("Rel. abundance")
        if mzRange is not None:
            plt.xlim(mz for mz in mzRange)
        plt.ylim(0, 1.05)
        plt.show()

    def getIsobaricSpecies(self):
        if self.isobaricSpecies is None:
            return None
        else:
            isobaricSpecies = []
            for macromolecule in self.isobaricSpecies:
                isobaricSpecies.append([macromolecule["moleculeData"].formula_ion, macromolecule["moleculeData"].massMostAbundant, list([str(list(repUnitsCombination)), self.endgroupPairs[endgroupPair]] for repUnitsCombination, endgroupPair in zip(macromolecule["repUnitsCombinations"],macromolecule["endgroupPairIndices"]))])
            return sorted(isobaricSpecies, key=itemgetter(1))

    def printIsobaricSpecies(self):
        isobaricSpecies = self.getIsobaricSpecies()
        if isobaricSpecies is not None:
            print("Formula (ion)\tMost abundant mass\tMonomer combinations\tEnd-groups")
            print("\t" + str(self.monomers))
            for macromolecule in isobaricSpecies:
                i = 1
                for repUnitsCombination, endgroupPair in macromolecule[2]:
                    if i == 1:
                        print(macromolecule[0] + "\t" + "%.4f" % round(macromolecule[1], 4) + "\t" + repUnitsCombination + "\t" + endgroupPair)
                    else:
                        print("\t\t" + repUnitsCombination + "\t" + endgroupPair)
                    i += 1
        else:
            print("No isobaric macromolecules in the simulation...")
