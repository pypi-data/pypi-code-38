# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 15:25:06 2019

@author: michaelek
"""
import os
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
#from collections import OrderedDict
#from datetime import datetime


#####################################
### Global parameters

date1 = pd.Timestamp.now()
date2 = date1.strftime('%Y%m%d%H%M')

sns.set_style("whitegrid")
sns.set_context('poster')
base_names = {'{}_allo': '{}_restr_allo', '{}_metered_allo': '{}_metered_restr_allo', '{}_usage': '{}_usage'}
base_label_names = {'{}_allo': '{} Allocation', '{}_restr_allo': '{} Allocation with Restrictions', '{}_metered_allo': '{} Metered Allocation', '{}_metered_restr_allo': '{} Metered Allocation with Restrictions', '{}_usage': '{} Usage'}
dict_type = {'water_supply': 'Water Supply', 'irrigation': 'Irrigation', 'stockwater': 'Stockwater', 'other': 'Other', 'industrial': 'Industrial', 'municipal': 'Municipal'}

#####################################
### Functions


def plot_group(self, freq, val='total', group='SwazName', with_restr=True, yaxis_mag=1000000, yaxis_lab='Million', col_pal='pastel', export_path='', **kwargs):
    """
    Function to plot the allocation, metered allocation, and usage as a time series barchart with three adjacent bars per time period. Optionally with restriction volumes.

    Parameters
    ----------
    freq : str
        The Pandas time series freq.
    val : str
        The volume value columns. Must be one of 'total', 'gw', or 'sw'.
    group : str
        The grouping of the plot sets. Where each plot will be broken into the group values.
    with_restr : bool
        Should the restriction volumes be included in the plots?
    yaxis_mag : int
        The magnitude that the volumes should be divided by and plotted with on the Y axis.
    yaxis_lab : str
        The label of the Y axis.
    col_pal : str
        The seaborn color palette to use.
    export_path : str
        The path where all the plots will be saved.
    **kwargs
        Any kwargs to be passed to get_ts.

    Returns
    -------
    None
        But outputs many png files to the export_path.
    """
    plt.ioff()

    ### prepare inputs
    col_pal1 = sns.color_palette(col_pal)

    vol_names = {key.format(val): value.format(val) for key, value in base_names.items()}
    label_names = {key.format(val): value.format(val.capitalize()) for key, value in base_label_names.items()}

    groupby = ['date']
    if isinstance(group, str):
        groupby.insert(0, group)

    datasets = ['allo', 'metered_allo', 'usage']
    if with_restr:
        datasets.extend(['restr_allo', 'metered_restr_allo'])

    ### Get ts data
    ts1 = self.get_ts(datasets, freq, groupby, **kwargs)

    ts2 = ts1[[c for c in ts1 if val in c]] / yaxis_mag

    ### Prepare data
    top_grp = ts2.groupby(level=group)

    for i, grp1 in top_grp:

        if grp1.size > 1:

            set1 = grp1.loc[i].reset_index()

            allo_all = pd.melt(set1, id_vars='date', value_vars=list(vol_names.keys()), var_name='tot_allo')

            index1 = allo_all.date.astype('str')

            ## Plot total allo
            fig, ax = plt.subplots(figsize=(15, 10))
            sns.barplot(x=index1, y='value', hue='tot_allo', data=allo_all, palette=col_pal1, edgecolor='0')

            if with_restr:
                allo_up_all = pd.melt(set1, id_vars='date', value_vars=list(vol_names.values()), var_name='up_allo')
                allo_up_all.loc[allo_up_all.up_allo.str.contains('usage'), 'up_allo'] = 'unused'
                allo_up_all.loc[allo_up_all.up_allo.str.contains('usage'), 'value'] = 0
                sns.barplot(x=index1, y='value', hue='up_allo', data=allo_up_all, palette=col_pal1, edgecolor='0', hatch='/')
            plt.ylabel('Water Volume $(' + yaxis_lab + '\; m^{3}/year$)')
            plt.xlabel('Water Year')

            # Legend
            handles, lbs = ax.get_legend_handles_labels()
            order1 = [lbs.index(j) for j in label_names if j in lbs]
            labels = [label_names[lbs[i]] for i in order1 if lbs[i] in label_names]
            plt.legend([handles[i] for i in order1], labels, loc='upper left')
    #        leg1.legendPatch.set_path_effects(pathe.withStroke(linewidth=5, foreground="w"))

            # Other plotting adjustments
            xticks = ax.get_xticks()
            if len(xticks) > 15:
                for label in ax.get_xticklabels()[::2]:
                    label.set_visible(False)
                ax.xaxis_date()
                fig.autofmt_xdate(ha='center')
                plt.tight_layout()
            plt.tight_layout()
#          sns.despine(offset=10, trim=True)

            # Save figure
            plot2 = ax.get_figure()
            export_name = '_'.join([i, val, date1.strftime('%Y%m%d%H%M')]) + '.png'
            export_name = export_name.replace('/', '-').replace(' ', '-')
            plot2.savefig(os.path.join(export_path, export_name))
            plt.close()

    plt.ion()


def plot_stacked(self, freq, val='total', stack='use_type', group='SwazName', yaxis_mag=1000000, yaxis_lab='Million', col_pal='pastel', export_path='', **kwargs):
    """
    Function to plot the allocation stacked by a specific 'stack' group as a time series barchart.

    Parameters
    ----------
    freq : str
        The Pandas time series freq.
    val : str
        The allocation volume column. Must be one of 'total', 'gw', or 'sw'.
    stack : str
        The field of categories used for the volume stacking.
    group : str
        The grouping of the plot sets. Where each plot will be broken into the group values.
    with_restr : bool
        Should the restriction volumes be included in the plots?
    yaxis_mag : int
        The magnitude that the volumes should be divided by and plotted with on the Y axis.
    yaxis_lab : str
        The label of the Y axis.
    col_pal : str
        The seaborn color palette to use.
    export_path : str
        The path where all the plots will be saved.
    **kwargs
        Any kwargs to be passed to get_ts.

    Returns
    -------
    None
        But outputs many png files to the export_path.
    """
    plt.ioff()

    ### Prepare inputs
    col_pal1 = sns.color_palette(col_pal)

    vol_name = '{}_allo'.format(val)
#    label_name = {'{}_allo'.format(val): '{} Allocation'.format(val.capitalize())}

    groupby = [stack, 'date']
    if isinstance(group, str):
        groupby.insert(0, group)

    datasets = ['allo']
#    if with_restr:
#        datasets.extend(['restr_allo'])

    ### Get ts data
    ts1 = self.get_ts(datasets, freq, groupby, **kwargs)

    ts2 = ts1[vol_name] / yaxis_mag

    ### Reorganize data

    ts3 = ts2.unstack([0,2]).cumsum().stack([0,1]).reorder_levels([1,0,2])
    ts3.name = 'vol'
    if stack == 'use_type':
        ts3.rename(dict_type, level='use_type', inplace=True)

    top_grp = ts3.groupby(level=group)

    stack_levels = ts3.index.levels[1]
    col_lab = {stack_levels[i]: col_pal1[i] for i in np.arange(stack_levels.size)}

    for i, grp1 in top_grp:
        i
        if grp1.size > 1:

            grp2 = grp1.groupby('use_type').sum().sort_values(ascending=False).index

            fig, ax = plt.subplots(figsize=(15, 10))

            for u in grp2:
                grp3 = grp1.loc[(i, u, slice(None))]
                allo_all = pd.melt(grp3.reset_index(), id_vars='date', value_vars='vol', var_name=u)

                index1 = allo_all.date.astype('str')
                sns.barplot(x=index1, y='value', data=allo_all, edgecolor='0', color=col_lab[u], label=u)

    #        plt.ylabel('Allocated Water Volume $(10^{' + str(pw) + '} m^{3}/year$)')
            plt.ylabel('Water Volume $(' + yaxis_lab + '\; m^{3}/year$)')
            plt.xlabel('Water Year')

            # Legend
            handles, lbs = ax.get_legend_handles_labels()
            plt.legend(handles, lbs, loc='upper left')

            xticks = ax.get_xticks()
            if len(xticks) > 15:
                for label in ax.get_xticklabels()[::2]:
                    label.set_visible(False)
                ax.xaxis_date()
                fig.autofmt_xdate(ha='center')
                plt.tight_layout()
            plt.tight_layout()
    #      sns.despine(offset=10, trim=True)

            # Save figure
            plot2 = ax.get_figure()
            export_name = '_'.join([i, vol_name, stack, date1.strftime('%Y%m%d%H%M')]) + '.png'
            export_name = export_name.replace('/', '-').replace(' ', '-')
            plot2.savefig(os.path.join(export_path, export_name))
            plt.close()

    plt.ion()

