import numpy as np
import xml.etree.ElementTree as ET
import gzip
import pandas as pd
import os
import gavia

def loadlog(projectdir):
    '''
    Load the gps log file for the specified project, given by the projectdir
    parameter

    Parameters
    ----------
    projectdir : string
        path to the gavia project

    Returns 
    -------
    Pandas DataFrame containing gps logs
    '''
    PROCESS = True
    ROOT    = False
    # check for processed log file in directory 
    dirfiles        = os.listdir(projectdir)

    # projectdir may not be given as the root folder
    if 'log_processed' in dirfiles:
        if 'gps.csv' in os.listdir(os.path.join(projectdir,'log_processed')):
            PROCESS = False
    elif 'files'in dirfiles: 
        ROOT = True
        dirfiles        = os.listdir(os.path.join(projectdir,'files'))
        # check if folders/files are contained within a 'files' directory
        if 'log_processed' in dirfiles:
            if 'gps.csv' in os.listdir(os.path.join(projectdir,'files','log_processed')):
                PROCESS = False

    if ROOT:
        # change the projectdir to the files\ directory
        projectdir = os.path.join(projectdir,'files')

    if PROCESS:
        print('Processing gps logs...')
        logdir      = os.path.join(projectdir,'log')
        loglist     = gavia.log.getlogs(logdir,'gps')
        if len(loglist) == 0: raise ValueError('no gps logs found in project')

        nlogs       = len(loglist)
        # combine log DataFrame
        df          = pd.DataFrame()
        for l in range(nlogs):
    
            # uncompress file and open 
            logfile     = os.path.join(logdir,loglist[l])
            xml_data    = gzip.open(logfile, 'rb').read()
            # create log class
            logclass    = gavia.log.GPS()
            try:
                root        = ET.XML(xml_data)
            except:
                print('cannot load:', logfile)
                continue
            # number of entries in xml
            N           = len(list(root))
            rootlist    = list(root)

            for n in range(N):
                parsed = logclass.init_dict()
                # children - [timestamp, time] 
                keys        = root[n].keys() 
                
                elements    = len(list(rootlist[n]))
                for el in range(elements):
                    parsed[rootlist[n][el].tag] = list(rootlist[n])[el].text 

                # split date and time 
                year,month,day,hour,minute,second,millisecond = gavia.log.parsedatetime(root[n].attrib.get(keys[1]))
                # split capture time into epoch and microseconds 
                timestamp_epoch,timestamp_micro = root[n].attrib.get(keys[0]).split('.')

                # add row 
                logclass.addrow(
                            timestamp=root[n].attrib.get(keys[0]),
                            timestamp_epoch=timestamp_epoch,
                            timestamp_nano=timestamp_micro,
                            time=root[n].attrib.get(keys[1]),
                            year=year,
                            month=month,
                            day=day,
                            hour=hour,
                            minute=minute,
                            second=second,
                            millisecond=millisecond,

                            UTC=parsed['UTC'],
                            cogt=parsed['cogt'],
                            diff_age=parsed['diff-age'],
                            hdop=parsed['hdop'],
                            lat=parsed['lat'],
                            lat_dev=parsed['lat-dev'],
                            lon=parsed['lon'],
                            lon_dev=parsed['lon-dev'],
                            messages_received=parsed['messages-received'],
                            quality=parsed['quality'],
                            raw_logged_bytes=parsed['raw-logged-bytes'],
                            received_telnet_bytes=parsed['received-telnet-bytes'],
                            sats=parsed['sats'],
                            sent_corr_bytes=parsed['sent-corr-bytes'],
                            sent_corr_packets=parsed['sent-corr-packets'],
                            sent_telnet_bytes=parsed['sent-telnet-bytes'],
                            sogk=parsed['sogk'],
                            sogm=parsed['sogm'],
                            stnRef=parsed['stnRef'],
                            time_since_sent=parsed['time-since-sent']
                )
            df              = pd.concat([df,logclass.df],ignore_index=True)
        
        if not os.path.exists(os.path.join(projectdir,'log_processed')):os.makedirs(os.path.join(projectdir,'log_processed'))
        df.to_csv(os.path.join(projectdir,'log_processed','gps.csv'))
        print('Complete')
        
    else:
        df              = pd.read_csv(os.path.join(projectdir,'log_processed','gps.csv'))
        del df['Unnamed: 0']

    return df