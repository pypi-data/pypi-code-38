#!/bin/python

import os
import matplotlib
from matplotlib.patches import Circle, Wedge, Polygon, Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import requests

from Bio import SeqIO
"""

This code is based on https://gist.github.com/kantale/e390cf7a47c4afdff9e4

"""


def plot_chromosome(ax, chromosome, reference_length, order):

    DIM = 1.0
    chromosome_length = chromosome["length"]

    x_start = order * DIM * 0.1
    x_end = x_start + (DIM * 0.04)
    y_start = DIM * 0.9 * (chromosome_length / reference_length)
    y_end = DIM * 0.1

    # We use the same colors as: http://circos.ca/tutorials/lessons/2d_tracks/connectors/configuration
    colors = {
        'gpos100': (0/255.0, 0/255.0, 0/255.0),
        'gpos': (0/255.0, 0/255.0, 0/255.0),
        'gpos75': (130/255.0, 130/255.0, 130/255.0),
        'gpos66': (160/255.0, 160/255.0, 160/255.0),
        'gpos50': (200/255.0, 200/255.0, 200/255.0),
        'gpos33': (210/255.0, 210/255.0, 210/255.0),
        'gpos25': (200/255.0, 200/255.0, 200/255.0),
        'gvar': (220/255.0, 220/255.0, 220/255.0),
        'gneg': (255/255.0, 255/255.0, 255/255.0),
        'acen': (217/255.0, 47/255.0, 39/255.0),
        'stalk': (100/255.0, 127/255.0, 164/255.0),
    }

    HighlightedNames = []
    for index, piece in enumerate(chromosome["regions"]):

        current_height = piece[2] - piece[1]
        current_height_sc = ((y_end - y_start) /
                             chromosome_length) * current_height
        if index == 0:
            y_previous = y_start

        y_next = y_previous + current_height_sc

        color = colors[piece[4]]

        # plot the caryotypes
        r = Rectangle((x_start, y_previous), x_end-x_start,
                      current_height_sc, color=color)
        ax.add_patch(r)

        Highlight = piece[5]
        if Highlight:
                HighlightedNames.append(piece[3])
        y_previous = y_next

    # Plot highlighted names
    y_names = y_start + 0.03 * len(HighlightedNames)
    for Name in HighlightedNames:
            ax.text(x_start, y_names, Name)
            y_names -= 0.03

    # Plot semicircles at the beginning and end of the chromosomes
    center_x = x_start + (x_end - x_start) / 2.0
    radius = (x_end - x_start) / 2.0
    theta1 = 0.0
    theta2 = 180.0

    w1 = Wedge((center_x, y_start), radius, theta1, theta2,
               width=0.00001, facecolor='white', edgecolor='black')
    w2 = Wedge((center_x, y_end), radius, theta2, theta1,
               width=0.00001, facecolor='white', edgecolor='black')

    ax.add_patch(w1)
    ax.add_patch(w2)
    ax.plot([x_start, x_start], [y_start, y_end], ls='-', color='black')
    ax.plot([x_end, x_end], [y_start, y_end], ls='-', color='black')

    ax.text(center_x, y_end - (DIM * 0.07), chromosome["name"])

    '''
    To create a karyo_filename go to: http://genome.ucsc.edu/cgi-bin/hgTables 
    group: Mapping and Sequencing
    track: Chromosome Band 
    An example of an output (hg19, Human) is here: http://pastebin.com/6nBX6sdE 
    The script will plot dots next to loci defined in metadata as:
    metadata = {
            '1' : [2300000, 125000000, 249250621],
    }
    '''


def readAnnotation(Annotation, HighlightGenes):
    Regions = {}
    for c, chromosome in enumerate(Annotation):
        Allowed = True
        for f, feature in enumerate(chromosome.features):
            if not f:
                if "chromosome" not in feature.qualifiers.keys():
                    Allowed = False
                    continue
                Chr = feature.qualifiers["chromosome"][0]
                Regions[Chr] = {
                        "length": feature.location.end,
                        "regions": [],
                        "name": Chr
                }

            if not Allowed:
                continue

            Highlight = False
            if feature.type == "gene":
                q = feature.location.start
                w = feature.location.end
                if "gene" in feature.qualifiers.keys():
                        Name = feature.qualifiers["gene"][0]
                elif "locus_tag" in feature.qualifiers.keys():
                        Name = feature.qualifiers["locus_tag"][0]

                color = "gpos75"
                if Name in HighlightGenes:
                        print(">%s" % Name)
                        color = "acen"
                        Highlight = True
                Tag = [
                        Chr,
                        q,
                        w,
                        Name,
                        color,
                        Highlight
                ]
                Regions[Chr]["regions"].append(Tag)

    return Regions


def drawIdeogram(fig, Regions, options=None):

    ax = fig.add_subplot(111)
    DIM = 1.0
    ax.set_xlim([0.0, DIM * 1.8])
    ax.set_ylim([0.0, DIM * 1.4])

    reference_length = max([
            Regions[k]["length"]
            for k in Regions.keys()
    ])

    for i, k in enumerate(Regions.keys()):
        plot_chromosome(ax, Regions[k], reference_length, i)

    ax.axis('off')


def plotIdeogram(fig, alnData,
                 RegionIndexes,
                 showLabelColors=False,
                 AnnotationPath=None):

    if not AnnotationPath:
        return

    HighlightGenes = alnData.fetchOriginalLociList()
    Annotation = SeqIO.parse(AnnotationPath, format="genbank")

    Features = readAnnotation(Annotation, HighlightGenes)

    drawIdeogram(fig, Features)
