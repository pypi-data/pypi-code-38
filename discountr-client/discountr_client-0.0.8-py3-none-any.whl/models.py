import json
from slugify import slugify


class BaseObject(dict):
    serialized_keys = []

    def to_json(self):
        temp = {}
        for key in self.serialized_keys:
            temp[key] = getattr(self, key)
        return json.dumps(temp)


class Brand(BaseObject):
    serialized_keys = [
        'name',
        'slug'
    ]

    @property
    def slug(self):
        return slugify(self.name, only_ascii=True)

    @property
    def name(self):
        return self.get('brand_name')


class Category(BaseObject):
    serialized_keys = [
        'name',
        'slug'
    ]

    @property
    def slug(self):
        return self.get('slug')

    @property
    def name(self):
        return self.get('name')


class Price(BaseObject):
    serialized_keys = [
        'value',
        'created_at',
        'product_id'
    ]

    @property
    def value(self):
        return self.get('value')

    @property
    def created_at(self):
        return self.get('created_at')

    @property
    def product_id(self):
        return self.get('product_id')


class Product(BaseObject):
    serialized_keys = [
        'name',
        'slug',
        'code',
        'brand_id',
        'category_id',
        'price_id'
    ]

    @property
    def slug(self):
        return self.get('slug')

    @property
    def name(self):
        return self.get('name')

    @property
    def code(self):
        return self.get('code')

    @property
    def brand_id(self):
        return self.get('brand_id')

    @property
    def category_id(self):
        return self.get('category_id')

    @property
    def price(self) -> Price:
        return Price(self)
