#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
"""
#=========================================================================================
This program performs differential CpG analysis using beta binomial model based on 
methylation proportions (in the form of "c,n", where "c" indicates "Number of reads with
methylated C", and "n" indicates "Number of total reads". Both c and n are non-negative
integers and c <= n). Below example showing input data on 2 CpGs of 3 groups (A,B, and C)
with each group has 3 replicates:
 
cgID  A_1   A_2   A_3   B_1   B_2   B_3   C_1   C_2   C_3
CpG_1 129,170 166,178 7,9 1 6,16  10,10 10,15 11,15 16,22 20,36     
CpG_2 0,77  0,99  0,85  0,77  1,37  3,37  0,42  0,153 0,6
...

allow for covariables. 

**
you must install R package "gamlss" before running this script
https://cran.r-project.org/web/packages/gamlss/index.html
**


#=========================================================================================
"""


import sys,os
import collections
import subprocess
import numpy as np
import re
from scipy import stats
from optparse import OptionParser
from cpgmodule import ireader
from cpgmodule.utils import *
from cpgmodule import BED
from cpgmodule import padjust

__author__ = "Liguo Wang"
__copyright__ = "Copyleft"
__credits__ = []
__license__ = "GPL"
__version__="0.1.4"
__maintainer__ = "Liguo Wang"
__email__ = "wang.liguo@mayo.edu"
__status__ = "Development"

	
def main():
	usage="%prog [options]" + "\n"
	parser = OptionParser(usage,version="%prog " + __version__)
	parser.add_option("-i","--input-file",action="store",type="string",dest="input_file",help="Data file containing methylation proportions (represented by \"methyl_count,total_count\", eg. \"20,30\") with the 1st row containing sample IDs (must be unique) and the 1st column containing CpG positions or probe IDs (must be unique). This file can be a regular text file or compressed file (*.gz, *.bz2) or accessible url.")
	parser.add_option("-g","--group",action="store",type="string",dest="group_file",help="Group file defining the biological groups of each sample as well as other covariables such as gender, age.  Sample IDs should match to the \"Data file\".")
	parser.add_option("-f","--family",action="store",type="int",dest="family_func",default=1, help="A gamlss (https://cran.r-project.org/web/packages/gamlss/index.html) family object. Can be integer 1, 2 or 3: 1 = \"BB (beta binomial)\", 2 = \"ZIBB (zero inflated beta binomial)\" or 3 = \"ZABB (zero adjusted beta binomial)\". Default=%default.")
	parser.add_option("-o","--output",action="store",type='string', dest="out_file",help="Prefix of the output file.")
	(options,args)=parser.parse_args()
	
	print ()
	if not (options.input_file):
		print (__doc__)
		parser.print_help()
		sys.exit(101)

	if not (options.group_file):
		print (__doc__)
		parser.print_help()
		sys.exit(102)
				
	if not (options.out_file):
		print (__doc__)
		parser.print_help()
		sys.exit(103)	

	if not os.path.isfile(options.input_file):
		print ("Input data file \"%s\" does not exist\n" % options.input_file) 
		sys.exit(104)
	if not os.path.isfile(options.group_file):
		print ("Input group file \"%s\" does not exist\n" % options.input_file) 
		sys.exit(105)
	
	ROUT = open(options.out_file + '.r','w')
	family = {1:'BB',2:'ZIBB', 3:'ZABB'}
	if not options.family_func in family.keys():
		print ("Incorrect value of '-f'!") 
		sys.exit(106)
	
	
	print ('library("gamlss")', file=ROUT)
	
	printlog("Read group file \"%s\" ..." % (options.group_file))
	(samples,cv_names, cvs, v_types) = read_grp_file2(options.group_file)
	for cv_name in cv_names:
		print ("%s: %s" % cv_name, v_types[cv_name])
		for sample in samples:
			print ('\t' + sample + '\t' + cvs[cv_name][sample])

	print ('bbr <- function (cgid, m,t,%s, app){' % ','.join(cv_names), file=ROUT)
	print ('  tryCatch(', file=ROUT)
	print ('\t{', file=ROUT) 
	print ('\tfit <- gamlss(cbind(m,t - m) ~ %s, family=%s)' % ('+'.join(cv_names),family[options.family_func]), file=ROUT)
	print ('\ts <- summary(fit, save=TRUE)', file=ROUT)
	print ('\tpvals <- s$coef.table[,4]', file=ROUT)
	print ('\tcoefs <- s$coef.table[,1]', file=ROUT)
	print ('\tif (app){write.table(file=\"%s\",x=matrix(c(cgid, as.vector(coefs), as.vector(pvals)), nrow=1),quote=FALSE, row.names=FALSE, sep="\\t",append = TRUE, col.names=FALSE)}' % (options.out_file + '.results.txt'),  file = ROUT) 
	print ('\telse {write.table(file=\"%s\",x=matrix(c(cgid, as.vector(coefs), as.vector(pvals)), nrow=1),quote=FALSE, row.names=FALSE, sep="\\t", append = FALSE, col.names=c("ID",paste(names(coefs), "coef",sep="."), paste(names(pvals), "pval",sep=".")))}' % (options.out_file + '.results.txt'),  file = ROUT) 
	print ('\t},', file=ROUT) 
	print ('\terror=function(error_message) {write.table(file=\"%s\",x=matrix(c(cgid, "Failed"), nrow=1), quote=FALSE, row.names=FALSE, sep="\\t", append=TRUE, col.names=FALSE)}' % (options.out_file + '.results.txt'), file=ROUT)
	print ('  )', file=ROUT) 
	print ('}', file=ROUT)	
	print ('\n', file=ROUT)


	
	printlog("Processing file \"%s\" ..." % (options.input_file))
	line_num = 0
	probe_list = []
	p_list = []
	for l in ireader.reader(options.input_file):
		line_num += 1
		f = l.split()
		if line_num == 1:
			sample_IDs = f[1:]
			# check if sample ID matches
			for s in samples:
				if s not in sample_IDs:
					printlog("Cannot find sample ID \"%s\" from file \"%s\"" % (s, options.input_file))
					sys.exit(3)
			for cv_name in cv_names:
				if v_types[cv_name] == 'continuous':
					print (cv_name + ' <- c(%s)' % (','.join([str(cvs[cv_name][s]) for s in  sample_IDs  ])), file = ROUT)
				elif  v_types[cv_name] == 'categorical':
					print (cv_name + ' <- as.factor(c(%s))' % (','.join([str(cvs[cv_name][s]) for s in  sample_IDs  ])), file = ROUT)
				else:
					printlog("unknown vaiable type!")
					sys.exit(1)	
			print ('\n', file=ROUT)
			
			continue
		else:
			methyl_reads = []	# c
			total_reads = []	# n
			cg_id = f[0]
			for i in f[1:]:
				#try:
				m = re.match(r'(\d+)\s*\,\s*(\d+)', i)
				if m is None:
					methyl_reads.append("NaN")
					total_reads.append("NaN")
					continue
				else:
					c = int(m.group(1))
					n = int(m.group(2))
					if n >= c and n > 0:
						methyl_reads.append(c)
						total_reads.append(n)
					else:
						printlog("Incorrect data format!")
						print (f)
						sys.exit(1)		
			if line_num == 2:
				print ('bbr(\"%s\", c(%s), c(%s), %s, FALSE)' % (cg_id, ','.join([str(read) for read in methyl_reads]), ','.join([str(read) for read in total_reads]), ','.join(cv_names)), file=ROUT)
			else:
				print ('bbr(\"%s\", c(%s), c(%s), %s, TRUE)' % (cg_id, ','.join([str(read) for read in methyl_reads]), ','.join([str(read) for read in total_reads]), ','.join(cv_names)), file=ROUT)
		
	ROUT.close()
	
	
	#sys.exit(0)
	try:
		printlog("Runing Rscript file \"%s\" ..." % (options.out_file + '.r'))
		subprocess.call("Rscript %s 2>%s" % (options.out_file + '.r', options.out_file + '.tmp_warnings.txt' ), shell=True)
	except:
		print ("Error: cannot run Rscript: \"%s\"" % (options.out_file + '.r'), file=sys.stderr)
		sys.exit(1)
	
if __name__=='__main__':
	main()
