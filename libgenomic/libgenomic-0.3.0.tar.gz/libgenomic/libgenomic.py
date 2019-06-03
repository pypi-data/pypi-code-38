#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:04:08 2018

@author: antony
"""

import collections
import libdna

CHECK = 42
VERSION = 1

GENE_NAME = 'gene_name'
GENE_ID = 'gene_id'


GENE = 'gene'
TRANSCRIPT = 'transcript'
EXON = 'exon'


def overlap(chr1, start1, end1, chr2, start2, end2):
    if chr1 != chr2 or end1 < start2 or end2 < start1:
        return None

    start = max(start1, start2)
    end = min(end1, end2)

    return libdna.Loc(chr, start, end)


class GenomicElement(libdna.Loc):
    def __init__(self, chr, start, end, level, strand = '+'):
        super().__init__(chr, start, end)
        
        self.__level = level
        self.__strand = strand
        self.__property_map = {}
        self.__tags = set()
        self.__children = collections.defaultdict(list)
    
    @property    
    def level(self):
        return self.__level
    
    @property
    def strand(self):
        return self.__strand
    
    def add(self, e):
        self.__children[e.level].append(e)
        
    def child_levels(self):
        return sorted(self.__children.keys())
    
    def children(self, level):
        return self.__children[level]
    
    def child_count(self, level):
        return len(self.__children[level])
    
    def tag_count(self):
        return len(self.__tags)
    
    def set_property(self, name, value):
        self.__property_map[name] = value
        
    def set_properties(self, properties):
        for key, value in properties.items():
            self.__property_map[key] = value
    
    def property_names(self):
        return sorted(self.__property_map.keys())
    
    def get_property(self, name):
        if name in self.__property_map:
            return self.__property_map[name]
        else:
            return ''
    
    @property
    def properties(self):
        return self.__property_map
    
    def property_count(self):
        return len(self.__ann_mapp)
    
    def _prop_str(self):
        ret = []
        
        for key in sorted(self.__property_map):
            ret.append('{}={}'.format(key, self.__property_map[key]))
            
        return ';'.join(ret)
    
    @property
    def tags(self):
        return sorted(self.__tags)
    
    def add_tag(self, tag):
        self.__tags.add(tag)
        
    def add_tags(self, tags):
        for tag in tags:
            self.__tags.add(tag)
    
    def _tags_str(self):
        return ';'.join(sorted(self.__tags))
    
    def __str__(self):
        return '{}\t{}\t{}\t{}\t{}'.format(self.level, super().__str__(), self.strand, self._prop_str(), self._tags_str())
    
    @property
    def basic_json(self):
        return {'level':self.level, 'loc':super().__str__(), 'strand':self.strand}
    
    @staticmethod
    def chr_map(entities):
        chr_map = collections.defaultdict(list)
        
        for e in entities:
            chr_map[e.chr].append(e)
            
        return chr_map
    

class GenomicEntity(GenomicElement):
    def __init__(self, chr, start, end, level, strand):
        super().__init__(chr, start, end, level, strand)
    
    @property
    def gene_name(self):
        return self.annotation(GENE_NAME)
    
    @property
    def symbol(self):
        return self.gene_name
    

class Exon(GenomicEntity):
    def __init__(self, chr, start, end, strand):
        super().__init__(chr, start, end, EXON, strand)
        
   
    def add_exon(self, exon):
        if exon.level == EXON:
            self.add(exon)
            
    def exons(self):
        return self.children(EXON)
    

class Transcript(GenomicEntity):
    def __init__(self, chr, start, end, strand):
        super().__init__(chr, start, end, TRANSCRIPT, strand)
        
    def add_exon(self, exon):
        if exon.level == EXON:
            self.add(exon)
            
    def exons(self):
        return self.children(EXON)


class Gene(GenomicEntity):
    def __init__(self, chr, start, end, strand):
        super().__init__(chr, start, end, GENE, strand)
   
    def add_exon(self, exon):
        if exon.level == TRANSCRIPT:
            self.add(exon)
            
    def transcripts(self):
        return self.children(TRANSCRIPT)


class Genes(object):
    pass
    
class SingleDBGenes(Genes):
    def __init__(self, db, genome):
        self.__db = db
        self.__genome = genome
        
    @property
    def db(self):
        return self.__db
    
    @property
    def genome(self):
        return self.__genome