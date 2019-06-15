#!/bin/python
import random
import pandas as pd

from optparse import OptionParser

from .Database import annotationManager


def Execute(options):
    print("\nSelecting annotation scaffold...\n")

    selectedAnnotation = annotationManager.loadAnnotation(
        options.inputAnnotationFolder,
        identifier=options.inputAnnotationName
    )

    selectedScaffold = selectedAnnotation[0]

    """
    if not options.inputAnnotationName:
        print("No chromosome selected. Available Chromosomes:")
        availableChromosomes = [c for c in selectedScaffold if "Unknown" not in c]
        print("\n".join(availableChromosomes))
        return
    """

    if not selectedScaffold:
        print("Chromosome %s not found." % options.inputAnnotationName)
        print(selectedScaffold)
        return

    print("Found feature source scaffold, please review: \n\n%s" % selectedScaffold)
    chosenFeatures = []
    nbFeatures = len(selectedScaffold.features)
    print("Scaffold of length %i. " % nbFeatures)

    # IT REPEATS A LOT OF LOCI, BECAUSE THE ANNOTATION HAS MANY ENTRIES WITH SAME NAME.
    # MAYBE MAKING A SET IS SUFFICIENT?
    scaffoldGenes = list(set(annotationManager.loadGenesFromScaffoldAnnotation(selectedScaffold)))

    data = []
    for gene in scaffoldGenes:
        if not gene.hasName:
            if random.random() > options.locusProbability:
                continue
        data.append({"LocusName": gene.Name})

    data = pd.DataFrame(data, columns=[
        "LocusName",
        "ForwardPrimer",
        "ReversePrimer"
    ]
    )

    data.to_csv(options.outputFile, index=False)

    print("\n%s written with %i primers." % (options.outputFile, data.shape[0]))


def parse_args():
    parser = OptionParser()

    parser.add_option("-d",
                      dest="inputAnnotationFolder",
                      default='annotations')

    parser.add_option("-c", "--chromosome",
                      dest="inputAnnotationName",
                      help="Chromosome identifier. E.g 'X' or 'II' or 'Ia'")

    parser.add_option("-o",
                      dest="outputFile")

    parser.add_option("-p",
                      dest="locusProbability",
                      type="float",
                      default=0.1)

    parser.add_option('-l',
                      dest="ListChromosomeNames",
                      action="store_true",
                      help="Print all chromosome names and exit.")

    options, args = parser.parse_args()

    return options


def main():
    print("\n\n")
    options = parse_args()
    Execute(options)


if __name__ == "__main__":
    main()
