

"""
This module defines the Folder and RootFolder classes.

A web site starts with one Folder instance as the root, and this in turn holds other Folder
instances (in a folders attribute dictionary), and Page instances (in a pages attribute dictionary).

New Folder instances which are sub folders of root should only be created
from a parent folder using the parents method *create_folder* or *create_admin_folder*

New Page instances should be similarly be created using method *create_page*
or *create_admin_page*
"""


import copy, os, cgi, collections, html, pprint, json, shutil, uuid

from http import cookies

from . import skiboot, responders
from .excepts import ServerError


class Folder(object):
    """Represents a folder as shown within a url

    A Folder instance contains items with keys corresponding to the folder and page names within the
    folder. so if fldr is a folder instance, and 'mypage' is a page name of a page under fldr:

    fldr['mypage'] is the corresponding Page instance. 

    *instance attributes:*

    *default_page_name*
      Normally "index", and is the page shown if the url only contains the folder name

    *folders*
      A dictionary of {folder_name: ident} for each folder in the folder

    *ident*
      A numeric number acting as a folder identifier, the root folder has number 1
      and further folders and pages are added with incrementing numbers.
      If this is an admin folder, the ident is a negative number.

    *name*
      The name of the folder, making up the url, and therefore should be lower case
      and url friendly

    *pages*
      A dictionary of {page_name: ident} for each page in the folder

    *parentfolder*
      This is the parent folder of this instance, the root folder has parentfolder None

    """

    # though this is not a page_type, it has a page_type class attribute so this
    # can be checked for any item
    page_type = "Folder"


    def __init__(self, name=None, brief = "New Folder", default_page_name = "", restricted=False):
        """Initiates a Folder instance

        name: None if root, any url friendly name for any other folder
        default_page_name: the page to be shown if the url gives this folder only
        """
        # self.pages is a dictionary of page.name:page.ident
        self.pages = {}
        # self.folders is a dictionary of folder.name:folder.ident
        self.folders = {}
        self.ident = None
        self._parentfolder_ident = None
        if name:
            self._name = name.lower()
        else:
            self._name = ""
        if default_page_name:
            self.default_page_name = default_page_name.lower()
        else:
            self.default_page_name = ""
        self._restricted = bool(restricted)
        self.brief = brief
        # the change is a uuid which alters whenever the page changes
        self.change = uuid.uuid4().hex

    @property
    def proj_ident(self):
        return self.ident.proj

    @property
    def project(self):
        if self.ident:
            return skiboot.getproject(proj_ident=self.ident.proj) 

    @property
    def restricted(self):
        return self._restricted

    def set_unrestricted(self):
        """Sets this folder as unrestricted, returns True if folder
           is unrestricted, or False (due to parent being restricted) if not"""
        if not self._restricted:
            # Folder is already unrestricted
            return True
        if self._parentfolder_ident is not None:
            parentfolder = skiboot.get_item(self._parentfolder_ident)
            if parentfolder.restricted:
                self._restricted = True
                # cannot set unrestricted as parent is restricted
                return False
        self._restricted = False
        return True


    def set_restricted(self):
        """Sets this folder as restricted, sets sub folders to also be restricted,
           returns a list of those folders (starting with self) which have been set to restricted,
           any that are already set, are not included in the list, so returns an empty list
           if this folder is already restricted """
        if self._restricted:
            # already restricted
            return []
        self._restricted = True
        self.default_page_name = ""
        restricted_list = [self]
        # set any subfolders to be restricted
        for folder_ident in self.folders.values():
            folder = skiboot.get_item(folder_ident)
            restricted_list.extend(folder.set_restricted())
        return restricted_list


    @property
    def default_page(self):
        "return a deep copy of the default page, or None if one not set"
        default_ident = self.default_page_ident()
        if default_ident:
            return skiboot.from_ident(default_ident)


    @property
    def default_page_ident(self):
        "return the default page ident, or None if one not set"
        if self._restricted:
            return
        if self.default_page_name and (self.default_page_name in self.pages):
            return self.pages[self.default_page_name]


    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name.lower()

    name = property(get_name, set_name)

    def get_parentfolder(self):
        if self._parentfolder_ident is None:
            return None
        return skiboot.get_item(self._parentfolder_ident)

    def set_parentfolder(self, parentfolder):
        "Warning, this does not set this folder into the parents folders dictionary, it just sets this parentfolder attribute"
        if parentfolder is None:
            self._parentfolder_ident = None
        else:
            self._parentfolder_ident = parentfolder.ident

    parentfolder = property(get_parentfolder, set_parentfolder)

    @property
    def parentfolder_ident(self):
        "Returns the parentfolder ident"
        return self._parentfolder_ident


    def parent_list(self):
        "returns a list of (name, identnumber) starting at root"
        if self.ident.num == 0:
            return [('root', 0)]
        p_list = self.parentfolder.parent_list()
        p_list.append((self.name, self.ident.num))
        return p_list


    @property
    def url(self):
        return self._parentfolder_ident.url() + self.name + "/"


    def page_ident_from_path(self, identitems, pathlist):
        """"Return a page ident, where pathlist is a list of folder names and a final page name
        pathlist does not include the initial project url or this folders name
        identitems is the project {ident:folder or page} dictionary
        Return None if page not found, or a folder in the path is restricted"""
        if self._restricted:
            return
        # If pathlist is empty, return default page ident
        if not pathlist:
            return self.default_page_ident
        name = pathlist[0]
        # could be a page
        if name in self.pages:
            if len(pathlist) > 1:
                # page followed by further items is an error
                return
            # its a  page
            return self.pages[name]
        if name in self.folders:
            # requesting a folder
            folder_ident = self.folders[name]
            folder = identitems[folder_ident]
            return folder.page_ident_from_path(identitems, pathlist[1:])


    def ident_from_path(self, path):
        "Return the page or folder ident, or if not found, return None"
        myurl = self.url
        if (myurl == path) or (myurl == path+"/"):
            # request matches url path, therefore return self.ident
            return self.ident
        first_bit, name = path.rsplit("/", 1)
        path_string = first_bit + "/"
        if path_string == myurl:
            # this is a request for a page or a folder inside this folder
            if name in self.pages:
                # get the page
                return self.pages[name]
            elif name in self.folders:
                # requesting a folder
                return self.folders[name]
            else:
                # the page is not found
                return None
        elif path.find(myurl) == 0 :
            # The request may be for a sub folder of this page
            remaining_path = path[len(myurl):]
            bits = remaining_path.split("/", 1)
            name = bits[0]
            if name in self.folders:
                folder = skiboot.get_item(self.folders[name])
                return folder.ident_from_path(path)
            else:
                # the path is not found
                return None
        else:
            # the path is not found
            return None


    def add_page(self, page, ident=None):
        """Adds the page to this folder and project.
           The given ident can be None, Ident object, string or integer.
           Checks the given item is a page, respondpage etc .. (not a Folder) then calls project.add_item
           Returns the page ident."""
        if page.page_type == 'Folder':
            raise ServerError(message="Sorry, requested item is not a page")
        return self.project.add_item(self.ident, page, ident)


    def add_folder(self, folder, ident=None):
        """Adds the given folder to this folder and project.
           The given ident can be None, Ident object, string or integer.
           Checks given item is a Folder, then calls project.add_item
           Returns the folder ident"""
        if folder.page_type != 'Folder':
            raise ServerError(message="Sorry, requested item is not a folder")
        return self.project.add_item(self.ident, folder, ident)


    def folder_idents(self):
        "Returns a list of folder idents within this folder, sorted by name"
        name_list = [name for name in self.folders]
        name_list.sort()
        return [self.folders[name] for name in name_list]

    def page_idents(self):
        "Returns a list of page idents within this folder, sorted by name"
        name_list = [name for name in self.pages]
        name_list.sort()
        return [self.pages[name] for name in name_list]

    @property
    def ident_numbers(self):
        "return a list of ident numbers within this folder, not including folder number itself"
        num_list = []
        for ident in self.folders.values():
            num_list.append(ident.num)
        for ident in self.pages.values():
            num_list.append(ident.num)
        num_list.sort()
        return num_list

    def contains_ident(self, ident):
        "Returns True if the given ident is beneath this Folder"
        ident = skiboot.Ident.to_ident(ident, self.ident.proj)
        if ident in self.pages.values():
            return True
        if ident in self.folders.values():
            return True
        return False

    def __getitem__(self, name):
        "returns the page or folder in this folder - if it is not in the folder, returns None"
        if name in self.pages:
            page = skiboot.get_item(self.pages[name])
            if page is None:
                del self.pages[name]
            else:
                return page
        if name in self.folders:
            folder = skiboot.get_item(self.folders[name])
            if folder is None:
                del self.folders[name]
            else:
                return folder

    def __contains__(self, name):
        if name in self.pages:
            return True
        if name in self.folders:
            return True
        return False

    def __len__(self):
        return len(self.pages) + len(self.folders)

    def __bool__(self):
        return True

    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False
        return self.ident == other.ident

    def __ne__(self, other):
        if not isinstance(other, self.__class__): return True
        return self.ident != other.ident

    def __str__(self):
        return self.url

    def __repr__(self):
        if self.ident:
            return "Folder ident %s" % (self.ident,)
        else:
            return "Folder name %s" % (self._name,)




