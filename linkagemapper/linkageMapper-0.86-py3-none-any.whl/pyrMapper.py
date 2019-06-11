#!/bin/python

from primerFinder import loadGenome

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
# sphinx_gallery_thumbnail_number = 2


def plot_heatmap(allWindows, windowNames):
    vegetables = ["cucumber", "tomato", "lettuce", "asparagus",
                  "potato", "wheat", "barley"]
    farmers = ["Farmer Joe", "Upland Bros.", "Smith Gardening",
               "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]

    _allWindows = np.array(allWindows)
    print(_allWindows)
    fig, ax = plt.subplots()
    im = ax.imshow(_allWindows)

    # We want to show all ticks...
    #ax.set_xticks(np.arange(len(farmers)))
    # ... and label them with the respective list entries
    #ax.set_xticklabels(farmers)

    ax.set_yticks(np.arange(len(windowNames)))
    ax.set_yticklabels(windowNames)

    # Rotate the tick labels and set their alignment.
    #plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
    #         rotation_mode="anchor")
    """
    # Loop over data dimensions and create text annotations.
    for i in range(len(vegetables)):
        for j in range(len(farmers)):
            text = ax.text(j, i, harvest[i, j],
                           ha="center", va="center", color="w")
    """
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Percent Pyr-Pyr", rotation=-90, va="bottom")
    ax.set_title("Genomic pyrimidine-pyrimidine content by chromssome.")
    fig.tight_layout()
    plt.show()

chr_info, chrs = loadGenome("genomes/ToxoDB-39_TgondiiVEG_Genome.fasta")

pyr = ['t', 'c']

windowsPerSequence = 50

allWindows = []
windowNames = []
for s, sequence in enumerate(chrs):
    print(chr_info[s])
    windowSize = len(sequence) // 50
    windows = []
    if len(sequence) < 10000:
        continue
    doubled = 0
    windowCount = 0
    print(len(sequence))
    for b, base in enumerate(sequence):
        try:
            nextBase = sequence[b + 1]
        except IndexError as e:
            print("Finished.")
            break

        if base in pyr:
            if nextBase in pyr:
                doubled += 1

        windowCount += 1
        if windowCount >= windowSize:
            windows.append(doubled / windowCount)
            doubled = 0
            windowCount = 0

    print(windows)
    windows = windows[:40]
    allWindows.append(windows)
    info = chr_info[s].split(" ")[0]
    windowNames.append(info)
    print(len(windows))

plot_heatmap(allWindows, windowNames)
