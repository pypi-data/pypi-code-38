import glob
import soundfile as sf
import numpy as np
import librosa
import os
from shutil import copyfile
import random

def list_all_files(dir_name):
    file_list = []
    for file in list(glob.iglob(dir_name+'/**/*', recursive=True)):
        if os.path.isfile(file):
            file_list.append(file)
    return file_list

def list_all_dirs(dir_name):
    file_list = []
    for file in list(glob.iglob(dir_name+'/**/*', recursive=True)):
        if os.path.isdir(file):
            file_list.append(file)
    return file_list

def sample_to_new_dir(src_dir,percentage):
    src_abs_dir = os.path.abspath(src_dir)
    current_dir_name = os.path.basename(src_abs_dir)
    trg_dir_name = ''.join([current_dir_name,'_',str(percentage)+'/'])
    traget_dir = src_abs_dir.replace(current_dir_name,trg_dir_name)

    dirs = list_all_dirs(src_dir)
    for d in dirs:
        try:
            d = d.replace(src_dir,traget_dir)
            os.makedirs(d)
        except:
            pass
    res = list_all_files(src_dir)
    random.shuffle(res)

    res_small = res[:int(percentage*len(res))]
    for i in res_small:
        traget_name = i.replace(src_dir,traget_dir)
        copyfile(i,traget_name)
    return traget_dir


if __name__ == "__main__":
    for i in range(1,10):
        percentage = i/10.0
        sample_to_new_dir('./',percentage)
    ##print(res)