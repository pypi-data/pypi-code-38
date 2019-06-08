import os
import fileinput
# To copy files
from shutil import copyfile
from datetime import date

#by default, do not print.
# Most hints on using variables came from this page: https://stackoverflow.com/questions/1977362/how-to-create-module-wide-variables-in-python 
# variable is a list, because lists are mutable.
__adr_verbose = [False]

def get_adr_verbosity():
    return __adr_verbose[0]

def set_adr_verbosity(verbosity):
    adr_print('verbosity set to ' + str(verbosity) )
    if verbosity == True:
        print('Verbose printing is enabled')
        __adr_verbose[0] = True
    else:
        #print('silent...')
        __adr_verbose[0] = False

# adr-config:
# Original bash implementation generates strings with paths to
# bin and template dir (both the same).

# In this python implementation I've changed this to a 
# dictionary. I think this is more future proof and way
# more 'pythonic' and less error prone.

def adr_print(text):
    if(get_adr_verbosity() == True):
        print(text)

def adr_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config = {"adr_bin_dir"     : dir_path ,
              "adr_template_dir": dir_path 
    }
    return(config)

# adr-init

# file IO:
# https://docs.python.org/3/tutorial/inputoutput.html

def adr_init(config, localpath, dirname):
    if (str(dirname) != 'doc/adr/'):
        with open('.adr-dir','w') as f:
            f.write(dirname)
# create subdirectories
# https://stackabuse.com/creating-and-deleting-directories-with-python/        
    try:  
        os.makedirs(dirname)
    except OSError:  
        print ("Creation of the directory %s failed" % dirname)
    else:  
        print ("Successfully created the directory %s" % dirname)
        adr_new(config, localpath, 'record-architecture-decisions')
    return(0)

# This function is used to read the .adr-dir file (written in adr_init), to determine the relative path for the 
# adrs. default is /doc/adr/ . 
# In order to find this file in another directory, an optional directory can be passed.
def find_alternate_dir(dir = 'doc/adr/'):
    directory = dir
    try:
        # open local file
        fh = open(os.path.join(dir,'.adr-dir'), 'r')
        # add slash to remain compatible with 'default' /doc/adr/
        directory = fh.read()+'/'
    except FileNotFoundError:
        None
    return directory


# adr-new
def adr_new(config, localpath, title, superseded = None, links = None):
    # start with no error; if it changes along the way, we have an error
    result = 'no error'

    # directory for the template
    src= config["adr_template_dir"]+'/template.md'
    
    #check input argument for the ADR title
    try:
        # check if title can be converted to string, and 
        # replace spaces with dashes on the go
        adr_print(title)
        
        if type(title) == list:
            title_checked = "-".join(title).replace(' ','-')
        elif type(title) == str:
            title_checked = (title).replace(' ','-')
    except ValueError:
        result = 'Title was no string'
        print ("adr-new had no valid input for the title")
    
    if (result == 'no error' ):
        # location of adrs
        adr_dir = _adr_dir()
        # find highest index

        # first, find last item in adr_list
        try:
            highest_file_name = adr_list(adr_dir)[-1]
           # extract filename from path
            adr_index = int(os.path.basename(highest_file_name)[:4])
        except:
            #if no valid index (for example when running adr-init), make a new one
            adr_index = 0
        adr_print('adr-new; highest index = ' + str(adr_index))
        # increment index for new adr
        adr_index += 1
        # Format number to string with 4 characters
        # https://stackoverflow.com/questions/11714859/how-to-display-the-first-few-characters-of-a-string-in-python
        adr_index_text = '{0:04d}'.format(adr_index)
 
        # combine data to make destination path
        dst =  os.path.join(adr_dir , adr_index_text + '-' + title_checked + '.md')
        adr_print('adr-new; ' + src + ' ' + dst)
        # copy template to destination directory, with correct title
        copyfile(src, dst)
        adr_write_number_and_header(dst, adr_index_text, title_checked)
        
        #Handle optional commands, -s and -l

        # -s 

        if superseded != None:
            for supersede in superseded:         
                supersede_text =supersede[0]
                # index zero of return value of _adr_file is the number of the adr
                adr_print('adr-new; supersede_text = ' + supersede_text +  ' , adr is ' + _adr_file(supersede_text)[1])
                _adr_remove_status('Accepted', _adr_file(supersede_text)[1])
                _adr_add_link(supersede_text, 'Superceded by', _adr_file(dst)[1])
                _adr_add_link(_adr_file(dst)[1], 'Supercedes', supersede_text )
        
        # -l 

        # example: -l "5:Amends:Amended by" 
        if links != None:
             for linkadr in links:
                try:
                    adr_print('adr-new; linktext = ' + linkadr )
                    #split by colon
                    target, link, reverse_link = linkadr.split(':')
                    # index zero of return value of _adr_file is the number of the adr
                    _adr_add_link(_adr_file(dst)[1] , link, _adr_file(target)[1])
                    _adr_add_link(_adr_file(target)[1], reverse_link, _adr_file(dst)[1] )
                except:
                    # error message, print even if verbosity is off
                    print("failed to process -l option. Error in argument formatting?")


    return(dst)