class RootFolder(Folder):
    """Represents the site root - inherits from Folder with some methods
       overwritten"""

    def __init__(self, proj_ident, brief = "The site root folder", default_page_name = "index"):
        """Initiates a RootFolder instance"""
        Folder.__init__(self, name=None, brief=brief, default_page_name = default_page_name, restricted=False)
        self.ident = skiboot.Ident(proj_ident, 0)  # rootfolder always has Ident.num of zero
        self._restricted = False

    @property
    def restricted(self):
        # root folder cannot be a restricted folder
        return False

    def set_unrestricted(self):
        # root is always unrestricted
        return True

    def set_restricted(self):
        # restricted attribute cannot be set on the root
        return []


    def get_name(self):
        return None

    def set_name(self, name):
        raise ServerError(message="Sorry, Root Folder name cannot be set")

    name = property(get_name, set_name)

    def get_parentfolder(self):
        return None

    def set_parentfolder(self, parent):
        raise ServerError(message="Sorry, The Root Folder cannot have a parentfolder set")

    parentfolder = property(get_parentfolder, set_parentfolder)


    @property
    def url(self):
        "Returns the project url"
        folder_project = skiboot.getproject(self.ident.proj)
        return folder_project.url

    def __repr__(self):
        return "RootFolder ident %s" % (self.ident,)


