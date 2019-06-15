#!/bin/python

import random
import re
import itertools
import numpy as np

from Bio.Seq import Seq

from . import GeneticEntities


PrimerTypes = ["ForwardPrimer", "ReversePrimer"]


"""

findPrimer(string, string):
returns the list of matched primers along with the sequence modification
 on the primer that resulted in match.

"""


def findPrimer(genome_segment, primer_sequence):
    Primer = Seq(primer_sequence)
    seqVarNames = [
        "Raw Primer",
        "Reverse Complement"
    ]

    sequenceVariations = [
        Primer,
        Primer.reverse_complement(),
    ]

    for n, sequenceVariation in enumerate(sequenceVariations):
        search_seq = str(sequenceVariation).lower()
        Matches = re.finditer(search_seq, genome_segment.sequence)
        Matches = list(Matches)
        if Matches:
            return Matches, seqVarNames[n]

    return [], None


def searchPrimerPairOnGenome(locusName, primerPair, genome):

    # INIT SUPPORT LIST;
    matchedPrimers = {}

    matchSuccess = [True, True]
    # ITERATE THRU PRIMER TYPES;
    for PT, PrimerType in enumerate(PrimerTypes):

        # screen info purposes;
        print(PrimerType)

        # fetch primer sequence;
        queryPrimer = primerPair[PrimerType]
        print(queryPrimer)
        matchedPrimers[PrimerType] = matchPrimerOnGenome(genome,
                                                         queryPrimer,
                                                         PrimerType)

        if not matchedPrimers[PrimerType]:
            print("No match...")
            matchSuccess[PT] = False

    for PT, PrimerType in enumerate(PrimerTypes):
        # CHECK FOR PRIMER LEAK;
        PrimerType = PrimerTypes[PT]

        if len(matchedPrimers[PrimerType]) > 1:
            print("Primer leak... trying to fix.")

            # TRY TO FIX PRIMER LEAK;
            # outright delete matches that doesn't have a pair in the same chromosome;
            # if PrimerTypes[1 - PT] in matchedPrimers.keys():
            opponentIndexes = [
                P.chr_index
                for P in matchedPrimers[PrimerTypes[1 - PT]]
            ]
            for p, P in enumerate(matchedPrimers[PrimerType]):
                if P.chr_index not in opponentIndexes:
                    matchedPrimers[PrimerType][p] = None

            matchedPrimers[PrimerType] = [
                p for p in matchedPrimers[PrimerType] if p
            ]

            # might be unnecessary
            matchedPrimers[PrimerType] = sorted(matchedPrimers[PrimerType],
                                                key=lambda x: x.chr_length,
                                                reverse=True)[:1]

            # PRIMER LEAK IS UNAVOIDABLE;
            if len(matchedPrimers[PrimerType]) > 1:
                matchSuccess[PT] = False
        print()

    print("\n\n")

    # RETRIEVE INTERPRIMER SEQUENCES;
    matchCount = sum([len(matchedPrimers[PrimerType])
                      for PrimerType in PrimerTypes])

    # TWO MATCHES... IDEAL SCENARIO;
    if matchCount == 2:
        Primers = [matchedPrimers[PrimerTypes[i]][0] for i in range(2)]
        # if anything goes wrong while building the amplicon, the match fails.
        # Amplicon may rase errors deliberately
        # when match result is not optimal.
        try:
            amplicon = GeneticEntities.Amplicon(genome, Primers[0], Primers[1])
        except ValueError:
            return "", [False, False]

        mp = (matchedPrimers[PrimerTypes[0]], matchedPrimers[PrimerTypes[1]])
        return amplicon.Sequence, mp
    else:
        return "", matchSuccess


def matchPrimerOnGenome(genome, PrimerSequence,
                        PrimerType, maxNumberMatches=None):
    matchedPrimers = []

    for chromosome in genome:
        primerMatches, sequenceVariationName = findPrimer(
            chromosome,
            PrimerSequence
        )
        if primerMatches:
            print("\t@%s" % sequenceVariationName)

            # TBD: what to do about this?
            if len(primerMatches) > 1:
                print("Primer overflow!")

            match = primerMatches[0]
            match_position = match.start()

            # SEARCH REGION ON ANNOTATED CHROMOSOMES;
            print("Found at chromosome %s" % chromosome.name)
            print("pos %i of %i" % (match.start(), chromosome.length))

            # RECORD PRIMER;
            matchedPrimer = GeneticEntities.primerMatch(
                match,
                PrimerType,
                chromosome,
                PrimerSequence
            )

            matchedPrimers.append(matchedPrimer)

            if maxNumberMatches is not None:
                if len(matchedPrimer) >= maxNumberMatches:
                    break

    return matchedPrimers


