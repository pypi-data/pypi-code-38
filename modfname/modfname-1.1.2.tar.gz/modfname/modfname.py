import sys
import os
import getpass

from os import stat
from pwd import getpwuid

__author__ = 'Yann Orieult'

# important constants:

# colors
CBRED = '\033[38;5;196;1m'
CBORANGE = '\033[38;5;202;1m'
CBGREEN = '\033[38;5;40;1m'
CBYELLOW = '\033[1;33m'
CBWHITE = '\033[1;37m'
CBPURPLE = '\033[1;35m'
CBBLUE = '\033[1;34m'
CBASE = '\033[0m'

COCCURRENCES = CBPURPLE
CFILE_PATHS = CBBLUE
CTEXT_FILES = CBWHITE


# indicator strings
INIT_STRINGS = ["--initial", "--init"]
LOWERCASE_STRINGS = ["--lowercase", "--lower"]
UPPERCASE_STRINGS = ["--uppercase", "--upper"]
DESTINATION_STRINGS = ["--destination", "--dest"]
SPECIFIC_STRINGS = ["--specific"]
LOCAL_STRINGS = ["--local"]
RECURSIVE_STRINGS = ["--recursive"]
PATHS_STRINGS = ["--paths"]
END_FLAG_STRINGS = ["--end_param", "--end"]

# supported short indicators
SUPPORTED_SHORT_INDICATORS = ['i', 'd', 's', 'l', 'r', 'p']


