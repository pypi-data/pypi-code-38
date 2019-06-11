import os
import pandas as pd
import gavia.time as gavtime
from gavia.version import __version__
import sys 

def getlogs(dir,logtype):
    '''
        get list of logs for camera 
    '''
    files = []
    loglist = os.listdir(dir)
    for log in loglist: 
        if logtype in log:
            files.append(log)

    # for gps, remove gpsfix 
    if logtype =='gps':
        delfiles = []
        for i in range(len(files)):
            if 'gpsfix' in files[i]: delfiles.append(files[i])
        for f in delfiles:
            del files[files.index(f)]  
    return sorted(files)


def parsedatetime(dateNtime):
    '''
        example: 2019 04 16 10:59:20.619
    '''
    # year,month,day,time         = dateNtime.split(' ') # this doesn't always work
    # hour,minute,secondsNmilli   = time.split(':')
    # second,millisecond          = secondsNmilli.split('.')
    year        = dateNtime[0:4]
    month       = dateNtime[5:7]
    day         = dateNtime[8:10]
    hour        = dateNtime[11:13]
    minute      = dateNtime[14:16]
    second      = dateNtime[17:19]
    millisecond  = dateNtime[20:23]
    return int(year),int(month),int(day),int(hour),int(minute),int(second),int(millisecond)


def matchmerge(df1,df1time,df2,df2time,df1cols=[None], df2cols=[None],df3=None,df3cols=[None], df3time=None):
    '''
        Match multiple log files by specified time header such as epoch time.
        If an exact match does not exist, use the closest sample entry. 
        
        Parameters
        ----------
        df1 : DataFrame 
            DataFrame to add to from other DataFrames
        dftime : string
            Column header in df1 used to match time of sample, this cannot be removed 
            even if it is not contained in df1cols
        df2 : DataFrame 
            DataFrame with entries to add to df1 according to closest matching time entry
        df1cols : list of strings
            List of strings containing df1 headers to keep in the DataFrame, Default [None]
            keeps all columns

        Returns 
        -------
        Modified df1 DataFrame with data from df2 (and df3 if df3 is a valid dataframe)

    '''
    # Assign headers for new DataFrame
    if None in df1cols: df1cols = list(df1)
    if None in df2cols: df2cols = list(df2)
    if ((df3 is not None) and (None in df3cols)):df3cols = list(df3)
    if ((df3 is not None) and (df3time == None)): raise ValueError('Need to specify df3time when using df3 parameter') 

    # Remove 'software_name', 'software_version', 'software_url' from df1cols
    for h in range(len(df1cols)):
        if df1cols[h] in ['software_name', 'software_version', 'software_url']:
            del df1cols[h]

    dfmcols     = df1cols.copy()

    # add any aditional values and remove any replicates from df2cols
    dellist = []
    for x in range(len(df2cols)): # change to one-liner
        if ((df2cols[x] not in dfmcols) and (df2cols[x] not in ['software_name', 'software_version', 'software_url'])):
            dfmcols.append(df2cols[x])
        else:
            dellist.append(df2cols[x])
    # remove replicates from df2
    for i in dellist:
        del df2cols[df2cols.index(i)]

    # add any aditional values and remove any replicates from df3cols if used
    if df3 is not None:
        dellist = []
        for x in range(len(df3cols)): # change to one-liner
            if ((df3cols[x] not in dfmcols) and (df3cols[x] not in ['software_name', 'software_version', 'software_url'])):
                dfmcols.append(df3cols[x])
            else:
                dellist.append(df3cols[x])
        # remove replicates from df2
        for i in dellist:
            del df3cols[df3cols.index(i)]

    # Add 'software_name', 'software_version', 'software_url' from dfmcols
    dfmcols.extend(['software_name', 'software_version', 'software_url'])

    # New DataFrame 
    dfm         = pd.DataFrame(columns=dfmcols)

    for i in range(len(df1)):
        row = []
        if pd.isna(df1.loc[i][df1time]): continue # skip nan values

        # Add to row from df1 
        for df1_head in df1cols:
            row.append(df1.loc[i][df1_head])    

        # df2 - index of smallest difference
        df2idx       = abs(df2[df2time] - df1.loc[i][df1time]).sort_values().index[0]
        # Add to row from df2 
        for df2_head in df2cols:
            row.append(df2.loc[df2idx][df2_head])

        if df3 is not None:
            # df3 - index of smallest difference
            df3idx       = abs(df3[df3time] - df1.loc[i][df1time]).sort_values().index[0]
            # Add to row from df3 
            for df3_head in df3cols:
                row.append(df3.loc[df3idx][df3_head])

        # Add 'software_name', 'software_version', 'software_url' to row 
        row.extend(['gavia',__version__,'github.com/brett-hosking/gavia'])

        # Add row to dataframe
        dfm.loc[len(dfm)] = row


    return dfm


