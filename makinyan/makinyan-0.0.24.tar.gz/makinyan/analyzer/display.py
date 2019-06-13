#!-*-coding:utf-8-*-
import os
import sys
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
sys.path.append("../../")
import makinyan as mak

plt.rcParams["font.family"] = "IPAexGothic"


__all__ = ["hist","boxplt","pairplot"]

def hist( data , save=False , path=False ):
    """
    Histgram
    """
    y = list( data.values() )
    x = list( data.keys() )
    plt.bar( np.array( range( len( x ) ) ) , y )
    plt.xticks( np.array( range( len( x ) ) ) , x )

    _saveorshow( flag=save , filename="tf_hist.png" , path=path )


def boxplt( df , title="" , xlabel="X" , ylabel="Y" , save=False , path=False ):
    """
    BoxPlot
    """
    sns.set(style="whitegrid")
    sns.boxplot(x=xlabel, y=ylabel, data=df);

    _saveorshow( flag=save , filename="box_plot.png" , path=path )
    plt.clf()


def pairplot( df , hue=False , save=False , path=False ):

    sns.set(style="darkgrid")

    if hue == False:
        sns.pairplot( df )
    else:
        sns.pairplot(df,hue=hue,palette="muted" )

    _saveorshow( flag=save , filename="paireplot.png" , path=path )
    plt.clf()


def _saveorshow( flag , filename , path ):
    if flag and path:
        plt.savefig( path + "/" + filename )
    else:
        plt.show()
