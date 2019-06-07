import os
import sys
import json
import argparse

def build_file(file, level=None):
    file = {
        "type": "file",
        "name": os.path.basename(file),
        "size": os.lstat(file).st_size
    }

    return file

def build_dir(directory, level=None):
    dir = {
        "type": "directory",
        "name": os.path.basename(directory),
        "size": 0,
    }

    if(level is None or level > 0):
        dir["children"] = build(directory, level-1 if level is not None else level)
        for child in dir["children"]:
            dir["size"] += child["size"]

    return dir

def build(directory, level=None):
    try:
        (root, dirs, files) = next(os.walk(directory))
    except StopIteration:
        print('lson.py: error: encountered permission denied')
        exit()
    obj = []
    for dirname in dirs:
        dir = {
            "type": "directory",
            "name": dirname,
            "size": 0,
        }
        if(level is None or level > 0):
            dir["children"] = build('{}/{}'.format(root, dirname), level-1 if level is not None else level)
            for child in dir["children"]:
                dir["size"] += child["size"]

        obj.append(dir)

    for file in files:
        obj.append({
            "type": "file",
            "name": file,
            "size": os.lstat('{}/{}'.format(root, file)).st_size
        })
    return obj

def main():
    parser = argparse.ArgumentParser(description='Display directory structure in json format.')
    parser.add_argument('file', help='file or folder to be the root of the directory structure')
    parser.add_argument('-l', '--level', type=int, help='number of levels deep the directory structure should go')
    args = parser.parse_args()

    print(args)

    if(not os.path.exists(args.file)):
        print("lson.py: {}: No such file or directory".format(args.file))
        exit()
    
    dir_structure = None
    if(os.path.isfile(args.file)):
        dir_structure = build_file(args.file, args.level)
    if(os.path.isdir(args.file)):
        dir_structure = build_dir(args.file, args.level)
    
    print(json.dumps(dir_structure, indent=2))

if __name__ == '__main__':
    main()