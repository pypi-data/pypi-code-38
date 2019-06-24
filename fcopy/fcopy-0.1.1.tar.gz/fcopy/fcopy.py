#!/usr/bin/env python
'''
Copy utility .

Homepage: https://github.com/e2raptor/fcopy

Copyright (C) 2019 Eduardo Pina Fonseca

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import os
import sys
import json
import shutil
import threading
from datetime import datetime
'''
The version of this script as an int tuple (major, minor, patch).
'''
__version__ = (0, 1, 1)
__version_str__ = '.'.join([str(__version__[0]), str(__version__[1]), str(__version__[2])])


# Global variables
module_config = os.path.dirname(__file__)+ '/config-path'
json_config_path = False
watchlist = []

def exists(path, log=True):
    if os.path.exists(path):
        return True
    else:
        if log:
            print('Path {} is incorrect'.format(path))
    return False


def getConfig():
    fconf = open(module_config)
    json_config_path = fconf.read()
    fconf.close()

    try:
        conf_file = open(json_config_path)
        config = json.load(conf_file)
        conf_file.close()
        return config
    except (IOError, OSError):
        print('There was an error reading the configuration file')
    return False

def copyFile(source, destination, isWatch=False):
    operation = "Updated" if os.path.exists(destination["path"]) else "Copied"
    key = "path" if isWatch else "file"
    if exists(source["path"]):
        try:
            shutil.copyfile(source["path"], destination["path"])  
            print("{}: {} => {}".format(operation, source[key], destination[key]))
        except shutil.SameFileError:
            pass
        except FileNotFoundError:
            print('Path {} is incorrect'.format(destination[key]))

def update(tasklist, watcher=False, type="group"):
    config = getConfig()

    if config:
        matchlist = []

        for name in tasklist:
            matchlist.extend(list(filter(lambda r: r[type] == name, config))) 

        #Proceed to copy
        for task in matchlist:
            src = task["source-path"]
            dest = task["target-path"]

            if (exists(src) and exists(dest)):
                print("{} => {}".format(src, dest))
                for fi in task["files"]:
                    source_file = {
                        "base": src,
                        "path": os.path.join(src, fi["name"]),
                        "file": fi["name"]
                    } 
                    dest_file = { 
                        "base": dest,
                        "path": os.path.join(dest, fi["as"]),
                        "file": fi["as"]
                    } 
                    copyFile(source_file, dest_file)
                    watchlist.append({
                        "src": source_file,
                        "dest": dest_file
                    })
                print()
            
                if watcher:
                    print("Watching for changes (Hold Ctrl+C to exit)...")
                    watch()

def watch():
    threading.Timer(1, watch).start()
    to_update = []
    for conf in watchlist:
        src = conf["src"]["path"]
        dest = conf["dest"]["path"]
        src_time = os.stat(src).st_mtime if exists(src, False) else 0
        dest_time = os.stat(dest).st_mtime if exists(dest, False) else 0
        if src_time > dest_time:
            to_update.append(conf)

    if len(to_update) > 0:
        print()
        print("Update: ", datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))
        for conf in to_update:
                copyFile(conf["src"], conf["dest"], True)
        print()
        print("Watching for changes (Hold Ctrl+C to exit)...")

def updateConfigPath(new_config):
    fconf = open(module_config, 'w')
    fconf.write(new_config)
    fconf.close