# Write ADR number in filename and header
def adr_write_number_and_header(dst,adr_index,adr_title=None):
    test=''
    # open file for appending and reading and replacing
    # https://kaijento.github.io/2017/05/28/python-replacing-lines-in-file/
    for line in fileinput.input(dst, inplace=True):
        if fileinput.filelineno() == 1:
            test = line
            # first replace number
            line = '# '+ str(int(adr_index)) +'. ' + test.split('.',1)[1]
            # now add title if needed
            if (adr_title != None):
                #insert title with one capital at the start
                line = line.split('.',1)[0] + '. ' + adr_title.replace('-',' ').capitalize()
            print(line,end='\n')
        elif fileinput.filelineno() == 3:
            # https://www.programiz.com/python-programming/datetime/current-datetime
            today = date.today()
            print('Date: ' + today.strftime("%Y-%m-%d") )
        elif fileinput.filelineno() == 7:
            print('Accepted', end='\n')
        else:
        #keep existing content 
            print(line, end='')
    fileinput.close()
    #print(test)

# add a link to another adr

def _adr_add_link(source, linktype, target):
    source_adr = _adr_file(source)[1]
    target_adr = _adr_file(target)[1]

    stats = "find_status"
    adr_print('_adr_add_link; source_adr = ' + source_adr + ' target_adr is ' + target_adr )
    link_text = '\n' + linktype + ' [' + _adr_title(target) +'](' + os.path.basename(target_adr)+')\n'
    # Careful! No adr_print stuff in this section, because it will end up
    # in the adr, as fileinput takes over stdout
    for line in fileinput.input(source_adr, inplace=True):
        if stats == "find_status":
            #try to find ## Status at start of line
            if line.find('## Status',0) == 0:
                stats = "in status"
            print(line, end='')
            #TODO, using _adr_title_ here causes printing of debug info in ADR file.
        elif stats == "in status":
            print(link_text + line, end='')
            stats = "copy all"
        elif stats == "copy all":
            print(line, end='')
        else:
            print(line, end='')
    fileinput.close()

# This is a very ugly state machine, based on the original awk application in adr-tools
# Probably it can be rewritten much better by someone skilled in the art of Python.
# Purpose of the function is to remove the status 'status' from the adr file. As far as I can judge, this 
# is only used in adr-new, to remove the 'Accepted' status.

