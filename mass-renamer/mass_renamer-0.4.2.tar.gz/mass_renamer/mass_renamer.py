# Code by mrniceguy127
# github.com/mrniceguy127

import os
import sys
import getopt
import re
from shutil import copy
from mass_renamer.special_chars import special_chars

def merge(left, right):
    merged = []
    
    while len(left) != 0 and len(right) != 0:
        if left[0] <= right[0]:
            merged.append(left[0])
            left = left[1:]
        else:
            merged.append(right[0])
            right = right[1:]

    while len(left) != 0:
        merged.append(left[0])
        left = left[1:]
    while len(right) != 0:
        merged.append(right[0])
        right = right[1:]

    return merged

def merge_sort(unsorted):
    if len(unsorted) <= 1:
        return unsorted

    left = []
    right = []

    for i in range(len(unsorted)):
        if i < (len(unsorted) // 2):
            left.append(unsorted[i])
        else:
            right.append(unsorted[i])

    left = merge_sort(left)
    right = merge_sort(right)

    return merge(left, right)

def parse_options(options):
    options_dict = {
        "to_replace": '',
        "replace_with": '',
        "path": './',
        "replace_what": 'file',
        "use_regex": False,
        "verbose": False,
        "num_width": 0
    }

    for option in options:
        option_name = option[0]
        args = option[:]

        if option_name == '-q':
            options_dict["to_replace"] = args[1]
        elif option_name == '-r':
            options_dict["replace_with"] = args[1]
        elif option_name == '-p':
            options_dict["path"] = args[1]
        elif option_name == '-t':
            options_dict["replace_what"] = args[1]
        elif option_name == '-x':
            options_dict["use_regex"] = True
        elif option_name == '-v':
            options_dict["verbose"] = True
        elif option_name == '-w':
            width = 0

            try:
                width = int(args[1])
            except:
                print('Error parsing -w option from command. Please verify that you provided a valid integer.')
                print('Exiting...')
                quit(0)

            options_dict["num_width"] = width

    return options_dict

def get_matching_items(items, options):
    matching_items = []

    if options['use_regex']:
        matching_items = [item for item in items if re.search(options['to_replace'], item)]
    else:
        matching_items = [item for item in items if options['to_replace'] in item]

    return matching_items

def get_num_with_width(num, width):
    new_num = str(num)
    if width - len(new_num) > 0:
      new_num = ('0' * (width - len(new_num))) + new_num
    return new_num

def rename_items(items, options):
    items_abs = []
    new_items_abs = []
    curr_item = "NONE"

    try:
        matching_items = merge_sort(get_matching_items(items, options))
        if len(matching_items) > 0:
            rep_dir = os.path.join(os.path.abspath(options["path"]), 'mass-renamed')
            if not os.path.isdir(rep_dir):
                os.mkdir(rep_dir)
            print("Renaming file 0/0...\r", end='')
            for i in range(0, len(matching_items)):
                item = matching_items[i]

                if not options["verbose"]:
                    print("Ranaming file %d/%d..." % (i + 1, len(matching_items)), ' ' * 10, '\r',  end='')

                curr_item = os.path.join(os.path.abspath(options["path"]), item)
                abs_path = curr_item
                new_item = item[:]

                if not options["use_regex"]:
                    new_item = item.replace(options["to_replace"], options["replace_with"])
                else:
                    new_item = re.sub(options["to_replace"], options["replace_with"], item)

                new_item = new_item.replace(special_chars["0_index"], get_num_with_width(i, options["num_width"]))
                new_item = new_item.replace(special_chars["1_index"], get_num_with_width(i + 1, options["num_width"]))
                new_item = new_item.replace(special_chars["original_name"], item)
                new_item = new_item.replace(special_chars["extension"], re.sub('.*(\.+)', '', item))

                new_abs_path = os.path.join(os.path.abspath(options["path"]) + '/mass-renamed', new_item)

                copy(abs_path, new_abs_path)

                if options["verbose"]:
                    print('RENAMED (%d): %s' % (i + 1, abs_path))
                    print('TO:', new_abs_path)

                items_abs.append(abs_path)
                new_items_abs.append(new_abs_path)

            print()
            print('Success!')
        else:
            print("No matching files or directories found.")

    except OSError as e:
        valid = False

        print(e)

        while not valid:
            print("Failed to replace all file/directory names.", "Failed at \"%s\"." % curr_item)
            print("Would you like to return the files to their original names (YES/NO)?")
            answer = ""
            try:
                answer = input()
            except:
                print("Error getting your answer...")
                quit(0)

            if answer == 'YES':
                valid = True
                i = 0
                try:
                    for item in new_items_abs:
                        curr_item = new_items_abs[i]
                        os.replace(item, items_abs[i])
                        i += 1
                    print("Successfully returned items to their original names!")
                except OSError:
                    print("Failed to return all items to their original names.", "Failed at \"%s\"." % curr_item)
            elif answer == 'NO':
                valid = True
                print("Did not return files to their original names.")
            else:
                print('Invalid response. Please answer "YES" or "NO".')

        quit(0)

def run():
    args = [
            '-x', '-v', '-w', '-p', '-q', '-r', '-t',
            'use_regex', 'verbose_logging', 'num_width', 'path', 'query', 'replace_with', 'item_type'
            ]

    options = {}

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'xvw:p:q:r:t:')

        options = parse_options(optlist)
    except getopt.GetoptError as err:
        print(err)
        print('Exiting...')
        quit(0)


    if options['to_replace'] == '':
        print("You must pass the -q option. This option must also be passed at least one character as an argument.")
    else:
        try:
            files = [f for f in os.listdir(options["path"]) if os.path.isfile(os.path.join(options["path"], f))]
            dirs = [f for f in os.listdir(options["path"]) if os.path.isdir(os.path.join(options["path"], f))]

            if options["replace_what"] == 'file':
                rename_items(files, options)
            elif options["replace_what"] == 'dir':
                rename_items(dirs, options)
            elif options["replace_what"] == 'both':
                rename_items(dirs + files, options)
            else:
                print('Invalid argument "' + options["replace_what"] + '" for option ' + '"-t"' + '.')

        except OSError:
            print('Error accessing the path "' + options["path"] + '".')
            print("Make sure you have proper access rights to this directory and that it exists.")

    print("Exiting...")

if __name__ == "__main__":
    run()
