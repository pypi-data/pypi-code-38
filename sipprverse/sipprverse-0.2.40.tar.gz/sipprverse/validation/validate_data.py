#!/usr/bin/env python
from olctools.accessoryFunctions.accessoryFunctions import SetupLogging
from validator_helper import validate
import argparse
import logging
import os


def check_all_reports_created(test_genesippr_folder):
    # Check that the test run created all the csv files we expected it to. If not, no sense in running other checks.
    all_files_present = True
    files_to_check_for = [os.path.join(test_genesippr_folder, 'reports', 'genesippr.csv'),
                          os.path.join(test_genesippr_folder, 'reports', 'mash.csv'),
                          os.path.join(test_genesippr_folder, 'reports', 'sixteens_full.csv'),
                          os.path.join(test_genesippr_folder, 'reports', 'resfinder.csv'),
                          os.path.join(test_genesippr_folder, 'reports', 'serosippr.csv'),
                          os.path.join(test_genesippr_folder, 'reports', 'virulence.csv'),
                          os.path.join(test_genesippr_folder, 'reports', 'mlst.csv'),
                          os.path.join(test_genesippr_folder, 'reports', 'GDCS.csv'),
                          os.path.join(test_genesippr_folder, 'reports', 'rmlst.csv')]
    for csv_file in files_to_check_for:
        if not os.path.isfile(csv_file):
            logging.warning('Could not find {} - GeneSippr must not have run successfully!'.format(csv_file))
            all_files_present = False
    return all_files_present


def run_all_validation_checks(validator_object):
    validation_checks = [validator_object.same_columns_in_ref_and_test(),
                         validator_object.all_test_columns_in_ref_and_test(),
                         validator_object.check_samples_present(),
                         validator_object.check_columns_match()]
    if False in validation_checks:
        return False
    else:
        return True


def validate_resfinder(test_resfinder_csv, ref_resfinder_csv):
    column_list = validate.find_all_columns(csv_file=ref_resfinder_csv,
                                            columns_to_exclude=['Strain'])

    validator = validate.Validator(reference_csv=ref_resfinder_csv,
                                   test_csv=test_resfinder_csv,
                                   column_list=column_list,
                                   identifying_column='Strain')
    checks_pass = validator.check_resfinderesque_output()
    if checks_pass is False:
        logging.warning('Resfinder validation failed.')
    return checks_pass


def validate_serosippr(test_serosippr_csv, ref_serosippr_csv):
    column_list = list()
    column_list.append(validate.Column(name='Serotype'))
    validator = validate.Validator(reference_csv=ref_serosippr_csv,
                                   test_csv=test_serosippr_csv,
                                   column_list=column_list,
                                   identifying_column='Strain')
    checks_pass = run_all_validation_checks(validator)
    if checks_pass is False:
        logging.warning('SeroSippr validation failed.')
    return checks_pass


def validate_virulence(test_virulence_csv, ref_virulence_csv):
    column_list = validate.find_all_columns(csv_file=ref_virulence_csv,
                                            columns_to_exclude=['Strain'])

    validator = validate.Validator(reference_csv=ref_virulence_csv,
                                   test_csv=test_virulence_csv,
                                   column_list=column_list,
                                   identifying_column='Strain')
    checks_pass = validator.check_resfinderesque_output()
    if checks_pass is False:
        logging.warning('Resfinder validation failed.')
    return checks_pass


def validate_mlst(test_mlst_csv, ref_mlst_csv):
    column_list = list()
    column_list.append(validate.Column(name='Genus'))
    column_list.append(validate.Column(name='SequenceType'))
    column_list.append(validate.Column(name='Matches'))

    validator = validate.Validator(reference_csv=ref_mlst_csv,
                                   test_csv=test_mlst_csv,
                                   column_list=column_list,
                                   identifying_column='Strain')
    validator.remove_duplicate_header_rows()
    checks_pass = validator.check_resfinderesque_output()
    if checks_pass is False:
        logging.warning('MLST validation failed.')
    return checks_pass


def validate_gdcs(test_gdcs_csv, ref_gdcs_csv):
    column_list = list()
    column_list.append(validate.Column(name='Genus'))
    column_list.append(validate.Column(name='Matches'))
    column_list.append(validate.Column(name='Pass/Fail'))
    validator = validate.Validator(reference_csv=ref_gdcs_csv,
                                   test_csv=test_gdcs_csv,
                                   column_list=column_list,
                                   identifying_column='Strain')
    checks_pass = run_all_validation_checks(validator)
    if checks_pass is False:
        logging.warning('GDCS validation failed.')
    return checks_pass


def validate_rmlst(test_rmlst_csv, ref_rmlst_csv):
    column_list = list()
    column_list.append(validate.Column(name='Genus'))
    column_list.append(validate.Column(name='SequenceType'))
    column_list.append(validate.Column(name='Matches'))

    validator = validate.Validator(reference_csv=ref_rmlst_csv,
                                   test_csv=test_rmlst_csv,
                                   column_list=column_list,
                                   identifying_column='Strain')
    validator.remove_duplicate_header_rows()
    checks_pass = validator.check_resfinderesque_output()
    if checks_pass is False:
        logging.warning('rMLST validation failed.')
    return checks_pass


