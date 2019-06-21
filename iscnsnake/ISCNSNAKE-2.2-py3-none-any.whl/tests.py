#!/usr/bin/env python

import ISCNSNAKE.ISCNParser as ISCN
import copy

def aberration_test(test_string, expected_chromosome,
    expected_starts, expected_ends, expected_values):
    """
    Tests ISCN.analyze_ISCN function
    Args:
        Test string (string): an ISCN with one aberration
        expected_chromosomes (string or list): a list of chromosomes
            per lost span 
        expected_starts (int or list): a list of starts per lost span
        expected_ends (int or list): a list of ends per lost span
        expected_values (int or list): a list of values per lost span
    Returns:
        list: list of tuples in the form (chromosome, start, end)
    """
    # Turns single items into lists
    if type(expected_chromosome) != list:
        expected_chromosome = [expected_chromosome]
    if type(expected_starts) != list:
        expected_starts = [expected_starts]
    if type(expected_ends) != list:
        expected_ends = [expected_ends]
    if type(expected_values) != list:
        expected_values = [expected_values]
    # Use -1 instead of 0 indexing for analysis of short forms
    results = ISCN.PolyclonalISCN(test_string).clones[0].aberrs[-1].bands
    expected_results = []
    for chromosome, start, end, value in  zip(expected_chromosome,
        expected_starts, expected_ends, expected_values):
        expected_dict = {'Chromosome' : chromosome,
            'Start' : start,
            'End' : end,
            'Value' : value}
        expected_results.append(expected_dict)
    # Checks for equality
    errors = []
    for dict in expected_results:
        if dict in results:
            results.remove(dict)
        else:
            errors.append('Error: expected dict not found:' + str(dict))
    if len(results) > 0:
        for item in results:
            errors.append('Error: unexpected result dict:' + str(item))
    if len(errors) > 0:
        global found_error
        found_error = True
        print('Errors found in ' + test_string)
        for error in errors:
            print(error)

def der_test(test_string, expected_chromosome,
    expected_starts, expected_ends, expected_values):
    """
    Tests ISCN.analyze_ISCN function
    Args:
        Test string (string): an ISCN with one aberration
        expected_chromosomes (string or list): a list of chromosomes
            per lost span 
        expected_starts (int or list): a list of starts per lost span
        expected_ends (int or list): a list of ends per lost span
        expected_values (int or list): a list of values per lost span
    Returns:
        list: list of tuples in the form (chromosome, start, end)
    """
    # Turns single items into lists
    if type(expected_chromosome) != list:
        expected_chromosome = [expected_chromosome]
    if type(expected_starts) != list:
        expected_starts = [expected_starts]
    if type(expected_ends) != list:
        expected_ends = [expected_ends]
    if type(expected_values) != list:
        expected_values = [expected_values]
    # Use -1 instead of 0 indexing for analysis of short forms
    results = []
    for aberr in ISCN.PolyclonalISCN(test_string).clones[0].ders[-1].aberrs:
        results += aberr.bands      
    expected_results = []
    for chromosome, start, end, value in  zip(expected_chromosome,
        expected_starts, expected_ends, expected_values):
        expected_dict = {'Chromosome' : chromosome,
            'Start' : start,
            'End' : end,
            'Value' : value}
        expected_results.append(expected_dict)
    # Checks for equality
    errors = []
    for dict in expected_results:
        if dict in results:
            results.remove(dict)
        else:
            errors.append('Error: expected dict not found:' + str(dict))
    if len(results) > 0:
        for item in results:
            errors.append('Error: unexpected result dict:' + str(item))
    if len(errors) > 0:
        global found_error
        found_error = True
        print('Errors found in ' + test_string)
        for error in errors:
            print(error)
found_error = False

# Testing various functions

# Testing find_span
start, end = ISCN.find_span('p11','1')
if start != 0 or end != 125000000:
    raise Exception("Error in find_span")

# Testing of main aberration parsing    

# Order of band losses determined through inspection of algorithm
# Testing Additio aberrations
# Additio on p
aberration_test('46,XX,add(1)(q11)',['hs1'],[125000000],
                      [249250621],[-1])
# Gain of 1 and Additio on q, Additio processed before gain
aberration_test('47,XX,+add(1)(q11)',['hs1','hs1'],[125000000,0],
                      [249250621,249250621],[-1,1])
# Tests short forms 
aberration_test('46,XX,add(1)(q11),+add(1)',
                ['hs1','hs1'],[125000000,0],
                [249250621,249250621],[-1,1])
                
# testing Amplification
aberration_test('46,XX,dup(2)(q11)',['hs2'],[93300000],
                [102700000],[1])
aberration_test('46,XX,trp(3)(p11)',['hs3'],[87200000],
                [91000000],[2])
aberration_test('46,XX,qdp(4)(q21)',['hs4'],[76300000],
                [88000000],[3])
aberration_test('46,XX,dp(5)(p11p14)',['hs5'],[18400000],
                [48400000],[1])
aberration_test('46,XX,tp(6)(q21q11)',['hs6'],[61000000],
                [114600000],[2])
aberration_test('46,XX,+qp(7)(q11q21)',['hs7','hs7'],[59900000,0],
                [98000000,159138663],[3,1])
# Testing Deletions
aberration_test('46,XX,del(3)(q11)','hs3',91000000,198022430,-1)
aberration_test('46,XX,del(3)(p13p14)','hs3',54400000,74200000,-1)
aberration_test('46,XX,del(3)(q11q11)','hs3',91000000,98300000,-1)
aberration_test('46,XX,del(3)(q11q27)','hs3',91000000,187900000,-1)
aberration_test('46,XX,del(3)(p12q22)','hs3',74200000,138700000,-1)

# Testing old known bug on derivative chromosome behaiviour
der_test('46,XX,der(1)t(1;2)(q11;q11)add(2)(q37)',['hs1','hs2','hs2'],
         [125000000,93300000,231000000],
         [249250621,243199373,243199373],
         [-1, 1, -1])
der_test('46,XX,der(1)t(1;2)(q11;q11)del(2)(q37)',['hs1','hs2','hs2'],
         [125000000,93300000,231000000],
         [249250621,243199373,243199373],
         [-1, 1, -1])
der_test('46,XX,der(1)t(1;2)(q11;q11)trp(2)(q37)',['hs1','hs2','hs2'],
         [125000000,93300000,231000000],
         [249250621,243199373,243199373],
         [-1, 1, 2])
# Testing Derivative + DerTranslocation

# cydas 
der_test('46,XX,der(1;2)(p10;q10)', ['hs1','hs2'], 
         [125000000, 0], [249250621, 93300000],
         [-1, -1])

# Testing Dicentric
aberration_test('45,XX,dic(9;20)(p11;q11)',['hs9','hs20'],[0,27500000],
                [49000000, 63025520],[-1,-1])
# Testing Fission

# Testing Gain
aberration_test('45,X,+X',['hsX'],[0],[155270560],[1])
# Testing Insertion

# Testing Isochromosome 

# Testing Loss
aberration_test('45,X,-Y',       ['hsY'],[0],
                [59373566],[-1]) #LOSS chr_y

# Testing Rings

# Testing Tricentric

# Testing errors 








if not found_error:
    print('Tests completed successfully.')
