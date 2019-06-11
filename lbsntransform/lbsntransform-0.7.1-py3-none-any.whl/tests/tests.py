# -*- coding: utf-8 -*-
"""
Tests for LBSNtransfer tool
"""

@staticmethod
def add_bundestag_group_example(twitter_records):
    """ Example: Manually add Group that applies to all entries.
        To use, must uncomment fieldMapping/extractUser
    """

    deutscher_bundestag_group = HF.createNewLBSNRecord_with_id(lbsnUserGroup(), "MdB (Bundestag)", twitter_records.origin)
    dbg_owner = HF.createNewLBSNRecord_with_id(lbsnUser(), "243586130", twitter_records.origin)
    dbg_owner.user_name = 'wahl_beobachter'
    dbg_owner.user_fullname = 'Martin Fuchs'
    deutscher_bundestag_group.user_owner_pkey.CopyFrom(dbg_owner.pkey)
    deutscher_bundestag_group.usergroup_description = 'Alle twitternden Abgeordneten aus dem Deutschen Bundestag #bundestag'
    twitter_records.lbsnRecords.AddRecordToDict(dbg_owner)
    twitter_records.lbsnRecords.AddRecordToDict(deutscher_bundestag_group)