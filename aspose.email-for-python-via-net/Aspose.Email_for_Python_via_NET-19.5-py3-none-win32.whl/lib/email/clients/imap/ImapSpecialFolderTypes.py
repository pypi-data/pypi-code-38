from enum import IntEnum

class ImapSpecialFolderTypes(IntEnum):
    REGULAR = 0
    ALL = 1
    ARCHIVE = 2
    DRAFTS = 3
    FLAGGED = 4
    JUNK = 5
    SENT = 6
    TRASH = 7
    IMPORTANT = 8
