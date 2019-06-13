from multiprocessing import Pool
import multiprocessing
import glob
import os
from tqdm import tqdm

def single_run(input_tuple):
    command,x,y = input_tuple
    try:
        os.system("{command} {x} {y}".format(command = input_tuple[0],
                                             x = input_tuple[1],
                                             y =input_tuple[2]))
        result = 1
    except:
        result = -1
    return result

class BatchCommand(object):
    def __init__(self,command, source_dir, target_dir):
        self.set_command(command)
        self.set_source_dir(source_dir)
        self.set_target_dir(target_dir)

    def set_command(self,command):
        self.command = command

    def set_source_dir(self,source_dir):
        self.source_dir = source_dir
        self.source_dir_list = glob.glob("{}{}*".format(source_dir,os.path.sep))

    def set_target_dir(self,target_dir):
        self.target_dir = target_dir

    def run(self,n_cpu = None):
        input_tuples = []
        target_dir = self.target_dir
        command = self.command
        source_dir_list = self.source_dir_list
        for f in source_dir_list:
            input_tuples.append((command, f, target_dir))


        if n_cpu == None:
            n_cpu = multiprocessing.cpu_count()
        with Pool(n_cpu) as p:
                results = list(tqdm(p.imap(single_run, input_tuples), total=len(input_tuples)))
        return results

if __name__ == "__main__":
    bc = BatchCommand(command="cp ",source_dir="./",target_dir="../")
    print(bc.run())
    