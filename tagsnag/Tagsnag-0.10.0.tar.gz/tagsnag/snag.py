##
#  snag.py
#  tagsnag
#
#  Created by Thomas Johannesmeyer (thomas@geeky.gent) on 01.11.2018.
#  Copyright (c) 2018 www.geeky.gent. All rights reserved.
#


class Snag():
    """ Data class to organize Snags """

    def __init__(self, url, repo_name, local_repo_path, containing_folder, tag, filename, extension, destination):
        self.url = url
        self.repo_name = repo_name
        self.local_repo_path = local_repo_path
        self.containing_folder = containing_folder
        self.tag = tag
        self.filename = filename
        self.extension = extension
        self.destination = destination

    def __repr__(self):
        return "".join([self.repo_name, self.tag])

