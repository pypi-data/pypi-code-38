from rhythmic.db import SQLiteDB;
from rhythmic.general import faultReturnHandler;
from os.path import expanduser as expandUser;
from . import configuration;

@faultReturnHandler
def getNameFromPath(absolute_path):
    if absolute_path == "~":
        directory = expandUser("~");
    else:
        directory = absolute_path;

    return directory[directory.rfind('/') + 1:]

@faultReturnHandler
def uniqueName(the_name):

    unique_name = the_name;

    probe = [None]
    i = 0;
    
    with SQLiteDB(configuration["db_file_name"]) as db:
        while len(probe) !=0:
            probe = db.execute("SELECT model_name FROM models_table WHERE model_name = '{}'".format(unique_name));
            if len(probe) !=0:
                i += 1;
                unique_name = "{}_{}".format(the_name, str(i)); 
    
    return unique_name;