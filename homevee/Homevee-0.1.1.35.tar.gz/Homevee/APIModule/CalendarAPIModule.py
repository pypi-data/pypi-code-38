from Homevee.APIModule import APIModule
from Homevee.Item.CalendarEntry import CalendarEntry
from Homevee.Item.Status import *
from Homevee.Manager.CalendarManager import CalendarManager

ACTION_KEY_GET_CALENDAR_ITEM_DATES = "getcalendaritemdates"
ACTION_KEY_GET_CALENDAR_DAY_ITEMS = "getcalendardayitems"
ACTION_KEY_ADD_EDIT_CALENDAR_ENTRY = "addeditcalendarentry"
ACTION_KEY_DELETE_CALENDAR_ENTRY = "deletecalendarentry"

class CalendarAPIModule(APIModule):
    def __init__(self):
        super(CalendarAPIModule, self).__init__()
        self.calendar_manager = CalendarManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_GET_CALENDAR_ITEM_DATES: self.get_calendar_item_dates,
            ACTION_KEY_GET_CALENDAR_DAY_ITEMS: self.get_calendar_day_items,
            ACTION_KEY_ADD_EDIT_CALENDAR_ENTRY: self.add_edit_entry,
            ACTION_KEY_DELETE_CALENDAR_ENTRY: self.delete_entry
        }

        return mappings

    def get_calendar_item_dates(self, user, request, db):
        dates = self.calendar_manager.get_calendar_item_dates(user, request['year'], db)
        return Status(type=STATUS_OK, data={'dates':dates})

    def get_calendar_day_items(self, user, request, db):
        items = self.calendar_manager.get_calendar_day_items(user, request['date'], db)
        return Status(type=STATUS_OK, data={'items': CalendarEntry.list_to_dict(items)})

    def add_edit_entry(self, user, request, db):
        self.calendar_manager.add_edit_entry(user, request['id'], request['name'], request['date'],
                                                        request['start'],
                                                        request['end'], request['note'], request['address'], db)
        return Status(type=STATUS_OK)

    def delete_entry(self, user, request, db):
        if self.calendar_manager.delete_entry(user, request['id'], db):
            return Status(type=STATUS_OK)
        else:
            return Status(type=STATUS_ERROR)