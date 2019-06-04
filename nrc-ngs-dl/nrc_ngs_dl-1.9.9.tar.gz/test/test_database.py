import os
import argparse
from ConfigParser import SafeConfigParser
import sys
import logging
#sys.path.append('/home/zhengc/NRC-LIMS-dataDownloader')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from nrc_ngs_dl.lims_database import LimsDatabase
from nrc_ngs_dl.web_parser import WebParser

def set_up_logging():
    logger = logging.getLogger('nrc_ngs_dl')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('information.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info('***********test_database**************')


def parse_input_args(argv):
    input_parser = argparse.ArgumentParser()
    input_parser.add_argument('-c', dest='config_file')
    args = input_parser.parse_args(argv)
    return args

def main():
    # get settings from cinfig.ini.sample file
    set_up_logging()
    logger= logging.getLogger('nrc_ngs_dl.lims_downloader')
    config_parser = SafeConfigParser()
    try:
        args = parse_input_args(sys.argv[1:])
    except:
        logger.info('Wrong command line args')
        sys.exit(1)
        
    if not args.config_file:
        logger.info('Missing the configuration file')
        logger.info('Usage: python lims_downloader.py /path/to/configuation.sample')
        sys.exit(1)
    
    config_file = args.config_file
    try: 
        with open(config_file) as f:
            config_parser.read(config_file)
    except IOError:
        logger.info('Cannot open file: config.ini.sample')
        sys.exit(1)
    try:   
        logger.info('Get settings ...')
        DB_NAME = config_parser.get('sqlite_database', 'name')
        USERNAME = config_parser.get('nrc_lims','username')
        PASSWORD = config_parser.get('nrc_lims','password')
        LOGIN_URL = config_parser.get('nrc_lims','login_url')
        RUNLIST_URL = config_parser.get('nrc_lims','runlist_url')
        DESTINATION_FOLDER = config_parser.get('output','path')
        TABLE_RUN_LIST = config_parser.get('run_list_setting','table')
        COLUMN_RUN_LINK = config_parser.get('run_list_setting','column_link')
        COLUMN_RUN_STATUS = config_parser.get('run_list_setting','column_status')
        TABLE_FILE_LIST = config_parser.get('file_list_setting','table')
        COLUMN_FILE_LINK = config_parser.get('file_list_setting','column_link')
        COLUMN_LANE = config_parser.get('file_list_setting','column_lane')
        
    except:
        logger.info('Cannot get the configuration settings' )
        sys.exit(1)
      
    if os.path.exists(DESTINATION_FOLDER) == False:
        logger.info('DESTINATION_FOLDER not exist; do not have permission to access the folder')
        sys.exit(1)
    #connect to database if the database exist
    #otherwise create tables for this database
    if os.path.isfile(DB_NAME):
        os.remove(DB_NAME)
        
    lims_database = LimsDatabase(DB_NAME)
    if lims_database is None:
        logger.info('Cannot access the database')
        sys.exit(1)
    
    #login to LIMS webpage
    try: 
        logger.info('Logging into ...')  
        web_parser = WebParser(LOGIN_URL,RUNLIST_URL,USERNAME,PASSWORD)
    except:
        logger.info('Cannot access the web page')
        sys.exit(1)
    #get a list of all the completed sequence runs
    #information for each run : url_for_the_run, run_name, plate_name, 
    #Plateform, Operator, Creation Date, Description, status
    try:
        logger.info('Getting run list ...') 
        run_list = web_parser.get_runlist(TABLE_RUN_LIST, COLUMN_RUN_LINK, COLUMN_RUN_STATUS)
    except:
        logger.info('Cannot get the list of sequence runs')
        sys.exit(1)
    
    #for each sequence run in the list,
    #1. check if it is a new data or re-processed data
    #2. in the case of new data: download the data, insert the information of the data into database tables
    #3. in the case of re-processed data: 
    
    for a_run in run_list:
        run_url = a_run
        run_info = web_parser.get_runinfo(run_url)
        lane_info = web_parser.get_laneinfo(run_url,TABLE_FILE_LIST, COLUMN_LANE,COLUMN_FILE_LINK)
        for a_lane in lane_info:
            case = lims_database.check_new_run(run_info,a_lane)
            if case ==3:
                logger.info('Deleting records in database for re-processed data (run_name %s, lane_index %s)' % (run_info['run_name'],a_lane[0]))
                lims_database.delete_old_run(run_info, a_lane)
            
            if case != 1:
                logger.info('downloading new/re-processed data (run_name %s, lane_index %s)' % (run_info['run_name'],a_lane[0]))
                file_info = web_parser.get_fileinfo(run_url,a_lane,TABLE_FILE_LIST)
                rowid = lims_database.insert_run_info(run_info)
                lims_database.insert_lane_info(rowid,run_url,a_lane)
                lims_database.insert_file_info(rowid,file_info)
        #lims_database.check_dp_table()
        #lims_database.check_df_table() 

    lims_database.disconnect()
    
    
if __name__ == '__main__':
    main()