def timeshift(df,shift):
    '''
        Introduce a time shift (in seconds) in log file and recalculate
        human-readbale times.

        Parameters
        ----------
        df : DataFrame
            gavia log with timestamp header and values given in seconds
        shift : float
            time shift in seconds 

        Returns
        -------
        New log as a DataFrame with adjusted time fields
    '''
    headers     = list(df)
    if 'timestamp' not in headers:raise ValueError('not a valid gavia logfile; the log should contain a timestamp header')

    # Shift the timestamp header
    df['timestamp'] = df['timestamp'] + shift

    if 'capture-time' in headers:
        # Shift the timestamp header
        df['capture-time'] = df['capture-time'] + shift

    # New DataFrame 
    dfc             = pd.DataFrame(columns=headers)


    # update human readable times 
    for i in range(len(df)):
        row = []
        if pd.isna(df.loc[i]['timestamp']): 
            row = df.loc[i].values.tolist()
        else:
            row = df.loc[i].values.tolist()
            row[headers.index('timestamp_epoch')],row[headers.index('timestamp_nano')] = str(df.iloc[i]['timestamp']).split('.')
            row[headers.index('time')] = gavtime.epoch2dtimeformat(df.iloc[i]['timestamp'])
            row[headers.index('year')],row[headers.index('month')],row[headers.index('day')],row[headers.index('hour')],row[headers.index('minute')],row[headers.index('second')],row[headers.index('millisecond')] = parsedatetime(row[headers.index('time')])

        if 'capture-time' in headers:
            if not pd.isna(df.loc[i]['capture-time']): 
                row[headers.index('capture_epoch')],row[headers.index('capture_micro')]  = str(df.iloc[i]['capture-time']).split('.')
                capture_dtime           = gavtime.epoch2datetime(row[headers.index('capture_epoch')])
                row[headers.index('capture_year')]      = capture_dtime[0]
                row[headers.index('capture_month')]     = capture_dtime[1]
                row[headers.index('capture_day')]       = capture_dtime[2]
                row[headers.index('capture_hour')]      = capture_dtime[3]
                row[headers.index('capture_minute')]    = capture_dtime[4]
                row[headers.index('capture_second')]    = capture_dtime[5]

        # Add row to new DataFrame
        dfc.loc[i] = row

    return dfc

