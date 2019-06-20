class Base:
    def from_dict(self, record):
        for k in record:
            v = record[k]
            setattr(self, k, v)

class Relation:
    def relatesObj(self, entity=None, identifier=None, value=None, plays=None):
        self.L = {
            'entity': entity,
            'identifier': identifier,
            'value': value,
            'as': plays
        }
        return self

    def withObj(self, entity=None, identifier=None, value=None, plays=None):
        self.R = {
            'entity': entity,
            'identifier': identifier,
            'value': value,
            'as': plays
        }
        self.relates = (self.L, self.R)
        return self


class Brand(Base):
    entity_name = 'brand'
    def __init__(self):
        pass

class Product(Base):
    entity_name = 'product'
    def __init__(self):
        pass

class Category(Base):
    entity_name = 'category'
    def __init__(self):
        pass

class CategoryTree(Relation):
    relation_name = 'category-tree'

class ProducedRel(Relation):
    relation_name = 'produce-rel'

class CategorizedRel(Relation):
    relation_name = 'categorized-rel'
