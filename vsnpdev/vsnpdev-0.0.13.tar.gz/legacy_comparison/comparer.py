#!/usr/bin/env python3
from accessoryFunctions.accessoryFunctions import SetupLogging
from argparse import ArgumentParser
from glob import glob
import pkg_resources
import logging
import pandas
import os
__author__ = 'adamkoziol'


class VSNPCompare(object):

    def main(self):
        self.parse_updated_tables()
        self.parse_legacy_tables()
        self.compare_outputs()

    def parse_updated_tables(self):
        self.updated_tables = glob(os.path.join(self.new_path, '*.xlsx'))
        for table in self.updated_tables:
            species = os.path.basename(table).split('_')[0]
            group = os.path.basename(table).split('_')[1]
            # print(species, group)
            if species not in self.updated_snp_dict:
                self.updated_snp_dict[species] = dict()
            if group not in self.updated_snp_dict[species]:
                self.updated_snp_dict[species][group] = dict()
            # Use pandas to read in the excel file, and subsequently convert the pandas data frame to a dictionary
            # (.to_dict())
            dictionary = pandas.read_excel(table).to_dict()
            strain_dict = dict()
            # Iterate through the dictionary - each header from the excel file
            for header in dictionary:
                ref_chrom = str()
                pos = int()
                # Sample is the primary key, and value is the value of the cell for that primary key, header combination
                for sample, value in dictionary[header].items():
                    if header == 'Strain':
                        if sample != 0:
                            strain_dict[sample] = value
                            if value not in self.updated_snp_dict[species][group] and value != 'Annotation':
                                self.updated_snp_dict[species][group][value] = dict()
                    else:

                        if sample == 0:
                            # ref_chrom, pos = value.split('_')
                            ref_chrom = '_'.join(value.split('_')[:-1])
                            pos = int(value.split('_')[-1])
                        else:
                            if strain_dict[sample] != 'Annotation':
                                if ref_chrom not in self.updated_snp_dict[species][group][strain_dict[sample]]:
                                    self.updated_snp_dict[species][group][strain_dict[sample]][ref_chrom] = dict()
                                self.updated_snp_dict[species][group][strain_dict[sample]][ref_chrom][pos] = value
        # for species, group_dict in self.updated_snp_dict.items():
        #     # print(species, self.updated_snp_dict[species])
        #     for group, strain_dict in group_dict.items():
        #         for strain, ref_dict in strain_dict.items():
        #             for ref_chrom, pos_dict in ref_dict.items():
        #                 # legacy
        #                 for pos, seq in pos_dict.items():
        #                     print(species, group, strain, ref_chrom, pos, seq)
        # quit()

    def parse_legacy_tables(self):
        folders = list()
        for species in self.updated_snp_dict:
            if species == 'af':
                glob_species = 'Mbovis'
            else:
                glob_species = species
            folders = glob(os.path.join(self.legacy_path, '*{species}*'.format(species=glob_species)))
            if folders:
                self.species = species
        if os.path.isdir(os.path.join(self.legacy_path, 'All_VCFs')):
            folders.append(os.path.join(self.legacy_path, 'All_VCFs'))

        for folder in sorted(folders):
            legacy_table = glob(os.path.join(folder, '*-organized-table.xlsx'))[0]
            group = os.path.basename(folder).split('_VCFs')[0]
            if self.species not in self.legacy_snp_dict:
                self.legacy_snp_dict[self.species] = dict()
            if group not in self.legacy_snp_dict[self.species]:
                self.legacy_snp_dict[self.species][group] = dict()
            # Use pandas to read in the excel file, and subsequently convert the pandas data frame to a dictionary
            # (.to_dict())
            dictionary = pandas.read_excel(legacy_table).to_dict()
            strain_dict = dict()
            # Iterate through the dictionary - each header from the excel file
            for header in dictionary:
                # ref_chrom = str()
                # pos = int()
                # Sample is the primary key, and value is the value of the cell for that primary key + header combination
                for sample, value in dictionary[header].items():
                    # print('header:', header, 'sample:', sample, 'value:', value)
                    if header == 'reference_pos':
                        if value not in ['reference_call', 'map-quality', 'annotations']:
                            strain_dict[sample] = value.split('_zc')[0]
                            # print('header:', header, 'sample:', sample, 'value:', strain_dict[sample])
                            if strain_dict[sample] not in self.legacy_snp_dict[self.species][group]:
                                self.legacy_snp_dict[self.species][group][strain_dict[sample]] = dict()
                    else:
                        if sample in strain_dict:
                            ref_chrom = ''.join(header.split('-')[:-1])
                            pos = int(header.split('-')[-1])
                            # , strain_dict[value], 'ref:', ref_chrom, 'pos:', pos
                            # print('header:', header, 'sample:', sample, 'value:', value, 'strain:', strain_dict[sample], 'ref:', ref_chrom, 'pos:', pos)
                            if ref_chrom not in self.legacy_snp_dict[self.species][group][strain_dict[sample]]:
                                self.legacy_snp_dict[self.species][group][strain_dict[sample]][ref_chrom] = dict()
                            self.legacy_snp_dict[self.species][group][strain_dict[sample]][ref_chrom][pos] = value

    def compare_outputs(self):
        for species, group_dict in self.legacy_snp_dict.items():
            if species not in self.discrepancy_dict:
                self.discrepancy_dict[species] = dict()
            # print(species, self.updated_snp_dict[species])
            for group, strain_dict in group_dict.items():
                if group not in self.discrepancy_dict[species]:
                    self.discrepancy_dict[species][group] = dict()
                for strain, ref_dict in strain_dict.items():
                    for ref_chrom, pos_dict in ref_dict.items():
                        if ref_chrom not in self.discrepancy_dict[species][group]:
                            self.discrepancy_dict[species][group][ref_chrom] = dict()
                        # legacy
                        for pos, seq in pos_dict.items():
                            try:
                                self.updated_snp_dict[self.species][group][strain][ref_chrom][pos]
                            except KeyError:
                                # print('species {species} group {group} strain {strain} ref_chrom {ref_chrom} pos {pos} '
                                #       'missing in update'.format(species=species,
                                #                                  group=group,
                                #                                  strain=strain,
                                #                                  ref_chrom=ref_chrom,
                                #                                  pos=pos))

                                if 'update' not in self.discrepancy_dict[species][group][ref_chrom]:
                                    self.discrepancy_dict[species][group][ref_chrom]['update'] = set()
                                self.discrepancy_dict[species][group][ref_chrom]['update'].add(pos)
                        for pos, seq in self.updated_snp_dict[self.species][group][strain][ref_chrom].items():
                            try:
                                pos_dict[pos]
                            except KeyError:
                                if 'legacy' not in self.discrepancy_dict[species][group][ref_chrom]:
                                    self.discrepancy_dict[species][group][ref_chrom]['legacy'] = set()
                                self.discrepancy_dict[species][group][ref_chrom]['legacy'].add(pos)
                                # print('species {species} group {group} strain {strain} ref_chrom {ref_chrom} pos {pos} '
                                #       'missing in legacy'.format(species=species,
                                #                                  group=group,
                                #                                  strain=strain,
                                #                                  ref_chrom=ref_chrom,
                                #                                  pos=pos))
        for species, group_dict in self.discrepancy_dict.items():
            for group, ref_dict in group_dict.items():
                for ref_chrom, type_dict in ref_dict.items():
                    for analysis_type, pos_set in type_dict.items():
                        print(species, group, ref_chrom, analysis_type, sorted(pos_set))

    def __init__(self, new_path, legacy_path, debug):
        # Determine the path in which the vSNP 2.0 files are located. Allow for ~ expansion
        if new_path.startswith('~'):
            self.new_path = os.path.abspath(os.path.expanduser(os.path.join(new_path)))
        else:
            self.new_path = os.path.abspath(os.path.join(new_path))
        self.debug = debug
        SetupLogging(self.debug)
        # Ensure that the path exists
        assert os.path.isdir(self.new_path), 'Invalid path specified: {path}'.format(path=self.new_path)
        logging.debug('Supplied sequence path: \n{path}'.format(path=self.new_path))
        # Initialise class variables
        self.report_path = os.path.join(self.new_path, 'reports')
        if legacy_path.startswith('~'):
            self.legacy_path = os.path.abspath(os.path.expanduser(os.path.join(legacy_path)))
        else:
            self.legacy_path = os.path.abspath(os.path.join(legacy_path))
        # Ensure that the path exists
        assert os.path.isdir(self.legacy_path), 'Invalid path specified: {path}'.format(path=self.legacy_path)
        logging.debug('Supplied vSNP legacy path: \n{path}'.format(path=self.legacy_path))
        self.updated_tables = list()
        self.updated_snp_dict = dict()
        self.species = str()
        self.legacy_snp_dict = dict()
        self.discrepancy_dict = dict()


def get_version():
    try:
        version = 'vSNP comparer {version}'.format(version=pkg_resources.get_distribution('vsnpdev').version)
    except pkg_resources.DistributionNotFound:
        version = 'vSNP comparer (Unknown version)'
    return version


def main():
    # Parser for arguments
    parser = ArgumentParser(description='Compares vSNP 2.0 outputs to legacy outputs')
    parser.add_argument('-v', '--version',
                        action='version',
                        version=get_version())
    parser.add_argument('-u', '--updated_path',
                        required=True,
                        help='Path to folder containing vSNP 2.0 summary tables')
    parser.add_argument('-l', '--legacy_path',
                        required=True,
                        help='Path to folder containing legacy vSNP outputs')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Enable debugging-level messages to be printed to the terminal')
    args = parser.parse_args()
    comparer = VSNPCompare(new_path=args.updated_path,
                           legacy_path=args.legacy_path,
                           debug=args.debug)
    comparer.main()


if __name__ == '__main__':
    main()
