import urllib
import json
class JsonSerializable(object):
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)
    def __repr__(self):
        return self.toJson()

class Node(JsonSerializable):
    def __init__(self, node_dict):
        self.id = node_dict["id"]
        self.name = urllib.parse.unquote(node_dict["name"]).replace(" ", "_")
        self.profile = node_dict["profile"]
        self.state_changed = node_dict["state_changed"]
        self.added = node_dict["added"]
        self.state = node_dict["state"]
        self.attributes = []
        self.add_attributes(node_dict['attributes'])

    def add_attributes(self, attributes):
        for attribute in attributes:
            self.attributes.append(Attribute(attribute))

    def as_dict(self):
        data = dict(self.__dict__)
        data['attributes'] = list(map(lambda a: a.as_dict(), self.attributes))
        return data

class Attribute(JsonSerializable):
    def __init__(self, attribute_dict):
        self.id = attribute_dict['id']
        self.node_id = attribute_dict['node_id']
        self.editable = attribute_dict['editable']
        self.value = attribute_dict['current_value']
        self.unit = urllib.parse.unquote(attribute_dict['unit'])
        self.type = attribute_dict['type']

    def as_dict(self):
        return self.__dict__

class Group(JsonSerializable):
    def __init__(self, group_dict):
        self.id = group_dict['id']
        self.category = group_dict['category']
        self.name = group_dict['name']
        self.image = group_dict['image']
        self.note = group_dict['note']
        self.owner = group_dict['owner']
        self.state = group_dict['state']
        self.phonetic_name = group_dict['phonetic_name']
        self.services = group_dict['services']
        self.order = group_dict['order']
        self.added = group_dict['added']

class Relationship(JsonSerializable):
    def __init__(self, relationship_dict):
        self.id = relationship_dict['id']
        self.homeegram_id = relationship_dict['homeegram_id']
        self.group_id = relationship_dict['group_id']
        self.node_id = relationship_dict['node_id']
        self.order = relationship_dict['order']

class Homeegram(JsonSerializable):
    def __init__(self, homeegram_dict):
        self.id = homeegram_dict['id']
        self.play = homeegram_dict['play']
        self.name = homeegram_dict['name']
        self.state = homeegram_dict['state']
        self.visible = homeegram_dict['visible']
        self.active = homeegram_dict['active']

