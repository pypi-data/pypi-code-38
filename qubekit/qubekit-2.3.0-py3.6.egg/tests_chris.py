#!/usr/bin/env python

from QUBEKit.engines import QCEngine, RDKit
from QUBEKit.ligand import Ligand, Protein
from QUBEKit.helpers import Configure

import os

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from numpy import arange
from numpy.polynomial.polynomial import polyfit

import networkx as nx


def main():
    """
    Currently you cannot pass marker style as a list in Matplotlib.
    To get around that, the data could be grouped by atom type and the colour passed as a list.
    Then it would be possible to plot atoms which are the same type together,
    while also maintaining the correct colours from the molecule names.

    Anyway, this function collects the data from the txt file for ONETEP, DDEC3&6 charges.
    The data are stored in a dictionary where the keys are the molecule names
    and the values are a list of lists. Each nested list is an atom in the form:
    ['Atom Type', 'DDEC3 charge', 'DDEC6 charge', 'ONETEP charge']

    Overall, this gives something like:

    data = {'Benzene': [['C', '-0.108887', '-0.101384', '-0.1146'], ['C', ... ], ... ], 'Methane': ... }

    The data are transformed to floats in the graphing section.
    """

    font = {'family': 'sans-serif',
            # 'weight': 'bold',
            'size': 14}

    plt.rc('font', **font)

    data = dict()

    # Extract molecule data, using 'Atom' header as start marker, and 'p' as end marker
    with open('../../../Documents/QUBEKit_vs_ONETEP/comparison_data.txt', 'r') as file:
        lines = file.readlines()

    for count, line in enumerate(lines):
        if line.startswith('Atom'):
            data[lines[count - 1][:-1]] = []
            i = 1
            while lines[count + i].split()[0] != 'p':
                data[lines[count - 1][:-1]].append(lines[count + i].split())
                i += 1

    # Can change colours used here if you want. Currently just using defaults.
    colours = {'Acetamide': 'r', 'Benzene': 'b', 'Acetic acid': 'y',
               'Acetophenone': 'k', 'Aniline': 'g', 'DMSO': 'm',
               '2-Heptanone': 'c', '1-Octanol': 'grey', 'Phenol': 'indigo',
               'Pyridine': 'olive'}

    # Marker dict to change element names to Matplotlib marker styles.
    markers = {'O': 'o', 'C': '<', 'H': 's', 'N': 'd', 'S': '*'}

    # Apply marker changes across all molecules' atoms (massive pain to implement into graph so currently useless).
    for key, val in data.items():
        for i in range(len(val)):
            data[key][i][0] = markers[data[key][i][0]]

    # Indicates the column positions for extracting from data = { ... }
    mark, ddec3, ddec6, onetep = 0, 1, 2, 3

    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.set_autoscaley_on(False)
    ax1.set_xlim([-1, 1])
    ax1.set_ylim([-1, 1])
    ax1.set(adjustable='box-forced', aspect='equal')

    # Add black diagonal line for reference.
    line = mlines.Line2D([0, 1], [0, 1], color='k')
    transform = ax1.transAxes
    line.set_transform(transform)
    ax1.add_line(line)

    [ax1.scatter([float(col[onetep]) for col in val], [float(col[ddec3]) for col in val],
                 marker='x', s=80) for key, val in data.items()]

    ax1.set_xlabel('ONETEP')
    ax1.set_ylabel('QUBEKit (IPCM, DDEC3)')
    ax1.grid(True)
    ax1.annotate('R² = 0.984', xy=(-0.8, 0.8))

    # Best fit
    x = arange(-1, 2)
    y = 0.9095 * x - 3 * (10 ** -8)
    b, m = polyfit(x, y, 1)
    ax1.plot(x, b + m * x, '-')

    ax2.set_autoscaley_on(False)
    ax2.set_xlim([-1, 1])
    ax2.set_ylim([-1, 1])
    ax2.set(adjustable='box-forced', aspect='equal')

    line = mlines.Line2D([0, 1], [0, 1], color='k')
    transform = ax2.transAxes
    line.set_transform(transform)
    ax2.add_line(line)

    [ax2.scatter([float(col[ddec6]) for col in val], [float(col[ddec3]) for col in val],
                 marker='x', s=80) for key, val in data.items()]

    ax2.set_xlabel('QUBEKit (IPCM, DDEC6)')
    ax2.set_ylabel('QUBEKit (IPCM, DDEC3)')
    ax2.grid(True)
    ax2.annotate('R² = 0.944', xy=(-0.8, 0.8))

    # Best fit
    x = arange(-1, 2)
    y = 1.1255 * x + 0.0021
    b, m = polyfit(x, y, 1)
    ax2.plot(x, b + m * x, '-')

    plt.legend(['Equally Charged', 'LSR'] + [str(key) for key, val in data.items()], loc='lower right')

    plt.show()


def parse_molecules():

    folder_names = []
    for root, dirs, files in os.walk('../../../Documents/SI_data/molecules'):
        folder_names.append(dirs)

    folder_names = [folder for folder in folder_names if folder]
    folder_names = folder_names[0]

    for folder in folder_names:
        try:
            os.system(f'cp ../../../Documents/SI_data/molecules/{folder}/MOL.pdb ../../../Documents/test_set/{folder.replace(",", "_").replace("-", "_")}.pdb')
            os.system(f'cp ../../../Documents/SI_data/molecules/{folder}/MOL.xml ../../../Documents/test_set/{folder.replace(",", "_").replace("-", "_")}.xml')
        except:
            pass


# import matplotlib.animation as animation
#
#
# fig = plt.figure()
# ax1 = fig.add_subplot(1, 1, 1)
#
#
# def animate(i):
#
#     pull_data = open('sample_data.txt').read()
#     data_array = pull_data.split('\n')
#     xar = []
#     yar = []
#     for each_line in data_array:
#         if len(each_line) > 1:
#             x, y = each_line.split(',')
#             xar.append(int(x))
#             yar.append(int(y))
#     ax1.clear()
#     ax1.plot(xar, yar)
#
#
# ani = animation.FuncAnimation(fig, animate, interval=1000)
#
# plt.show()

try:
    a = 1/0
except ZeroDivisionError:
    raise
