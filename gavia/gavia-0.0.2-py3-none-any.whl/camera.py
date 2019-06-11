import numpy as np
import xml.etree.ElementTree as ET
import gzip
import pandas as pd
import os
import gavia


def getimagepaths(dir):
    '''
    Get a list of directory names and the images 
    contained within those directory

    Parameters
    ----------
    dir : string
        path to directory containing folders of images

    Returns 
    -------
    List of folder names and image files in corresponding folders, in the format 
    [[imagefolder][imagefile]]
    
    '''
    foldernames = os.listdir(dir)
    nfolders    = len(foldernames)
    imagepaths  = []
    for f in range(nfolders):
        path = os.path.join(dir,foldernames[f])
        imagepaths.append([foldernames[f]] + os.listdir(path))

    return imagepaths


def findpath(imgpaths,filename):
    '''
    find the filename in filepaths 
    [[imagefolder][imagefile]]
    '''
    diridx = 0
    while True:
        try:
            if filename + '.ppm' in imgpaths[diridx]:
                return imgpaths[diridx][0]
        except: 
            return None

        diridx+=1


def loadlog(projectdir):
    '''
    Load the camera log file for the specified project, given by the projectdir
    parameter

    Parameters
    ----------
    projectdir : string
        path to the gavia project

    Returns 
    -------
    Pandas DataFrame containing camera logs
    '''
    PROCESS = True
    ROOT    = False
    # check for processed log file in directory 
    dirfiles        = os.listdir(projectdir)

    # projectdir may not be given as the root folder
    if 'log_processed' in dirfiles:
        if 'camera.csv' in os.listdir(os.path.join(projectdir,'log_processed')):
            PROCESS = False
    elif 'files'in dirfiles: 
        ROOT = True
        dirfiles        = os.listdir(os.path.join(projectdir,'files'))
        # check if folders/files are contained within a 'files' directory
        if 'log_processed' in dirfiles:
            if 'camera.csv' in os.listdir(os.path.join(projectdir,'files','log_processed')):
                PROCESS = False

    if ROOT:
        # change the projectdir to the files\ directory
        projectdir = os.path.join(projectdir,'files')

    if PROCESS:
        print('Processing camera logs...')
        logdir      = os.path.join(projectdir,'log')
        imgdir      = os.path.join(projectdir,'images')
        if not os.path.exists(imgdir): raise ValueError('no image directory found in project')
        loglist     = gavia.log.getlogs(logdir,'camera')
        if len(loglist) == 0: raise ValueError('no camera logs found in project')
        imagepaths  = getimagepaths(imgdir)

        nlogs       = len(loglist)
        # combine log DataFrame
        df          = pd.DataFrame()
        for l in range(nlogs):
            logfile     = os.path.join(logdir,loglist[l])
            logclass    = gavia.log.Camera()
            xml_data    = gzip.open(logfile, 'rb').read()
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
                # epoch       = datetime2epoch([year,month,day,hour,minute,second])
                # split capture time into epoch and microseconds 
                timestamp_epoch,timestamp_micro = root[n].attrib.get(keys[0]).split('.')

                if parsed['capture-time'] != None:
                    capture_epoch,capture_micro     = parsed['capture-time'].split('.')
                    # capture epoch into datetime 
                    capture_dtime                    = gavia.time.epoch2datetime(capture_epoch)

                    # image filepath and filename
                    filename                         = ''.join(('frame', "%06d" % (int(parsed['frames-captured'])), '_',capture_epoch,'_',capture_micro))
                    # find filename in imagepaths
                    imgfiledir                       = findpath(imagepaths,filename)
                    if not imgfiledir == None:
                        filepath                     = os.path.join(imgfiledir,filename)
                    else:
                        filepath                     = None
                else:
                    capture_epoch,capture_micro     = None,None
                    capture_dtime                   = [None,None,None,None,None,None]
                    filename                        = None 
                    imgfiledir                      = None
                    filepath                        = None

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
                            filepath=filepath,
                            filename=filename,
                            capture_time=parsed['capture-time'],
                            capture_epoch=capture_epoch,
                            capture_year=capture_dtime[0],
                            capture_month=capture_dtime[1],
                            capture_day=capture_dtime[2],
                            capture_hour=capture_dtime[3],
                            capture_minute=capture_dtime[4],
                            capture_second=capture_dtime[5],
                            capture_micro=capture_micro,
                            clock_drift=parsed['clock-drift'],
                            delivered_frame_rate=parsed['delivered-frame-rate'],
                            frame_drop_count=parsed['frame-drop-count'],
                            frame_loss_percentage=parsed['frame-loss-percentage'],
                            frames_captured=parsed['frames-captured'],
                            frames_written=parsed['frames-written'],
                            pc_time=parsed['pc-time'],
                            process_in_Q=parsed['process-in-Q'],
                            process_out_Q=parsed['process-out-Q'],
                            process_pop_q_size=parsed['process-pop-q-size'],
                            build_number=parsed['build-number'],
                            build_tag=parsed['build-tag'],
                            strobe_pin=parsed['strobe-pin'],
                            mode=parsed['mode'],
                            framerate=parsed['framerate'],
                            bayer_filter=parsed['bayer_filter'],
                            port=parsed['port'],
                            host_interface=parsed['host_interface'],
                            shutter_auto=parsed['shutter_auto'],
                            shutter_max=parsed['shutter_max'],
                            shutter_min=parsed['shutter_min'],
                            shutter=parsed['shutter'],
                            gain_auto=parsed['gain_auto'],
                            gain_max=parsed['gain_max'],
                            gain_min=parsed['gain_min'],
                            gain=parsed['gain'],
                            exposure=parsed['exposure'],
                            whitebalance_auto=parsed['whitebalance_auto'],
                            whitebalance_bu=parsed['whitebalance_bu'],
                            whitebalance_rv=parsed['whitebalance_rv'],
                            path=parsed['path'],
                            save_raw=parsed['save_raw'],
                            jpeg_quality=parsed['jpeg_quality'],
                            manipthreads=parsed['manipthreads'],
                            img_q_size=parsed['img_q_size'],
                            frame_drop_interval=parsed['frame_drop_interval'],
                            exposure_test=parsed['exposure_test'],
                            abort_data_timeout=parsed['abort_data_timeout']
                        )

            df          = pd.concat([df,logclass.df],ignore_index=True)
            
        # Check that all images are present in the logfile, if not, add them using their filename timestamp
        logclass    = gavia.log.Camera()
        for impath in os.listdir(imgdir):
            imfiles     = os.listdir(os.path.join(imgdir,impath))
            for f in imfiles:
                if f[:-4] in df['filename'].values: # swap this for the pandas version
                    # print(f[:-4], ' is in dataframe')
                    continue
                else:
                    ''' example: frame000308_1556725072_875606 '''
                    # print(f[:-4], ' is NOT in dataframe')
                    frames_captured, capture_epoch, capture_micro      = f[:-4].split('_')
                    frames_captured = int(frames_captured[5:])
                    capture_time    = capture_epoch + '.' + capture_micro
                    capture_dtime   = gavia.time.epoch2datetime(capture_epoch)
                    # add to dataframe and sort by capture_time at the end
                    # add row 
                    logclass.addrow(
                            filepath=os.path.join(impath,f[:-4]),
                            filename=f[:-4],
                            capture_time=capture_time,
                            capture_epoch=capture_epoch,
                            capture_year=capture_dtime[0],
                            capture_month=capture_dtime[1],
                            capture_day=capture_dtime[2],
                            capture_hour=capture_dtime[3],
                            capture_minute=capture_dtime[4],
                            capture_second=capture_dtime[5],
                            capture_micro=capture_micro,
                            frames_captured=frames_captured
                    )

        # sort by cature_time
        df              = pd.concat([df,logclass.df],ignore_index=True,sort=False)
        df              = df.sort_values(by=['capture-time'])
        if not os.path.exists(os.path.join(projectdir,'log_processed')):os.makedirs(os.path.join(projectdir,'log_processed'))
        df.to_csv(os.path.join(projectdir,'log_processed','camera.csv'))
        print('Complete')

    else:
        df              = pd.read_csv(os.path.join(projectdir,'log_processed','camera.csv'))
        del df['Unnamed: 0']

    return df