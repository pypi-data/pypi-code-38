

"""Validators that deal with path, folder and file names

Each Validator is a class, with a _check method

"""


from .. import tag
from .. import skiboot
from . import Validator
from ..excepts import ValidateError


class PathLeadingTrailingSlashes(Validator):
    "Validates a path, and ensures leading or trailing slashes are in the path"

    arg_descriptions = {'leading_slash':True,
                       'trailing_slash':True }

    def __setitem__(self, arg_name, value):
        "Sets an argument value"
        Validator.__setitem__(self, arg_name, value)
        if isinstance(value, str):
            if val.lower() == 'false':
                self._val_args[arg_name] = False
        self._val_args[arg_name] = bool(value)


    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        if not item and (self["leading_slash"] or self["trailing_slash"]):
            return "/", True
        if not item:
            return '', False
        # strip leading and trailing slashes
        item = item.strip("/")
        item = item.strip()
        if not item and (self["leading_slash"] or self["trailing_slash"]):
            return "/", True
        if not item:
            return '', False
        if not item[0].isalnum():
            return '', False
        # add leading /
        if self["leading_slash"]:
            item = "/"+item
        # add an end /
        if self["trailing_slash"]:
            item = item+"/"
        return item, True


class IdentExists(Validator):
    "Ensures a given ident exists"

    arg_descriptions = {'is_folder':False,
                       'is_page':True,
                       'can_be_empty':False}

    def __setitem__(self, arg_name, value):
        "Sets an argument value"
        Validator.__setitem__(self, arg_name, value)
        if isinstance(value, str):
            if val.lower() == 'false':
                self._val_args[arg_name] = False
        self._val_args[arg_name] = bool(value)

    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        if (not item) and (item is not 0) and self["can_be_empty"]:
            # ident item is empty, and this is allowed
            return '', True
        page = skiboot.from_ident(item)
        if page is None:
            return '', False
        if (page.page_type == "Folder") and self["is_folder"]:
            return str(page.ident), True
        if (page.page_type != 'Folder') and self["is_page"]:
            return str(page.ident), True
        return '', False


class NameNotInFolder(Validator):
    """Checks the given name does not exist within the folder,
       which has its ident given in the field 'folder_ident_field'
    """

    arg_descriptions = {'folder_ident_field':''}

    def __setitem__(self, arg_name, value):
        "Sets an argument value"
        Validator.__setitem__(self, arg_name, value)
        if not value:
            self._val_args[arg_name] = ''
        self._val_args[arg_name] = skiboot.make_widgfield(value)


    def _check(self, widgfield, item, environ, lang, form_data, call_data, caller_page_ident):
        # Get the folder
        folder = None
        if self["folder_ident_field"] in form_data:
            folder = skiboot.from_ident(form_data[self["folder_ident_field"]])
        if not folder:
            return '', False
        if folder.page_type != 'Folder':
            return '', False
        # we have the folder, is this item in the folder
        name = item.lower()
        if name in folder:
            return '', False
        return name, True


