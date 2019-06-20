from django.core.cache import cache

from saleboxdjango.models import Product, ProductCategory, ProductVariant


class SaleboxCategory:
    def __init__(self):
        self.populated_categories_only = True
        self.product_attribute_include = {}
        self.product_attribute_exclude = {}
        self.variant_attribute_include = {}
        self.variant_attribute_exclude = {}

        self.valid_ids = []

    def get_tree(self, cache_key=None, cache_timeout=86400, category_id=None):
        tree = None
        if cache_key is not None:
            tree = cache.get(cache_key)

        # build tree
        if tree is None:
            tree = self._get_tree(self._get_root_categories())
            if cache_key is not None:
                cache.set(cache_key, tree, cache_timeout)

        # create output
        current = self._find_node(tree, category_id) if category_id else None
        output = {
            'tree': tree,
            'current': current,
            'ancestors': self._find_ancestors(tree, [], current['parent'] if current else None)
        }

        return output

    def _find_ancestors(self, tree, ancestors, id):
        if id is not None:
            curr = self._find_node(tree, id)
            del curr['children']
            if curr is not None:
                ancestors.append(curr)
                if curr['parent'] is not None:
                    ancestors = self._find_ancestors(tree, ancestors, curr['parent'])

        return ancestors

    def _find_node(self, tree, id):
        for c in tree:
            if id == c['id']:
                return c
            else:
                res = self._find_node(c['children'], id)
                if res is not None:
                    return res

    def _get_root_categories(self):
        tree = []
        categories = ProductCategory \
                        .objects \
                        .filter(active_flag=True) \
                        .order_by('name')
        for c in categories:
            if c.is_root_node():
                tree.append(c)

        return tree

    def _get_product_count(self, category):
        ids = category \
                .get_descendants(include_self=True) \
                .values_list('id', flat=True)

        pv = ProductVariant \
                .objects \
                .filter(product__category__id__in=list(ids)) \
                .filter(product__active_flag=True) \
                .filter(active_flag=True) \
                .filter(available_on_ecom=True) \

        if len(self.product_attribute_include.keys()) > 0:
            pv = pv.filter(**self.product_attribute_include)

        if len(self.product_attribute_exclude.keys()) > 0:
            pv = pv.exclude(**self.product_attribute_exclude)

        if len(self.variant_attribute_include.keys()) > 0:
            pv = pv.filter(**self.variant_attribute_include)

        if len(self.variant_attribute_exclude.keys()) > 0:
            pv = pv.exclude(**self.variant_attribute_exclude)

        return pv \
                .order_by('product__id') \
                .distinct('product__id') \
                .count()

    def _get_tree(self, categories):
        output = []

        for c in categories:
            count = self._get_product_count(c)
            if self.populated_categories_only and count == 0:
                continue

            children = self._get_tree(
                c.get_children().filter(active_flag=True)
            )

            output.append({
                'id': c.id,
                'children': children,
                'i18n': c.i18n,
                'image': c.local_image,
                'name': c.name,
                'parent': c.parent.id if c.parent else None,
                'product_count': count,
                'short_name': c.short_name,
                'slug': c.slug,
                'slug_path': c.slug_path,
            })

        return output

    def set_product_attribute_include(self, attribute_number, value):
        key = 'product__attribute_%s' % attribute_number
        self.product_attribute_include[key] = value

    def set_product_attribute_include_keyvalue(
            self,
            attribute_number,
            field_name,
            field_value,
            field_modifier=None
        ):
        key = 'product__attribute_%s__%s' % (attribute_number, field_name)
        if field_modifier is not None:
            key = '%s__%s' % (key, field_modifier)
        self.product_attribute_include[key] = field_value

    def set_product_attribute_exclude(self, attribute_number, value):
        key = 'product__attribute_%s' % attribute_number
        self.product_attribute_exclude[key] = value

    def set_product_attribute_exclude_keyvalue(
            self,
            attribute_number,
            field_name,
            field_value,
            field_modifier=None
        ):
        key = 'product__attribute_%s__%s' % (attribute_number, field_name)
        if field_modifier is not None:
            key = '%s__%s' % (key, field_modifier)
        self.product_attribute_exclude[key] = field_value

    def set_variant_attribute_include(self, attribute_number, value):
        key = 'attribute_%s' % attribute_number
        self.variant_attribute_include[key] = value

    def set_variant_attribute_include_keyvalue(
            self,
            attribute_number,
            field_name,
            field_value,
            field_modifier=None
        ):
        key = 'attribute_%s__%s' % (attribute_number, field_name)
        if field_modifier is not None:
            key = '%s__%s' % (key, field_modifier)
        self.variant_attribute_include[key] = field_value

    def set_variant_attribute_exclude(self, attribute_number, value):
        key = 'attribute_%s' % attribute_number
        self.variant_attribute_exclude[key] = value

    def set_variant_attribute_exclude_keyvalue(
            self,
            attribute_number,
            field_name,
            field_value,
            field_modifier=None
        ):
        key = 'attribute_%s__%s' % (attribute_number, field_name)
        if field_modifier is not None:
            key = '%s__%s' % (key, field_modifier)
        self.variant_attribute_exclude[key] = field_value
