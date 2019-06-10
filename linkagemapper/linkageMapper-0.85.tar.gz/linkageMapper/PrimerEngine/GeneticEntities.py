#!/bin/python


from Bio.Seq import Seq
from collections import OrderedDict
import os


class Genome():
    def __init__(self, genomeFilePath):
        self.name = os.path.splitext(os.path.basename(genomeFilePath))[0]
        self.chromosomes = self.loadFromFasta(genomeFilePath)

        self.idx = 0

    def __iter__(self):
        return self

    def __getitem__(self, idx):
        return self.chromosomes[idx]

    def __next__(self):
        self.idx += 1
        try:
            return self.chromosomes[self.idx - 1]
        except IndexError:
            self.idx = 0
            raise StopIteration  # Done iterating.

    def loadFromFasta(self, filePath, contigLengthThreshold=1000):

        genome = open(filePath).read()

        chromosomes = genome.lower().split(">")

        output_chromosomes = []
        for chromosome in chromosomes:
            schromosome = chromosome.split('\n')
            name = schromosome[0]

            sequence = "".join(schromosome[1:])

            # IGNORE SEQUENCE CONTIGS OF SMALL SIZES;
            if len(sequence) > contigLengthThreshold:
                Index = len(output_chromosomes)
                output_chromosome = Chromosome(Index, name, sequence)
                output_chromosomes.append(output_chromosome)

        return output_chromosomes


class Chromosome():
    def __init__(self, index, name, sequence):
        self.name = name
        self.sequence = sequence
        self.length = len(self.sequence)
        self.index = index


class Amplicon():
    # BUILD THE AMPLICON;
    def __init__(self, genome, leadingPrimer, trailingPrimer):
        Primers = [leadingPrimer, trailingPrimer]
        readingFrame = [p.position for p in Primers]

        # just check...
        chromosome_indexes = [p.chr_index for p in Primers]
        if len(list(set(chromosome_indexes))) > 1:
            print("FAILURE: Building amplicon with markers at different chromosomes?")
            raise ValueError


        chromosome_index = chromosome_indexes[0]
        chromosome = genome[chromosome_index]

        # SOMETIMES GENOMIC SEQUENCES COME IN AS REVERSE COMPLEMENTS...
        ReversedAmplicon = False
        readingFramePos = [r.start() for r in readingFrame]
        if sorted(readingFramePos) != readingFramePos:
            readingFrame = readingFrame[::-1]
            ReversedAmplicon = True

        readingFrameBounds = [
            readingFrame[0].end(),
            readingFrame[1].start()
        ]

        self.Sequence = chromosome.sequence[readingFrameBounds[0]:readingFrameBounds[1]]
        if ReversedAmplicon:
            self.Sequence = str(Seq(self.Sequence).reverse_complement())

        self.chr_name = leadingPrimer.chr_name


class primerMatch():
    def __init__(self, pos, label, chromosome, primer_seq):
        self.position = pos
        self.label = label
        self.chr_name = chromosome.name
        self.chr_length = chromosome.length
        self.chr_index = chromosome.index
        self.sequence = primer_seq

    def to_dict(self, locusName):
        row = OrderedDict()
        row["Locus"] = locusName
        row["Sequence"] = self.sequence
        row["Chromosome"] = self.chr_name

        positions = (self.position.start(), self.position.end())
        row["PositionStart"] = min(positions)
        row["PositionEnd"] = max(positions)
        return row
