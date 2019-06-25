import os, sys
import modules.logging.logging as logging_config
import json
import logging

# root dir
root_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

#logs dir full path
logs_dir_full_path =""

#logs dir name
logs_dir_name ="logs"

#configs dir full path
configs_dir_full_path =""

#configs dir name
configs_dir_name ="configs"


#data dir full path
data_dir_full_path =""

#data dir name
data_dir_name ="data"

# engine version code
version_code = "0.1"

#build version code
build_version_code =-1

# engine name
engine_name = "HoneyBoard"

# system name
system_name = "HoneyBoard System"

# show all info when running
show_system_info_on_start = False

#logging config file name
logging_config_file_name = "logging.yaml"

#logging config file full pat
logging_config_file_full_path = ""


#buildcode file name
build_code_file_name = "build_code.json"

#logging config file full pat
build_code_file_full_path = ""


#test file name
test_file_name = 'CHARON_EXPORT_ТОО Беркут Логистик_20190228165209890350.gz'
#test file full path
test_file_name_full_path =''

#temp dir full path
temp_dir_full_path =""

#temp dir name
temp_dir_name ="temp"


# all versions
versions_container = [
    ["0.1", "Pikeman"],
    ["0.2", "Halberdier"],
    ["0.3", "Archer"],
    ["0.4", "Marksman"],
    ["0.5", "Griffin"],
    ["0.6", "Royal Griffin"],
    ["0.7", "Swordsman"],
    ["0.8", "Crusader"],
    ["0.9", "Monk"],
    ["1.0", "Zealot"],
    ["1.1", "Cavalier"],
    ["1.2", "Champion"],
    ["1.3", "Angel"],
    ["1.4", "Archangel"],
    ["1.5", "Green Dragon"],
    ["1.6", "Gold Dragon"],
    ["1.7", "Giant"],
    ["1.8", "Titan"],
    ["1.9", "Bone Dragon"],
    ["2.0", "Ghost Dragon"],
    ["2.1", "Red Dragon"],
    ["2.2", "Black Dragon"],
    ["2.3", "Behemoth"],
    ["2.4", "Ancient Behemoth"],
    ["2.5", "Hydra"],
    ["2.6", "Chaos Hydra"],
    ["2.7", "Firebird"],
    ["2.8", "Phoenix"]
]


# --------------- methods---------------#
#load and increase build version
def load_build_version():
    try:

        with open(build_code_file_full_path) as f:
            data = json.load(f)
            global build_version_code
            build_version_code= int(data["build_version_code"])
            build_version_code+=1
            data["build_version_code"] = build_version_code

        with open(build_code_file_full_path, "w") as jsonFile:
            json.dump(data, jsonFile)
            t=0
        pass
    except Exception as e:
        pass

def get_version_name():
    try:
        versions = versions_container
        current_version_code = version_code

        for version in versions:
            if (version[0] == current_version_code):
                return version[1]

        pass
    except Exception as e:
        return str(e)
        pass

#join system paths
def join_path(paths):
    try:
        path = os.path.join(*paths)
        path =os.path.normpath(path)
        # path =os.path.normcase(path)
        return path
    except Exception as e:
        return str(e)


# show start info
def show_system_info():
    try:
        print("Start init configuration")
        print("Root dir : "+root_dir)
        print("System name : "+system_name)
        print("Engine name : "+engine_name)
        print("Engine version code: "+version_code)
        print("Engine version name: "+get_version_name())
        print("Build version code: "+str(build_version_code))


        pass
    except Exception as e:
        pass

#check single dir
def check_single_dir(dir_path):
    try:
        dir_exists = os.path.exists(dir_path)

        if (dir_exists==False):
            os.mkdir(dir_path)
            logging.info("Create directory "+dir_path)
    except Exception as e:
        logging.error(str(e))



#check system dirs
def check_dirs():
    try:
        check_single_dir(configs_dir_full_path)
        check_single_dir(logs_dir_full_path)
    except Exception as e:
        logging.error(str(e))

#config system paths
def config_paths():
    try:
        global configs_dir_full_path
        configs_dir_full_path = join_path([root_dir,configs_dir_name])

        global logging_config_file_full_path
        logging_config_file_full_path =join_path([configs_dir_full_path,logging_config_file_name])

        global build_code_file_full_path
        build_code_file_full_path = join_path([configs_dir_full_path,build_code_file_name])

        global logs_dir_full_path
        logs_dir_full_path = join_path([root_dir,logs_dir_name])

        global data_dir_full_path
        data_dir_full_path = join_path([root_dir, data_dir_name])

        global temp_dir_full_path
        temp_dir_full_path = join_path([root_dir, temp_dir_name])

        global test_file_name_full_path
        test_file_name_full_path = join_path([data_dir_full_path, test_file_name])

        check_dirs()
    except Exception as e:
        logging.error(str(e))

# init config
def init_config():
    try:
        config_paths()
        load_build_version()
        logging_config.setup_logging(default_path=logging_config_file_full_path)

        if (show_system_info_on_start == True):
            show_system_info()

        logging.info("Config init successful")

    except Exception as e:
        logging.error(str(e))
        pass