class GPS:

    def __init__(self):
        self.df         = pd.DataFrame(columns=self.headers())

    def save(self,path):
        self.df.to_csv(path)

    def init_dict(self):
        return {    'timestamp': None,
                    'time': None,
                    'UTC': None,
                    'cogt':None,
                    'diff-age': None,
                    'hdop': None, 
                    'lat': None,
                    'lat-dev': None,
                    'lon':None,
                    'lon-dev':None,
                    'messages-received':None,
                    'quality': None,
                    'raw-logged-bytes': None,
                    'received-telnet-bytes':None,
                    'sats':None,
                    'sent-corr-bytes':None,
                    'sent-corr-packets':None,
                    'sent-telnet-bytes':None,
                    'sogk':None,
                    'sogm':None,
                    'stnRef':None,
                    'time-since-sent':None
        }

    def addrow( self, 
                timestamp=None,
                timestamp_epoch=None,
                timestamp_nano=None,
                time=None,
                year=None,
                month=None,
                day=None,
                hour=None,
                minute=None,
                second=None,
                millisecond=None,

                UTC=None,
                cogt=None,
                diff_age=None,
                hdop=None,
                lat=None,
                lat_dev=None,
                lon=None,
                lon_dev=None,
                messages_received=None,
                quality=None,
                raw_logged_bytes=None,
                received_telnet_bytes=None,
                sats=None,
                sent_corr_bytes=None,
                sent_corr_packets=None,
                sent_telnet_bytes=None,
                sogk=None,
                sogm=None,
                stnRef=None,
                time_since_sent=None,

                software_name='gavia',
                software_version=__version__,
                software_url='github.com/brett-hosking/gavia'
        ):
        self.df.loc[len(self.df)] = [
                    timestamp,
                    timestamp_epoch,
                    timestamp_nano,
                    time,
                    year,
                    month,
                    day,
                    hour,
                    minute,
                    second,
                    millisecond,

                    UTC,
                    cogt,
                    diff_age,
                    hdop,
                    lat,
                    lat_dev,
                    lon,
                    lon_dev,
                    messages_received,
                    quality,
                    raw_logged_bytes,
                    received_telnet_bytes,
                    sats,
                    sent_corr_bytes,
                    sent_corr_packets,
                    sent_telnet_bytes,
                    sogk,
                    sogm,
                    stnRef,
                    time_since_sent,

                    software_name,
                    software_version,
                    software_url
        ]

    def headers(self):
        return [    
                    'timestamp',
                    'timestamp_epoch',
                    'timestamp_nano',
                    'time',
                    'year',
                    'month',
                    'day',
                    'hour',
                    'minute',
                    'second',
                    'millisecond',

                    'UTC',
                    'cogt',
                    'diff_age',
                    'hdop',
                    'lat',
                    'lat_dev',
                    'lon',
                    'lon_dev',
                    'messages_received',
                    'quality',
                    'raw_logged_bytes',
                    'received_telnet_bytes',
                    'sats',
                    'sent_corr_bytes',
                    'sent_corr_packets',
                    'sent_telnet_bytes',
                    'sogk',
                    'sogm',
                    'stnRef',
                    'time_since_sent',

                    'software_name',
                    'software_version',
                    'software_url'
        ]

