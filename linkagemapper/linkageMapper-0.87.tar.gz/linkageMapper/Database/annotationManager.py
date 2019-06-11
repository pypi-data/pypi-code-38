#!/bin/python

import os
from Bio import SeqIO


class Gene():
    def __init__(self, Name, hasName):
        self.Name = Name
        self.hasName = hasName


def loadGenesFromScaffoldAnnotation(Scaffold):
    genes = []
    for feature in Scaffold.features:
        COND1 = "gene" in feature.qualifiers.keys()
        COND2 = "locus_tag" in feature.qualifiers.keys()

        NAME = None
        hasName = False
        if COND1:
            NAME = feature.qualifiers["gene"][0]
        elif COND2:
            NAME = feature.qualifiers["locus_tag"][0]

        if NAME:
            genes.append(Gene(NAME, hasName))

    return genes


def loadFeatures(annotationFilePath):
    annotation = SeqIO.read(annotationFilePath, "genbank")
    outputFeatures = []
    for feature in annotation.features:
        if feature.type in ["gene"]:
            outputFeatures.append(feature)

    return outputFeatures


"""

This returns the most suitable annotation file from the annotations folder,
as a list of scaffolds.

"""


def loadAnnotation(annotationFolder, identifier=None, Verbose=False):
    annotationFiles = os.listdir(annotationFolder)
    annotationFiles = sorted([File
                              for File in annotationFiles
                              if File.endswith(".gbff")])

    if not annotationFiles:
        print("Annotation file not found! Check your annotation folder.")
        exit(1)

    def sortScaffolds(scaffold):
        genes = loadGenesFromScaffoldAnnotation(scaffold)
        return len(genes)

    def sortAnnotations(annotation):
        genes = loadGenesFromScaffoldAnnotation(annotation[0])
        return len(genes)

    annotationContents = []
    for annotationFile in annotationFiles:
        annotationFilePath = os.path.join(annotationFolder, annotationFile)
        annotationScaffolds = list(SeqIO.parse(annotationFilePath, "genbank"))

        #print(identifier)

        if identifier:
            wantedIdentifiers = [
                identifier,
                "chromosome_%s" % identifier
            ]

            # -- pick only those that contain the identifier
            allIdentifiers = []
            wantedScaffolds = []
            for Scaffold in annotationScaffolds:
                Qualifiers = Scaffold.features[0].qualifiers
                if 'chromosome' in Qualifiers.keys():
                    ChromosomeName = Qualifiers['chromosome'][0]
                    allIdentifiers.append(ChromosomeName)
                    for wantedIdentifier in wantedIdentifiers:
                        #print(identifier)
                        #print(ChromosomeName)
                        if wantedIdentifier.lower() == ChromosomeName.lower():
                            wantedScaffolds.append(Scaffold)

            annotationScaffolds = wantedScaffolds

        if not annotationScaffolds:
            continue

        annotationScaffolds = sorted(
            annotationScaffolds,
            key=sortScaffolds,
            reverse=True
        )

        annotationContents.append(annotationScaffolds)

    if Verbose:
        print("\n====")
        for aS in annotationScaffolds:
            print(len(aS.features))

    annotationContents = sorted(annotationContents, key=sortAnnotations, reverse=True)

    return annotationContents[0]