def validatePrimer(V):
    if type(V) == np.float64:
        return False
    if type(V) == float:
        return False
    elif not V:
        return False
    else:
        return True


def matchLocusOnGenomes(locus_name,
                        locus_info,
                        genomes,
                        overallProgress=(0, 0),
                        rebootTolerance=20,
                        bruteForceSearcher=None):
    LocusAmpliconSet = {}

    def initPrimerHolder():
        return {k: [] for k in locus_info.keys()}

    primerTrash = initPrimerHolder()
    testablePrimers = initPrimerHolder()


    # load primer pair data from user-made Primer file;
    primerPair = dict(locus_info)

    RebootCount = 0

    # ITERATE GENOMES UNTIL SUCCESS;
    for Genome in itertools.cycle(genomes):
        # print("Genome: %s --\n" % genome)

        # Show header;
        HEADER_INFO = (
            *overallProgress,
            RebootCount + 1,
            locus_name,
            Genome.name
        )
        M = ">>> Locus %i of %i | run number %i ->  Searching %s on %s"
        print(M % HEADER_INFO)

        # primer sequence may be uknown/invalid;
        primerIntegrity = [
            validatePrimer(primerPair[PrimerType])
            for PrimerType in PrimerTypes
        ]

        AmpliconSequence = ""
        print("\n")

        # fix this later..
        matchSuccess = primerIntegrity

        if all(primerIntegrity):
            print("Searching sequence for locus %s" % locus_name)

            AmpliconSequence, matchSuccess =\
                searchPrimerPairOnGenome(locus_name, primerPair, Genome)

            # print(matchSuccess)

        # FAILURE ON MATCHING A PRIMER?
        if not all(matchSuccess):
            for PT, match in enumerate(matchSuccess):
                PrimerType = PrimerTypes[PT]
                if not match:
                    print("Resetting %s!" % PrimerType)

                    # delete current primer;
                    if validatePrimer(primerPair[PrimerType]):
                        primerTrash[PrimerType].append(primerPair[PrimerType])

                    primerPair[PrimerType] = None

                    # RESET ALL MATCHES!
                    LocusAmpliconSet = {}

                    RebootCount += 1
                    # brute force for the problematic genome!
                    print("Searching new primer on gene sequence...")
                    # print(bruteForceSearcher.matchedGenome)

                    # MANAGE PRIMERS ON HOLSTER;
                    if not testablePrimers[PrimerType]:
                        if bruteForceSearcher:
                            newPrimers =\
                                bruteForceSearcher.launchBruteForcePrimerSearch(locus_name, Genome, PT)
                            if not newPrimers:
                                print("Warning: No bruteforce primers found...")

                            testablePrimers[PrimerType] = newPrimers
                        else:
                            print("Brute force primer finder is disabled.")
                            return None, None, None

                    while testablePrimers[PrimerType]:
                        print("Fetching new primer from reserve...")
                        random.shuffle(testablePrimers[PrimerType])
                        primerPair[PrimerType] = testablePrimers[PrimerType].pop()
                        if primerPair[PrimerType] not in primerTrash[PrimerType]:
                            break
        else:
            # Final sucess check.
            Sucess = True
            print("Found amplicon of length %i" % len(AmpliconSequence))
            if len(AmpliconSequence) <= 100:
                # AMPLICON IS TOO SHORT;
                print("Resetting due to short amplicon.")
                Sucess = False

            if "n" in AmpliconSequence.lower():
                print("Resetting due to N found in sequence.")
                Sucess = False

            if Sucess:
                LocusAmpliconSet[Genome.name] = AmpliconSequence
            else:
                print("Resetting all primers, amplicon too short.")
                for s in range(2):
                    if validatePrimer(primerPair[PrimerTypes[s]]):
                        primerTrash[PrimerTypes[s]].append(primerPair[PrimerTypes[s]])
                    primerPair[PrimerTypes[s]] = None
                # Reset Matches;
                LocusAmpliconSet = {}

        # CHECK LOCUS PROGRESS ACROSS ALL GENOMES;
        progressMark = len(list(LocusAmpliconSet.keys())) / len(genomes)
        print("%s match progress: %.2f%%" % (locus_name, progressMark * 100))
        print()

        # IS LOCUS DONE?
        if progressMark == 1:
            print(">>> Matched %s on all genomes." % locus_name)
            print()
            print()

            primerPair["RebootCount"] = RebootCount

            # exit loop...
            return LocusAmpliconSet, matchSuccess, primerPair

        # IF IT FAILS ENOUGH, SKIP LOCUS;
        elif RebootCount > rebootTolerance:
            return None, None, None