class Camera:

    def __init__(self):
        self.df         = pd.DataFrame(columns=self.headers())

    def save(self,path):
        self.df.to_csv(path)

    def init_dict(self):
        return {    'timestamp': None,
                    'time': None,
                    'capture-time': None,
                    'clock-drift': None,
                    'delivered-frame-rate': None,
                    'frame-drop-count': None,
                    'frame-loss-percentage': None,
                    'frames-captured':None,
                    'frames-written': None,
                    'pc-time':None,
                    'process-in-Q':None,
                    'process-out-Q':None,
                    'process-pop-q-size':None,
                    'build-number':None,
                    'build-tag':None,
                    'strobe-pin':None,
                    'mode':None,
                    'framerate':None,
                    'bayer_filter':None,
                    'port':None,
                    'host_interface':None,
                    'shutter_auto':None,
                    'shutter_max':None,
                    'shutter_min':None,
                    'shutter':None,
                    'gain_auto':None,
                    'gain_max':None,
                    'gain_min':None,
                    'gain':None,
                    'exposure':None,
                    'whitebalance_auto':None,
                    'whitebalance_bu':None,
                    'whitebalance_rv':None,
                    'path':None,
                    'save_raw':None,
                    'jpeg_quality':None,
                    'manipthreads':None,
                    'img_q_size':None,
                    'frame_drop_interval':None,
                    'exposure_test':None,
                    'abort_data_timeout':None,
                    'software_name':'gavia',
                    'software_version':__version__,
                    'software_url':'github.com/brett-hosking/gavia'}

    def addrow( self, 
                timestamp=None,
                timestamp_epoch=None,
                timestamp_nano=None,
                time=None,
                year=None,
                month=None,
                day=None,
                hour=None,
                minute=None,
                second=None,
                millisecond=None,
                filepath=None,
                filename=None,
                capture_time=None,
                capture_epoch=None,
                capture_year=None,
                capture_month=None,
                capture_day=None,
                capture_hour=None,
                capture_minute=None,
                capture_second=None,
                capture_micro=None,
                clock_drift=None,
                delivered_frame_rate=None,
                frame_drop_count=None,
                frame_loss_percentage=None,
                frames_captured=None,
                frames_written=None,
                pc_time=None,
                process_in_Q=None,
                process_out_Q=None,
                process_pop_q_size=None,
                build_number=None,
                build_tag=None,
                strobe_pin=None,
                mode=None,
                framerate=None,
                bayer_filter=None,
                port=None,
                host_interface=None,
                shutter_auto=None,
                shutter_max=None,
                shutter_min=None,
                shutter=None,
                gain_auto=None,
                gain_max=None,
                gain_min=None,
                gain=None,
                exposure=None,
                whitebalance_auto=None,
                whitebalance_bu=None,
                whitebalance_rv=None,
                path=None,
                save_raw=None,
                jpeg_quality=None,
                manipthreads=None,
                img_q_size=None,
                frame_drop_interval=None,
                exposure_test=None,
                abort_data_timeout=None,
                software_name='gavia',
                software_version=__version__,
                software_url='github.com/brett-hosking/gavia'
                ):

            self.df.loc[len(self.df)] = [
                    timestamp,
                    timestamp_epoch,
                    timestamp_nano,
                    time,
                    year,
                    month,
                    day,
                    hour,
                    minute,
                    second,
                    millisecond,
                    filepath,
                    filename,
                    capture_time,
                    capture_epoch,
                    capture_year,
                    capture_month,
                    capture_day,
                    capture_hour,
                    capture_minute,
                    capture_second,
                    capture_micro,
                    clock_drift,
                    delivered_frame_rate,
                    frame_drop_count,
                    frame_loss_percentage,
                    frames_captured,
                    frames_written,
                    pc_time,
                    process_in_Q,
                    process_out_Q,
                    process_pop_q_size,
                    build_number,
                    build_tag,
                    strobe_pin,
                    mode,
                    framerate,
                    bayer_filter,
                    port,
                    host_interface,
                    shutter_auto,
                    shutter_max,
                    shutter_min,
                    shutter,
                    gain_auto,
                    gain_max,
                    gain_min,
                    gain,
                    exposure,
                    whitebalance_auto,
                    whitebalance_bu,
                    whitebalance_rv,
                    path,
                    save_raw,
                    jpeg_quality,
                    manipthreads,
                    img_q_size,
                    frame_drop_interval,
                    exposure_test,
                    abort_data_timeout,
                    software_name,
                    software_version,
                    software_url
            ]


    def headers(self):
        return [    
                    'timestamp',
                    'timestamp_epoch',
                    'timestamp_nano',
                    'time',
                    'year',
                    'month',
                    'day',
                    'hour',
                    'minute',
                    'second',
                    'millisecond',
                    'filepath',
                    'filename',
                    'capture-time',
                    'capture_epoch',
                    'capture_year',
                    'capture_month',
                    'capture_day',
                    'capture_hour',
                    'capture_minute',
                    'capture_second',
                    'capture_micro',
                    'clock-drift',
                    'delivered-frame-rate',
                    'frame-drop-count',
                    'frame-loss-percentage',
                    'frames-captured',
                    'frames-written',
                    'pc-time',
                    'process-in-Q',
                    'process-out-Q',
                    'process-pop-q-size',
                    'build-number',
                    'build-tag',
                    'strobe-pin',
                    'mode',
                    'framerate',
                    'bayer_filter',
                    'port',
                    'host_interface',
                    'shutter_auto',
                    'shutter_max',
                    'shutter_min',
                    'shutter',
                    'gain_auto',
                    'gain_max',
                    'gain_min',
                    'gain',
                    'exposure',
                    'whitebalance_auto',
                    'whitebalance_bu',
                    'whitebalance_rv',
                    'path',
                    'save_raw',
                    'jpeg_quality',
                    'manipthreads',
                    'img_q_size',
                    'frame_drop_interval',
                    'exposure_test',
                    'abort_data_timeout',
                    'software_name',
                    'software_version',
                    'software_url']



