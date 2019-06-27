# standard libraries

# third party libraries
# None

# local libraries
from . import Event


class Observable:

    """
        Provide basic observable object. Sub classes should implement properties,
        items, and collections and call appropriate notifications when necessary.
    """

    def __init__(self):
        super().__init__()
        self.property_changed_event = Event.Event()
        self.item_set_event = Event.Event()
        self.item_cleared_event = Event.Event()
        self.item_inserted_event = Event.Event()
        self.item_removed_event = Event.Event()
        self.item_content_changed_event = Event.Event()

    def notify_property_changed(self, key):
        self.property_changed_event.fire(key)

    def notify_set_item(self, key, item):
        self.item_set_event.fire(key, item)

    def notify_clear_item(self, key):
        self.item_cleared_event.fire(key)

    def notify_insert_item(self, key, value, before_index):
        self.item_inserted_event.fire(key, value, before_index)

    def notify_remove_item(self, key, value, index):
        self.item_removed_event.fire(key, value, index)

    def notify_item_content_changed(self, key, value, index):
        self.item_content_changed_event.fire(key, value, index)