class Modifier(object):

    def __init__(self, input_parms):
        self.input_parms = input_parms
        self.nb_args = len(self.input_parms)
        self.args_not_used_indexes = list(range(self.nb_args))
        self.lowercase = False
        self.uppercase = False
        self.specific = True
        self.local = False
        self.recursive = False
        self.init_strs = []
        self.dest_str = None
        self.fpaths = []
        self.fpath = None
        self.nb_occs = [0, 0]  # [found, replaced]

    def treat_input_parms(self):

        for arg_index, arg in enumerate(self.input_parms):
            if arg.startswith("--"):
                if arg in INIT_STRINGS + DESTINATION_STRINGS + LOWERCASE_STRINGS + UPPERCASE_STRINGS + \
                        SPECIFIC_STRINGS + LOCAL_STRINGS + RECURSIVE_STRINGS + PATHS_STRINGS + END_FLAG_STRINGS:
                    if arg in LOWERCASE_STRINGS:
                        self.lowercase = True
                    if arg in UPPERCASE_STRINGS:
                        self.uppercase = True
                    if arg in SPECIFIC_STRINGS:
                        self.specific = True
                    elif arg in LOCAL_STRINGS:
                        self.local = True
                        self.specific = False
                    elif arg in RECURSIVE_STRINGS:
                        self.recursive = True
                        self.specific = False
                    elif arg in END_FLAG_STRINGS:
                        pass

                    elif arg_index < self.nb_args - 1:
                        if arg in INIT_STRINGS:
                            self._get_arg_list("init_str", arg_index)

                        if arg in DESTINATION_STRINGS:
                            self._get_dest_str(arg_index)

                        if arg in PATHS_STRINGS:
                            self._get_arg_list("paths", arg_index)

                    else:
                        ERROR("no parameter after %s indicator" % arg)
                        raise ValueError("needs a parameter after the %s indicator" % arg)

                    self.args_not_used_indexes.remove(arg_index)

                else:
                    ERROR("the indicator %s is not supported" % arg)
                    raise ValueError("please remove the %s parameter from the command" % arg)
            elif arg.startswith("-"):
                for short_ind in arg[1:]:
                    if short_ind not in SUPPORTED_SHORT_INDICATORS:
                        ERROR("the short indicator -%s is not supported" % short_ind)
                        raise ValueError("please remove the -%s short indicator from the command" % short_ind)
                    elif short_ind == 'i':
                        self._get_arg_list("init_str", arg_index)
                    elif short_ind == 'd':
                        self._get_dest_str(arg_index)
                    elif short_ind == 's':
                        self.specific = True
                    elif short_ind == 'l':
                        self.local = True
                        self.specific = False
                    elif short_ind == 'r':
                        self.recursive = True
                        self.specific = False
                    elif short_ind == 'p':
                        self._get_arg_list("paths", arg_index)

                self.args_not_used_indexes.remove(arg_index)

    def _get_dest_str(self, arg_index):
        next_arg = self.input_parms[arg_index + 1]
        if next_arg.startswith("-"):
            self.dest_str = ""
        else:
            self.dest_str = next_arg
            self.args_not_used_indexes.remove(arg_index + 1)

    def _get_arg_list(self, var, ref_arg_index):

        for arg_index, arg in enumerate(self.input_parms[ref_arg_index + 1:]):
            if arg.startswith("-"):
                return
            else:
                if var == "init_str":
                    self.init_strs.append(arg)
                elif var == "paths":
                    self.fpaths.append(arg)
                self.args_not_used_indexes.remove(ref_arg_index + 1 + arg_index)

    def check_integrity_inputs(self):
        self._check_mode_integrity()
        self._check_modifier_integrity()

    def _check_mode_integrity(self):
        nb_mode_on = 0
        for mode in [self.specific, self.local, self.recursive]:
            if mode:
                nb_mode_on += 1
        if nb_mode_on != 1:
            ERROR("the current modfname mode is not correct:\n\t\tspecific: %s\tlocal: %s\trecursive: %s" % (
                self.specific, self.local, self.recursive))
            raise ValueError("check the input parameters to get a correct modfname mode")

    def _check_modifier_integrity(self):
        if self.lowercase:
            if self.uppercase or self.init_strs or self.dest_str:
                self._conf_error_msg()
        elif self.uppercase:
            if self.lowercase or self.init_strs or self.dest_str:
                self._conf_error_msg()

        elif self.init_strs:
            if self.lowercase or self.uppercase or self.dest_str is None:
                self._conf_error_msg()

        elif self.dest_str:
            if self.lowercase or self.uppercase or not self.init_strs:
                self._conf_error_msg()
        else:
            self._conf_error_msg()

    def _conf_error_msg(self):
        ERROR("modfname conf is not correct:\n\tlowercase: %s\n\tuppercase: %s\n\tinit_strs: "
              "%s\n\tdest_str: %s" % (self.lowercase, self.uppercase, self.init_strs, self.dest_str))
        raise ValueError("check the input parameters to get a correct modfname conf")

    def get_final_params(self):

        if not self.lowercase and not self.uppercase and not self.init_strs and not self.dest_str and len(self.args_not_used_indexes) > 2:
            self.init_strs.append(self.input_parms[0])
            self.dest_str = self.input_parms[1]
            for arg_left in self.input_parms[2:]:
                self.fpaths.append(arg_left)
            self.args_not_used_indexes = []

        elif not self.fpaths:
            if not self.args_not_used_indexes:
                ERROR("arguments are missing ... please review the command syntax")
                raise ValueError("the file path arg is not defined")
            for arg_not_used_index in self.args_not_used_indexes:
                self.fpaths.append(self.input_parms[arg_not_used_index])
                self.args_not_used_indexes.pop()
        elif not self.lowercase and not self.uppercase and self.dest_str is None:
            if not self.args_not_used_indexes:
                ERROR("arguments are missing ... please review the command syntax")
                raise ValueError("the destination string arg is not defined")
            self.dest_str = self.input_parms[-1]
            self.args_not_used_indexes.pop()
        elif not self.lowercase and not self.uppercase and not self.init_strs:
            if not self.args_not_used_indexes:
                ERROR("arguments are missing ... please review the command syntax")
                raise ValueError("the initial strings arg is not defined")
            for arg_not_used_index in self.args_not_used_indexes:
                self.init_strs.append(self.input_parms[arg_not_used_index])
                self.args_not_used_indexes.pop()

        if self.args_not_used_indexes:
            ERROR("too much arguments entered ... please review the command syntax")
            raise ValueError("the args %s have not been used" % self.args_not_used_indexes)

    def mod_fnames(self, fpath):

        self._check_user_perm(fpath)

        fpath = self._init_strs_to_dest_str(fpath)

        if os.path.isdir(fpath):
            fpath = self._init_strs_to_dest_str(fpath)
            if self.recursive:
                try:
                    list_files_and_folders = os.listdir(fpath)

                except PermissionError:
                    return
                for file_or_folder_name in list_files_and_folders:
                    self.mod_fnames(_concat_paths(fpath, file_or_folder_name))

    @staticmethod
    def _check_user_perm(fpath):
        current_user = getpass.getuser()
        owner_f = getpwuid(stat(fpath).st_uid).pw_name
        if owner_f != current_user:
            WARNING("the file " + CFILE_PATHS + "%s" % fpath + CBASE + " is owned by " + CFILE_PATHS + "%s"
                    % owner_f + CBASE + ", might be necessary to manage its permissions")

    def _init_strs_to_dest_str(self, path):
        base_path = os.path.dirname(path)
        fname = os.path.basename(path)
        fname_origin = fname

        if self.lowercase or self.uppercase:
            self.nb_occs[0] += 1
            fpath = _concat_paths(base_path, fname)
            print(CFILE_PATHS + "%s" % fpath + CBWHITE)
            new_fname = None
            if self.lowercase:
                new_fname = fname.lower()
            if self.uppercase:
                new_fname = fname.upper()

            mod_fname_check = input("\tchange " + COCCURRENCES + "%s" % fname + CBWHITE + " to " + COCCURRENCES +
                "%s" % new_fname + CBWHITE + " ?\n\t\t[ENTER] to proceed\t[sS] to skip\t[aA] to abort\n")

            if mod_fname_check == "":
                fname = new_fname
                self.nb_occs[1] += 1
            elif mod_fname_check in ["a", "A"]:
                _abort_process()
            else:
                INFO(CFILE_PATHS + "%s" % fpath + CBWHITE + " not changed")

        elif self.init_strs:
            for init_str in self.init_strs:
                if init_str in fname:
                    self.nb_occs[0] += 1
                    fpath = _concat_paths(base_path, fname)
                    print(CBASE + "\nthere is " + COCCURRENCES + "\"%s\"" % init_str + CBASE + " in " + CFILE_PATHS + "%s" % fpath + CBWHITE)

                    new_fname = fname.replace(init_str, self.dest_str)
                    mod_fname_check = input("\tchange " + COCCURRENCES + "%s" % fname + CBWHITE + " to " + COCCURRENCES +
                        "%s" % new_fname + CBWHITE + " ?\n\t\t[ENTER] to proceed\t[sS] to skip\t[aA] to abort\n")

                    if mod_fname_check == "":
                        fname = new_fname
                        self.nb_occs[1] += 1
                    elif mod_fname_check in ["a", "A"]:
                        _abort_process()
                    else:
                        INFO(CFILE_PATHS + "%s" % fpath + CBWHITE + " not changed")

        else:
            self._conf_error_msg()

        if fname != fname_origin:
            new_path = _concat_paths(base_path, fname)
            os.rename(path, new_path)
            OK(CFILE_PATHS + "%s/" % os.path.dirname(new_path) + COCCURRENCES + "%s" % fname + CFILE_PATHS + "\tdone")
            path = new_path

        return path

    def occs_summary(self):
        if self.nb_occs[0] == 0:
            print(CFILE_PATHS + "\n\t0" + CBASE + " occurrence of " + COCCURRENCES + "%s" % self.init_strs + CBASE + " found")
        elif self.nb_occs[0] == 1:
            print(CFILE_PATHS + "\n\t1" + CBASE + " occurrence of " + COCCURRENCES + "%s" % self.init_strs +
                  CBASE + " found and " + CFILE_PATHS + "%s" % self.nb_occs[1] + CBASE + " replaced")
        else:
            print(CFILE_PATHS + "\n\t%s" % self.nb_occs[0] + CBASE + " occurrences of " + COCCURRENCES + "%s" % self.init_strs
                  + CBASE + " found and " + CFILE_PATHS + "%s" % self.nb_occs[1] + CBASE + " replaced")


