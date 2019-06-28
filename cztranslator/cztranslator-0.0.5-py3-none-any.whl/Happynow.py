# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 09:27:51 2019

@author: Noven
"""

# translate the Mandarin to Chaozhou dialect 
import pandas as pd
import numpy as np
import os
mydict=pd.read_csv('CZtxt.csv',header=None)

CZdict=mydict[0]
MDdict=mydict[1]

def menu(mydict):
    
    print("1. Look up ChaoZhou dialect  \n2. Add your newly learned words. \n0. Exit ")
    Menu=input("Choose Function:")
    
    if Menu=="1":
        lookup(mydict)
        
    elif Menu=="2":
        addnew(mydict)
        
    elif Menu=="0":
        return
    
    else:
        print("Enter some valid choices.")
        menu(mydict)

def lookup(mydict):
    
    CZ=input("Enter the word you want to search:")
    MDidx = MDdict.str.contains(CZ)
    MDpossible=MDdict[MDidx]
    
    if len(MDpossible)==0:
        print("Nothings found here, go to learn more!")
        menu(mydict)
        return
    print("-1: Back to last menu")
    print(MDpossible)
    inp=input("Enter the index:")
    
    if inp=="-1":
        lookup(mydict)
    else:
        while int(inp) not in MDpossible.index:
            inp=input("Enter the Right index:")
            
        result=CZdict[int(inp)]
        print("The word you are looking for is: "+result)
        menu(mydict)
        return
    

        
def addnew(mydict):

    addCZ=input("Enter the Chaozhou word you want to add:")
    addMD=input("Enter the Mandarin word you want to add:")
    
    new=pd.DataFrame([addCZ,addMD]).T
    mydict=pd.concat([mydict,new],ignore_index=True)
    
    mydict.to_csv("CZtxt.csv")
    print("Update complete!")
    menu(mydict)
    return

_=menu(mydict)