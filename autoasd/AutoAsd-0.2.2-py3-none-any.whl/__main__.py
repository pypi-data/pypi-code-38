import time
import os
import importlib
import sys
import datetime
#import pexpect
from shutil import copyfile

dev=True
computer='desktop'

timeout=5
share_loc=''
RS3_loc=''
ViewSpecPro_loc=''

if not dev:
    dir='\\'.join(__file__.split('\\')[0:-1])
    sys.path.append(dir)
    os.chdir(dir)

if computer == 'old': 
    if dev:
        sys.path.append('c:/users/rs3admin/hozak/python/autoasd/')
        os.chdir('c:/users/rs3admin/hozak/python/autoasd')
    share_loc='C:\\SpecShare'
    RS3_loc=r"C:\Program Files\ASD\RS3\RS3.exe"
    ViewSpecPro_loc=r"C:\Program Files\ASD\ViewSpecPro\ViewSpecPro.exe"
    
elif computer =='new':
    if dev:
        sys.path.append('C:\\users\\hozak\\Python\\AutoASD\\autoasd')
        os.chdir('C:\\users\\hozak\\Python\\AutoASD\\autoasd')
    share_loc='C:\\SpecShare'
    RS3_loc=r"C:\Program Files (x86)\ASD\RS3\RS3.exe"
    ViewSpecPro_loc=r"C:\Program Files (x86)\ASD\ViewSpecPro\ViewSpecPro.exe"
    
elif computer =='desktop':
    if dev:
        sys.path.append('C:\\AutoASD\\autoasd')
        os.chdir('C:\\AutoASD\\autoasd')
    share_loc='C:\\SpecShare'
    RS3_loc=r"C:\Program Files (x86)\ASD\RS3\RS3.exe"
    ViewSpecPro_loc=r"C:\Program Files (x86)\ASD\ViewSpecPro\ViewSpecPro.exe"

import asd_controls
from asd_controls import RS3Controller
from asd_controls import ViewSpecProController

import spectralon_corrector
from spectralon_corrector import apply_spectralon_correction

read_command_loc=share_loc+'\\commands\\from_control'
write_command_loc=share_loc+'\\commands\\from_spec'
temp_data_loc=share_loc+'\\temp'

data_loc=share_loc

#This is needed to make sure modules are updated to reflect changes during development. Otherwise, python might just use cached old versions.
if dev:
    importlib.reload(asd_controls)
    from asd_controls import RS3Controller
    from asd_controls import ViewSpecProController