def _abort_process():
    print(CBYELLOW + "\n\n\t\t\taborted ...\n\t\t\t\tSee you later\n" + CBASE)
    exit(0)


def _concat_paths(root_path, final_path):
    if root_path.endswith('/') and final_path.startswith('/'):
        global_path = root_path[:-1] + final_path
    elif (root_path.endswith('/') and not final_path.startswith('/')) or (not root_path.endswith('/') and final_path.startswith('/')):
        global_path = root_path + final_path
    else:
        global_path = root_path + '/' + final_path
    return global_path


def _check_folder_path_exists(folderpath):
    if not os.path.isdir(folderpath):
        WARNING(CFILE_PATHS + " %s " % folderpath + CBASE + "folder doesn't exist")
        raise ValueError("the directory path to apply %s doesn't exist, you may review it" % folderpath)


def _check_path_exists(path):
    if not os.path.exists(path):
        WARNING(CFILE_PATHS + " %s " % path + CBASE + "path doesn't exist")
        return False
    return True


def check_help_request(arguments):
    if len(arguments) == 1 and (arguments[0] == "-h" or arguments[0] == "--help"):
        README_path = "/usr/lib/modfname/README.md"

        f = open(README_path, 'r')
        print(CFILE_PATHS + "\n\t#######      modfname documentation      #######\n" + CBWHITE)

        for line in f:
            if line == "```sh\n" or line == "```\n" or line == "<pre>\n" or line == "</pre>\n":
                continue

            line = line.replace('```sh', '').replace('```', '').replace('<pre>', '').replace('</b>', '').\
                replace('<b>', '').replace('<!-- -->', '').replace('<br/>', '').replace('```sh', '').\
                replace('***', '').replace('***', '').replace('**', '').replace('*', '')

            print(" " + line, end='')
        print(CBASE)
        exit()


