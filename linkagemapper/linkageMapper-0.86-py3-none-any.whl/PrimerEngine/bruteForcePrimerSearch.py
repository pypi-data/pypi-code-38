#!/bin/python

import os
import re

from . import PrimerDock
from Bio import SeqIO

from linkageMapper.Database.StrainNames import fetchStrainName

"""

This finds a feature compatible to the query gene name, in a chromosome feature table.

returns: (Name of chromosome, position of sequence inside chromosome)
"""


class bruteForceSearcher():
    def __init__(self, genomeFeatures, genomeFilePaths):
        self.genomeFeatures = genomeFeatures
        self.matchedGenome = self.locateMatchingGenome(genomeFilePaths)
        if self.matchedGenome is None:
            print()
            print("Warning: automatic primer search disabled. No matching genome found!")
            print()
            return None

    def locateMatchingGenome(self, genomeFilePaths, Verbose=True):
        AnnotationDescriptor = self.genomeFeatures[0].description
        if Verbose:
            print("\nSearching a genome that matches the annotation:")
            print(AnnotationDescriptor)

        matchingGenomeFilePath = None
        annotationStrain = fetchStrainName(AnnotationDescriptor)

        # -- SEARCH BY ANNOTATION INFORMATION;
        for genomePath in genomeFilePaths:
            features = list(SeqIO.parse(genomePath, format="fasta"))
            GenomeDescriptor = features[0].description
            if Verbose:
                print(">%s" % GenomeDescriptor)

            strain = fetchStrainName(GenomeDescriptor)
            if strain and strain == annotationStrain:
                matchingGenomeFilePath = genomePath
                matchingGenomeDescriptor = GenomeDescriptor
                matchingStrain = strain
        if matchingGenomeFilePath is None:
            print("No genome matching annotation!")
            return None
        else:
            print("Found matching genome to annotation, for automatic primer search: %s" % matchingGenomeFilePath)
            print("Matching genome descriptor: %s" % matchingGenomeDescriptor)
            print("Detected genome strain: %s" % matchingStrain)

        genome = list(SeqIO.parse(matchingGenomeFilePath, format="fasta"))
        return genome

    def retrieveGeneLocation(self, geneName):
        for g, FeatureGroup in enumerate(self.genomeFeatures):
            #print(FeatureGroup)
            for feature in FeatureGroup.features:
                if feature.type == "gene":
                    MATCH = False
                    if "gene" in feature.qualifiers.keys():
                        if geneName in feature.qualifiers['gene']:
                            MATCH = True
                    else:
                        if geneName in feature.qualifiers['locus_tag']:
                            MATCH = True
                    if MATCH:
                        return FeatureGroup.description, feature.location
        print("Warning: Gene %s not found." % geneName)
        #exit(1)

    def locateAndFetchSequence(self, location, chr_descriptor):
        wantedDescriptors = [chr_descriptor, "complete genome"]
        if not self.matchedGenome:
            print("No matching genome to find gene sequence.")
            return ""
        for c, Chromosome in enumerate(self.matchedGenome):
            for Descriptor in wantedDescriptors:
                print("Fetching primers from %s..." % Descriptor)
                if Descriptor in Chromosome.description:
                    Sequence = Chromosome.seq[location.start.position:location.end.position]
                    if location.strand == -1:
                        Sequence = Sequence.reverse_complement()
                    return Sequence

    def fetchGeneSequence(self, geneName, outputFilePath):

        # FETCH PRIMER METHODS. TO BE INTEGRATED;
        geneLocation = self.retrieveGeneLocation(geneName)

        if geneLocation is None:
            print("Aborting brute force primer search: Gene name not found.")
            return

        chr_descriptor, location = geneLocation


        # print(AnnotationDescription)

        SEQ = self.locateAndFetchSequence(location,
                                          chr_descriptor
                                          )

        if not SEQ:
            print("\n")
            print("Error: Failure on feching brute force sequence.")
            print("genomePath: %s" % self.matchedGenome)
            print("chromosome descripor: %s" % chr_descriptor)
            print("location: %s" % location)

        # Save sequence;
        outputFile = open(outputFilePath, 'w')
        outputFile.write(str(SEQ))
        outputFile.close()

    def launchBruteForcePrimerSearch(self, locus_name, chromosomes, Reverse):

        # BRUTE FORCE PRIMER FINDER OPERATIONS;
        geneSequenceFile = "%s.fasta" % locus_name

        PrimerSourcesDirectory = "PrimerSources"
        if not os.path.isdir(PrimerSourcesDirectory):
            os.mkdir(PrimerSourcesDirectory)

        geneSequenceFilePath = os.path.join(PrimerSourcesDirectory, geneSequenceFile)

        if not os.path.isfile(geneSequenceFilePath):
            # Fetch gene sequence;
            self.fetchGeneSequence(locus_name, geneSequenceFilePath)

        if os.path.isfile(geneSequenceFilePath):
            geneSequenceRaw = open(geneSequenceFilePath).read()
        else:
            print("Primer source not found.")
            return None

        geneSequence = geneSequenceRaw.split("\n")
        if ">" in geneSequence[0]:
            geneSequence = geneSequence[1:]
        geneSequence = "".join(geneSequence).lower()

        foundPrimers =\
            self.findPrimerBruteForce(chromosomes,
                                      geneSequence,
                                      Reverse=Reverse
            )

        if foundPrimers:
            print("Brute force forward primer search returns %i primers." % len(foundPrimers))

        resultingPrimers = [p[0].upper() for p in foundPrimers] 

        return resultingPrimers

    def findPrimerBruteForce(self,
                             genome,
                             gene_sequence,
                             Reverse=False,
                             maximumPrimerCount=36,
                             Verbose=False):
        PRIMER_LENGTH = 20
        SEARCH_STEP = 5

        # FOCUS SEARCH ON A REGION ON THE MIDDLE OF THE GENE SEQUENCE;
        sequenceLength = len(gene_sequence)
        sequenceLengthAim = 1500
        if sequenceLength > sequenceLengthAim:
            sequenceLengthBounds = (
                sequenceLength // 2 - sequenceLengthAim // 2,
                sequenceLength // 2 + sequenceLengthAim // 2
            )
            gene_sequence = gene_sequence[sequenceLengthBounds[0]:sequenceLengthBounds[1]]

        if Reverse:
            Indexes = range(len(gene_sequence) - PRIMER_LENGTH, 0, -SEARCH_STEP)
        else:
            Indexes = range(0, len(gene_sequence), SEARCH_STEP)

        foundPrimers = []
        for s in Indexes:
            primer_sequence = gene_sequence[s:s + PRIMER_LENGTH]
            for c, _chr in enumerate(genome):
                matches, sequenceVariationName = PrimerDock.findPrimer(_chr, primer_sequence)
                if len(matches) > 1:
                    if Verbose:
                        print("Leak.")
                    continue
                if matches:
                    if Verbose:
                        print(matches[0][0].upper())
                        print(sequenceVariationName)
                    foundPrimers.append(matches[0])
                    if len(foundPrimers) > maximumPrimerCount:
                        return foundPrimers

            if (s <= (len(gene_sequence) // 5)) == Reverse:
                break

        return foundPrimers


