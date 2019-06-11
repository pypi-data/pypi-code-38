#!/bin/python

import os

from Bio.Graphics import GenomeDiagram
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio import SeqIO
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# from ..Database import annotationManager
import pdfrw

import re
import numpy as np


def plotGeneArea(Primers, referenceGenome):
    # PLOT SURROUNDING GENE AREA;
        #geneSearchPosition = np.mean([p.position.start() for p in Primers])

        PrimerPositions = [P.position for P in Primers]
        MED = np.median(PrimerPositions)

        chromosomeGenes = None
        chromosomeFeatures = None
        for chromosome in referenceGenome:
            query_chr = " %s," % chromosome
            if query_chr.lower() in amplicon.chr_name:
                # chromosomeGenes = allGenes[allGenes.chromosome == gene_chr]
                chromosomeShortName = re.findall(" (\w+),", amplicon.chr_name)[0].upper()
                CFIndex = genomeFeaturesChromosomes.index(chromosomeShortName)
                chromosomeFeatures = genomeFeatures[CFIndex]

        if chromosomeFeatures is None:
            print("Sequence features not found in chromosome sequences.")


        # LOCATE FEATURES LOCATED NEAR PRIMER SITE;
        wanted_max_span = 150000

        PrimerFeatures = []
        for feature in chromosomeFeatures.features:
            if feature.type in ["gene"]:
                Distance = abs(geneSearchPosition - feature.location.start.real)
                if Distance < wanted_max_span:
                    if "gene" in feature.qualifiers.keys():
                        print(feature)
                        PrimerFeatures.append(feature)

        if PrimerFeatures:
            PRIMERDATA[locus_name] = {}
            PRIMERDATA[locus_name]["features"] = PrimerFeatures
            PRIMERDATA[locus_name]["primers"] = \
                [(p.position.start(), p.label)
                 for p in Primers]

            PRIMERDATA[locus_name]["chromosome"] = Primers[0].chr_name
            filepath = os.path.join(options.outputPath, "region_map.pdf")
            geneGraphs.plotMultiChr(PRIMERDATA, filepath)

        print("\n")


def plotAnnotationFile(annotationFilePath, outputDirectory):

    outputFileName = os.path.split(annotationFilePath)[-1]
    outputFeatures = annotationManager.loadFeatures(annotationFilePath)
    # this is kinda crappy... need to organize this whole gene graphs situation.

    # this will hold lists of features, each list for one page of plot.
    outputFeaturesList = []
    d = []
    for k in outputFeatures:
        d.append(k)
        if len(d) == 28:
            outputFeaturesList.append(d)
            d = []

    for out, _outputFeatures in enumerate(outputFeaturesList):
        _outputFeatures = {
            outputFileName: {
                "features": _outputFeatures,
                "primers": []
            },
        }
        _outputFileName = "%s_%i" % (outputFileName, out + 1)
        _outputFilePath = os.path.join(outputDirectory, _outputFileName) + ".pdf"
        plotMultiChr(_outputFeatures, _outputFilePath)


def plotMultiChr(genes, outputPath, multipleFiles=False):
    gene_list = sorted(list(genes.keys()))
    Name = ""
    Diagram = GenomeDiagram.Diagram(name=Name)
    Track = Diagram.new_track(1, name=Name)
    TrackSet = Track.new_set(name=Name)

    for g, gene in enumerate(gene_list):
        Name = "150kb em volta de %s" % gene

        for feature in genes[gene]["features"]:
            color = colors.blue if "gene" in feature.qualifiers else colors.lightblue
            TrackSet.add_feature(feature,
                                 sigil="ARROW",
                                 label=True,
                                 label_position="middle",
                                 label_size=14,
                                 color=color)

        for p, primer in enumerate(genes[gene]["primers"]):
            primer_pos, primer_name = primer
            strand = 1 if p == 0 else -1
            primer_feature = SeqFeature(FeatureLocation(primer_pos, primer_pos + 10, strand=strand))

            TrackSet.add_feature(primer_feature,
                                 name=primer_name,
                                 label=False,
                                 label_size=17,
                                 label_angle=0,
                                 label_color=colors.red,
                                 color=colors.red)

        startingPos = genes[gene]["features"][0].location.start.real
        Diagram.draw(
            format="linear",
            pagesize='A2',
            fragments=6,
            start=startingPos
        )

    Diagram.write(outputPath, "PDF")
    watermarkAndSave(gene, outputPath)


def watermarkAndSave(figureName, outputPath, subtitle=None, verticalLabel=40):
    # CREATE WATERMARK AND SAVE PDF FILE;

    watermark = canvas.Canvas("dummy.pdf")
    watermark.setFont("Helvetica", 20)
    watermark.drawString(10, verticalLabel, figureName)

    if subtitle:
        watermark.setFont("Helvetica", 14)
        watermark.drawString(20, verticalLabel - 20, subtitle)
    watermark.save()

    #outputPath = "graphs/TGONDIILOCI_%s.pdf" % gene


    # JOIN WATERMARK WITH OUTPUT
    base = pdfrw.PdfReader(outputPath)
    watermark = pdfrw.PdfReader("dummy.pdf").pages[0]

    merger = pdfrw.PageMerge(base.pages[0])
    merger.add(watermark).render()
    writer = pdfrw.PdfWriter()
    writer.write(outputPath, base)

    os.remove("dummy.pdf")


if __name__ == "__main__":
    annotationDirectory = "annotations"
    outputDirectory = "graphs"

    for annotation in os.listdir(annotationDirectory):
        filePath = os.path.join(annotationDirectory, annotation)
        plotAnnotationFile(filePath, outputDirectory)
