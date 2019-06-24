from enum import IntEnum

class StandardIpmFolder(IntEnum):
    INBOX = 0
    DELETED_ITEMS = 1
    OUTBOX = 2
    SENT_ITEMS = 3
    APPOINTMENTS = 4
    CONTACTS = 5
    DRAFTS = 6
    JOURNAL = 7
    NOTES = 8
    TASKS = 9
    UNSPECIFIED = 10
