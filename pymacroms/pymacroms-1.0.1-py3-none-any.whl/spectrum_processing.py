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
import pandas as pd
import numpy as np
from operator import itemgetter, attrgetter
import re
from sklearn import linear_model
import sys
import os
import progressbar
from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Frame, Spacer, Image, PageBreak
from reportlab.lib import colors
# from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.lib.units import cm, inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from io import BytesIO

reportStyles = getSampleStyleSheet()

class Spectrum:

    def __init__(self,
                 MSData,
                 mzRange,
                 minRelAbundance = 0.01,
                 ppmDev = 5,
                 resolution = None,
                 activeScan = None,
                 mergePeaksWithinResolution = False,
                 filterByMonomer = None,
                 customMonomersDatabase = None):
        """

        :type filename: str
        :type mzRange: list
        :type minRelAbundance: float
        :type ppmDev: float
        :type resolution: float
        :type activeScan: str
        :type mergePeaksWithinResolution: bool
        :type filterByMonomer: Counter or str
        :type customMonomersDatabase: dict
        """

        self.MSData = MSData # necessary to be able to write the results later on
        self.mzRange = mzRange
        self.minRelAbundance = minRelAbundance
        self.ppmDev = ppmDev
        self.resolution = resolution
        self.filename = MSData.filename
        self.extension = MSData.extension
        if len(self.MSData.scans) == 1:
            self.activeScan = '1'
        elif activeScan is None:
            sys.exit("Multiple scans found in imported spectrum, please provide arg activeScan to Spectrum to select the one to be analysed.")
        else:
            self.activeScan = activeScan
        if customMonomersDatabase is not None:
            self.customMonomersDatabase = customMonomersDatabase
        else:
            self.customMonomersDatabase = dict()

        self.peakData = MSData.scans[self.activeScan]["spectrum"].copy(deep=True)
        self.peakData.columns = ["mz", "relAbundance"]
        # max_val = pd.max(spectrum["abundance"])
        # spectrum["relAbundance"] = spectrum.abundance/spectrum.loc[(spectrum["mz"] >= mzRange[0]) & (spectrum["mz"] <= mzRange[1])].abundance.max()
        # spectrum["outsideROI"] = ~((spectrum.mz >= mzRange[0]) & (spectrum.mz <= mzRange[1])) # condition is true when inside the range, ~ negates the condition
        # outsideROI is not necessary because the filter for repeating units will ignore the mass peaks outside the ROI and set those rows for deletion anyway
        # calculate the RelAbundance based on the abundances in the ROI only
        self.peakData.relAbundance = self.peakData.relAbundance / self.peakData.loc[(self.peakData.mz >= mzRange[0]) & (self.peakData.mz <= mzRange[1])].relAbundance.max()  # devides the abundance by the maximum of the abundances of which the mass is not outside the region of interest
        self.rawSpectrum = pd.DataFrame(self.peakData.loc[(self.peakData.mz >= mzRange[0]) & (self.peakData.mz <= mzRange[1])])
        self.rawSpectrum.reset_index(drop=True, inplace=True)

        print("Filtering spectrum...")
        if filterByMonomer is not None:
            if type(filterByMonomer) == str:
                if filterByMonomer in self.customMonomersDatabase:
                    filterByMonomer = pymacroms.getMonoIsotopicMass(self.customMonomersDatabase[filterByMonomer])
                elif filterByMonomer in pymacroms.database.monomers:
                    filterByMonomer = pymacroms.getMonoIsotopicMass(pymacroms.database.monomers[filterByMonomer])
                else:
                    sys.exit("Filter by monomer: " + filterByMonomer + " not found in either custom or built-in database!")
            else:
                filterByMonomer = pymacroms.getMonoIsotopicMass(filterByMonomer)
            # filter the spectrum for peaks that only have a corresponding peak at + and - 1 repeating unit (the first monomer is used for this assessment)
            noPlusMinOneRU = []
            for mz in self.peakData.mz:
                if mz >= mzRange[0] and mz <= mzRange[1]:
                    noPlusMinOneRU.append(not self.hasPlusMinOneRU(mz, filterByMonomer))
                else:
                    noPlusMinOneRU.append(True)
            self.peakData["noPlusMinOneRU"] = noPlusMinOneRU
            print("--> Peaks outside mass range removed")
            print("--> Peaks without a +/- 1 repeating unit counterpart removed")
        else:
            self.peakData["noPlusMinOneRU"] = ~((self.peakData.mz >= mzRange[0]) & (self.peakData.mz <= mzRange[1]))  # condition is true when inside the range, ~ negates the condition
            print("--> Peaks outside mass range removed")
        self.peakData.drop(self.peakData[self.peakData["noPlusMinOneRU"]].index, inplace=True)
        self.peakData.drop(columns=["noPlusMinOneRU"], inplace=True)
        self.peakData.reset_index(drop=True, inplace=True)
        if mergePeaksWithinResolution:
            self.peakData = pymacroms.combineIsotopes(self.peakData, resolution)
            self.peakData.relAbundance = self.peakData.relAbundance / self.peakData.relAbundance.max() # recalculate relative abundance
            print("--> Merged peaks that are not separated with a resolution of " + str(self.resolution))
        # tag the entries that have a too low RelAbund to be deleted
        # self.peakData.loc[(self.peakData.relAbundance < minRelAbundance)].relAbundance = None # Doesn't work, only works when setting the whole 'matched' row to None, but mz values still needed for later matching of +- 1 RU
        self.peakData["tooLowRelAbund"] = self.peakData.relAbundance < minRelAbundance
        # self.peakData["toBeDeleted"] = self.peakData.tooLowRelAbund | self.peakData.noPlusMinOneRU
        self.peakData.drop(self.peakData[self.peakData["tooLowRelAbund"]].index, inplace=True)
        self.peakData.drop(columns=["tooLowRelAbund"], inplace=True)
        self.peakData.reset_index(drop=True, inplace=True)
        print("--> Peaks with too low relative abundance removed")
        print("--> Done\n")

    def hasPlusMinOneRU(self, mz, RUMass):
        mzRangeMinOne = [mz - mz * self.ppmDev * 1e-6 - RUMass - (mz - mz * self.ppmDev * 1e-6 - RUMass) * self.ppmDev * 1e-6,
                         mz + mz * self.ppmDev * 1e-6 - RUMass + (mz + mz * self.ppmDev * 1e-6 - RUMass) * self.ppmDev * 1e-6]
        # The 'true' mass of an experimental peak should be within a certain ppm range of that experimental peak,
        # but the experimental peak can again be ppmDev apart from that range -RUMass
        mzRangePlusOne = [mz - mz * self.ppmDev * 1e-6 + RUMass - (mz - mz * self.ppmDev * 1e-6 + RUMass) * self.ppmDev * 1e-6,
                          mz + mz * self.ppmDev * 1e-6 + RUMass + (mz + mz * self.ppmDev * 1e-6 + RUMass) * self.ppmDev * 1e-6]
        if len(self.peakData.loc[(self.peakData.mz >= mzRangeMinOne[0]) & (self.peakData.mz <= mzRangeMinOne[1])]) > 0 and len(
                self.peakData.loc[(self.peakData.mz >= mzRangePlusOne[0]) & (self.peakData.mz <= mzRangePlusOne[1])]) > 0:
            return True
        else:
            return False

    def matchPeaks(self, polymerSimulation):
        self.polymerSimulation = polymerSimulation

        print("Matching experimental spectrum to peaks of the simulated polymer...")
        print("(accuracy = " + str(self.ppmDev) + " ppm, resolution = " + str(self.resolution) + ")")
        if self.resolution is not None: # check if the isotopes have to be aggregated
            # check if the isotopes have been aggregated yet for the first macromolecule,
            # if yes then it should have been done for all of them and this step can be skipped
            if hasattr(self.polymerSimulation.macromolecules[0]["moleculeData"], 'resolution'):
                if self.polymerSimulation.macromolecules[0]["moleculeData"].resolution == self.resolution:
                    aggregateIsotopes = False
                else:
                    aggregateIsotopes = True
            else:
                aggregateIsotopes = True
        else:
            aggregateIsotopes = False
        if aggregateIsotopes:
            print("--> Combining isotopologues within resolution limits for all %i macromolecules" % len(self.polymerSimulation.macromolecules))
            sys.stdout.flush()
            for macromolecule in progressbar.progressbar(self.polymerSimulation.macromolecules, 0, len(self.polymerSimulation.macromolecules)):
                macromolecule["moleculeData"].resolution = self.resolution
                macromolecule["moleculeData"].isotopicDist_resolution = pymacroms.combineIsotopes(macromolecule["moleculeData"].isotopicDist, self.resolution)
                macromolecule["moleculeData"].massMostAbundant = sorted(macromolecule["moleculeData"].isotopicDist_resolution, key=itemgetter(1), reverse=True)[0][0]
        print("--> Total amount of experimental peaks: " + str(len(self.peakData)))
        theoPeakContributions = []  # for every experimental peak, this variable contains the theoretical composition:
        # [[indices of contributing macromolecules], [corresponding normalised abundances]]
        # identifiedMacromolecules = []
        matchedIsotopes = dict()
        peakMatched = []
        print("--> Matching...")
        sys.stdout.flush()
        for mz, relAbundance in progressbar.progressbar(self.peakData.itertuples(index=False, name=None), 0, len(self.peakData)):
            moleculeList = self.polymerSimulation.getMoleculeList(mz, self.ppmDev, self.resolution)
            if moleculeList is not None:
                macromolecules = []
                normAbundances = []
                for macromoleculeIndex, repUnitsCombination, isotopesNearMass in moleculeList:
                    macromolecules.append(macromoleculeIndex)
                    normAbundances.append(sum(list(zip(*isotopesNearMass))[1])) # the normAbundance, i.e. contribution of 1 macromolecule to the experimental peak is the sum of the normalised abundances within the accuracy of ppmDev
                    if macromoleculeIndex in matchedIsotopes:
                        matchedIsotopes[macromoleculeIndex] += list((mz, isotopeMass, deviation) for isotopeMass, normAbundance, deviation in isotopesNearMass)
                    else:
                        matchedIsotopes[macromoleculeIndex] = list((mz, isotopeMass, deviation) for isotopeMass, normAbundance, deviation in isotopesNearMass)
                theoPeakContributions.append([macromolecules, normAbundances])
                # identifiedMacromolecules += macromolecules
                # matchedCalcMass.append(np.average(masses, weights=massWeightingFactors))
                peakMatched.append(True)
            else:
                # matchedCalcMass.append(None)
                peakMatched.append(False)
        self.peakData["peakMatched"] = peakMatched
        self.theoPeakContributions = theoPeakContributions
        # self.identifiedMacromolecules = np.unique(identifiedMacromolecules)
        # self.identifiedMacromolecules = sorted(list(matchedIsotopes.keys()))
        self.matchedIsotopes = matchedIsotopes
        print("--> %i peaks successfully matched" % len(self.peakData[self.peakData.peakMatched]))
        print("--> These peaks are (potentially) originating from %i macromolecules" % len(self.matchedIsotopes))
        print("--> %i experimental m/z values could not be matched to a calculated m/z" % len(self.peakData[~self.peakData.peakMatched]))
        print("--> Done\n")

    def plotMatchPeaksOverview(self, mzRange: list = None, showMatched: bool = True, showNotMatched: bool = True, savePlotAs: str = None, reportOutput: bool = False):
        y_val = 0 if reportOutput else -0.1
        if showMatched:
            mz_axis = []
            relAbund_axis = []
            for mz, relAbund in self.peakData[["mz", "relAbundance"]].loc[self.peakData.peakMatched].itertuples(index=False, name=None):
                mz_axis += list([mz - 1e-10, mz, mz + 1e-10])
                relAbund_axis += list([y_val, relAbund, y_val])
            plt.plot(mz_axis, relAbund_axis, color="green", label="Matched to theoretical m/z")
        if showNotMatched:
            mz_axis = []
            relAbund_axis = []
            for mz, relAbund in self.peakData[["mz", "relAbundance"]].loc[~self.peakData.peakMatched].itertuples(index=False, name=None):
                mz_axis += list([mz - 1e-10, mz, mz + 1e-10])
                relAbund_axis += list([y_val, relAbund, y_val])
            plt.plot(mz_axis, relAbund_axis, color="red", label="Not matched to theoretical m/z")
        plt.legend()
        plt.title("Filtered experimental spectrum")
        plt.xlabel("m/z")
        plt.ylabel("Rel. abundance")
        if mzRange is not None:
            plt.xlim(mz for mz in mzRange)
        plt.ylim(0, 1.05)
        if savePlotAs is not None:
            plt.savefig(self.filename + "_matchPeaksOverview." + savePlotAs, dpi=300, format=savePlotAs)
        if reportOutput:
            imgdata = BytesIO()
            plt.savefig(imgdata, format="svg")
            plt.close()
            imgdata.seek(0)  # rewind the data
            return Image(svg2rlg(imgdata))
        else:
            plt.show()
            # plt.close()

    def calcComposition(self, minimumAmount: float = 0, minimumIsotopeFraction: float = 0.1):
        self.compositionMinimumAmount = minimumAmount # save for future reference
        print("Calculating the composition by fitting the experimental and theoretical intensities...")
        # target = pd.DataFrame(np.zeros(len(self.theoPeakComposition)), columns=["relAbundance"])
        target = pd.DataFrame(self.peakData.loc[self.peakData.peakMatched].relAbundance, columns=["relAbundance"])
        # target.reset_index(drop=True, inplace=True)
        df = pd.DataFrame(np.zeros((len(self.theoPeakContributions), len(self.matchedIsotopes))), columns=sorted(list(self.matchedIsotopes.keys())))
        for index, [macromolecules, normAbundances] in enumerate(self.theoPeakContributions): #index, [indices of contributing macromolecules], [corresponding normalised abundances]]
            # target.iloc[index].relAbundance = relAbundance
            for macromolecule, normAbundance in zip(macromolecules, normAbundances):
                df.loc[index, macromolecule] = normAbundance
        df.index = target.index
        dfColumnsSum = pd.DataFrame(df.sum(), columns=["dfSum"])
        # this sum represents the fraction of the (normAbundance of the) isotopic pattern that is matched in the spectrum:
        # if all the peaks of the theoretical pattern are matched, this sum should be 1;
        # if only 1 minor peak of the isotopic pattern is found in the experimental spectrum, the sum will be low --> probably mismatch
        df.drop(columns=dfColumnsSum.loc[dfColumnsSum.dfSum < minimumIsotopeFraction].index, inplace=True)
        regression = linear_model.LinearRegression(fit_intercept=False)
        regression.fit(df, target)
        regressionR2 = regression.score(df, target)
        print("--> Composition found with an R^2 of %.5f" % round(regressionR2, 5))
        regResult = pd.DataFrame(np.transpose(regression.coef_), index=df.columns, columns=["amounts"])
        # self.peakData["fittedRelAbundance"] = pd.DataFrame(np.dot(df, regResult), index=target.index, columns=["calcRelAbundance"]).calcRelAbundance # Don't do this, use the dedicated method getFittedIsotopicDist instead: this will exclude isotopes that were not matched while they will be included when calculating the whole spectrum
        self.peakData["diffRelAbundance"] = pd.DataFrame(np.dot(df, regResult), index=target.index, columns=["calcRelAbundance"]).calcRelAbundance - target.relAbundance
        regResult.amounts = regResult.amounts / regResult.amounts.max() # normalisation
        while regResult.amounts.min() < minimumAmount:
            print("--> One or more macromolecules have a contribution\n    that is either negative or below the threshold of %.2f!" % round(minimumAmount, 2))
            print("--> Recalculating...")
            # remove values that are too low and repeat linear regression
            df.drop(columns=regResult.loc[regResult.amounts < minimumAmount].index, inplace=True)
            regression.fit(df, target)
            regressionR2 = regression.score(df, target)
            print("--> Composition found with an R^2 of %.5f" % round(regressionR2, 5))
            regResult = pd.DataFrame(np.transpose(regression.coef_), index=df.columns, columns=["amounts"])
            self.peakData["diffRelAbundance"] = pd.DataFrame(np.dot(df, regResult), index=target.index, columns=["calcRelAbundance"]).calcRelAbundance - target.relAbundance
            regResult.amounts = regResult.amounts / regResult.amounts.max() # normalisation
        if len(regResult) == 0:
            self.composition = None
            self.regressionR2 = None
        else:
            self.composition = regResult
            self.regressionR2 = regressionR2
            composition_processed = []
            for macromolecule, amount in regResult.itertuples(name=None):
                composition_processed.append([list(self.polymerSimulation.macromolecules[macromolecule]["repUnitsCombination"]),
                                    self.polymerSimulation.endgroupPairs[
                                        self.polymerSimulation.macromolecules[macromolecule]["endgroupPairIndex"]],
                                    self.polymerSimulation.macromolecules[macromolecule]["moleculeData"].formula_ion,
                                    amount,
                                    self.polymerSimulation.macromolecules[macromolecule]["moleculeData"].molecularWeight,
                                    self.polymerSimulation.macromolecules[macromolecule][
                                        "moleculeData"].massMostAbundant,
                                    self.matchedIsotopes[macromolecule]])
            self.MSData.scans[self.activeScan]['composition'] = sorted(composition_processed, key=itemgetter(4))
            self.MSData.scans[self.activeScan]['Mn'] = sum(list(Mw * N for a, b, c, N, Mw, d, e in composition_processed)) / sum(list(N for a, b, c, N, Mw, d, e in composition_processed))
            self.MSData.scans[self.activeScan]['Mw'] = sum(list(Mw * Mw * N for a, b, c, N, Mw, d, e in composition_processed)) / sum(list(Mw * N for a, b, c, N, Mw, d, e in composition_processed))
            self.MSData.scans[self.activeScan]['dispersity'] = self.MSData.scans[self.activeScan]['Mw'] / self.MSData.scans[self.activeScan]['Mn']
        print("--> Done\n")

    def getComposition(self):
        composition = []
        for macromolecule, amount in self.composition.itertuples(name=None):
            composition.append([list(self.polymerSimulation.macromolecules[macromolecule]["repUnitsCombination"]),
                           self.polymerSimulation.endgroupPairs[
                               self.polymerSimulation.macromolecules[macromolecule]["endgroupPairIndex"]],
                           self.polymerSimulation.macromolecules[macromolecule]["moleculeData"].formula_ion,
                           amount,
                           self.polymerSimulation.macromolecules[macromolecule]["moleculeData"].massMostAbundant,
                           self.matchedIsotopes[macromolecule]])
        return sorted(composition, key=itemgetter(4))

    def printComposition(self):
        if not hasattr(self, "composition"):
            sys.exit("Calculate the composition first using Spectrum.calcComposition")
        if self.composition is not None:
            composition = self.getComposition()
            print("R^2 = %.5f" % round(self.regressionR2, 5))
            print("Monomer combination\tEnd-groups\tFormula (ion)\tAmount\tMost abundant mass\tMatched isotopes")
            print(str(self.polymerSimulation.monomers) + "\t\t\t\t\t(m/z (exp), m/z (calc), dev (ppm))")
            for repUnitsCombination, endgroupPair, formula_ion, amount, massMostAbundant, matchedIsotopes in composition:
                print(str(repUnitsCombination) + "\t" + endgroupPair + "\t" + formula_ion + "\t" + "%.2f" % round(amount, 2) + "\t" + str(massMostAbundant) + "\t" + str(matchedIsotopes))
        else:
            print("No matching molecules found...")

    def saveComposition(self):
        if not hasattr(self, "composition"):
            sys.exit("Calculate the composition first using Spectrum.calcComposition")
        if self.composition is not None:
            composition = self.getComposition()
            export = pd.DataFrame(list((repUnitsCombination, endgroupPair, formula_ion, amount, massMostAbundant, list(matchedIsotopes)) for repUnitsCombination, endgroupPair, formula_ion, amount, massMostAbundant, matchedIsotopes in composition), columns=["Monomer combination", "End-groups", "Formula (ion)", "Amount", "Most abundant mass", "Matched isotopes (m/z (exp), m/z (calc), dev (ppm))"])
        else:
            export = pd.DataFrame(columns=["No matching molecules found..."])
        if len(self.MSData.scans) == 1:
            export.to_csv(self.filename + "_composition.csv", index=False)
        else:
            export.to_csv(self.filename + "_composition_scan" + self.activeScan + ".csv", index=False)


        isobaricSpecies = self.polymerSimulation.getIsobaricSpecies()
        if isobaricSpecies is not None:
            report = []
            for macromolecule in isobaricSpecies:
                i = 1
                for repUnitsCombination, endgroupPair in macromolecule[2]:
                    if i == 1:
                        report.append([macromolecule[0], macromolecule[1], repUnitsCombination, endgroupPair])
                    else:
                        report.append([None, None, repUnitsCombination, endgroupPair])
                    i += 1
            export = pd.DataFrame(list((formula_ion, massMostAbundant, repUnitsCombination, endgroupPair) for formula_ion, massMostAbundant, repUnitsCombination, endgroupPair in report),
                                  columns=["Formula (ion)", "Most abundant mass", "Monomer combinations", "End-groups"])
        else:
            export = pd.DataFrame(columns=["No isobaric macromolecules in the simulation..."])
        if len(self.MSData.scans) == 1:
            export.to_csv(self.filename + "_isobaric.csv", index=False)
        else:
            export.to_csv(self.filename + "_isobaric_scan" + self.activeScan + ".csv", index=False)

    def getFittedIsotopicDist(self, resolution: float = None):
        if not hasattr(self, "composition"):
            sys.exit("Calculate the composition first using Spectrum.calcComposition")
        if self.composition is not None:
            fittedIsotopicDist = pd.DataFrame(columns=["mz", "normAbundance"])
            for macromolecule, amount in self.composition.itertuples(name=None):
                for mz, normAbund in self.polymerSimulation.macromolecules[macromolecule]["moleculeData"].isotopicDist:
                    fittedIsotopicDist = fittedIsotopicDist.append(pd.DataFrame([[mz, normAbund * amount]], columns=["mz", "normAbundance"]), ignore_index=True)
            fittedIsotopicDist.normAbundance = fittedIsotopicDist.normAbundance / fittedIsotopicDist.normAbundance.sum() # normalise
            # fittedIsotopicDist["relAbundance"] = fittedIsotopicDist.normAbundance / fittedIsotopicDist.normAbundance.max()
            fittedIsotopicDist.sort_values("mz", inplace=True)
            fittedIsotopicDist.reset_index(drop=True, inplace=True)
            if resolution is not None:
                return pymacroms.combineIsotopes(fittedIsotopicDist, resolution)
            else:
                return fittedIsotopicDist
        else:
            return None

    def printFittedSpectrum(self, resolution: float = None):
        fittedIsotopicDist = self.getFittedIsotopicDist(resolution)
        if fittedIsotopicDist is not None:
            print("Fitted spectrum")
            print("Mass\tRel. Abundance")
            for mz, relAbund in pymacroms.toRelativeAbundance(list(fittedIsotopicDist.itertuples(index=False, name=None))):
                print(str(mz) + "\t" + str(relAbund))
        else:
            print("No matching molecules found...")

    def plotFittedSpectrum(self, resolution: float = None, color = "black", mzRange: list = None):
        fittedIsotopicDist = self.getFittedIsotopicDist(resolution)
        if fittedIsotopicDist is not None:
            mz_axis = []
            relAbund_axis = []
            for mz, relAbund in pymacroms.toRelativeAbundance(list(fittedIsotopicDist.itertuples(index=False, name=None))):
                mz_axis += list([mz - 1e-10, mz, mz + 1e-10])
                relAbund_axis += list([-0.1, relAbund, -0.1])
            plt.plot(mz_axis, relAbund_axis, color=color)
            plt.title("Fitted spectrum")
            plt.xlabel("m/z")
            plt.ylabel("Rel. abundance")
            if mzRange is not None:
                plt.xlim(mz for mz in mzRange)
            plt.ylim(0, 1.05)
            plt.show()
        else:
            print("No matching molecules found...")

    def plotComparisonSpectrum(self, resolution: float = None, color = "black", mzRange: list = None, savePlotAs: str = None, reportOutput: bool = False):
        fittedIsotopicDist = self.getFittedIsotopicDist(resolution)
        if fittedIsotopicDist is not None:
            y_val = 0 if reportOutput else -0.1
            rawSpectrum = plt.subplot(211)
            mz_axis = []
            relAbund_axis = []
            for mz, relAbund in self.rawSpectrum.itertuples(index=False, name=None):
                mz_axis += list([mz - 1e-10, mz, mz + 1e-10])
                relAbund_axis += list([y_val, relAbund, y_val])
            rawSpectrum.plot(mz_axis, relAbund_axis, color=color, label="Raw data")
            plt.legend()
            plt.title("Spectrum comparison")
            plt.ylabel("Rel. abundance")
            if mzRange is not None:
                plt.xlim(mz for mz in mzRange)
            plt.ylim(0, 1.05)
            fittedSpectrum = plt.subplot(212, sharex=rawSpectrum, sharey=rawSpectrum)
            mz_axis = []
            relAbund_axis = []
            for mz, relAbund in pymacroms.toRelativeAbundance(list(fittedIsotopicDist.itertuples(index=False, name=None))):
                mz_axis += list([mz - 1e-10, mz, mz + 1e-10])
                relAbund_axis += list([y_val, relAbund, y_val])
            fittedSpectrum.plot(mz_axis, relAbund_axis, color=color, label="Fitted spectrum")
            # plt.title(r"Isotopic distribution ({}{} adducts) of a (co)polymer of".format(self.amountAdductIons,
            #                                                                              re.sub("([0-9]+)", "$_{\\1}$",
            #                                                                                     re.sub("([+-]+)",
            #                                                                                            "$^{\\1}$",
            #                                                                                            self.adductIon))) + "\n" +
            #           "{} with end-group(s): {}".format(re.sub("([0-9]+)", "$_{\\1}$", str(self.monomers)),
            #                                             re.sub("([0-9]+)", "$_{\\1}$", str(self.endgroupPairs))))
            plt.legend()
            plt.xlabel("m/z")
            plt.ylabel("Rel. abundance")
            if mzRange is not None:
                plt.xlim(mz for mz in mzRange)
            plt.ylim(0, 1.05)
            if savePlotAs is not None:
                plt.savefig(self.filename + "_comparisonSpectrum." + savePlotAs, dpi=300, format=savePlotAs)
            if reportOutput:
                imgdata = BytesIO()
                plt.savefig(imgdata, format="svg")
                plt.close()
                imgdata.seek(0)  # rewind the data
                return Image(svg2rlg(imgdata))
            else:
                plt.show()
                # plt.close()
        else:
            if reportOutput:
                return Paragraph("No isobaric macromolecules in the simulation...", reportStyles['Normal'])
            else:
                print("No matching molecules found...")

    def plotDiffIsotopicDist(self, mzRange: list = None, showExperimental: bool = True, showNonMatched: bool = False, showFitted: bool = False, resolution: float = None):
        if not hasattr(self, "composition"):
            sys.exit("Calculate the composition first using Spectrum.calcComposition")
        if self.composition is not None:
            filteredSpectrum = plt.subplot(211)
            if showExperimental:
                mz_axis = []
                relAbund_axis = []
                for mz, relAbund in self.peakData[["mz", "relAbundance"]].loc[self.peakData.peakMatched].itertuples(
                        index=False, name=None):
                    mz_axis += list([mz - 1e-10, mz, mz + 1e-10])
                    relAbund_axis += list([-0.1, relAbund, -0.1])
                filteredSpectrum.plot(mz_axis, relAbund_axis, color="green", label="(Filtered) matched experimental")
            if showNonMatched:
                mz_axis = []
                relAbund_axis = []
                for mz, relAbund in self.peakData[["mz", "relAbundance"]].loc[~self.peakData.peakMatched].itertuples(
                        index=False, name=None):
                    mz_axis += list([mz - 1e-10, mz, mz + 1e-10])
                    relAbund_axis += list([-0.1, relAbund, -0.1])
                filteredSpectrum.plot(mz_axis, relAbund_axis, color="red", label="Not matched to theoretical m/z")
            if showFitted:
                fittedIsotopicDist = self.getFittedIsotopicDist(resolution)
                if fittedIsotopicDist is not None:
                    mz_axis = []
                    relAbund_axis = []
                    for mz, relAbund in pymacroms.toRelativeAbundance(list(fittedIsotopicDist.itertuples(index=False, name=None))):
                        mz_axis += list([mz - 1e-10, mz, mz + 1e-10])
                        relAbund_axis += list([-0.1, relAbund, -0.1])
                    filteredSpectrum.plot(mz_axis, relAbund_axis, color="blue", label="(Fitted) calculated")
            plt.legend()
            plt.title("Filtered experimental spectrum")
            # plt.xlabel("m/z")
            plt.ylabel("Rel. abundance")
            if mzRange is not None:
                plt.xlim(mz for mz in mzRange)
            plt.ylim(0, 1.05)

            diffFittedSpectrum = plt.subplot(212, sharex=filteredSpectrum)
            mz_axis = []
            diffRelAbund_axis = []
            for mz, diffRelAbund in self.peakData[["mz", "diffRelAbundance"]].loc[self.peakData.peakMatched].itertuples(index=False, name=None):
                mz_axis += list([mz - 1e-10, mz, mz + 1e-10])
                diffRelAbund_axis += list([0, diffRelAbund, 0])
            diffFittedSpectrum.plot(mz_axis, diffRelAbund_axis, color="black", label="Difference fitted-experimental")
            plt.legend()
            plt.xlabel("m/z")
            plt.ylabel("Rel. abundance")
            if mzRange is not None:
                plt.xlim(mz for mz in mzRange)
            # plt.ylim(-0.55, 0.55)
            # plt.savefig("output.pdf", dpi=300, format='pdf')
            plt.show()
            # plt.close()

    def saveReport(self, plotMatchPeaksOverview=True, plotComparisonSpectrum=True, composition=True, savePlotsAs: str = None, AppMolFr=False):
        if len(self.MSData.scans) == 1:
            reportFile = SimpleDocTemplate(self.filename + "_report.pdf", rightMargin=0.5 * inch, leftMargin=0.5 * inch, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
        else:
            reportFile = SimpleDocTemplate(self.filename + "_report_scan" + self.activeScan + ".pdf", rightMargin=0.5 * inch, leftMargin=0.5 * inch, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
        reportContent = []

        reportContent.append(Paragraph("Experiment " + re.sub("\A(.*)/([^/]*)\Z", "\\2", self.filename), reportStyles['Title']))

        reportContent.append(Paragraph("Processing parameters", reportStyles['Heading1']))
        parametersTable = [["endgroupPairs", "monomers", "mzRange", "minRelAbundance", "resolution", "ppmDev", "adductIon", "charge"]]
        parametersTable.append([self.polymerSimulation.endgroupPairs[0], self.polymerSimulation.monomers[0], str(self.mzRange),
                          self.minRelAbundance, self.resolution,
                          self.ppmDev, self.polymerSimulation.adductIon,
                          self.polymerSimulation.charge])
        for endgroup, monomer in itertools.zip_longest(self.polymerSimulation.endgroupPairs[1:], self.polymerSimulation.monomers[1:], fillvalue=''):
            parametersTable.append([endgroup, monomer])

        table = Table(parametersTable, repeatRows=2, style=[
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0, 0.7, 0.7)),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ])
        reportContent.append(table)
        reportContent.append(Spacer(1*cm, 1*cm))
        # reportContent.append(PageBreak())


        if plotMatchPeaksOverview:
            elementTitle = Paragraph("Matching overview", reportStyles['Heading1'])
            elementTitle.keepWithNext = True
            reportContent.append(elementTitle)
            reportContent.append(self.plotMatchPeaksOverview(reportOutput=True, savePlotAs=savePlotsAs))

        if plotComparisonSpectrum:
            elementTitle = Paragraph("Experimental vs. calculated spectrum", reportStyles['Heading1'])
            elementTitle.keepWithNext = True
            reportContent.append(elementTitle)
            reportContent.append(self.plotComparisonSpectrum(resolution=self.resolution, color="darkblue", reportOutput=True, savePlotAs=savePlotsAs))

        #
        # if AppMolFr:  # dangerous part, if this is called before the composition table it breaks the code
        #     story.append(pymacroms.apparentMoleFractions(
        #         filename=filename,
        #         charge=polymerSimulation.charge,
        #         adductIon=polymerSimulation.adductIon,
        #         endgroupPairs=polymerSimulation.endgroupPairs,
        #         monomers=polymerSimulation.monomers,
        #         minRepeatingUnits=10,
        #         maxRepeatingUnits=25,
        #         ppmDev=spectrumExperimental.ppmDev,
        #     ).plotApparentMoleFractions())

        if composition:
            reportContent.append(Spacer(1 * cm, 1 * cm))
            reportContent.append(Paragraph("Identified species", reportStyles['Heading1']))
            composition = self.getComposition()

            compositionTable = [["Polymer composition", "", "", "", "", "Matched peaks", "", ""],
                    ["Monomers", "Endgroups", "Formula & ion", "Amount", "Most abundant\nisotope", "m/z\n(exp)",
                     "m/z\n(calc)", "\u0394\n(ppm)"]]
            for repUnitsCombination, endgroupPair, formula_ion, amount, massMostAbundant, matchedIsotopes in composition:
                compositionTable.append([str(repUnitsCombination), endgroupPair, formula_ion,
                                         "%.2f" % round(amount, 2), "%.4f" % round(massMostAbundant, 4),
                                         "%.4f" % round(matchedIsotopes[0][0], 4), "%.4f" % round(matchedIsotopes[0][1], 4), "%.2f" % round(matchedIsotopes[0][2], 2)])
                for mz_exp, mz_calc, mz_dev in matchedIsotopes[1:]:  # skip the first tuple, that is dealt with in the previous loop
                    compositionTable.append(
                        ["", "", "", "", "", "%.4f" % round(mz_exp, 4), "%.4f" % round(mz_calc, 4), "%.2f" % round(mz_dev, 2)])
            table = Table(compositionTable, repeatRows=2, style=[
                ('BACKGROUND', (0, 0), (-1, 1), colors.Color(0, 0.7, 0.7)),
                ('SPAN', (0, 0), (1, 0)),
                ('SPAN', (-3, 0), (-1, 0)),
                ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ])
            reportContent.append(table)

            reportContent.append(Spacer(1 * cm, 1 * cm))
            reportContent.append(Paragraph("Isobaric species", reportStyles['Heading1']))
            isobaricSpecies = self.polymerSimulation.getIsobaricSpecies()
            if isobaricSpecies is not None:
                isobaricTable = [["Formula (ion)", "Most abundant mass", "Monomer combinations", "End-groups"]]
                for macromolecule in isobaricSpecies:
                    isobaricTable.append([macromolecule[0], macromolecule[1], macromolecule[2][0][0], macromolecule[2][0][1]])
                    for repUnitsCombination, endgroupPair in macromolecule[2][1:]:
                        isobaricTable.append([None, None, repUnitsCombination, endgroupPair])
                table = Table(isobaricTable, repeatRows=2, style=[
                    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0, 0.7, 0.7)),
                    ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ])
                reportContent.append(table)
            else:
                reportContent.append(Paragraph("No isobaric macromolecules in the simulation...", reportStyles['Normal']))


        reportFile.build(reportContent)






