import pandas as pd

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class GraphUtils:
    """
    Contains graph utility methods
    """
    def __init__(self, prev_release: str, curr_release: str):
        """
        Init code
        """
        self.last_release = prev_release
        self.this_release = curr_release
        
        self.objects_to_colors = {
            'Account': '#6C76cf',
            'Case': '#EEC74A',
            'CollaborationGroup': '#6589EE',
            'Contact': '#8E7DE8',
            'Lead': '#F47450',
            'Opportunity': '#FAAB4a',
            'User': '#2EB1C2'
        }

        self.sobjects = ['Account', 'Contact', 'Case', 'CollaborationGroup', 'Lead', 'Opportunity', 'User']

        self.appversion_colors = {
          self.this_release: '#aa000044',
          self.last_release: '#00aa0044'
        }

        self.network_colors = {
          'Wifi': '#aa000044',
          'LTE': '#00aa0044',
          '3G': '#0000aa44'
        }

    

    def visualize_using_boxplot(self, obj: object, numcols: int, release_criteria: int, ylimit: int):
      try:
        v = [str(self.last_release), str(self.this_release)] # `v` is a sorted (older -> newer) list of app Versions.
        p = ['#00a1e0ff', '#7c868dff', '#00b2a9ff', '#963cbdff']
        
        if (numcols == 1): 
          #v = [str(last_release), str(this_release)] # `v` is a sorted (older -> newer) list of app Versions.
          #p = ['#00a1e0ff', '#7c868dff', '#00b2a9ff', '#963cbdff']
          fig, ax = plt.subplots(nrows=1, ncols=numcols, figsize=(12,8), sharey=True)
          sns.boxplot(x="appVersion", y="EPT", hue="appVersion", data=obj, order=v, palette=p)
          ax.plot(np.linspace(-20,120,1000), [release_criteria]*1000, 'r')  # Draw a horizontal line at y=300 for the P95 goal 
        else:
          # fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=numcols, figsize=(24,12), sharey=True)
          fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12,8), sharey=True)
          sns.boxplot(y="EPT", x="entitytype", data=obj[obj['appVersion']==self.this_release], order=self.objects_to_colors.keys(), palette=self.objects_to_colors.values())
          ax.set_title(self.this_release + ' - Wifi')
          ax.plot(np.linspace(-20,120,1000), [release_criteria]*1000, 'r')  # Draw a horizontal line at y=300 for the P95 goal
        if (ylimit != None):
          # IF ylimit is None it implies this plot is for android otherwise its for iOS
          plt.ylim(0,ylimit)
          plt.show()
        sns.despine(offset=10, trim=True)
      except Exception as e:
        print("visualize_using_boxplot():: Error ploting data: ", e)


    # Violin Function 
    def visualize_using_voilinplot(self, obj: object, numcols: int ,release_criteria: int):
      try:
        if (numcols == 1): 
          fig, ax = plt.subplots(nrows=1, ncols=numcols, figsize=(250,12), sharey=True)
          sns.violinplot(y="EPT",x="appVersion", hue="appVersion", data=obj, order=v, palette=p)
          ax.plot(np.linspace(-20,120,1000), [release_criteria]*1000, 'r')
        else:
          import matplotlib.pyplot as plt
          fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=numcols, figsize=(24,12), sharey=True)

          sns.violinplot(ax=ax1, y="EPT", x="entitytype", data=obj[obj['appVersion']==last_release], order=objects_to_colors.keys(), palette=objects_to_colors.values())
          sns.violinplot(ax=ax2, y="EPT", x="entitytype", data=obj[obj['appVersion']==this_release], order=objects_to_colors.keys(), palette=objects_to_colors.values())

          plt.ylim(0,None)
          ax1.set_title(str(last_release) + ' - Wifi')
          ax2.set_title(str(this_release) + ' - Wifi')
          ax1.plot(np.linspace(-20,120,1000), [release_criteria]*1000, 'r')  # Draw a horizontal line at y=release_criteria for the P95 goal
          ax2.plot(np.linspace(-20,120,1000), [release_criteria]*1000, 'r')  # Draw a horizontal line at y=release_criteria for the P95 goal
        sns.despine(offset=10, trim=True)
      except Exception as e:
        print("visualize_using_voilinplot():: Error plotting data: ", e)
      

    #Entity Based Distribution Plots
    def cmp_aura_flexipage(self, obj, xaxislimit: int):
      try:
        fig, ax = plt.subplots(nrows=len(sobjects), ncols=1, figsize=(12,14), sharex=True)
        for i, sobj in enumerate(sobjects):
          for appversion in [last_release, this_release]:
            d =  obj[(obj['entitytype'] == sobj) & (obj['appVersion'] == appversion)]['EPT']
            sns.kdeplot(d, color=appversion_colors[appversion], ax=ax[i], shade=True, label=appversion)
            ax[i].set(yticks=[])
            ax[i].set_xlabel('')
            ax[i].set_ylabel(sobj)
            plt.xlim(0,xaxislimit)
            sns.despine(ax=ax[i], bottom=True, left=True)
        
        fig.subplots_adjust(hspace=.25)
      except Exception as e:
        print("cmp_aura_flexipage():: Error ploting data: ", e)

    #Entity Based Network EPT Distribution Plots
    def cmp_network(self, obj, xaxislimit: int):
      try:
        fig, ax = plt.subplots(nrows=len(self.sobjects), ncols=1, figsize=(12,16), sharex=True)
        for i, sobj in enumerate(self.sobjects):
          for network in ['Wifi', 'LTE', '3G']:
            d =  obj[(obj['entitytype'] == sobj) & (obj['network'] == network)]['EPT']
            sns.kdeplot(d, color=self.network_colors[network], ax=ax[i], shade=True, label=network)
            ax[i].set(yticks=[])
            ax[i].set_xlabel('')
            ax[i].set_ylabel(sobj)
            plt.xlim(0,xaxislimit)
            sns.despine(ax=ax[i], bottom=True, left=True)
        
        fig.subplots_adjust(hspace=.25)
      except Exception as e:
        print("cmp_network():: Error ploting data: ", e)