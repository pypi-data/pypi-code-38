#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:04:08 2018

@author: antony
"""

import collections
import os
import sys
import struct
import libgff
import libgenomic
import libdna

CHECK = 42
VERSION = 1
INT_BYTES = 4


VERSION_BYTE_OFFSET = INT_BYTES
GENES_BYTES_OFFSET = VERSION_BYTE_OFFSET + 1
RADIX_BYTES_OFFSET = GENES_BYTES_OFFSET + INT_BYTES
WINDOW_BYTE_OFFSET = RADIX_BYTES_OFFSET
BINS_BYTE_OFFSET = WINDOW_BYTE_OFFSET + INT_BYTES
HEADER_BYTES_OFFSET = BINS_BYTE_OFFSET + INT_BYTES
RADIX_TREE_PREFIX_BYTES = 1 + INT_BYTES

ENCODE_GENE = 1
ENCODE_TRANSCRIPT = 2
ENCODE_EXON = 4

DEFAULT_WINDOW = 1000


def get_file_name(genome, chrom, window=DEFAULT_WINDOW):
    return '{}.{}.{}.gfb'.format(genome, chrom, 'w{}'.format(window))


def get_radix_file_name(genome):
    return '{}.rgfb'.format(genome)

def level_enc(level):
    """
    Encode the level as a number
    
    Parameters
    ----------
    level : str
        Either 'gene', 'transcript', or 'exon'
        
    Returns
    -------
    int
        Int representation of level.
    """
    
    if level == libgenomic.EXON:
        return ENCODE_EXON
    elif level == libgenomic.TRANSCRIPT:
        return ENCODE_TRANSCRIPT
    else:
        return ENCODE_GENE
    

class GFBWriter(object):
    def __init__(self, genome, window=1000):
        self.__genome = genome
        self.__window = window
        
    
    def _varchar_size(s):
        return 1 + len(s)
    
    
    @staticmethod
    def _tag_sizes_bytes(entity, size_map):
        
        for key in entity.annotation_names():
            value = entity.get_annotation(key)
            size_map.put(key, GFBWriter._varchar_size(key))
            size_map.put(value, GFBWriter._varchar_size(value))
    
        for t in entity.tags():
            size_map.put(t, GFBWriter._varchar_size(t))

        for l in entity.child_levels():
            for c in entity.children(t):
                GFBWriter._tag_sizes_bytes(c, size_map)
                
    @staticmethod         
    def gene_sizes_bytes(e):
        s = 0

        #id
        s += INT_BYTES

        # type
        s += 1

        s += GFBWriter._varchar_size(e.chr)

        # Start, end
        s += INT_BYTES + INT_BYTES
        
        # strand
        s += 1

        #number of exons + exon starts and ends
        s += 1 + e.child_count(libgenomic.EXON) * INT_BYTES * 2

        # 1 byte for number of ids
        s += 1 + e.id_count()() * 2 * INT_BYTES

        # number of tags (must be fewer than 256)
        s += 1 + e.tag_count() * INT_BYTES

        #Number of children
        s += 1

        if e.level == libgenomic.GENE:
            children = e.children(libgenomic.TRANSCRIPT)
        elif e.level == libgenomic.TRANSCRIPT:
            children = e.children(libgenomic.EXON)
        else:
            # Exons etc
            children = []

        for child in children:
            s += GFBWriter._gene_sizes_bytes(child)

        return s
    
    @staticmethod
    def _write_int(i, writer):
        writer.write(struct.pack('>I', i))
    
    @staticmethod
    def _write_byte(b, writer):
        writer.write(struct.pack('>B', b))
    
    @staticmethod
    def _write_varchar(s, writer):
        l = len(s)
        GFBWriter._write_byte(l, writer)
        writer.write(s.encode('utf-8'))
        
        
    @staticmethod
    def _write_tags(tag_offset_bytes_map, writer):
        
        GFBWriter._write_int(len(tag_offset_bytes_map), writer)
        
        sort_map = {}
        
        # sort by offset before writing since we need strings correctly
        # ordered by offset address
        for tag, offset in tag_offset_bytes_map.items():
            sort_map[offset] = tag
            
        for offset in sorted(sort_map):
            GFBWriter._write_varchar(sort_map[offset], writer)
            

    @staticmethod
    def _write_entity(id, e, tags_start_bytes, tag_offset_bytes_map, writer):
        GFBWriter._write_int(id, writer)
        id += 1
        
        GFBWriter._write_int(id, writer)
        
        GFBWriter._write_byte(level_enc(e.level), writer)
        
        GFBWriter._write_varchar(e.chr, writer)
        GFBWriter._write_int(e.start, writer)
        GFBWriter._write_int(e.end, writer)
        
        GFBWriter._write_byte(e.annotation_count(), writer)
        
        for key, value in e.annotations().items():
            GFBWriter._write_int(tags_start_bytes + tag_offset_bytes_map[key], writer)
            GFBWriter._write_int(tags_start_bytes + tag_offset_bytes_map[value], writer)

        GFBWriter._write_byte(e.tag_count(), writer)

        for tag in e.tags():
            GFBWriter._write_int(tags_start_bytes + tag_offset_bytes_map[tag], writer)
                
        if e.level == libgenomic.GENE:
            children = e.children(libgenomic.TRANSCRIPT)
            GFBWriter._write_byte(e.child_count(libgenomic.TRANSCRIPT), writer)
        elif e.level == libgenomic.TRANSCRIPT:
            children = e.children(libgenomic.EXON)
            GFBWriter._write_byte(e.child_count(libgenomic.EXON), writer)
        else:
            children = []
            GFBWriter._write_byte(0, writer)
        
        for child in children:
            id = GFBWriter._write_entity(id, child, tags_start_bytes, tag_offset_bytes_map, writer)
            
        return id
    
                
    def encodeGTF(self, file):
        
        dir = os.path.dirname(os.path.abspath(file))
        
        genes = libgff.GTFReader(file).nested()
        
        chrom_map = libgenomic.GenomicEntity.chr_map(genes)
        
        writers = {}

        for chrom, entities in chrom_map.items():
            if chrom not in writers:
                file = os.path.join(dir, get_file_name(self.__genome, chrom, self.__window))

                writer = open(file, 'wb')

                writers[chrom] = writer
                
                writer.write(struct.pack('I', CHECK))
                writer.write(struct.pack('B', VERSION))

             
            writer = writers[chrom]

            max_bin = 0
            
            bins_map = collections.defaultdict(list)

            for e in entities:
                bs = e.start # self.__window
                be = e.end # self.__window

                bins_map[bs][e]
                bins_map[be][e]

                if be > max_bin:
                    max_bin = be

            bins_count = max_bin + 1

            bin_sizes_bytes = {}

            bins_width_bytes = 0

            for b in range(0, max_bin + 1):
                s = INT_BYTES + len(bins_map[b]) * INT_BYTES

                bin_sizes_bytes.put(b, s)

                bins_width_bytes += s

            tag_size_bytes_map = {}
            tag_offset_bytes_map = {}

            GFBWriter._tag_sizes_bytes(entities, tag_size_bytes_map, tag_offset_bytes_map)

            bin_addresses_width_bytes = bins_count * INT_BYTES

            gene_offset_bytes = {}
            genes_width_bytes = 0
            
            for e in entities:
                s = GFBWriter._gene_size_bytes(e)

                gene_offset_bytes[e] = genes_width_bytes
                genes_width_bytes += s
                
            #
            offset = HEADER_BYTES_OFFSET + bin_addresses_width_bytes + bins_width_bytes

            GFBWriter._write_int(offset, writer)

            #the size of the block windows (e.g. 1000)
            GFBWriter._write_int(self.__window, writer)

            # The number of bins encoded
            GFBWriter._write_int(bins_count, writer)

            # check version genome, window, size
            offset = HEADER_BYTES_OFFSET + bin_addresses_width_bytes
            
            # Write out the bin addresses where we can find gene addresses
            for b in range(0, max_bin + 1):
                writer.write(struct.pack('I', offset))

                offset += bin_sizes_bytes.get(b)

            # for each bin, write the address to the genes it contains
            
            # The header + the space occupied by the bin addresses + the space
            # occupied by the bins + the gene count
            genes_start_bytes = HEADER_BYTES_OFFSET + bin_addresses_width_bytes + bins_width_bytes + INT_BYTES

            tags_start_bytes = genes_start_bytes + genes_width_bytes + INT_BYTES
            
            #int tags_start_bytes = idsStartBytes + idsWidthBytes + INT_BYTES
            
            for b in sorted(bins_map):
                bins = bins_map[b]
                GFBWriter._write_int(len(bins), writer)

                for e in bins:
                    # Addresses
                    GFBWriter._write_int(genes_start_bytes + gene_offset_bytes[e], writer)
                

            # Now write out the genes
            id = 0
             
            # Write out the number of genes
            GFBWriter._write_int(len(entities), writer)
             
            for e in entities:
                GFBWriter._write_entity(writer, id, e, tags_start_bytes, tag_offset_bytes_map)

            GFBWriter.write_tags(writer, tag_offset_bytes_map)
        
        for chrom, writer in writer.items():
            writer.close()


class GFBReader(libgenomic.SingleDBGenes):
    def __init__(self, db, genome, dir, window=DEFAULT_WINDOW):
        super().__init__(db, genome)
        
        self.__window = window
        self.__dir = dir
        self.__radix_file = os.path.join(dir, get_radix_file_name(genome))
        self.__reader = None
        self.__radix_reader = None
        self.__current_chr = ''


    @staticmethod
    def _find_closest_genes(loc, genes, min_bp=1):
        ret = []
        
        for gene in genes:
            overlap = libgenomic.overlap(loc.chr, loc.start, loc.end, gene.chr, gene.start, gene.end)

            if overlap is not None and overlap.length >= min_bp:
                ret.append(gene)

        return ret
    
    
    @staticmethod
    def  _gene_addresses_from_bins(addresses, reader):
        ret = []
        
        used = set()
        
        for address in addresses:
            reader.seek(address)

            size = GFBReader._read_int(reader)
              
            for i in range(0, size):
                ga = GFBReader._read_int(reader)
                
                if ga not in used:
                    ret.append(ga)
                    used.add(ga)
                    
        return ret


    @staticmethod
    def _read_varchar(reader):
        # The length is 1 byte and the max length of the string is 256
        # so buffer 257 bytes to reduce file reads
        #d = reader.read(257)
        #n, offset = GFBReader._scan_byte(d)
        #s, _ = GFBReader._scan_string(d, n, offset=offset)
        
        # First int tells us the length of the string
        n = GFBReader._read_byte(reader)

        # Read n bytes into the buffer
        s = reader.read(n).decode('utf-8')
        
        return s

    @staticmethod
    def _read_string(address, reader):
        reader.seek(address)

        return GFBReader._read_varchar(reader)


    @staticmethod
    def _read_tag(reader):
        address = GFBReader._read_int(reader)
    
        pos = reader.tell()
    
        ret = GFBReader._read_string(address, reader)
    
        reader.seek(pos)
    
        return ret
    
    @staticmethod
    def _read_tags(reader):
        n = GFBReader._read_byte(reader)
        
        ret = [''] * n
        
        for i in range(0, n):
            ret[i] = GFBReader._read_tag(reader)
            
        return ret
            
            
    @staticmethod
    def _read_id(reader):
        #address = GFBReader._read_int(reader)
        #address2 = GFBReader._read_int(reader)
        d = reader.read(8)
        address, offset = GFBReader._scan_int(d)
        address2, _ = GFBReader._scan_int(d, offset=offset)
    
        pos = reader.tell()
        
        key = GFBReader._read_string(address, reader)
        value = GFBReader._read_string(address2, reader)
        
        #print('id', key, value)
    
        reader.seek(pos)
        
        return key, value
        
        
    @staticmethod
    def _read_ids(reader):
        """
        Loads the ids for a given entity onto the entity.
        
        Parameters
        ----------
        e : GenomicEntity
            Will be modified in place
        reader : file reader
            File pointer must be set to where id section of entity
            begins in the file.
        """
        
        ret = {}
        
        n = GFBReader._read_byte(reader)
        
        for i in range(0, n):
            key, value = GFBReader._read_id(reader)
            
            ret[key] = value
        
        return ret
            
    @staticmethod
    def _gene_addresses_from_radix(id, reader):
        id = id.lower()

        # Find the tree start
        reader.seek(RADIX_BYTES_OFFSET)
    
        address = 0

        found = False

        for c in id:
            # for speed, get ord of char and then compare to numerical
            # byte value of each letter in radix tree rather than converting
            # both to strings each time
            
            o = ord(c)
            
            # Number of child letters
            n = GFBReader._read_byte(reader)
            
            # assume we won't find a match
            found = False

            for i in range(0, n):
                #leafc = GFBReader._read_byte(reader)
                #address = GFBReader._read_int(reader)
                
                # Read 5 bytes to use a byte and a 4 byte int
                d = reader.read(5)
                leafc, offset = GFBReader._scan_byte(d)
                address, _ = GFBReader._scan_int(d, offset=offset)
                
                if leafc == o:
                    # The letter matches a tree prefix so move to the
                    # letter's node address and keep going
                    found = True
                    reader.seek(address)
                    break
                
            if not found:
                break

        if not found:
            return []

        # This means we kept finding a child matching the prefix so the seek
        # is at the beginning of a node either because we ran out of chars
        # or nodes. In this case we must skip over the child addresses and
        # just look at the addresses of the genes
    
        # skip past number of addresses and the addresses themselves
        # reader.seek(address + N_BYTES + reader.readInt() *
        # RADIX_TREE_PREFIX_BYTES)
        
        reader.seek(GFBReader._read_byte(reader) * RADIX_TREE_PREFIX_BYTES, 1)

        # Should be on a node that is hopefully matches our search term
        # Since we checked all the children, the seek is at the position of
        # the gene addressses so we can get them
    
        n = GFBReader._read_int(reader)
        
        ret = [0] * n
    
        for i in range(0, n):
            ret[i] = GFBReader._read_int(reader)
        
        type(reader)
        
        return ret

    def get_names(self):
        genes = self.get_genes()

        ret = set()

        for gene in genes:
            ret.add(gene.symbol)
                
        return list(sorted(ret))
    
    @staticmethod
    def _read_int(reader):
        return struct.unpack('>I', reader.read(4))[0]
        
    @staticmethod
    def _read_byte(reader):
        return struct.unpack('>B', reader.read(1))[0]
    
    
    @staticmethod
    def _scan_int(d, offset=0):
        return struct.unpack('>I', d[offset:(offset+4)])[0], offset + 4
        
    @staticmethod
    def _scan_byte(d, offset=0):
        return d[offset], offset + 1
    
    @staticmethod
    def _scan_string(d, n, offset=0):
        return d[offset:(offset + n)].decode('utf-8'), offset + n
       
    @staticmethod
    def _read_char(reader):
        return reader.read(1).decode('utf-8') #struct.unpack('>c', reader.read(1))[0]
  
    @staticmethod
    def _read_bin_address(reader, bin):
        reader.seek(HEADER_BYTES_OFFSET + bin * INT_BYTES)
        return GFBReader._read_int(reader)
    
    @staticmethod
    def _read_genes_address(reader):
        reader.seek(GENES_BYTES_OFFSET)
        return GFBReader._read_int(reader)
   
    @staticmethod
    def _read_check_num(reader):
        pos = reader.tell()
        reader.seek(0)
        ret = GFBReader._read_int(reader)
        reader.seek(pos)
        return ret
    
    @staticmethod
    def _read_version(reader):
        reader.seek(VERSION_BYTE_OFFSET)
        return GFBReader._read_byte(reader)
    
    @staticmethod
    def _read_bin_count(reader):
        reader.seek(BINS_BYTE_OFFSET)
        return GFBReader._read_int(reader)
    
    @staticmethod
    def _read_window(reader):
        reader.seek(WINDOW_BYTE_OFFSET)
        return GFBReader._read_int(reader)
    
    @staticmethod
    def _read_location(reader):
        chrom = GFBReader._read_varchar(reader)
        start = GFBReader._read_int(reader)
        end = GFBReader._read_int(reader)

        return libdna.Loc(chrom, start, end)
    
    @staticmethod
    def _read_strand(reader):
        s = GFBReader._read_byte(reader)
        
        if s == 0:
            return '+'
        else:
            return '-'
    
    
    @staticmethod
    def _read_entity(level, reader):
        
        # Skip id (int) and type (byte)
        reader.seek(INT_BYTES + 1, 1) # .readInt()

        loc = GFBReader._read_location(reader)
        
        strand = GFBReader._read_strand(reader)
        

        if level == libgenomic.GENE:
            gene = libgenomic.Gene(loc.chr, loc.start, loc.end, strand)
        elif level == libgenomic.EXON:
            gene = libgenomic.Exon(loc.chr, loc.start, loc.end, strand)
        else:
            gene = libgenomic.Transcript(loc.chr, loc.start, loc.end, strand)

        gene.set_properties(GFBReader._read_ids(reader))
        gene.add_tags(GFBReader._read_tags(reader))
        
        return gene
    
    
    @staticmethod
    def _read_exons(level, transcript, reader, ret):
        # number of exons using transcript block
        n = GFBReader._read_byte(reader)
        
        for i in range(0, n):
            exon = GFBReader._read_entity(libgenomic.EXON, reader)

            # skip byte for exon child count, since exons cannot have children
            # so this byte is always set to zero.
            reader.seek(1, 1)

            if transcript is not None:
                transcript.add(exon)

            if level == libgenomic.EXON:
                ret.append(exon)
    

    @staticmethod
    def _read_transcripts(level, gene, reader, ret):
        n = GFBReader._read_byte(reader)
        
        for i in range(0, n):
            transcript = GFBReader._read_entity(libgenomic.TRANSCRIPT, reader)

            if gene is not None:
                gene.add(transcript)

            if level == libgenomic.TRANSCRIPT:
                ret.append(transcript)
            
            GFBReader._read_exons(level, transcript, reader, ret)
    
    
    @staticmethod
    def _read_genes(level, reader, ret):
        gene = GFBReader._read_entity(libgenomic.GENE, reader)
        
        if (level == libgenomic.GENE):
            ret.append(gene)
            
        GFBReader._read_transcripts(level, gene, reader, ret)
            
    
    @staticmethod
    def _genes_from_gene_addresses(level, addresses, reader):
        ret = []
        
        for address in addresses:
            reader.seek(address)
            
            GFBReader._read_genes(level, reader, ret)
            
        return ret
    
    
    @staticmethod
    def _bin_addresses_from_bins(bins, reader):
        ret = []

        for bin in bins:
            ret.append(GFBReader._read_bin_address(reader, bin))
            
        return ret
    
    
    @staticmethod
    def _overlapping_genes(loc, genes, min_bp=1):
        ret = []
        
        for gene in genes:
            
            overlap = libgenomic.overlap(loc.chr, loc.start, loc.end, gene.chr, gene.start, gene.end)

            if overlap is not None and overlap.length >= min_bp:
                ret.append(gene)

        return ret
    
    
    def get_genes(self, id, db=None, level=libgenomic.TRANSCRIPT):
        if self.__radix_reader is None:
            self.__radix_reader = open(self.__radix_file, 'rb')

        addresses = GFBReader._gene_addresses_from_radix(id, self.__radix_reader)

        genes = GFBReader._genes_from_gene_addresses(level, addresses, self.__radix_reader)
        
        return genes


    def _find_genes(self, loc, level=libgenomic.TRANSCRIPT):
        loc = libdna.parse_loc(loc)
        
        # Cache current chr
        if loc.chr != self.__current_chr or self.__reader is None:
            file = os.path.join(self.__dir, get_file_name(self.genome, loc.chr, self.__window))
            self.__reader = open(file, 'rb')
            self.__current_chr = loc.chr
    
        sb = loc.start // self.__window
        eb = loc.end // self.__window

        bins = [i for i in range(sb, eb + 1)] #ArrayUtils.array(sb, eb)

        bins = GFBReader._bin_addresses_from_bins(bins, self.__reader)
        
        addresses = GFBReader._gene_addresses_from_bins(bins, self.__reader)
        
        ret = GFBReader._genes_from_gene_addresses(level, addresses, self.__reader)

        return ret
    
    
    def find_closest_genes(self, loc, db=None, level=libgenomic.TRANSCRIPT):
        genes = self._find_genes(loc.chr, loc.start, loc.end, type)

        mid = (loc.end + loc.start) // 2
        minD = sys.maxint

        for gene in genes:
            d = abs(mid - gene.start) # GenomicRegion.mid(gene))

            if d < minD:
                minD = d
        
        ret = []
        
        for gene in genes:
            d = abs(mid - gene.start)

            if d == minD:
                ret.append(gene)

        return ret
    
    
    def find_genes(self, loc, level=libgenomic.TRANSCRIPT, db=None):
        loc = libdna.parse_loc(loc)
        
        genes = self._find_genes(loc, level=level)
        
        return genes #GFBReader._overlapping_genes(loc, genes)
    
    
    def close(self):
        """
        Close any open file connections
        """
        
        if self.__radix_reader is not None:
            self.__radix_reader.close()
            
        if self.__reader is not None:
            self.__reader.close()
    
    
if __name__ == '__main__':
    reader = GFBReader('gencode', 'grch38', '/home/antony/Desktop/gff/gfb/grch38')
    
    genes = reader.find_genes('chr3:187,721,177-187,736,497')
    
    print('tada-------------------------------------------')
    
    for gene in genes:
        print(gene, id(gene), id(gene.ids))
        
        
    
    
    
#    print('sff')
#    
#    genes = reader.get_genes('BCL6')
#    
#    for gene in genes:
#        print(gene)
#        
#    reader.close()
        
        
