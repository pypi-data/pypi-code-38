
import numpy as np
import xml.etree.ElementTree as ET
import gzip
import pandas as pd
import os
import gavia

def loadlog(projectdir):
    '''
    Load the navigator log file for the specified project, given by the projectdir
    parameter

    Parameters
    ----------
    projectdir : string
        path to the gavia project

    Returns 
    -------
    Pandas DataFrame containing navigator logs
    '''
    PROCESS = True
    ROOT    = False
    # check for processed log file in directory 
    dirfiles        = os.listdir(projectdir)

    # projectdir may not be given as the root folder
    if 'log_processed' in dirfiles:
        if 'navigator.csv' in os.listdir(os.path.join(projectdir,'log_processed')):
            PROCESS = False
    elif 'files'in dirfiles: 
        ROOT = True
        dirfiles        = os.listdir(os.path.join(projectdir,'files'))
        # check if folders/files are contained within a 'files' directory
        if 'log_processed' in dirfiles:
            if 'navigator.csv' in os.listdir(os.path.join(projectdir,'files','log_processed')):
                PROCESS = False

    if ROOT:
        # change the projectdir to the files\ directory
        projectdir = os.path.join(projectdir,'files')

    if PROCESS:
        print('Processing navigator logs...')
        logdir      = os.path.join(projectdir,'log')
        loglist     = gavia.log.getlogs(logdir,'navigator')
        if len(loglist) == 0: raise ValueError('no navigator logs found in project')

        nlogs       = len(loglist)
        # combine log DataFrame
        df          = pd.DataFrame()
        for l in range(nlogs):
    
            # uncompress file and open 
            logfile     = os.path.join(logdir,loglist[l])
            xml_data    = gzip.open(logfile, 'rb').read()
            # create log class
            logclass    = gavia.log.Navigator()
            try:
                root        = ET.XML(xml_data)
            except:
                print('cannot load:', logfile)
                continue
            # number of entries in xml
            N           = len(list(root))
            rootlist    = list(root)
            for n in range(N):
                maindict        = logclass.init_dict()
                DRdict          = logclass.init_deadreckoning_dict()
                orientdict      = logclass.init_orientation_dict()
                posdict         = logclass.init_position_dict()
                vardict         = logclass.init_variance_dict()
                veldict         = logclass.init_velocity_dict()
                # children - [timestamp, time] 
                keys        = root[n].keys() 
                elements    = list(rootlist[n])
                nelements   = len(elements)

                # print(nelements)
                # print(elements)
                for el in range(nelements):
                    if rootlist[n][el].tag in [     'dead-reckoning-orientation', 
                                                    'dead-reckoning-position',
                                                    'dead-reckoning-variance',
                                                    'dead-reckoning-velocity']:
                        for dr in list(rootlist[n][el]):
                            DRdict[dr.tag] = dr.text
                    elif rootlist[n][el].tag == 'orientation':
                        for orient in list(rootlist[n][el]):
                            orientdict[orient.tag] = orient.text
                    elif rootlist[n][el].tag == 'position':
                        for pos in list(rootlist[n][el]):
                            posdict[pos.tag] = pos.text
                    elif rootlist[n][el].tag == 'variance':
                        for var in list(rootlist[n][el]):
                            vardict[var.tag] = var.text
                    elif rootlist[n][el].tag == 'velocity':
                        for vel in list(rootlist[n][el]):
                            veldict[var.tag] = vel.text
                    else:
                        maindict[rootlist[n][el].tag] = list(rootlist[n])[el].text
                    
                # split date and time 
                year,month,day,hour,minute,second,millisecond = gavia.log.parsedatetime(root[n].attrib.get(keys[1]))
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

                            deadreckoning_heading=DRdict['heading'],
                            deadreckoning_pitch=DRdict['pitch'],
                            deadreckoning_roll=DRdict['roll'],
                            deadreckoning_heave=DRdict['heave'],
                            deadreckoning_surge=DRdict['surge'],
                            deadreckoning_sway=DRdict['sway'],
                            deadreckoning_lat=DRdict['lat'],
                            deadreckoning_lon=DRdict['lon'],
                            deadreckoning_var_lat=DRdict['var_lat'],
                            deadreckoning_var_lat_lon=DRdict['var_lat_lon'],
                            deadreckoning_var_lon=DRdict['var_lon'],

                            orientation_heading=orientdict['heading'],
                            orientation_pitch=orientdict['pitch'],
                            orientation_roll=orientdict['roll'],

                            position_depth=posdict['depth'],
                            position_lat=posdict['lat'],
                            position_lon=posdict['lon'],    

                            variance_var_lat=vardict['var_lat'],
                            variance_var_lat_lon=vardict['var_lat_lon'],
                            variance_var_lon=vardict['var_lon'],

                            velocity_heave=veldict['heave'],
                            velocity_surge=veldict['surge'],
                            velocity_sway=veldict['sway'],

                            build_number=maindict['build-number'],
                            build_tag=maindict['build-tag'],
                            calculate_magnetic_deviation=maindict['calculate-magnetic-deviation'],
                            magnetic_deviation=maindict['magnetic-deviation'],
                            pressure_timeout=maindict['pressure-timeout'],
                            compass_timeout=maindict['compass-timeout'],
                            dead_reckoning_sog_timeout=maindict['dead-reckoning-sog-timeout'],
                            dvl_timeout=maindict['dvl-timeout'],
                            gps_timeout=maindict['gps-timeout'],
                            gps_validation_enabled=maindict['gps-validation-enabled'],
                            veto_use_water_velocity=maindict['veto-use-water-velocity'],
                            station_keeping_enabled=maindict['station-keeping-enabled'],
                            sound_velocity_timeout=maindict['sound-velocity-timeout'],
                            temperature_timeout=maindict['temperature-timeout'],
                            seanav_timeout=maindict['seanav-timeout'],
                            # use_presssure=maindict['use-presssure'],
                            max_allowed_variance=maindict['max-allowed-variance'],
                            variance_exceeded_warning_level=maindict['variance-exceeded-warning-level'],
                            lat_lon_precision=maindict['lat-lon-precision'],
                            max_dead_reckoning_distance=maindict['max-dead-reckoning-distance'],
                            dead_reckoning_distance=maindict['dead-reckoning-distance'],
                            pressure_depth_conversion=maindict['pressure-depth-conversion'],
                            average_water_density=maindict['average-water-density'],
                            use_water_velocity=maindict['use-water-velocity'],
                            sound_velocity=maindict['sound-velocity'],
                            temperature=maindict['temperature'],
                            density_abort_limit=maindict['density-abort-limit'],
                            gps_variance=maindict['gps-variance'],
                            lbl_variance=maindict['lbl-variance'],
                            revolutions_bias=maindict['revolutions-bias'],
                            revolutions_scale=maindict['revolutions-scale'],
                            dvl_bias=maindict['dvl-bias'],
                            dvl_scale=maindict['dvl-scale'],
                            gyro_bias=maindict['gyro-bias'],
                            control_rate=maindict['control-rate'],
                            motor_default=maindict['motor-default'],
                            stationary_radius=maindict['stationary-radius'],
                            stationary_p=maindict['stationary-p'],
                            stationary_idle=maindict['stationary-idle'],
                            stationary_depth_timeout=maindict['stationary-depth-timeout'],
                            estimate_speed=maindict['estimate-speed'],
                            observe_timer_on=maindict['observe-timer-on'],
                            predict_timer_on=maindict['predict-timer-on'],
                            binary_log=maindict['binary-log'],
                            broadcast_interface=maindict['broadcast-interface'],
                            broadcast_enable=maindict['broadcast-enable'],
                            broadcast_frequency=maindict['broadcast-frequency'],
                            broadcast_navigation_message=maindict['broadcast-navigation-message'],
                            broadcast_depth_message=maindict['broadcast-depth-message'],
                            broadcast_sound_velocity_message=maindict['broadcast-sound-velocity-message'],
                            idle_status=maindict['idle-status'],
                            maxWarningLevel=maindict['maxWarningLevel'],
                            pilot_status=maindict['pilot-status'],
                            valid=maindict['valid'],
                            zero_altitude=maindict['zero-altitude'],
                            altitude=maindict['altitude'])

            df              = pd.concat([df,logclass.df],ignore_index=True)

        if not os.path.exists(os.path.join(projectdir,'log_processed')):os.makedirs(os.path.join(projectdir,'log_processed'))
        df.to_csv(os.path.join(projectdir,'log_processed','navigator.csv'))
        print('Complete')
        
    else:
        df              = pd.read_csv(os.path.join(projectdir,'log_processed','navigator.csv'))
        del df['Unnamed: 0']

    return df