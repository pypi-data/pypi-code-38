import os
import argparse
from ConfigParser import SafeConfigParser
import sys
import logging
#sys.path.append('/home/zhengc/NRC-LIMS-dataDownloader')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from nrc_ngs_dl.lims_database import LimsDatabase
from nrc_ngs_dl.web_parser import WebParser


def parse_input_args(argv):
    input_parser = argparse.ArgumentParser()
    input_parser.add_argument('-c', dest='config_file')
    args = input_parser.parse_args(argv)
    return args

def main():
    # get settings from cinfig.ini.sample file
    config_parser = SafeConfigParser()
    try:
        args = parse_input_args(sys.argv[1:])
    except:
        sys.exit(1)
        
    if not args.config_file:
        sys.exit(1)
    
    config_file = args.config_file
    try: 
        with open(config_file) as f:
            config_parser.read(config_file)
    except IOError:
        sys.exit(1)
    try:   
        DB_NAME = config_parser.get('sqlite_database', 'name')
        
    except:
        sys.exit(1)
         
    lims_database = LimsDatabase(DB_NAME)
    if lims_database is None:
        sys.exit(1)
        
    lims_database.modify_http_header(9, '1876989409')
    #lims_database.delete_a_run(2)
    #login to LIMS webpage
    lims_database.disconnect()
    
    
if __name__ == '__main__':
    main()
    
    