class Navigator:

    def __init__(self):
        self.df         = pd.DataFrame(columns=self.headers())

    def save(self,path):
        self.df.to_csv(path)

    def init_deadreckoning_dict(self):
        '''
        dead-reckoning-orientation 
        dead-reckoning-velocity
        dead-reckoning-position
        dead-reckoning-variance
        '''
        return {    'heading':None,
                    'pitch':None,
                    'roll':None,
                    'heave':None,
                    'surge':None,
                    'sway':None,
                    'lat':None,
                    'lon':None,
                    'var_lat':None,
                    'var_lat_lon':None,
                    'var_lon':None
        }

    def init_orientation_dict(self):
        '''
        orientation
        '''
        return {    'heading':None,
                    'pitch':None,
                    'roll':None
        }


    def init_variance_dict(self):
        '''
        Variance
        '''
        return {    'var_lat':None,
                    'var_lat_lon':None,
                    'var_lon':None
        }


    def init_position_dict(self):
        '''
        Position
        '''
        return {    'depth':None,    
                    'lat':None,
                    'lon':None
        }

    def init_velocity_dict(self):
        '''
        Velocity
        '''
        return {    'heave':None,
                    'surge':None,
                    'sway':None
        }

    def init_dict(self):
        return {    'timestamp': None,
                    'time': None,
                    'build-number':None,
                    'build-tag':None,
                    'calculate-magnetic-deviation':None,
                    'magnetic-deviation':None,
                    'pressure-timeout':None,
                    'compass-timeout':None,
                    'dead-reckoning-sog-timeout':None,
                    'dvl-timeout':None,
                    'gps-timeout':None,
                    'gps-validation-enabled':None,
                    'veto-use-water-velocity':None,
                    'station-keeping-enabled':None,
                    'sound-velocity-timeout':None,
                    'temperature-timeout':None,
                    'seanav-timeout':None,
                    'use-pressure':None,
                    'max-allowed-variance':None,
                    'variance-exceeded-warning-level':None,
                    'lat-lon-precision':None,
                    'max-dead-reckoning-distance':None,
                    'dead-reckoning-distance':None,
                    'pressure-depth-conversion':None,
                    'average-water-density':None,
                    'use-water-velocity':None,
                    'sound-velocity':None,
                    'temperature':None,
                    'density-abort-limit':None,
                    'gps-variance':None,
                    'lbl-variance':None,
                    'revolutions-bias':None,
                    'revolutions-scale':None,
                    'dvl-bias':None,
                    'dvl-scale':None,
                    'gyro-bias':None,
                    'control-rate':None,
                    'motor-default':None,
                    'stationary-radius':None,
                    'stationary-p':None,
                    'stationary-idle':None,
                    'stationary-depth-timeout':None,
                    'estimate-speed':None,
                    'observe-timer-on':None,
                    'predict-timer-on':None,
                    'binary-log':None,
                    'broadcast-interface':None,
                    'broadcast-enable':None,
                    'broadcast-frequency':None,
                    'broadcast-navigation-message':None,
                    'broadcast-depth-message':None,
                    'broadcast-sound-velocity-message':None,
                    'idle-status':None,
                    'maxWarningLevel':None,
                    'pilot-status':None,
                    'valid':None,
                    'zero-altitude':None,
                    'altitude':None,
                    'software_name':'gavia',
                    'software_version':__version__,
                    'software_url':'github.com/brett-hosking/gavia'}

    def addrow( self, 
                timestamp=None,
                timestamp_epoch=None,
                timestamp_nano=None,
                time=None,
                year=None,
                month=None,
                day=None,
                hour=None,
                minute=None,
                second=None,
                millisecond=None,

                deadreckoning_heading=None,
                deadreckoning_pitch=None,
                deadreckoning_roll=None,
                deadreckoning_heave=None,
                deadreckoning_surge=None,
                deadreckoning_sway=None,
                deadreckoning_lat=None,
                deadreckoning_lon=None,
                deadreckoning_var_lat=None,
                deadreckoning_var_lat_lon=None,
                deadreckoning_var_lon=None,

                orientation_heading=None,
                orientation_pitch=None,
                orientation_roll=None,

                position_depth=None,
                position_lat=None,
                position_lon=None,    

                variance_var_lat=None,
                variance_var_lat_lon=None,
                variance_var_lon=None,

                velocity_heave=None,
                velocity_surge=None,
                velocity_sway=None,

                build_number=None,
                build_tag=None,
                calculate_magnetic_deviation=None,
                magnetic_deviation=None,
                pressure_timeout=None,
                compass_timeout=None,
                dead_reckoning_sog_timeout=None,
                dvl_timeout=None,
                gps_timeout=None,
                gps_validation_enabled=None,
                veto_use_water_velocity=None,
                station_keeping_enabled=None,
                sound_velocity_timeout=None,
                temperature_timeout=None,
                seanav_timeout=None,
                use_pressure=None,
                max_allowed_variance=None,
                variance_exceeded_warning_level=None,
                lat_lon_precision=None,
                max_dead_reckoning_distance=None,
                dead_reckoning_distance=None,
                pressure_depth_conversion=None,
                average_water_density=None,
                use_water_velocity=None,
                sound_velocity=None,
                temperature=None,
                density_abort_limit=None,
                gps_variance=None,
                lbl_variance=None,
                revolutions_bias=None,
                revolutions_scale=None,
                dvl_bias=None,
                dvl_scale=None,
                gyro_bias=None,
                control_rate=None,
                motor_default=None,
                stationary_radius=None,
                stationary_p=None,
                stationary_idle=None,
                stationary_depth_timeout=None,
                estimate_speed=None,
                observe_timer_on=None,
                predict_timer_on=None,
                binary_log=None,
                broadcast_interface=None,
                broadcast_enable=None,
                broadcast_frequency=None,
                broadcast_navigation_message=None,
                broadcast_depth_message=None,
                broadcast_sound_velocity_message=None,
                idle_status=None,
                maxWarningLevel=None,
                pilot_status=None,
                valid=None,
                zero_altitude=None,
                altitude=None,
                software_name='gavia',
                software_version=__version__,
                software_url='github.com/brett-hosking/gavia'
                ):

            self.df.loc[len(self.df)] = [
                    timestamp,
                    timestamp_epoch,
                    timestamp_nano,
                    time,
                    year,
                    month,
                    day,
                    hour,
                    minute,
                    second,
                    millisecond,

                    deadreckoning_heading,
                    deadreckoning_pitch,
                    deadreckoning_roll,
                    deadreckoning_heave,
                    deadreckoning_surge,
                    deadreckoning_sway,
                    deadreckoning_lat,
                    deadreckoning_lon,
                    deadreckoning_var_lat,
                    deadreckoning_var_lat_lon,
                    deadreckoning_var_lon,

                    orientation_heading,
                    orientation_pitch,
                    orientation_roll,

                    position_depth,
                    position_lat,
                    position_lon, 

                    variance_var_lat,
                    variance_var_lat_lon,
                    variance_var_lon,

                    velocity_heave,
                    velocity_surge,
                    velocity_sway,

                    build_number,
                    build_tag,
                    calculate_magnetic_deviation,
                    magnetic_deviation,
                    pressure_timeout,
                    compass_timeout,
                    dead_reckoning_sog_timeout,
                    dvl_timeout,
                    gps_timeout,
                    gps_validation_enabled,
                    veto_use_water_velocity,
                    station_keeping_enabled,
                    sound_velocity_timeout,
                    temperature_timeout,
                    seanav_timeout,
                    use_pressure,
                    max_allowed_variance,
                    variance_exceeded_warning_level,
                    lat_lon_precision,
                    max_dead_reckoning_distance,
                    dead_reckoning_distance,
                    pressure_depth_conversion,
                    average_water_density,
                    use_water_velocity,
                    sound_velocity,
                    temperature,
                    density_abort_limit,
                    gps_variance,
                    lbl_variance,
                    revolutions_bias,
                    revolutions_scale,
                    dvl_bias,
                    dvl_scale,
                    gyro_bias,
                    control_rate,
                    motor_default,
                    stationary_radius,
                    stationary_p,
                    stationary_idle,
                    stationary_depth_timeout,
                    estimate_speed,
                    observe_timer_on,
                    predict_timer_on,
                    binary_log,
                    broadcast_interface,
                    broadcast_enable,
                    broadcast_frequency,
                    broadcast_navigation_message,
                    broadcast_depth_message,
                    broadcast_sound_velocity_message,
                    idle_status,
                    maxWarningLevel,
                    pilot_status,
                    valid,
                    zero_altitude,
                    altitude,
                    software_name,
                    software_version,
                    software_url
            ]

    # def velocityheader(self):
    #     return [    'heave',
    #                 'surge',
    #                 'sway'
    #     ]

    def headers(self):
        return [    
                    'timestamp',
                    'timestamp_epoch',
                    'timestamp_nano',
                    'time',
                    'year',
                    'month',
                    'day',
                    'hour',
                    'minute',
                    'second',
                    'millisecond',

                    'deadreckoning_heading',
                    'deadreckoning_pitch',
                    'deadreckoning_roll',
                    'deadreckoning_heave',
                    'deadreckoning_surge',
                    'deadreckoning_sway',
                    'deadreckoning_lat',
                    'deadreckoning_lon',
                    'deadreckoning_var_lat',
                    'deadreckoning_var_lat_lon',
                    'deadreckoning_var_lon',

                    'orientation_heading',
                    'orientation_pitch',
                    'orientation_roll',

                    'position_depth',
                    'position_lat',
                    'position_lon', 

                    'variance_var_lat',
                    'variance_var_lat_lon',
                    'variance_var_lon',

                    'velocity_heave',
                    'velocity_surge',
                    'velocity_sway',

                    'build-number',
                    'build-tag',
                    'calculate-magnetic-deviation',
                    'magnetic-deviation',
                    'pressure-timeout',
                    'compass-timeout',
                    'dead-reckoning-sog-timeout',
                    'dvl-timeout',
                    'gps-timeout',
                    'gps-validation-enabled',
                    'veto-use-water-velocity',
                    'station-keeping-enabled',
                    'sound-velocity-timeout',
                    'temperature-timeout',
                    'seanav-timeout',
                    'use-pressure',
                    'max-allowed-variance',
                    'variance-exceeded-warning-level',
                    'lat-lon-precision',
                    'max-dead-reckoning-distance',
                    'dead-reckoning-distance',
                    'pressure-depth-conversion',
                    'average-water-density',
                    'use-water-velocity',
                    'sound-velocity',
                    'temperature',
                    'density-abort-limit',
                    'gps-variance',
                    'lbl-variance',
                    'revolutions-bias',
                    'revolutions-scale',
                    'dvl-bias',
                    'dvl-scale',
                    'gyro-bias',
                    'control-rate',
                    'motor-default',
                    'stationary-radius',
                    'stationary-p',
                    'stationary-idle',
                    'stationary-depth-timeout',
                    'estimate-speed',
                    'observe-timer-on',
                    'predict-timer-on',
                    'binary-log',
                    'broadcast-interface',
                    'broadcast-enable',
                    'broadcast-frequency',
                    'broadcast-navigation-message',
                    'broadcast-depth-message',
                    'broadcast-sound-velocity-message',
                    'idle-status',
                    'maxWarningLevel',
                    'pilot-status',
                    'valid',
                    'zero-altitude',
                    'altitude',
                    'software_name',
                    'software_version',
                    'software_url']