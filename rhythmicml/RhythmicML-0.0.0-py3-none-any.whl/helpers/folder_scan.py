from os import scandir as scanDir, access, W_OK;
from os.path import abspath as absolutePath, isdir as isDir, expanduser as expandUser;
from rhythmic.general import faultReturnHandler;
from . import configuration;

@faultReturnHandler
def scanFolder(folder_to_scan = "~", show_started_with_dot = False, look_level_above = True, exclusions = False):
    """
     scanFolder(folder_to_scan = "~", show_started_with_dot = False, look_level_above = True, exclusions = False)

     show_started_with_dot: sow files and folders with names started with '.'
     look_level_above: check if there is accessible '..' path and show when there is.

     exclusions = a list of strings with base names to exclude from returned list

     Shows all the items in the folder the user has permission to write to.
    """

    if folder_to_scan == "~":
        the_folder = expandUser("~");
    else:
        the_folder = folder_to_scan;

    absolute_path = absolutePath(the_folder);

    folder_contents = [];

    if look_level_above:
        level_above = absolute_path[0:absolute_path.rfind("/")];

        if ( (isDir(level_above)) and (access(level_above, W_OK)) ):
            folder_contents.append(
                {
                    "absolute_path": level_above,
                    "base_name": "< .. >",
                    "is_dir": True
                }
            );

    the_folder_scan = scanDir(absolute_path);

    for item in sorted(the_folder_scan, key = lambda the_item: the_item.name):

        if item.name.startswith("."):
            inclusion = show_started_with_dot;
        else:
            inclusion = True;

        if exclusions:
            if item.name in exclusions:
                inclusion = False;

        if ( inclusion and access(item.path, W_OK) ):
            folder_contents.append(
                {
                    "absolute_path": item.path,
                    "base_name": item.name,
                    "is_dir": item.is_dir(),
                    "last_modified_time": item.stat().st_mtime
                }
            );

    return folder_contents;

@faultReturnHandler
def scanModelFolder(folder, descend_level = 3):

    if descend_level == 0:
        return False;

    files_list = [];
    current_folder_contents = scanFolder(folder, show_started_with_dot = True, look_level_above = False, exclusions = [configuration["storage_folder_name"]]);

    for item in current_folder_contents:
        if item["is_dir"]:
            item_scan = scanModelFolder(item["absolute_path"], descend_level - 1);
            if item_scan:
                files_list.extend(item_scan);
        else:
            files_list.append(
                {
                    "file_path": item["absolute_path"], 
                    "last_modified_time": item["last_modified_time"]
                }
            );

    return files_list;
