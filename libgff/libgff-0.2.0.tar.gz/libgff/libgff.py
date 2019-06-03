#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:04:08 2018

@author: antony
"""


import libgenomic

class GFFReader(object):
    def __init__(self, file):
        self.__file = file
    
    @property    
    def file(self):
        return self.__file
    
    def __iter__(self):
        'Returns itself as an iterator object'
        return self
    
    def next(self):
        pass
    
    def __next__(self):
        return self.next()

    def tolist(self):
        """
        Return a list of all entries
        """
        
        ret = []
        
        for e in self:
            ret.append(e)
            
        return ret
    
    def nested(self):
        ret = []
        
        for e in self:
            if e.level == 'gene':
                ret.append(e)
                gene = e
            elif e.level == 'transcript':
                gene.add(e)
                transcript = e
            elif e.level == 'exon':
                transcript.add(e)
            else:
                pass
            
        return ret
    

class GTFReader(GFFReader):
    def __init__(self, file):
        super().__init__(file)
    
    def __iter__(self):
        self.__f = open(self.file, 'r')
        self.__pc = 0
        
        for self.__line in self.__f:
            # skip headers
            if not self.__line.startswith('#'):
                break
        
        return self
    
    def next(self):
        if not self.__line or self.__pc == 20:
            self.__f.close()
            raise StopIteration
        
        tokens = self.__line.strip().split('\t')
            
        chr = tokens[0]
        level = tokens[2]
        start = int(tokens[3])
        end = int(tokens[4])
        strand = tokens[6]
            
        annotations = tokens[8].replace('"', '').split(';')
        
        ann_map = {}
        
        for annotation in annotations:
            at = annotation.strip().split(' ')
            
            if len(at) > 1:
                key, value = at[0:2]
                ann_map[key] = value
                
        e = libgenomic.GenomicEntity(chr, start, end, level, strand, ann_map)
        
        # move to next line
        self.__line = self.__f.readline()
        self.__pc += 1
            
        return e
    

if __name__ == '__main__':
    import sys
    sys.path.append('/ifs/scratch/cancer/Lab_RDF/abh2138/scripts/python/lib/libgenomic/libgenomic')

    reader = GTFReader('/home/antony/Desktop/gff/gencode.v27.basic.annotation.gtf')
    
    for e in reader:
        print(e)
     
    print('run2')
        
    for e in reader:
        print(e)
        
        