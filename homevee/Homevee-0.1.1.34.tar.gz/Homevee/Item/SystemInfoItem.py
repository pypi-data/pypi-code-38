from Homevee.Item import Item


class SystemInfoItem(Item):
    def __init__(self, name, icon, value):
        super(SystemInfoItem, self).__init__()
        self.name = name
        self.icon = icon
        self.value = value