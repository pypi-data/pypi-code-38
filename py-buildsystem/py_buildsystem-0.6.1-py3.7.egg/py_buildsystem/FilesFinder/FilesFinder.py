import re
import os


class FilesFinder:

    def __init__(self, list_of_paths_to_search="", file_name_search_regex=".*", list_of_paths_to_exlude_from_search=None,
                 search_subdirectories=True):

        self.set_search_paths(list_of_paths_to_search)
        self.set_filename_search_regex(file_name_search_regex)
        self.set_excluded_directiories(list_of_paths_to_exlude_from_search)
        self.set_search_subdirectories(search_subdirectories)

    def set_search_paths(self, list_of_paths_to_search):
        # Check if the list_of_paths_to_search is string or the list of strings, otherwise raise TypeError
        if not(isinstance(list_of_paths_to_search, str) or
                (isinstance(list_of_paths_to_search, list) and all(isinstance(path, str) for path in list_of_paths_to_search))):
            raise TypeError("list_of_paths_to_search must be a string or list of strings")

        # if the list_of_paths_to_search is not a list make it into a list
        if (isinstance(list_of_paths_to_search, str)):
            self.__paths_to_search = [list_of_paths_to_search]
        else:
            self.__paths_to_search = list_of_paths_to_search

    def set_filename_search_regex(self, file_name_search_regex):
        # Check if the regex is string, otherwise raise TypeError
        if not(isinstance(file_name_search_regex, str)):
            raise TypeError("file name search regex must be a string not a'{}'".format(type(file_name_search_regex)))

        self.__file_name_search_regex = file_name_search_regex

    def set_excluded_directiories(self, list_of_paths_to_exlude_from_search):
        # Check if the list_of_paths_to_exlude_from_search is string or the list of strings, otherwise raise TypeError
        if not(list_of_paths_to_exlude_from_search is None or
               isinstance(list_of_paths_to_exlude_from_search, str) or
                (isinstance(list_of_paths_to_exlude_from_search, list) and
                 all(isinstance(path, str) for path in list_of_paths_to_exlude_from_search))):
            raise TypeError("list_of_paths_to_exlude_from_search must be a string or list of strings")

        # if the list_of_paths_to_exlude_from_search is not a list make it into a list
        if (isinstance(list_of_paths_to_exlude_from_search, str)):
            self.__list_of_paths_to_exlude_from_search = [list_of_paths_to_exlude_from_search]
        else:
            self.__list_of_paths_to_exlude_from_search = list_of_paths_to_exlude_from_search

    def set_search_subdirectories(self, search_subdirectories):
        # Check if the search_subdirectories is a bool
        if not(isinstance(search_subdirectories, bool)):
            raise TypeError("search_subdirectories must be a bool not a'{}'".format(type(search_subdirectories)))

        self.__search_subdirectories = search_subdirectories

    def search(self):
        __compiled_regex = re.compile(self.__file_name_search_regex)
        __found_files = []

        if self.__search_subdirectories is True:
            for directory in self.__paths_to_search:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if (self.__list_of_paths_to_exlude_from_search is None or
                                not any(__excluded_path in os.path.join(root, file).replace("\\", "/") for
                                        __excluded_path in self.__list_of_paths_to_exlude_from_search)):
                            if __compiled_regex.match(file) is not None:
                                __found_files.append(os.path.join(root, file).replace("\\", "/"))
        else:
            for directory in self.__paths_to_search:
                for file in os.listdir(directory):
                    if os.path.isfile(os.path.join(directory, file)):
                        if __compiled_regex.match(file) is not None:
                            __found_files.append(os.path.join(directory, file).replace("\\", "/"))

        return __found_files

    def set_files_extentions(self, extentions):
        # Check if the extention is string or the list of strings, otherwise raise TypeError
        if not(isinstance(extentions, str) or (isinstance(extentions, list) and all(isinstance(path, str) for path in extentions))):
            raise TypeError("extentions must be a string or list of strings")

        if isinstance(extentions, str):
            if(extentions.startswith("*")):
                extentions = extentions[1:]  # remove * from the begining
            self.__file_name_search_regex = ".*" + extentions.replace(".", "\.") + "$"
        else:
            self.__file_name_search_regex = ".*("
            for extention in extentions:
                if(extention.startswith("*")):
                    extention = extention[1:]  # remove * from the begining
                self.__file_name_search_regex += "(" + extention.replace(".", "\.") + ")|"

            self.__file_name_search_regex = self.__file_name_search_regex[:-1] + ")$"  # remove last "|" and end the regex with ")$"
