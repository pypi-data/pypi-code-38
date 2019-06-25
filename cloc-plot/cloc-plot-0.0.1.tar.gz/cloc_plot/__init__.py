import os
import sys
import json
import subprocess
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.transforms import Bbox
from collections import OrderedDict

def die(msg):
    print('\033[31:1m !!! \033[0m{}'.format(msg))
    sys.exit(1)

def info(msg):
    print('\033[32:1m *** \033[0m{}'.format(msg))

def label(pct):
    if pct > 5:
        return '{:.1f}%'.format(pct)
    return None

def main():
    projects = sys.argv[1:]

    if len(projects) <= 0:
        die('Please provide projects to count the lines of code')

    for project in projects:
        if not os.path.isdir(project):
            die('The project {} does not exist!'.format(project))

    project_stats = []
    for project in projects:
        info('Collecting statistics for {}...'.format(project))
        process = subprocess.Popen(
            ['cloc', '--exclude-dir=target,vendor,node_modules,build', '--json', project],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        out, _ = process.communicate()
        if process.returncode != 0:
            die('Failed to count the lines of code for {}!'.format(project))

        stats = json.loads(out)
        stats.pop('header', None)
        stats.pop('SUM', None)
        stats = {
            'name': project,
            'loc': [ { 'lang': key, 'lines': value['code'] } for key, value in stats.items() ],
            'sum': sum(v['code'] for v in stats.values()),
        }

        project_stats.append(stats)

    fig, ax = plt.subplots(figsize = (16, 8))
    size = 0.3
    languages = []
    locs = []
    for stats in project_stats:
        languages.extend([ v['lang'] for v in stats['loc'] ])
        locs.extend([ v['lines'] for v in stats['loc'] ])

    color_dict = {}
    cmap = plt.get_cmap('Set3')
    for idx, lang in enumerate(languages):
        if lang not in color_dict:
            color_dict[lang] = cmap((idx + 3) % 12)
    colors = [ color_dict[l] for l in languages ]

    wedges, texts, autotexts = ax.pie(
        locs,
        radius = 1 - size,
        labels = languages,
        colors = colors,
        labeldistance = None,
        autopct = label,
        pctdistance = 0.75,
        textprops=dict(color='w'),
        wedgeprops=dict(width=size, edgecolor='w'),
    )
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    ax.legend(
        by_label.values(),
        by_label.keys(),
        title = 'Languages',
        bbox_to_anchor = (0.975, 0, 0.5, 1),
        loc = 'best',
    )
    plt.setp(autotexts, size = 12, weight = 'bold')
    loc_sum = sum(locs)
    wedges, texts, autotexts = ax.pie(
        [v['sum'] for v in project_stats],
        radius = 1,
        colors = plt.get_cmap('Accent')(range(len(project_stats))),
        labels = [v['name'] for v in project_stats],
        labeldistance = 1.1,
        autopct = lambda pct: '{:.2f} k'.format((pct / 100) * loc_sum / 1000) if pct > 5 else None,
        pctdistance = 0.85,
        #textprops=dict(color='w'),
        wedgeprops=dict(width=size, edgecolor='w'),
    )
    plt.setp(autotexts, size = 12, weight = 'bold', color = 'w')
    plt.text(1, -1.25,'created with github.com/fin-ger/py-cloc-plot')

    plt.savefig('plot.png')