def OK(msg=""):
    print(CBGREEN + "\n\t[MODFNAME] " + CBASE + msg)


def INFO(msg=""):
    print(CBWHITE + "\n\t[MODFNAME] " + CBASE + msg)


def WARNING(msg=""):
    print(CBORANGE + "\n\t[MODFNAME] " + CBASE + msg)


def ERROR(msg=""):
    print(CBRED + "\n\t[MODFNAME] " + CBASE + msg)


def skipped():
    print(CBBLUE + "\n\t\t\tskipped\n\n" + CBASE)


def check_nb_parameters(args):
    if len(args) < 3:
        ERROR("no enough arguments")
        raise ValueError("no enough arguments. Needs at least the initial string, the destination string and "
                         "one file/folder path such as:\nmodfname -r \" \" \"_\" \"$MHOME/dev/tests/this is a test\"")


def modify_fname():

    input_parms = sys.argv[1:]
    check_help_request(input_parms)
    check_nb_parameters(input_parms)

    m = Modifier(input_parms)
    m.treat_input_parms()
    m.get_final_params()

    m.check_integrity_inputs()

    if m.recursive or m.local:
        if len(m.fpaths) != 1:
            ERROR("in recursive mode only one folder path must be given\ngiven %s" % m.fpaths)
            raise ValueError("please enter only one input folder path in recursive mode")

        m.fpath = m.fpaths[0]
        _check_folder_path_exists(m.fpath)
        if not m.fpath.startswith('/'):
            m.fpaths = _concat_paths(os.getcwd(), m.fpath)

        # files_folders = os.listdir(m.fpath)
        for f_name in os.listdir(m.fpath):
            m.mod_fnames(_concat_paths(m.fpath, f_name))
    else:
        if len(m.fpaths) == 0:
            ERROR("needs at least one file/folder path")
            raise ValueError("please enter at least one path")

        for fpath in m.fpaths:
            if not fpath.startswith('/'):
                fpath = _concat_paths(os.getcwd(), fpath)
            if not _check_path_exists(fpath):
                skipped()
                continue
            m.mod_fnames(fpath)

    m.occs_summary()


if __name__ == "__main__":
    modify_fname()
