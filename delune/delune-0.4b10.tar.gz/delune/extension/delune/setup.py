#!/usr/bin/env python
import os
import glob
from distutils.core import setup, Extension
import platform
osbit, _dummy = platform.architecture()
dira = osbit == "32bit" and "x86" or "x64"
data_files = []

if os.name == "nt":
	include_dirs = ["../win32/__prebuilts__/2.7/zlib/%s" % dira, "../win32/__prebuilts__/2.7/pthread2/%s" % dira]
	library_dirs = ["../win32/__prebuilts__/2.7/zlib/%s" % dira, "../win32/__prebuilts__/2.7/pthread2/%s" % dira]
	libraries = ["zlib", "pthreadVC2"]	
else:
	include_dirs = ["/usr/include"]
	library_dirs = ["/usr/lib/x86_64-linux-gnu"]
	libraries = ["z", "pthread"]
		
module = Extension(
	'_delune',
	sources = [
		'core.c', 
		'analyzer/analyzer.c', 		
		'analyzer/stopword.c', 
		'analyzer/endword.c', 
		'analyzer/formalizer.c', 		
		'analyzer/stem.c',
		'analyzer/stem_fr.c',
		'analyzer/stem_de.c',
		'analyzer/stem_it.c',
		'analyzer/stem_es.c',
		'analyzer/stem_pt.c',
		'analyzer/stem_fi.c',
		'analyzer/stem_sv.c',
		'analyzer/stem_hu.c',
		'analyzer/stem_ar.c',
		'analyzer/removeaccents.c',
		'index/sort.c', 
		'index/osutil.c', 
		'index/search.c', 
		'index/compfunc.c',
		'index/heapsort.c', 
		'index/termhashtable.c', 
		'index/generichash.c',
		'index/bfile.c', 
		'index/zip.c',
		'index/mempool.c',
		'index/ibucket.c',
		'index/util.c',
		'mod_analyzer.c',		
		'mod_util.c', 
		'mod_int.c', 
		'mod_bits.c', 
		'mod_mergeinfo.c', 
		'mod_document.c',
		'mod_posting.c', 
		'mod_termtable.c',
		'mod_terminfo.c',
		'mod_sortmap.c',   
		'mod_memorypool.c',		
		'mod_selector.c',		
		'mod_classifier.c',
		'mod_dbint.c',
		'mod_calculator.c',
		'mod_binfile.c',		
		'mod_sgmlparser.c',
		'mod_compute.c',
	],
	include_dirs = include_dirs,
	library_dirs = library_dirs,
	libraries = libraries
)

setup (name = '_delune',
       version = '2.0.0',       
       author = 'Hans Roh',
       author_email = 'hansroh@gmail.com',
       url = '',
       ext_modules = [module]       
)

