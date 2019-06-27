"""
Class for easier geo nesting manipulation
v0.2
"""

class NoSuchLevelFound(Exception):
    pass


class GeoNesting:
    def __init__(self, geo_nesting):
        self.geo_nesting = geo_nesting
        self.data = geo_nesting[0]
        self.index = 0
        self.unpack_data(self.data)

    # def __repr__(self):
    #     print('Sum level: ' + self.sum_level)
    #     print('Name: ' + self.name)
    #     print('Fips length: ' + str(self.full_fips))
    #     print('Partial fips length: ' + str(self.partial_fips))
    #     print('Indent: ' + str(self.indent))

    @staticmethod
    def get_nesting_from_metadata_file(file_path):
        from lxml import etree as et
        geo_types = et.parse(file_path).xpath('//geoType')
        geo_types = [[g.attrib['Name'], g.attrib['Label'], g.attrib['FipsCodeLength'], g.attrib['FipsCodePartialLength'], g.attrib['Indent']] for g in geo_types]
        return geo_types

    @classmethod
    def unpack_data(cls, data):
        cls.sum_level = data[0]
        cls.name = data[1]
        cls.full_fips_len = data[2]
        cls.partial_fips_len = data[3]
        cls.indent = data[4]

    def get_parent(self):
        if self.index > 0:
            for index in reversed(range(self.index)):
                if self.geo_nesting[index][4] == self.indent:
                    continue
                else:
                    self.index = index
                    self.data = self.geo_nesting[self.index]
                    self.unpack_data(self.data)
                    break
        else:
            print('No more parents on this branch!')

    def get_child(self):
        if self.index + 1 >= len(self.geo_nesting):
            print('No more children on this branch!')
        else:
            for index in range(self.index, len(self.geo_nesting)):
                if self.geo_nesting[index][4] < self.indent:
                    break
                elif self.geo_nesting[index][4] == self.indent:
                    continue
                else:
                    self.index = index
                    self.data = self.geo_nesting[self.index]
                    self.unpack_data(self.data)
                    break

    def get_lower_levels(self):
        lower_levels = []
        for index in reversed(range(self.index)):
            if self.geo_nesting[index][4] < self.indent:
                lower_levels.append(self.geo_nesting[index][0])
            else:
                continue

        return lower_levels

    def print_tree(self):
        for geo_level in self.geo_nesting:
            print('-' * int(geo_level[4]) + geo_level[0])

    def find_level(self, level):
        for i, geo_level in enumerate(self.geo_nesting):
            if level == geo_level[0]:
                self.index = i
                self.data = geo_level
                self.unpack_data(self.data)
                break
        else:
            raise NoSuchLevelFound('No such level found!')
