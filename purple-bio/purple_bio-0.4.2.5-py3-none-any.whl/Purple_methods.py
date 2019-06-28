# -*- coding: utf-8 -*-
"""
Welcome to Purple: Picking unique relevant peptides for viral experiments

This is the methods file.
Please save this file in the same folder as the main file, then execute the main file. 

"""

import csv
import json
import os
import pprint
import re
import sys
import time
from collections import Counter
from datetime import datetime
from shutil import rmtree
from sys import exit
from timeit import default_timer as timer
#from tkinter import messagebox

import yaml
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from tqdm import tqdm


def load_config_yml(config_file):
    """
    imports a configuration-file in yml-format
    """
    try:
        with open(config_file, 'r') as infile:
            return yaml.load(infile, Loader=yaml.FullLoader)
    except IOError:
        sys.exit('Config-file not found! Please check if "'+config_file+'" really exists in the folder!')


def loadBG(path):
    # load preprocessed background database.
    # Dictionary, saved with the pickle library.
    # key: peptide
    # value: fasta description of proteins, where peptide occures
    # File was created by the function for new background databases named 'prepare_new_BG_file'.
    # Saves time by just loading instead of creating it new each time
    print("\nLoading background...")
    try:
        with open(path + 'Background_peptides.txt', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        exit('Database not found in ' + path + '. Please set update_DB = true to create a database.')


def create_species_list(writefile, OS, P, path):
    # creates a lists with all origin species of the database and the number of peptides assigned to each species
    # For the user to check the overall database.
    # For a later reloading of the data. This improves the runtime. A new species file is only created,
    # if the database is newly created by 'prepare_new_BG_file'.
    print("\nStart extracting species...")

    for all_descriptions in tqdm(P.items(), file=sys.stdout, ncols =75):
        descriptions = all_descriptions[1]
        for description in descriptions:
            species = getOS(description)
            if species not in OS:
                OS[species] = 0  # no else
            OS[species] += 1

    if writefile:
        with open(path + 'species.txt', 'w') as f:
            for key, value in OS.items():
                f.write(key)
                f.write('\t')
                f.write(str(value))
                f.write('\n')

    return OS


def getOS(x):
    # IN: Fasta description
    # OUT: origin species. by extracting the string following 'OS='
    regex = re.search("OS=[^=]*", x)
    if regex is None:
        print(x)
        exit('Error in the input file! The given fasta file does not have an "OS=" section in the description.'
             ' Without it, this program cannot identify the origin species. Please use a different input or modify'
             ' the "getOS" and "getName" function in the script. Please excuse the inconvenience.')
    pos = regex.span()
    return x[pos[0] + 3:pos[1] - 3]


def loadOS(path):
    # loads a file, where all origin species of the background file are listed, with the number of peptides assigned
    # to each species
    # File was created by the function for new background databases named 'prepare_new_BG_file' e.g. by 'create
    # _species_list'.
    # Saves time by just loading instead of creating it new every time
    print("\nLoading origin species...")
    OS = {}
    with open(path + 'species.txt', 'r') as f:
        for line in f:
            text = line.split('\t')
            OS[text[0]] = text[1]
    return OS


def do_you_mean_this_target(target, db, ask):
    # confirms hits for target in database. Option to enable quit by request
    # Returns clear table of target hits for an easy confirmation.
    # If 'ask' is set to true, the program stops after printing the table and waits for an user input: continue or quit

    target_species = {}
    target = [x.lower() for x in target]
    for species, Nr_pep in db.items():
        if any(alias in species.lower() for alias in target):
            target_species[species] = Nr_pep

    if len(target_species) == 0:
        exit('Target not found. Please try a different target name. For an overview please check the species file')

    print('The target matches to:')

    print ("{:<65} {:<8}".format('Species', 'Number of Peptides'))
    print('-' * 84)
    for species, Nr_pep in target_species.items():
        print ("{:<65} {:<8}".format(species, Nr_pep))
    print('-' * 84)
    sumTargetPeptides = sum(list(map(int, target_species.values())))
    print ("{:<65} {:<8}".format('Total:', str(sumTargetPeptides)))
    if ask:
        print('\n')
        print("Is this what you are looking for?")
        answer = input('Type "y" if you like to continue or "n" to quit: ')
        if answer != 'y':
            exit('Exit requested by User.')

    return target_species, sumTargetPeptides

'''
def do_you_mean_this_target_GUI(target, OS, ask):
    # confirms hits for target in database. Option to enable quit by request
    # Returns clear table of target hits for an easy confirmation.
    # If 'ask' is set to true, the program stops after printing the table and waits for an user input: continue or quit

    target_species = {}
    target = [x.lower() for x in target]
    for species, Nr_pep in OS.items():
        if any(alias in species.lower() for alias in target):
            target_species[species] = Nr_pep

    if len(target_species) == 0:
        exit('Target not found. Please try a different target name. For an overview please check the species file')

    print('The target matches to:')

    print ("{:<60} {:<8}".format('Species', 'Number of Peptides'))
    print('-' * 79)
    for species, Nr_pep in target_species.items():
        print ("{:<60} {:<8}".format(species, Nr_pep))
    print('-' * 79)
    sumTargetPeptides = sum(list(map(int, target_species.values())))
    if ask:
        if not messagebox.askyesno("Target preview", "Is this what you are looking for?"):
            exit('Exit requested by User.')

    return target_species, sumTargetPeptides
'''

def digest(DB, min_len_threshold, max_len_threshold, P, removeFragments, leucine_distinction, proline_digestion,
           type_digest='trypsin_simple'):
    # digests proteins into peptides
    # @param DB  dictionary: keys: fasta description, values: protein
    # @return P dictionary: keys: peptides, values: list of fasta description of the origin proteins,
    # simple trypsin digestion is used as a default
    # Uses the digest_one_protein function
    
    print("\nStart digesting...")
    for  description, protein_seq in tqdm(DB.items(), file=sys.stdout, ncols =75):  # for each protein...
        isFragment = (description.find("(Fragment)") >= 0)
        if (removeFragments and not isFragment) or not removeFragments:
            peptides = digest_one_protein(str(protein_seq), type_digest, leucine_distinction, proline_digestion)
            # peptides stores all possible peptides of the current protein

            # Stores the peptides in P
            for pep in peptides:
                # only peptides that are at least "threshold" long are stored
                if min_len_threshold <= len(pep) <= max_len_threshold and "X" not in pep:
                    try:
                        P[pep].append(description)
                    except KeyError:
                        P[pep] = [description]
    return P


def digest_one_protein(seq, type_digest, leucine_distinction, proline_digestion):
    # digestion of one protein into peptides by different digestion types.
    # As of now, there is only one digestion type: "trypin_simple", which does not allow any missed cleavages.
    # Please feel free to add your own digestion type here.
    if type_digest == "trypsin_simple":
        """
        Trypsin Simple:
        - no missed cleavages allowed
        - cuts at K and R, unless P follows
        
        """
        cuts = [0]
        peptides = []

        if leucine_distinction:
            seq = seq.replace("I","L")
            
        # Find all sites, where trypsin cuts
        if proline_digestion:
            for i in range(len(seq) - 1):
                if seq[i] == 'R' and seq[i + 1] != 'P':
                    cuts.append(i + 1)
                elif seq[i] == 'K' and seq[i + 1] != 'P':
                    cuts.append(i + 1)
                    # Save also End
        else:
            for i in range(len(seq) - 1):
                if seq[i] == 'R':
                    cuts.append(i + 1)
                elif seq[i] == 'K':
                    cuts.append(i + 1)
                    # Save also End
        if cuts[-1] != len(seq):
            cuts.append(len(seq))

        # Find Peptides following the cuts
        if len(cuts) > 2:  # if sites were found
            for j in range(len(cuts) - 1):
                peptides.append(seq[cuts[j]:cuts[j + 1]])
        else:  # there was no cut site found
            peptides.append(seq)

        return peptides  # !!!!!!!!!!!!!!!!

    elif type_digest == "my_customized_digestion":
        print("Do your own here")

    else:
        exit("Sorry, there is a typo in the digestion type")


def print_parameter(where, v, path_output=''):
    # v is the vector with all parameter
    # shows parameter of run in console
    # and prints parameter of run and results in log file called 'ResultTable'
    where = str(where)
    if where == 'console':
        # parameter = [target,threshold,path_DB,update_BG, min_len_peptides,max_len_peptides]
        print()
        print('The target is:', v[0])
        print('The background consensus threshold is at', v[1], '%')
        print()
        if v[2] == 1:
            print('A new background was created!')
            print('Source:', v[3])
            print('Minimal peptide length:', v[4])
            print('Maximal peptide length:', v[5])

        print()

    elif where == 'file':

        for i in range(len(v)):
            v[i] = str(v[i])

        # parameter = [target,threshold,path_DB,update_BG, min_len_peptides,max_len_peptides][targets,runtime,comment,len(Uniques),freq_scores, species_list]
        order_for_backward_compatibility = [0, 6, 2, 4, 5, 7, 8, 10, 1, 9, 11, 3]
        line = ''
        for i in order_for_backward_compatibility:
            line = line + v[i] + '\t'
        with open(path_output + "/" + "log_book.txt", "a") as f:  # a for add
            f.write("target\t#peptide per target\tunknown\tminimum peptide length\tmaximum peptide length\tseconds"
                    "\texperiment name\thomologous matching threshold\tdistribution\t#exact matching\t#peptides"
                    "\tdatabase directory\n")
            f.write(line)
            f.write('\n')

    else:
        exit('Error: Typo in print_parameter')


def prepare_new_BG_file(do, path, min_len_peptides, max_len_peptides, removeFragments, leucine_distinction,
                        proline_digestion):
    # creating of new background database
    # only done, if do == True
    # reads in fasta files in the folder "path" and stores them with Bio.python
    # all proteins are digested and stored in a peptide dictionary.
    # this will be saved, so it can be loaded later, and does not to be calculated every time.
    # additionally the file species_list is saved for an overview over the created database,
    # which will be loaded as well.

    if do == 0:
        return 0
    # warnings.filterwarnings("ignore")
    print("\n######################################\n# "
          "Start creating background database"
          " #\n######################################\n")

    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    # http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
    # Strip all non fasta files from file list
    for i in range(len(files) - 1, -1, -1):
        if str.split(files[i], '.')[-1] != 'fasta':
            files.remove(files[i])
    print("Used databases: ",files)

    P = {}
    OS = {}
    writeOS = 0
    for file in files:
        print("\nProcessing " + file)
        DB = {}
        with open(path + '/' + file) as f:
            for name, seq in read_fasta(f):
                DB[name] = seq
        P = digest(DB, min_len_peptides, max_len_peptides, P, removeFragments,leucine_distinction,proline_digestion)

        if file == files[-1]:
            writeOS = True
        OS = create_species_list(writeOS, OS, P, path)  # updates species list
        print("done")
    with open(path + 'Background_peptides.txt', 'w') as f:
        json.dump(P, f)

    return 1


def read_fasta(fp):  # from the BioPython Code: https://github.com/biopython/biopython/blob/master/Bio/SeqIO/FastaIO.py
    name, seq = None, []
    for line in fp:
        line = line.rstrip()
        if line.startswith(">"):
            if name: yield (name, ''.join(seq))
            name, seq = line, []
        else:
            seq.append(line)
    if name: yield (name, ''.join(seq))


def extract_target_from_BG(BG, targets, path_output):
    # Exact matching
    # by extracting the target from the background
    # the unique target peptides are stored in Uniques and deleted from the background.
    # the background is updated by returning it
    targets = list(targets.keys())
    uniques = {}
    shared = {}
    delete_me = []
    write = True
    print("\nExtracting target from background...")
    with open(path_output+'peptides_digested.tsv', mode='w', newline='') as file:
        file_writer = csv.writer(file, delimiter='\t')
        file_writer.writerow(["peptide", "protein", "species", "fasta header"])
        for pep, descriptions in tqdm(BG.items(), file=sys.stdout, ncols=75):
            not_target = [2] * len(descriptions)  # initialize. If "2" is still there: error
            for i in range(len(descriptions)):
                species = getOS(descriptions[i])
                if species in targets:
                    not_target[i] = 0
                    if write:
                        file_writer.writerow([pep,dict(Counter(list(map(getName,descriptions)))),dict(Counter(list(map(getOS,descriptions)))),descriptions])
                        write = False
                else:
                    not_target[i] = 1
                if sum(not_target) == 0:  # unique target peptide found
                    uniques[pep] = descriptions
                    delete_me.append(pep)
                elif 1 in not_target and 0 in not_target:
                    shared[pep] = descriptions
            write = True

    print("\nUpdating background...")
    for pep in tqdm(delete_me, file=sys.stdout, ncols =75):  # update background
        del BG[pep]
    return uniques, shared, BG


def homologousMatching(Uniques, BG, threshold_pct):
    # homologous matching
    # Each peptides is compared to the whole background and is assigned a score
    print("\nStarting homologous matching...")
    S = {}
    threshold_pct = int(threshold_pct)
    for pep in tqdm(Uniques, file=sys.stdout, ncols =75):
        S[pep] = getScoreRelative(pep, BG, threshold_pct)  # save worst score as final score for peptide

    return S


##
# Method to calculate the distance of a sequence and all sequences in the background by returning
# the percentage of the highest consensus.
# Example: AAAA and AAAB would have a score of 75.00.
# @param pep A peptide sequence
# @param BG Background with all peptide sequences
# @param threshold_pct Threshold for the filtering in percent (0-100)
# @return final_score Returns the final score with two decimal digits (xxx.xx)
# @author Felix Hartkopf
##
def getScoreRelative(pep, BG, threshold_pct): 
    worst_score = 0
    for bg_pep in BG:
        matches = 0
        if len(bg_pep) == len(pep):
            for i in range(len(pep)):
                matches += (pep[i] == bg_pep[i])
            if matches > worst_score:
                if matches/len(pep)*100 >= threshold_pct:
                    final_score = matches / len(pep) * 100
                    return round(final_score, 2)   # worst score possible, so stop immediately
                worst_score = matches
    final_score = worst_score / len(pep) * 100
    return round(final_score, 2)  # return in percent: 12,34%


def get_print_threshold(allscores):
    # calculates the threshold for a peptide to be flagged and therefore be printed in console
    positive_scores = [x for x in allscores if x != -1]
    if len(positive_scores) <= 15:  # if only 15 peptides or less display all
        return 0
    return sum(positive_scores) / float(len(positive_scores))  # average


def print_result(peps, print_peps,threshold):
    # calculates the frequency of the scores
    # prints flagged peptides in console, if print_peps == True
    # peptides are flagged, if they are greater than the average of all positive scores
    scores = list(peps.values())
    scores_in_tens = [int(round(i, -1)) if i <= threshold else -1 for i in scores]  # only round positiv scores
    freq_scores = {x: scores_in_tens.count(x) for x in scores_in_tens}  # Dictionary Comprehension
    print("\n###############################\n# Homologous Peptides Histogram #\n##############################\n")
    print("Score")
    countTotal = len(peps)
    for i in range(1,21):
        axis = str(100-i*5)+" to "+str(100-(i-1)*5)
        if i == 1:
            axis = axis
        elif 19 > i > 1:
            axis = (axis + (abs(len(axis)-7))*" ")
        elif i == 19 :
            axis = str(100-i*5)+" to "+str(100-(i-1)*5)+" "*2
        elif i == 20:
            axis = str(100-i*5)+" to "+str(100-(i-1)*5)+" "*3
        print(axis+"\t|"+str(int(count(peps.values(), 100-i*5, 100-(i-1)*5)/countTotal*300)*'|')
              +str(count(peps.values(), 100-i*5, 100-(i-1)*5)))
    print("---------------------------Frequency--------------------------->")
    print("\n")
    
    if print_peps == 1:
        display_me = {}
        print_threshold = get_print_threshold(scores)
        for pep, score in peps.items():
            if score >= print_threshold:
                display_me[pep] = score

        pp = pprint.PrettyPrinter(width=200)
        pp.pprint(display_me)
    print()
    print(freq_scores)
    return freq_scores


def count(list1, l, r):
    # x for x in list1 is same as traversal in the list 
    # the if condition checks for the number of numbers in the range  
    # l to r  
    # the return is stored in a list 
    # whose length is the answer 
    return len(list(x for x in list1 if l <= x <= r)) 


def inspect_BG(BG, mini, maxi):
    # for database analysis, not called
    freq_dict = {}
    for i in range(mini, maxi + 1):
        freq_dict[i] = 0
    for pep in BG:
        freq_dict[len(pep)] += 1
    freq_list = [0] * (maxi + 1)
    for key, value in freq_dict.items():
        freq_list[key] = value
    return freq_list


def getName(x):
    # extract name of protein from fasta description
    return str.split(str.split(x, '|')[2], ' OS=')[0]


def create_output_file(Uniques, Scores, target, path_output,threshold):
    # creates result file of the unique peptides with score and fasta description
    # file is named like the string target input and combined with the date and time
    if not os.path.exists(path_output):
        os.makedirs(path_output)
        
    regex = re.compile('[^a-zA-Z0-9]') 
    target_clean = regex.sub(' ', target[0])
    target_clean = target_clean.replace('  ', ' ')
    target_clean = target_clean.replace(' ', '_')
    
    path = path_output + "/" + target_clean + '_' + get_date() + '.txt'
    with open(path, 'w') as f:
        f.write('peptide' + '\t' + 'peptide weight' + '\t' + 'highest background consensus' + '\t' + 'occurrences'
                + '\t' + 'species' + '\t' + 'proteins' + '\t' + 'protein names' + '\t' + 'fasta entries' +
                '\t' + 'descriptions' + '\n')
        for pep, descriptions in Uniques.items():
            score = Scores[pep]
            if score > threshold:
                continue
            else:
                score_string = str(score) + '%'
            names = list(set([getName(x) for x in descriptions]))
            allOS = list(set([getOS(x) for x in descriptions]))
            
            prot = ProteinAnalysis(pep.upper())
            weight = prot.molecular_weight()
            
            line = str(pep) + '\t' + str(weight) + '\t' + score_string + '\t' + str(len(descriptions)) + '\t'\
                   + str(allOS) + '\t' + str(len(names)) + '\t' + str(names) + '\t' + str(len(list(set(descriptions))))\
                   + '\t' + str(list(set(descriptions))) + '\n'
            f.write(line)


def get_date():
    # gets date and time and converts it into a usable string
    x = str(datetime.now())
    x = x.replace(' ', '_')
    x = x.replace(':', '-')
    return x.split('.')[0]


##
# Method to remove target species entries from database. 
# @param dbPath Path to database folder
# @param targetFile File name of target
# @param backgroundFile File name of background.
# @author Felix Hartkopf
##
def cleanDB(dbPath, targetFile, backgroundFile):
        print("\nCleaning "+backgroundFile+"...")         
 
        targetDB = []    
        with open(dbPath+"/"+targetFile, "rU") as handle:
            for record in SeqIO.parse(handle, "fasta"):
                targetDB.append(record)
        
        targetOS = set([])
        for record in targetDB:
            targetOS.add(getOS(record.description))

        targetOS = set(targetOS)
        print("\nAmount of species in target database: ", len(targetOS))
    
        backgroundDB = []
        countBackground = 0   
        with open(dbPath+"/"+backgroundFile, "rU") as handle:
            for record in SeqIO.parse(handle, "fasta"):
                countBackground += 1
                if not getOS(record.description) in targetOS :
                    backgroundDB.append(record)

        if not os.path.exists(dbPath+"/clean"):
            os.makedirs(dbPath+"/clean")
            
        with open(dbPath+"/clean/"+backgroundFile, "w") as output_handle:
            SeqIO.write(backgroundDB, output_handle, "fasta")
        with open(dbPath+"/clean/"+targetFile, "w") as output_handle:
            SeqIO.write(targetDB, output_handle, "fasta")
            
        print("Amount of entries removed from background database: ", countBackground - len(backgroundDB))
    
        return list(targetOS)


##
# Method to clean all databases. 
# @param dbPath Path to database folder
# @param targetFile File name of target
# @author Felix Hartkopf
##
def cleanAllDBs(path_DB, targetFile):
    print("\nCleaning background files...")         
    files = [f for f in os.listdir(path_DB) if os.path.isfile(os.path.join(path_DB, f))]
    # http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
    # Strip all non fasta files from file list
    for i in range(len(files) - 1, -1, -1):
        if str.split(files[i], '.')[-1] != 'fasta':
            files.remove(files[i])
    files.remove(targetFile)
    print("Used databases: ", files)
    for backgroundFile in tqdm(files, file=sys.stdout, ncols=75):
        targetOS = cleanDB(path_DB, targetFile, backgroundFile)
        
    return targetOS


##
# Method write unique homologous peptides to tsv file 
# @param path Path to output folder
# @param peptides List of peptides
# @param exact True if peptides are result of exact matching
# @param threshold Threshold to filter high consensus sequences with background 
# @author Felix Hartkopf
##
def writeHomologousPeptidesToTSV(path, peptides, uniques, threshold):
    with open(path+'peptides_homologous_matching.tsv', mode='w', newline='') as file:
        file_writer = csv.writer(file, delimiter='\t')
        file_writer.writerow(["peptide", "highest background consensus", "protein", "species", "fasta header"])
        for key, value in peptides.items():  
            if value <= threshold:
                file_writer.writerow([key, value, dict(Counter(list(map(getName, uniques[key])))),
                                      dict(Counter(list(map(getOS, uniques[key])))), str(uniques[key])])


##
# Method write shared peptides after homologous to tsv file 
# @param path Path to output folder
# @param shared List of peptides
# @param exact True if peptides are result of exact matching
# @author Felix Hartkopf
##
def writeSharedPeptidesToTSV(path, shared, uniques, scores, threshold):
    with open(path+'peptides_shared.tsv', mode='w', newline='') as file:
        file_writer = csv.writer(file, delimiter='\t')
        file_writer.writerow(["peptide", "highest background consensus", "protein", "species", "fasta header"])
        for key, value in scores.items(): 
            if value > threshold:
                file_writer.writerow([key, value, dict(Counter(list(map(getName, uniques[key])))),
                                      dict(Counter(list(map(getOS, uniques[key])))), str(uniques[key])])
        for key, value in shared.items(): 
            file_writer.writerow([key, 100, dict(Counter(list(map(getName, shared[key])))),
                                  dict(Counter(list(map(getOS, shared[key])))), str(shared[key])])


##
# Method write unique exact peptides to tsv file 
# @param path Path to output folder
# @param peptides List of peptides
# @param exact True if peptides are result of exact matching
# @author Felix Hartkopf
##
def writeExactPeptidesToTSV(path,peptides):
    with open(path+'peptides_exact_matching.tsv', mode='w', newline='') as file:
        file_writer = csv.writer(file, delimiter='\t')
        file_writer.writerow(["peptide", "protein", "species", "fasta header"])
        for peptide in peptides:
            file_writer.writerow([peptide, dict(Counter(list(map(getName, peptides[peptide])))),
                                  dict(Counter(list(map(getOS, peptides[peptide])))), peptides[peptide]])

##
# Method to create target specific output folder 
# @param path Path to output folder
# @param targets list of targets
# @author Felix Hartkopf
##
def createOutputDir(path,targets):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    if not os.path.exists(path):
        os.makedirs(path)
    regex = re.compile('[^a-zA-Z0-9]') 
    key = next(iter(targets.keys()))
    targets_clean = regex.sub(' ', key)
    targets_clean = targets_clean.replace('  ', ' ')
    targets_clean = targets_clean.replace(' ', '_')
    if targets_clean[-1] == "_":
        targets_clean = targets_clean[:-1]
    path_output = path + timestr + "_" + targets_clean + "/"
    if not os.path.exists(path_output):
        os.makedirs(path_output)
    return path_output

##            
# Main to run a complete Purple workflow
# @param config Path to config file
# @author Felix Hartkopf
##
def main(config):
    print("    ######  #     # ######  ######  #       #######")
    print("    #     # #     # #     # #     # #       #      ")
    print("    #     # #     # #     # #     # #       #      ")
    print("    ######  #     # ######  ######  #       #####  ")
    print("    #       #     # #   #   #       #       #      ")
    print("    #       #     # #    #  #       #       #      ")
    print("    #        #####  #     # #       ####### #######")
    print("Picking Unique Relevant Peptides for viraL Experiments")
    print("                    Version: 0.4.1\n")
    print("\n#############################\n# Start reading config file #\n#############################\n")

    config = load_config_yml(config)

    print("Config file: ",config)

    print("\n- Purple: ")
    target = config['purple']['target']
    print("\tTarget: ", target)
    threshold = int(config['purple']['threshold'])
    print("\tThreshold: ", threshold)
    path_DB = str(config['purple']['path_DB'])
    print("\tPath to databases: ", path_DB)
    update_DB = bool(config['purple']['update_DB'])
    print("\tUpdate database: ", update_DB)
    targetFile = config['purple']['targetFile']
    print("\ttargetFile: ", targetFile)

    min_len_peptides = int(config['purple']['min_len_peptides'])
    print("\tMinimum length of peptide: ", min_len_peptides)
    max_len_peptides = int(config['purple']['max_len_peptides'])
    print("\tMaximum length of peptide: ", max_len_peptides)
    removeFragments = bool(config['purple']['removeFragments'])
    print("\tExclude fragments from fasta files: ", removeFragments)

    path_output = str(config['purple']['path_output'])
    print("\tPath to output: ", path_output)
    i_am_not_sure_about_target = bool(config['purple']['i_am_not_sure_about_target'])
    print("\tAre you sure about the target: ", i_am_not_sure_about_target)
    leucine_distinction = bool(config['purple']['leucine_distinction'])
    print("\tLeucine and Isoleucine distinction: ", leucine_distinction)
    proline_digestion = bool(config['purple']['proline_digestion'])
    print("\tProline digestion rule: ", proline_digestion)
    print_peptides = bool(config['purple']['print_peptides'])
    print("\tPrint peptides: ", print_peptides)
    comment = str(config['purple']['comment'])
    print("\tComment: ", comment)

    # get path of this script
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    print("\nWorking directory: ", dname)

    # Clean database from targets
    if not targetFile == "":
        target = cleanAllDBs(path_DB, targetFile)
        path_DB = path_DB+"/clean/"

    # if requested, creation of new BG
    prepare_new_BG_file(update_DB, path_DB, min_len_peptides, max_len_peptides, removeFragments, leucine_distinction,
                        proline_digestion)

    # load DBs
    BG = loadBG(path_DB)
    species_list = loadOS(path_DB)

    parameter = [target, threshold, update_DB, path_DB, min_len_peptides, max_len_peptides]
    print_parameter('console', parameter)

    # Check search-string against species list
    targets, Nr_target_peptides = do_you_mean_this_target(target, species_list, i_am_not_sure_about_target)

    # Add output folder for experiment
    path_output = createOutputDir(path_output, targets)

    timeStart = timer()

    # Extract target from BG / Exact Matching
    uniques, shared, BG = extract_target_from_BG(BG, targets, path_output)

    # Write exact unique peptides to tsv file
    writeExactPeptidesToTSV(path_output, uniques)

    # Runtime prediction
    print('\nNumber of found peptides without matching:', len(uniques))

    # homologous matching
    unique_peptides_scores = homologousMatching(uniques, BG, threshold)

    # Add output folder for experiment
    writeHomologousPeptidesToTSV(path_output,unique_peptides_scores, uniques, threshold)

    # Print results
    freq_scores = print_result(unique_peptides_scores, print_peptides, threshold)
    create_output_file(uniques, unique_peptides_scores, target, path_output, threshold)
    writeSharedPeptidesToTSV(path_output, shared, uniques, unique_peptides_scores, threshold)

    # Write record in log file
    timeEnd = timer()
    runtime = round(timeEnd - timeStart, 2)
    print ('Runtime: ', runtime, 'sec, or', round(runtime / 60, 1), 'minutes.')
    parameter.extend([targets, runtime, comment, len(uniques), freq_scores, Nr_target_peptides])
    print_parameter('file', parameter, path_output)

    # Delete clean directory
    if not targetFile == "":
        rmtree(path_DB)


"""
Created on Thu Sep 29 10:15:35 2016

@author: LechnerJ
@author: HartkopfF

"""