def validate_sixteens(test_genesippr_sixteens_csv, ref_genesippr_sixteens_csv):
    column_list = list()
    column_list.append(validate.Column(name='Gene'))
    column_list.append(validate.Column(name='Genus'))
    column_list.append(validate.Column(name='PercentIdentity', column_type='Range', acceptable_range=1.5))
    column_list.append(validate.Column(name='FoldCoverage', column_type='Range', acceptable_range=20))

    validator = validate.Validator(reference_csv=ref_genesippr_sixteens_csv,
                                   test_csv=test_genesippr_sixteens_csv,
                                   column_list=column_list,
                                   identifying_column='Strain')
    checks_pass = run_all_validation_checks(validator)
    if checks_pass is False:
        logging.warning('SixteenS validation failed.')
    return checks_pass


def validate_mash(test_mash_csv, ref_mash_csv):
    column_list = list()
    column_list.append(validate.Column(name='ReferenceGenus'))
    column_list.append(validate.Column(name='ReferenceFile'))
    column_list.append(validate.Column(name='Pvalue', column_type='Range', acceptable_range=0.03))

    validator = validate.Validator(reference_csv=ref_mash_csv,
                                   test_csv=test_mash_csv,
                                   column_list=column_list,
                                   identifying_column='Strain')
    checks_pass = run_all_validation_checks(validator)
    if checks_pass is False:
        logging.warning('MASH validation failed.')
    return checks_pass


def validate_genesippr(test_genesippr_csv, ref_genesippr_csv):
    column_list = validate.percent_depth_columns(csv_file=ref_genesippr_csv,
                                                 columns_to_exclude=['Strain', 'Genus'],
                                                 percent_range=2,
                                                 depth_range=3)
    column_list.append(validate.Column(name='Genus'))

    validator = validate.Validator(reference_csv=ref_genesippr_csv,
                                   test_csv=test_genesippr_csv,
                                   column_list=column_list,
                                   identifying_column='Strain')
    checks_pass = run_all_validation_checks(validator)
    if checks_pass is False:
        logging.warning('GeneSippr target detection validation failed.')
    return checks_pass


def main(reference_genesippr_folder, test_genesippr_folder):
    check_list = list()
    reports_created = check_all_reports_created(test_genesippr_folder)
    if reports_created is False:
        logging.warning('Not all reports were created. GeneSippr validation not successful.')
        return
    logging.info('Checking 16S...')
    check_list.append(validate_sixteens(test_genesippr_sixteens_csv=os.path.join(test_genesippr_folder, 'reports', 'sixteens_full.csv'),
                                        ref_genesippr_sixteens_csv=os.path.join(reference_genesippr_folder, 'reports', 'sixteens_full.csv')))
    logging.info('Checking GDCS...')
    check_list.append(validate_gdcs(test_gdcs_csv=os.path.join(test_genesippr_folder, 'reports', 'GDCS.csv'),
                                    ref_gdcs_csv=os.path.join(reference_genesippr_folder, 'reports', 'GDCS.csv')))
    logging.info('Checking GeneSippr Target detection...')
    check_list.append(validate_genesippr(test_genesippr_csv=os.path.join(test_genesippr_folder, 'reports', 'genesippr.csv'),
                                         ref_genesippr_csv=os.path.join(reference_genesippr_folder, 'reports', 'genesippr.csv')))
    logging.info('Checking Mash...')
    check_list.append(validate_mash(test_mash_csv=os.path.join(test_genesippr_folder, 'reports', 'mash.csv'),
                                    ref_mash_csv=os.path.join(reference_genesippr_folder, 'reports', 'mash.csv')))
    logging.info('Checking MLST...')
    check_list.append(validate_mlst(test_mlst_csv=os.path.join(test_genesippr_folder, 'reports', 'mlst.csv'),
                                    ref_mlst_csv=os.path.join(reference_genesippr_folder, 'reports', 'mlst.csv')))
    logging.info('Checking rMLST...')
    check_list.append(validate_rmlst(test_rmlst_csv=os.path.join(test_genesippr_folder, 'reports', 'rmlst.csv'),
                                     ref_rmlst_csv=os.path.join(reference_genesippr_folder, 'reports', 'rmlst.csv')))
    logging.info('Checking SeroSippr...')
    check_list.append(validate_serosippr(test_serosippr_csv=os.path.join(test_genesippr_folder, 'reports', 'serosippr.csv'),
                                         ref_serosippr_csv=os.path.join(reference_genesippr_folder, 'reports', 'serosippr.csv')))
    logging.info('Checking Virulence...')
    check_list.append(validate_virulence(test_virulence_csv=os.path.join(test_genesippr_folder, 'reports', 'virulence.csv'),
                                         ref_virulence_csv=os.path.join(reference_genesippr_folder, 'reports', 'virulence.csv')))
    logging.info('Checking ResFinder...')
    check_list.append(validate_resfinder(test_resfinder_csv=os.path.join(test_genesippr_folder, 'reports', 'resfinder.csv'),
                                         ref_resfinder_csv=os.path.join(reference_genesippr_folder, 'reports', 'resfinder.csv')))
    if False in check_list:
        logging.warning('GeneSippr Validation unsuccessful :(')
    else:
        logging.info('GeneSippr Validation successful! :D')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script validates that GeneSippr is working properly, and should '
                                                 'be run whenever GeneSippr or it\'s databases are updated. To use, '
                                                 'run sippr.py with the -F flag, and use the output folder (what you '
                                                 'specified with -o) as -t for this script.')
    parser.add_argument('-r', '--reference_genesippr_folder',
                        required=True,
                        help='Path to reference genesippr result folder.')
    parser.add_argument('-t', '--test_genesippr_folder',
                        required=True,
                        help='Path to test genesippr result folder.')
    args = parser.parse_args()

    SetupLogging()

    main(args.reference_genesippr_folder, args.test_genesippr_folder)
