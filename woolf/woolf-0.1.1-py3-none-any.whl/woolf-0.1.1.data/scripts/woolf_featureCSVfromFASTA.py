#!python

# ############################### #
# featureCSVfromFASTA.py
#
# Creates a feature table with class identificiations from multiple fasta files.
#
# Anna Farrell-Sherman 3/31/19
# ############################### #

#import packages
import argparse # to format command line arguments
import sys #for command line parsing
import os #for creating file names

#import import Woolf module for creating feature tables
import featureCSVfromFASTA

#create parser for command line 
parser = argparse.ArgumentParser(description="Build a CVS feature table from amino acid FASTA files")

#Output file info (user specified output)
parser.add_argument("-c", "--comparisonFileName", default="featureTable", help="an identifying tag for all output files")
parser.add_argument("-f", "--folder", default="", help="A folder to contain the output files")

#choose machine learning algorithm
group = parser.add_mutually_exclusive_group()
group.add_argument("-b", "--binary", action="store_true")
group.add_argument("-t", "--predict", action="store_true")

#add arguments for positive and negative class fasta files
# Though permissible, short versions of shell args are typically a single letter.
parser.add_argument("-p", "--posFasta", nargs='+', help="a single fasta file for a Binary Feature Table, or a set of one or more fasta files for a multiClass Feature Table")
parser.add_argument("-n", "--negFasta", nargs='+', help="one or more fasta files containing the negative class sequences for a multiClass Feature Table")


args = parser.parse_args()

if len(sys.argv)==1:
	parser.print_help(sys.stderr)
	sys.exit(1)

if args.folder:
	# os.path.join() (used later) takes care of the slashes, (also lets it work on windows).
	folderName = args.folder
	if not os.path.isdir(folderName):
		os.mkdir(folderName)
	fileName = os.path.join(folderName, args.comparisonFileName + '.csv')

#Creating a binary feature table
if args.binary:
	if args.posFasta and args.negFasta:
		seqFeatureTable = binaryFeatureTable(args.posFasta, args.negFasta)
		saveCSV(seqFeatureTable, fileName)
		print('Binary Table')
		print('Saved csv file to: ' + fileName)
	else:
		print("For a binary feature table please provide both positive and negative class fasta files with [-pf] and [-nf]")
#creating a prediction feature table
elif args.predict:
	if args.posFasta:
		print(args.posFasta)
		seqFeatureTable = predictDataFeatureTable(args.posFasta)
		saveCSV(seqFeatureTable, fileName)
		print('Prediction Table')
		print('Saved csv file to: ' + fileName)
	else:
		print("For a prediction feature table please provide a fasta file with [-pf]")
#Error message and printing help if no feature table type is passed
else:
	print('Error: Please select either binary or predict as discribed below:\n')
	parser.print_help(sys.stderr) # might be good to *also* add a descriptive message
