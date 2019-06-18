#!/usr/bin/env python

"""
Quick Script for assembling a new ISCNParser setting
"""

import sys
import ISCNSNAKE.ISCNParser as ISCN

if '-i' in sys.argv:
    database_path = sys.argv[sys.argv.index('-i') + 1]
else:
    database_path = input('Enter the path to the data file: ')
if '-d' in sys.argv:
    datatype = sys.argv[sys.argv.index('-d') + 1]
else:
    datatype = input('If the file strictly conforms to the format of the'
                     'Mitelman Database type "Mitelman". If the file only'
                     'contains karyotypes type "ISCN". Otherwise please'
                     'convert data to match one of these types.     ')
while datatype not in ["Mitelman", "ISCN"]:
    print('Invalid datatype option.')
    datatype = input('If the file strictly conforms to the format of the'
                     'Mitelman Database type "Mitelman". If the file only'
                     'contains karyotypes type "ISCN". Otherwise please'
                     'convert data to match one of these types.     ')
if '-f' in sys.argv and datatype == "Mitelman":
    filters = sys.argv[sys.argv.index('-f') + 1]
elif datatype == "ISCN":
    filters = "none"
else:
    valid_filters = False
    while not valid_filters:
        filters = input('Enter as many filters as you want, seperated by'
                        'double forward slashes(//) or "none" for no filters: '
                        )
        if filters == 'none' or filters == 'None':
            filters == ''
            valid_filters = True
        elif ':' not in filters or ' ' in filters:
            print('Error: Invalid filter syntax.')
            print('Please use format column1:field1//column2:field2')
            print('Example: Topography:Breast//Morphology:Adenocarcinoma')
        else:
            valid_filters = True
if '-p' in sys.argv:
    cancertype = sys.argv[sys.argv.index('-p') + 1]
else:
    cancertype = input('Enter the desired file suffix: ')
if '-o' in sys.argv:
    output_folder = sys.argv[sys.argv.index('-o') + 1]
else:
    output_folder = './' + cancertype + '_ISCNSNAKE_ results'
if '-v' in sys.argv:
    verbosity = True
else:
    yn = input('Verbose? (y/n): ')
    if yn == 'y':
        verbosity = True
    else:
        verbosity = False

x = ISCN.parse_file(database_path,
                    datatype=datatype,
                    skip_menu=True,
                    clone_method='merge',
                    mode="relative",
                    verbose=verbosity,
                    autocsv=True,
                    folderpath=output_folder,
                    gainname=cancertype + '_Gain.txt',
                    lossname=cancertype + '_Del.txt',
                    deepgainname=cancertype + '_DeepAmp.txt',
                    deeplossname=cancertype + '_DeepDel.txt',
                    rawname=cancertype + '_AllQuantitative.txt',
                    recurrance=True,
                    recurrance_filename=(cancertype
                                          + '_recurrance.txt'),
                    filters=filters)
print('Finished. Files created: ')
print(cancertype + '_Gain.txt - gain frequency')
print(cancertype + '_Del.txt - heterogyzgous deletion frequency')
print(cancertype + '_DeepAmp.txt - amplification frequency')
print(cancertype + '_DeepDel.txt - homozygous deletion frequency')
print(cancertype + '_AllQuantitative.txt - a copy number matrix of all' +
      'patients analyzed')
print(cancertype + '_recurrance.txt - frequency of recurring aberrations')