def _adr_remove_status(status, adr):
    stats = "find_status"
    adr_print('_adr_remove_status; status = ' + status + ' adr is ' + adr )
    for line in fileinput.input(adr, inplace=True):
        if stats == "find_status":
            #try to find ## Status at start of line
            if line.find('## Status',0) != -1:
                #adr_print('_adr_remove_status, ## Status found in '+ str(fileinput.lineno()))
                stats = "in status"
            print(line, end='')
        elif stats == "in status":
            # break if a new header is found
            if '##' in line:
                stats = "copy all"
                print(line, end='')
            # if requested status is at the start of the line
            elif line.find(status + '\n',0) != -1:
                #adr_print('_adr_remove_status; found ' + status )
                #remove contents
                print('',end='')
                stats = "after removal"
            else:
                print(line, end='')
        elif stats == "after removal":
            # meant to remove trailing empty line if needed. Not sure how to implement.
            if line.isalnum():
                print(line, end='')
            else:
                #remove whitespace
                print('',end='')
            stats = "copy all"
        else:
            print(line, end='')
    fileinput.close()

def _adr_dir():
    newdir = dir = os.getcwd()

# confuscated do-while
# https://www.javatpoint.com/python-do-while-loop
    while True:
        adr_print('_adr_dir: ' + dir)
        dir_docadr = os.path.join(dir , 'doc/adr')
        path_adrdir = os.path.join(dir , '.adr-dir')
        if (os.path.isdir(dir_docadr)):
            adr_print('_adr_dir, found /doc/adr in ' + dir_docadr )
            newdir = dir_docadr
            break
        elif (os.path.isfile(path_adrdir)):
            adrdir_directory=os.path.join(dir,find_alternate_dir(dir))
            adr_print('_adr_dir, found .adr_dir, referring to ' + adrdir_directory)
            newdir = adrdir_directory
            break
        # https://stackoverflow.com/questions/9856683/using-pythons-os-path-how-do-i-go-up-one-directory
        # Go up one directory
        newdir = os.path.dirname(dir)
        # If you can't go up further, you've reached the root.
        if newdir ==  dir:
            #default value is 'doc/adr/'
            newdir = 'doc/adr/'
            break
        
        dir = newdir
    # original adr-tools returns relative path w.r.t path from which the function was called.
    return(os.path.relpath(newdir,os.getcwd()))


# adr_file returns first file that contains the text. Since list_of_adrs returns a 
# sorted list, searching for the ADR number will generally yield the correct ADR. 
# 
def _adr_file(adr_text):
    list_of_adrs = adr_list(_adr_dir())
    # string or integer input 
    if type(adr_text) is int:
        adr_text = str(adr_text)
    for adr in list_of_adrs:
        #adr_print("_adr_file; adr = " + adr)
        if adr_text in adr:
            adr_print("_adr_file; found " + adr_text + " in " + adr)
            return (int(os.path.basename(adr)[0:4]),adr)
    adr_print("_adr_file; no record found containing " + adr_text)
    return (0,"")


# adr_title returns first line of ADR, without the # and without newline at the end
def _adr_title(text):
    # adr_file returns tuple with number and string
    adr = _adr_file(text)
    adr_print('_adr_title; number is ' + str(adr[0]) + ', adr is '+  adr[1] + 'path is '+ os.getcwd())
    with open(adr[1],'r') as f:
        adrline = f.readline()   
        adr_print('_adr_title; line is ')
    # Strip markdown header 1 (#), and strip newline
    return(adrline[2:-1])

# adr_list returns a sorted list of all ADRs

def adr_list(dir):
    from os import listdir
    from os.path import isfile, join

    adr_dir = _adr_dir()
    adr_list = list()
    adr_print('adr_list; adr directory is '+ adr_dir)
    onlyfiles = [f for f in listdir(adr_dir) if isfile(join(adr_dir, f))]
    # make list of adr files. All files *not* starting with 4 numbers are skipped.
    for file in onlyfiles:
        try:
            # if this fails, the 'except' will be executed, and actions past this line will be skipped 
            adr_list.append(file)
        except: 
            adr_print (file + " is not a valid ADR filename")
            None
    adr_paths = list()
    # create full path adr list
    for adr in sorted(adr_list):
        adr_paths.append(os.path.join(adr_dir,adr))
    return adr_paths
