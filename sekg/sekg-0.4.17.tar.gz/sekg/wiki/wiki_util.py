import json
from pathlib import Path


class WikiDataPropertyTable:
    instance = None

    @classmethod
    def get_instance(clss):
        if clss.instance is None:
            clss.instance = WikiDataPropertyTable()

        return clss.instance

    def __init__(self, property_table_path=str(Path(__file__).parent / "wikidata_property_table.json")):
        self.property_id_2_name_map = {}
        self.property_name_2_id_map = {}

        self.load_property_table(property_table_path)

    def load_property_table(self, property_table_path):
        with Path(property_table_path).open("r", encoding="utf-8") as f:
            self.property_id_2_name_map = json.load(f)
        self.property_name_2_id_map = {}
        for property_id, property_name in self.property_id_2_name_map.items():
            self.property_name_2_id_map[property_name] = property_id

    def property_id_2_name(self, property_id):
        """
        parse the property id to property name
        :param property_id: the id of property. eg. "P27"
        :return:
        """
        return self.property_id_2_name_map.get(property_id, None)

    def property_name_2_id(self, property_name):
        """
        the
        :param property_name:
        :return:
        """
        return self.property_name_2_id_map.get(property_name, None)
