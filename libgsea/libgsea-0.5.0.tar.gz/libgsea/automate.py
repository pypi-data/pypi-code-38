#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 16:47:01 2019

@author: antony
"""

import subprocess
import sys

JAR = '/ifs/scratch/cancer/Lab_RDF/ngs/tools/gsea/bin/gsea2-2.2.0.jar'


def auto_gsea(name, gct_file, gmx_file, cls_file, classes_file, n=20, pwd='.'):
    """
    Run GSEA in an automated way.
    
    Parameters
    ----------
    name : str
        Name of experiment
    gmx_file : str
        Path to GMX file.
    cls_file : str
        Path to CLS file.
    classes_file : str
        Path to classes file. Each row must contain two tab separated values
        one for each class to be compared. First line is a header.
    n : int, optional
        Number of plots to create (default 20).
    """

    print(gmx_file)
    #f = open(gmx_file, 'r')
    #name = f.readline().strip()
    #f.close()

    dir = pwd + '/gsea/' + name

    print(classes_file)
    
    class_tests = []
    
    f = open(classes_file, 'r')
    f.readline()
    
    for line in f:
        n1, n2 = line.strip().split('\t')[0:2]
        
        class_tests.append((n1, n2,))
    
    for classes in class_tests:
        c1 = classes[0]
        c2 = classes[1]
        
        cc = cls_file + '#' + c1 + '_versus_' + c2
        print(cc)
        
        label = c1 + '_vs_' + c2
      
        cmd = []
        cmd.append('java')
        cmd.append('-Xmx8G')
        cmd.append('-cp')
        cmd.append(JAR)
        cmd.append('xtools.gsea.Gsea')
        cmd.append('-res')
        cmd.append(gct_file)
        cmd.append('-gmx')
        cmd.append(gmx_file)
        cmd.append('-cls')
        cmd.append(cc)
        cmd.append('-collapse')
        cmd.append('false')
        cmd.append('-permute')
        cmd.append('gene_set')
        cmd.append('-rpt_label')
        cmd.append(label)
        cmd.append('-plot_top_x')
        cmd.append(str(n))
        cmd.append('-out')
        cmd.append(dir)
        cmd.append('-gui')
        cmd.append('false')
        
        print(" ".join(cmd))
        
        process = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
        process.wait()