def main():
    print('Starting AutoASD...\n')
    cmdnum=0

    print('Removing old commands and temporary data...')
    delme=os.listdir(read_command_loc)
    for file in delme:
        os.remove(read_command_loc+'\\'+file)
    print('\tCommand folder for reading clean')
    
    delme=os.listdir(write_command_loc)
    for file in delme:
        os.remove(write_command_loc+'\\'+file)
    print('\tCommand folder for writing clean')
        
    delme=os.listdir(temp_data_loc)
    for file in delme:
        os.remove(temp_data_loc+'\\'+file)
    print('\tTemporary data directory clean')
        
    print('Done.\n')
        
    print('Initializing ASD connections...')
    spec_controller=RS3Controller(share_loc, RS3_loc)
    process_controller=ViewSpecProController(share_loc, ViewSpecPro_loc)
    print('Done.\n')
    print('Ready!\n')
    logger=Logger()
    
    delme=os.listdir(write_command_loc)
    for file in delme:
        os.remove(write_command_loc+'\\'+file)
    
    cmdfiles0=os.listdir(read_command_loc)
    
    data_files_to_ignore=[]
    no_connection=None
    while True:
        #check connectivity with spectrometer
        connected=spec_controller.check_connectivity()
        if not connected:
            try:
                #Let's not accumulate 500000 files
                files=os.listdir(write_command_loc)

                if no_connection==None or no_connection==False: #If this is the first time we've realized we aren't connected. It will be None the first time through the loop and True or False afterward.
                    print('Waiting for RS³ to connect to the spectrometer...')
                    no_connection=True #Use this to know to print an announcement if the spectrometer reconnects next time.
                with open(write_command_loc+'\\lostconnection','w+') as f:
                    pass
                files=os.listdir(write_command_loc)

            except:
                pass
            time.sleep(1)
        if connected and no_connection==True: #If we weren't connected before, let everyone know we are now!
            no_connection=False
            print('RS³ to connected to the spectrometer. Listening!')
                
        
        #check for unexpected files in data adirectory
        file=check_for_unexpected(spec_controller.save_dir, spec_controller.hopefully_saved_files, data_files_to_ignore)
        while file !=None:
            data_files_to_ignore.append(file)
            with open(write_command_loc+'\\unexpectedfile'+str(cmdnum)+'&'+file,'w+') as f:
                    pass
            cmdnum+=1
            file=check_for_unexpected(spec_controller.save_dir, spec_controller.hopefully_saved_files, data_files_to_ignore)
               
        #check for new commands in the read_command location
        cmdfiles=os.listdir(read_command_loc)

        if cmdfiles!=cmdfiles0:
            print('***************')
            for file in cmdfiles:
                if file not in cmdfiles0:
                    cmd,params=filename_to_cmd(file)
                    print('Command received: '+cmd)
                    try: #Occasionally get already in use error, presumably that is temporary so let's just try again if that happens
                        os.remove(read_command_loc+'\\'+file)
                    except PermissionError as e:
                        time.sleep(1)
                        os.remove(read_command_loc+'\\'+file)

                    if 'checkwriteable' in cmd: #Check whether you can write to a given directory
                        try:
                            os.mkdir(params[0]+'\\autospec_temp')
                            os.removedirs(params[0]+'\\autospec_temp')
                            print('writeable')
                            with open(write_command_loc+'\\yeswriteable'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            print('not writeable')
                            with open(write_command_loc+'\\notwriteable'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1

                    elif 'spectrum' in cmd: #Take a spectrum

                        if spec_controller.save_dir=='': #If there's no save configuration set on this computer, tell the control computer you need one. This comes up if the script restarts on the spec compy but there is no restart on the control compy.
                            with open(write_command_loc+'\\noconfig'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        if spec_controller.numspectra==None: #Same as above, but for instrument configuration (number of spectra to average)
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                            
                        #We're going to need to know what filename to expect to be saved so that we can 1) check if the file exists and warn the user beforehand and 2) confirm whether the spectrum was actually taken. This filename will be based on a basename and number, both passed from control compy
                        filename=''
                        if computer=='old': #There are different file formats for old and new RS3 versions. 
                            filename=params[0]+'\\'+params[1]+'.'+params[2]
                        elif computer=='new' or computer=='desktop':
                            filename=params[0]+'\\'+params[1]+params[2]+'.asd'
                            
                        label=params[3]
                        i=params[4]
                        e=params[5]
                        
                        #Check if the file already exists. If it does, let the user know. They will have the option to remove and retry.
                        exists=False
                        if os.path.isfile(filename):
                            exists=True
                            with open(write_command_loc+'\\savespecfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                            
                        #After saving a spectrum, the spec_controller updates its list of expected files to include one more. Wait for this number to change before moving on.
                        #old=len(spec_controller.hopefully_saved_files)
                             
                        spec_controller.take_spectrum(filename)

                        # while True:
                        #     
                        #     time.sleep(0.2)
                        #     new=len(spec_controller.hopefully_saved_files)
                        #     if new>old:
                        #         break
                                
                        #Now wait for the data file to turn up where it belongs.
                        saved=False
                        t0=time.perf_counter()
                        t=time.perf_counter()
                        while t-t0<int(spec_controller.numspectra)*4 and saved==False: #Depending on the number of spectra we are averaging, this might take a while.
                            saved=os.path.isfile(filename)
                            time.sleep(0.2)
                            t=time.perf_counter()
                        print(filename+' saved and found?:'+ str(saved))

                        if saved:
                            logger.log_spectrum(spec_controller.numspectra, i, e, filename, label)
                            filestring=cmd_to_filename('savedfile'+str(cmdnum),[filename])
                        else:
                            spec_controller.hopefully_saved_files.pop(-1)
                            spec_controller.nextnum=str(int(spec_controller.nextnum)-1)
                            filestring=cmd_to_filename('failedtosavefile'+str(cmdnum),[filename])
                            
                        with open(write_command_loc+'\\'+filestring,'w+') as f:
                            pass
                        cmdnum+=1
                        
                    elif cmd=='saveconfig':
                        save_path=params[0]

                        file=check_for_unexpected(save_path, spec_controller.hopefully_saved_files, data_files_to_ignore)
                        found_unexpected=False
                        while file !=None:
                            found_unexpected=True
                            data_files_to_ignore.append(file)
                            with open(write_command_loc+'\\unexpectedfile'+str(cmdnum)+'&'+file,'w+') as f:
                                    pass
                            cmdnum+=1
                            file=check_for_unexpected(save_path, spec_controller.hopefully_saved_files, data_files_to_ignore)
                        if found_unexpected==True:
                            time.sleep(2)
                        with open(write_command_loc+'\\donelookingforunexpected'+str(cmdnum),'w+') as f:
                                    pass
                        
                        basename=params[1]
                        startnum=params[2]
                        filename=''
                        if computer=='old':
                            filename=save_path+'\\'+basename+'.'+startnum
                        elif computer=='new' or computer =='desktop':
                            filename=save_path+'\\'+basename+startnum+'.asd'
                        
                        if os.path.isfile(filename):
                            with open(write_command_loc+'\\saveconfigfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            skip_spectrum()

                            cmdfiles0=cmdfiles
                            continue
                        try:
                            spec_controller.spectrum_save(save_path, basename, startnum)
                            if spec_controller.failed_to_open:
                                spec_controller.failed_to_open=False
                                with open(write_command_loc+'\\saveconfigerror'+str(cmdnum),'w+') as f:
                                    pass
                                cmdnum+=1
                                skip_spectrum()
                            else:
                                logger.logfile=find_logfile(save_path)
                                if logger.logfile==None:
                                    logger.logfile=make_logfile(save_path)
                                    data_files_to_ignore.append(logger.logfile.split('\\')[-1])

                                with open(write_command_loc+'\\saveconfigsuccess'+str(cmdnum),'w+') as f:
                                    pass
                                    cmdnum+=1
                        except Exception as e:
                            print(e)
                            spec_controller.failed_to_open=False
                            with open(write_command_loc+'\\saveconfigerror'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            skip_spectrum()
                            instrument_config_num=None



                            
                    elif cmd=='wr': 
                        if spec_controller.save_dir=='':
                            with open(write_command_loc+'\\noconfig'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        if spec_controller.numspectra==None:
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                            
                        if computer=='old':
                            filename=spec_controller.save_dir+'\\'+spec_controller.basename+'.'+spec_controller.nextnum
                        elif computer=='new' or computer=='desktop':
                            filename=spec_controller.save_dir+'\\'+spec_controller.basename+spec_controller.nextnum+'.asd'
                        exists=False
                        
                        if os.path.isfile(filename):
                            
                            exists=True
                            with open(write_command_loc+'\\wrfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        spec_controller.white_reference()

                        if spec_controller.wr_success==True:
                            with open(write_command_loc+'\\wrsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        else:
                            with open(write_command_loc+'\\wrfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        spec_controller.wr_success=False
                        spec_controller.wr_failure=False
                        
                    elif cmd=='opt': 
                    
                        #This makes sure that there was always a save configuration set before optimizing. Data files don't get saved during optimization, but this needs to happen anyway because we need to know where to put the log file when we record that we optimized.
                        if spec_controller.save_dir=='':
                            with open(write_command_loc+'\\noconfig'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
    
                        
                        #And, we do need to know how many spectra we are averaging so we know when to time out
                        if spec_controller.numspectra==None:
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        try:
                            spec_controller.optimize()
                            if spec_controller.opt_complete==True:
                                logger.log_opt()
                                with open(write_command_loc+'\\optsuccess'+str(cmdnum),'w+') as f:
                                    pass
                                cmdnum+=1
                            else:
                                
                                with open(write_command_loc+'\\optfailure'+str(cmdnum),'w+') as f:
                                    pass
                                cmdnum+=1
                        except:
                            print('Exception occurred and optimization failed.')
                            with open(write_command_loc+'\\optfailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                   
                    elif 'process' in cmd:
                        input_path=params[0] 
                        output_path=params[1]
                        csv_name=params[2]
                        logfile_for_reading=None #We'll find it in the data folder.
                        
                        if input_path=='spec_share_loc':
                            input_path=temp_data_loc
                        if output_path=='spec_share_loc':
                            output_path=temp_data_loc

                        
                        #check if the input directory exists. if not, send an error back
                        if not os.path.exists(input_path):
                            with open(write_command_loc+'\\processerrornodirectory'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                            
                        #Look through files in data directory until you find a log file
                        for potential_log in os.listdir(input_path):
                            if '.txt' in potential_log:
                                try:
                                    with open(input_path+'\\'+potential_log, 'r') as f:
                                        firstline=f.readline()
                                        if '#AutoSpec log' in firstline:
                                            logfile_for_reading=input_path+'\\'+potential_log
                                            break
                                except Exception as e:
                                    print(e)
                                    
                        if logfile_for_reading==None:
                            print('ERROR: No logfile found in data directory')
                        
                        if os.path.isfile(output_path+'\\'+csv_name) and csv_name != 'proc_temp.csv':
                            with open(write_command_loc+'\\processerrorfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        elif os.path.isfile(output_path+'\\'+csv_name):
                            print('overwriting proc_temp')
                            writeable=os.access(output_path,os.W_OK)
                            if not writeable:
                                with open(write_command_loc+'\\processerrorcannotwrite'+str(cmdnum),'w+') as f:
                                    pass
                                cmdnum+=1
                                cmdfiles0=cmdfiles
                                continue
                                
                            os.remove(output_path+'\\'+csv_name)
                            
                        writeable=os.access(output_path,os.W_OK)
                        

                       
                        if not writeable:
                            with open(write_command_loc+'\\processerrorcannotwrite'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                            
                        #If the specified output path is in the C drive, we can write straight to it. Otherwise, we're going to temporarily store the file in C:\\SpecShare\\temp
                        else:
                            if output_path[0:3]!='C:\\':
                                temp_output_path='C:\\SpecShare\\temp'
                            else:
                                temp_output_path=output_path
                            
                            datafile=temp_output_path+'\\'+csv_name

                            try:

                                process_controller.process(input_path, temp_output_path, csv_name)

                                
                                #Check that the expected file arrived fine after processing. This sometimes wasn't happening if you fed ViewSpecPro data without taking a white reference or optimizing.
                                saved=False
                                t0=time.perf_counter()
                                t=time.perf_counter()
                                while t-t0<5 and saved==False:
                                    saved=os.path.isfile(datafile)
                                    time.sleep(0.2)
                                    t=time.perf_counter()
                                corrected=False
                                if not saved:
                                    print('not saved??')
                                    print(datafile)
                                if saved:
                                    #Load headers from the logfile, then apply correction
                                    if logfile_for_reading!=None:
                                        print('Loading headers from log file')
                                        warnings=set_headers(datafile, logfile_for_reading)
                                        print('applying correction')
                                        try:
                                            apply_spectralon_correction(datafile) #applies a correction based on measured BRDF for spectralon (see Biliouris et al 2007?)
                                            corrected=True
                                        except:
                                            print('warning! correction not applied')
                                    else:
                                        print('Warning! No log file found!')
                                        tsv_to_csv(datafile) #still replace tabs with commas
                                        warnings='no log found'
                                    
                                    print('done')
                                    final_datafile=output_path+'\\'+csv_name #May or may not be the same loc as temporary.
                                    data_base='.'.join(csv_name.split('.')[0:-1]) #E.g. for a csv name of foo.csv, returns foo
                                    final_logfile=output_path+'\\'+data_base+'_log' #We're going to copy the logfile along with it, givnig it a sensible name e.g. foo_log.txt
                                    print(final_logfile)
                                    
                                    #But first we have to make sure there isn't an existing file with that name.
                                    i=1
                                    logfile_base=final_logfile
                                    while os.path.isfile(final_logfile+'.txt'):
                                        final_logfile=logfile_base+'_'+str(i)
                                        i+=1
                                    final_logfile+='.txt'
                                    #Ok, now copy!
                                    if logfile_for_reading !=None:
                                        os.system('copy '+logfile_for_reading+' '+final_logfile)
                                        print(output_path)
                                        print(spec_controller.save_dir)
                                        if output_path==spec_controller.save_dir:
                                            print(final_logfile.split('\\')[-1])
                                            data_files_to_ignore.append(final_logfile.split('\\')[-1])
                                        #If we need to move the data to get it to its final destination, do it!
                                    if temp_output_path!=output_path:
                                        tempfilename=datafile
                                        os.system('move '+tempfilename+' '+final_datafile)
                                        
              
                                    #If the output directory is the same (or within) the data directory, there's no need to alert the user to an unexpected file being introduced since clearly it was expected.
                                    if spec_controller.save_dir!=None and spec_controller.save_dir!='':
                                        if spec_controller.save_dir in final_datafile:
                                            expected=final_datafile.split(spec_controller.save_dir)[1].split('\\')[1]
                                            spec_controller.hopefully_saved_files.append(expected)
                                            
                                    if corrected==True and logfile_for_reading!=None:
                                        with open(write_command_loc+'\\processsuccess'+str(cmdnum),'w+') as f:
                                            pass
                                    elif logfile_for_reading!=None:
                                        with open(write_command_loc+'\\processsuccessnocorrection'+str(cmdnum),'w+') as f:
                                            pass
                                    else:
                                        with open(write_command_loc+'\\processsuccessnolog'+str(cmdnum),'w+') as f:
                                            pass
                                #We don't actually know for sure that processing failed because of failing to optimize or white reference, but ViewSpecPro sometimes silently fails if you haven't been doing those things.
                                else:
                                    with open(write_command_loc+'\\processerrorwropt'+str(cmdnum),'w+') as f:
                                        pass
                                cmdnum+=1
                            except Exception as e:
                                print(e)
                                process_controller.reset()
                                with open(write_command_loc+'\\processerror'+str(cmdnum),'w+') as f:
                                    pass
                                cmdnum+=1
                    elif 'instrumentconfig' in cmd:                        
                        instrument_config_num=params[0]
                        try:
                            spec_controller.instrument_config(instrument_config_num)
                            with open(write_command_loc+'\\iconfigsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\iconfigfailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                    #I am really not sure what this was all about... probably delete.
                    elif 'ignorefile' in cmd:
                        print('hooray!')
                        data_files_to_ignore.append('hooray!')
                    elif 'rmfile' in cmd:
                        try:
                            delme=params[0]+'\\'+params[1]+params[2]+'.asd'
                            os.remove(delme)
                            with open(write_command_loc+'\\rmsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\rmfailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                    #Used for copying remote data over to the control compy for plotting, etc
                    elif 'transferdata' in cmd:
                        source=params[0]
                        destination=params[1]

                        if params[0]=='spec_share_loc':
                            source=share_loc+'\\'+params[2]
                        if params[1]=='spec_share_loc':
                            destination=share_loc+'\\'+params[2]

                        try:
                            copyfile(source,destination)
                            with open(write_command_loc+'\\datacopied'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except Exception as e:
                            print(str(e))
                            with open(write_command_loc+'\\datafailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            

                            
                    #List directories within a folder for the remote file explorer on the control compy
                    elif 'listdir' in cmd:
                        try:
                            dir=params[0]
                            print(dir)
                            if dir[-1]!='\\':dir+='\\'
                            cmdfilename=cmd_to_filename(cmd,[params[0]])
                            print('cmdfilename:')
                            print(cmdfilename)
                            files=os.listdir(dir)
                            with open(write_command_loc+'\\'+cmdfilename,'w+') as f:
                                for file in files:
                                    print(os.path.isdir(dir+file))
                                    if os.path.isdir(dir+file) and file[0]!='.':
                                        f.write(file+'\n')
                                pass
                            cmdnum+=1
                        except(PermissionError):
                            print('permission')
                            with open(write_command_loc+'\\'+'listdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\'+'listdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        
                    #List directories and files in a folder for the remote file explorer on the control compy
                    elif 'listcontents' in cmd:
                        

                        try:
                            dir=params[0]
                            if dir[-1]!='\\':dir+='\\'
                            cmdfilename=cmd_to_filename(cmd,[params[0]])
                            files=os.listdir(dir)
                            sorted_files=[]
                            for i, file in enumerate(files):
                                if os.path.isdir(dir+file) and file[0]!='.':
                                    sorted_files.append(file)
                                elif file[0]!='.':
                                    #This is a way for the control compy to differentiate files from directories
                                    sorted_files.append('~:'+file)
                            sorted_files.sort()
                            with open(write_command_loc+'\\'+cmdfilename,'w+') as f:
                                for file in sorted_files:
                                    f.write(file+'\n')
                            cmdnum+=1
                        
                        except(PermissionError):
                            print('permission')
                            with open(write_command_loc+'\\'+'listdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except:
                            with open(write_command_loc+'\\'+'listdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    
                    #make a directory
                    elif 'mkdir' in cmd:
                        try:
                            os.makedirs(params[0])
                            if spec_controller.save_dir!=None and spec_controller.save_dir!='':
                                print(params[0])
                                if '\\'.join(params[0].split('\\')[:-1])==spec_controller.save_dir:
                                    expected=params[0].split(spec_controller.save_dir)[1].split('\\')[1]
                                    spec_controller.hopefully_saved_files.append(expected)
                            
                            with open(write_command_loc+'\\'+'mkdirsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except(FileExistsError):
                            print(params[0])
                            with open(write_command_loc+'\\'+'mkdirfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except(PermissionError):
                            with open(write_command_loc+'\\'+'mkdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except:
                            with open(write_command_loc+'\\'+'mkdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    
                    #Not implemented yet!
                    elif 'rmdir' in cmd:
                        try:
                            shutil.rmtree(params[0])
                            if spec_controller.save_dir!=None and spec_controller.save_dir!='':
                                print(params[0])
                                if params[0] in spec_controller.save_dir:
                                    spec_controller.save_dir=None
                            
                            with open(write_command_loc+'\\'+'rmdirsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except(PermissionError):
                            with open(write_command_loc+'\\'+'rmdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except:
                            with open(write_command_loc+'\\'+'rmdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        
        time.sleep(0.25)
        cmdfiles0=cmdfiles
        
def filename_to_cmd(filename):
    cmd=filename.split('&')[0]
    if 'listdir' not in cmd and 'listcontents' not in cmd: #For listdir, we need to remember the cmd number sent over - the control compy will be watching for an exact filename match.
        while cmd[-1] in '1234567890':
            cmd=cmd[0:-1]
    params=filename.split('&')[1:]
    i=0
    for param in params:
        params[i]=param.replace('+','\\').replace('=',':')
        i=i+1
    return cmd,params
    
def cmd_to_filename(cmd, params):
    filename=cmd
    i=0
    for param in params:
        filename=filename+'&'+param.replace('\\','+').replace(':','=')
        i=i+1
    return filename

def skip_spectrum():
    time.sleep(2)
    print('remove spec commands')
    files=os.listdir(read_command_loc)
    #print(files)
    for file in files:
        if 'spectrum' in file:
            os.remove(read_command_loc+'\\'+file)
    #print(os.listdir(read_command_loc))
    time.sleep(1)

def check_for_unexpected(save_dir, hopefully_saved_files, data_files_to_ignore):
    data_files=[]
    try:
        data_files=os.listdir(save_dir)
    except:
        pass
    expected_files=[]
    for file in hopefully_saved_files:
        expected_files.append(file.split('\\')[-1])
    for file in data_files:
        #print('This file is here:'+file)
        if file not in data_files_to_ignore:
            if file not in expected_files:
                #print('And it is not expected.')
                return file
    return None

def find_logfile(directory):
    logfile=None
    for potential_log in os.listdir(directory):
        print(potential_log)
        if '.txt' in potential_log:
            try:
                with open(directory+'\\'+potential_log, 'r') as f:
                    firstline=f.readline()
                    print(firstline)
                    if '#AutoSpec log' in firstline:
                        logfile=directory+'\\'+potential_log
                        break
            except Exception as e:
                print(e)
    if logfile!=None:
        with open(logfile,'a') as f:
            datestring=''
            datestringlist=str(datetime.datetime.now()).split('.')[:-1]
            for d in datestringlist:
                datestring=datestring+d
            f.write('#AutoSpec log re-opened on '+datestring+'.\n\n')
    return logfile
    

            
def make_logfile(directory):
    files=os.listdir(directory)
    i=1
    logfile='log.txt'
    while logfile in files:
        logfile='log'+str(i)+'.txt'
        i+=1
    with open(directory+'\\'+logfile,'w+') as f:
        datestring=''
        datestringlist=str(datetime.datetime.now()).split('.')[:-1]
        for d in datestringlist:
            datestring=datestring+d
        f.write('#AutoSpec log initialized on '+datestring+'.\n\n')
        
    return directory+'\\'+logfile

#convert to csv
def tsv_to_csv(datafile):
    data=[]
    with open(datafile, 'r') as file:
        line=file.readline()
        while line != '':
            data.append(line.replace('\t',','))
            line=file.readline()
        with open(datafile,'w+') as file:
            for i, line in enumerate(data):
                if i==0:
                    file.write('Sample Name:'+line.strip('Wavelength'))
                    w_line='Wavelength'
                    for _ in range(len(line.split(','))-1):
                        w_line+=','
                    file.write(w_line+'\n')
                else:
                    file.write(line)
    print('converted to .csv')
  
    
def set_headers(datafile,logfile):
    
    labels={}
    nextfile=None
    nextnote=None
    
    if os.path.exists(logfile):
        with open(logfile) as log:
            line=log.readline()
            while line!='':
                while 'i: ' not in line and line!='':
                    line=log.readline() #skip the first few lines until you get to viewing geometry
                if 'i:' in line:
                    try:
                        nextnote=' (i='+line.split('i: ')[-1].strip('\n')
                    except:
                        nextnote=' (i=?'
                while 'e: ' not in line and line!='':
                    line=log.readline()
                if 'e:' in line:
                    try:
                        nextnote=nextnote+' e='+line.split('e: ')[-1].strip('\n')+')'
                    except:
                        nextnote=nextnote+' e=?)'
                while 'filename' not in line and line!='':
                    line=log.readline()
                if 'filename' in line:
                    if '\\' in line:
                        line=line.split('\\')
                    else:
                        line=line.split('/')
                    nextfile=line[-1].strip('\n')
                    nextfile=nextfile.split('.')
                    nextfile=nextfile[0]+nextfile[1]
                        
                while 'Label' not in line and line!='':
                    line=log.readline()
                if 'Label' in line:
                    nextnote=line.split('Label: ')[-1].strip('\n')+nextnote
                    
                if nextfile != None and nextnote != None:
                    nextnote=nextnote.strip('\n')
                    labels[nextfile]=nextnote
        
                    nextfile=None
                    nextnote=None
                line=log.readline()
            if len(labels)!=0:

                data_lines=[]
                with open(datafile,'r') as data:
                    line=data.readline().strip('\n')
                    data_lines.append(line)
                    while line!='':
                        line=data.readline().strip('\n')
                        data_lines.append(line)
                
                datafiles=data_lines[0].split('\t')[1:] #The first header is 'Wavelengths', the rest are file names
                    
                spectrum_labels=[]
                unknown_num=0 #This is the number of files in the datafile headers that aren't listed in the log file.
                for i, filename in enumerate(datafiles):
                    label_found=False
                    filename=filename.replace('.','')
                    spectrum_label=filename
                    if filename in labels:
                        label_found=True
                        if labels[filename]!='':
                            spectrum_label=labels[filename]
                            
                    #Sometimes the label in the file will have sco attached. Take off the sco and see if that is in the labels in the file.
                    filename_minus_sco=filename[0:-3]
                    if filename_minus_sco in labels:
                        label_found=True
                        if labels[filename_minus_sco]!='':
                            spectrum_label=labels[filename_minus_sco]
                            
                    if label_found==False:
                        unknown_num+=1
                    spectrum_labels.append(spectrum_label)
                

                    
                
                header_line=data_lines[0].split('\t')[0] #This will just be 'Wavelengths'
                for i, label in enumerate(spectrum_labels):
                    header_line=header_line+'\t'+label
                
                data_lines[0]=header_line
                
                with open(datafile,'w') as data:
                    for line in data_lines:
                        data.write(line+'\n')
            
            #Now reformat data to fit WWU spectral library format. 
            data=[]
            metadata=['Database of origin:,Western Washington University Planetary Spectroscopy Lab','Sample Name','Viewing Geometry']

            for i, line in enumerate(data_lines):
                if i==0:
                    headers=line.split('\t')
                    headers[-1]=headers[-1].strip('\n')
                    for i, header in enumerate(headers):
                        if i==0:
                            continue
                        #If sample names and geoms were read successfully from logfile, this should always work fine. But in case logfile is missing or badly formatted, don't break, just don't have geom info either.
                        try:
                            sample_name=header.split('(')[0]
                        except:
                            sample_name=header
                        try:
                            geom=header.split('(')[1].strip(')')
                            print(geom)
                        except:
                            geom=''
                        metadata[1]+=','+sample_name
                        metadata[2]+=','+geom
                    metadata.append('')
                    metadata.append('Wavelength')
        
                else:
                    data.append(line.replace('\t',','))
                        
            with open(datafile,'w+') as file:
                for line in metadata:
                    file.write(line)
                    file.write('\n')
                for line in data:
                    file.write(line)
                    file.write('\n')

            if len(labels)==0:
                return 'nolabels'
            elif unknown_num==0:
                return ''#No warnings
            elif unknown_num==1:
                return '1unknown' #This will succeed but the control computer will print a warning that not all samples were labeled. Knowing if it was one or more than one just helps with grammar.

            elif unknown_num>1:
                return 'unknowns'
    else:
        return 'nolog'

class Logger():
    def __init__(self):
        self.logfile=''
        
    def log_spectrum(self, numspectra, i, e, filename, label):
        if label=='GARBAGE': #These are about to be deleted. No need to log them.
            return
            
        if 'White reference' in label:
            info_string='White reference saved.'
        else:
            info_string='Spectrum saved.'
    
        info_string+='\n\tSpectra averaged: ' +numspectra+'\n\ti: '+i+'\n\te: '+e+'\n\tfilename: '+filename+'\n\tLabel: '+label+'\n'
    
        self.log(info_string)
        
    def log_opt(self):
        self.log('Instrument optimized.')
        
    def log(self, info_string):

        datestring=''
        datestringlist=str(datetime.datetime.now()).split('.')[:-1]
        for d in datestringlist:
            datestring=datestring+d
            
        while info_string[0]=='\n':
            info_string=info_string[1:]
    
        space=str(80)
        if '\n' in info_string:
            lines=info_string.split('\n')
    
            lines[0]=('{1:'+space+'}{0}').format(datestring,lines[0])
            info_string='\n'.join(lines)
        else:
            info_string=('{1:'+space+'}{0}').format(datestring,info_string)
            
        if info_string[-2:-1]!='\n':
            info_string+='\n'
            
        print(info_string)
        print('\n')
        print(self.logfile)
        with open(self.logfile,'a') as log:
            log.write(info_string)
            log.write('\n')
        


if __name__=='__main__':
    main()