from functools import reduce
import math
import operator

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Case, F, Q, Value, When
from django.http import Http404

from saleboxdjango.lib.common import fetchsinglevalue, \
    dictfetchall, get_rating_display

from saleboxdjango.models import Attribute, AttributeItem, \
    Product, ProductCategory, ProductVariant, ProductVariantRating


class SaleboxProduct:
    def __init__(self, active_status='active_only'):
        # product filters
        self.query = ProductVariant.objects
        self.active_status = active_status
        self.exclude_product_ids = []
        self.exclude_productvariant_ids = []
        self.min_price = None
        self.max_price = None
        self.max_result_count = None
        self.order = []
        self.prefetch_product_attributes = []
        self.prefetch_variant_attributes = []

        # pagination
        self.offset = 0
        self.page_number = 1
        self.limit = 50
        self.items_per_page = 50
        self.pagination_url_prefix = ''

        # misc
        self.fetch_user_ratings = True
        self.flat_discount = 0
        self.flat_member_discount = 0

    def get_list(self, request=None):
        # TODO: retrieve from cache
        #
        #
        data = None

        # cache doesn't exist, build it...
        if data is None:
            # retrieve list of variant IDs (one variant per product)
            # which match our criteria
            self.query = \
                self.query \
                    .exclude(product__id__in=self.exclude_product_ids) \
                    .order_by('product__id', 'price') \
                    .distinct('product__id') \
                    .values_list('id', flat=True)

            variant_ids = self._retrieve_variant_ids(do_exclude=True)

            data = {
                'variant_ids': variant_ids,
                'qs': self._retrieve_results(variant_ids)
            }

            # TODO: save data to cache
            #
            #

        # pagination calculations
        if self.max_result_count:
            total_results = min(len(data['variant_ids']), self.max_result_count)
        else:
            total_results = len(data['variant_ids'])
        number_of_pages = math.ceil(total_results / self.items_per_page)

        if request is None:
            products = data['qs']
        else:
            products = self.retrieve_user_interaction(request, data['qs'])

        # create output dict
        return {
            'count': {
                'from': self.offset + 1,
                'to': self.offset + len(data['qs']),
                #'total': len(data['variant_ids']),
                'total': total_results
            },
            'pagination': {
                'page_number': self.page_number,
                'number_of_pages': number_of_pages,
                'page_range': range(1, number_of_pages + 1),
                'has_previous': self.page_number > 1,
                'previous': self.page_number - 1,
                'has_next': self.page_number < number_of_pages,
                'next': self.page_number + 1,
                'url_prefix': self.pagination_url_prefix,
                'valid': self.page_number <= max(number_of_pages, 1)
            },
            'products': products
        }

    def get_related(self, request, variant, sequence):
        variant_ids = []
        exclude_product_ids = [variant.product.id]
        number_of_items = self.max_result_count or 1

        # loop through options
        sequence.append(None)
        for seq in sequence:
            if seq and seq[0] == 'product':
                key = 'product__attribute_%s' % seq[1]
                value = getattr(variant.product, 'attribute_%s' % seq[1]).first()
            elif seq and seq[0] == 'variant':
                key = 'attribute_%s' % seq[1]
                value = getattr(variant, 'attribute_%s' % seq[1]).first()
            else:
                key = None
                value = None

            for category in [variant.product.category, None]:
                res = self._retrieve_related(
                    key,
                    value,
                    category,
                    exclude_product_ids,
                    number_of_items - len(variant_ids)
                )
                for r in res:
                    variant_ids.append(r[0])
                    exclude_product_ids.append(r[1])
                    if len(variant_ids) == number_of_items:
                        break

                if len(variant_ids) == number_of_items:
                    break

            if len(variant_ids) == number_of_items:
                break

        # return results
        return self.retrieve_user_interaction(
            request,
            self._retrieve_results(variant_ids, True)
        )

    def get_single(self, request, id, slug):
        self.query = \
            self.query \
                .filter(id=id) \
                .filter(slug=slug) \
                .values_list('id', flat=True)

        # ensure variant exists
        variant_ids = self._retrieve_variant_ids(do_exclude=False)
        if len(variant_ids) == 0:
            raise Http404

        # retrieve variant
        return self.retrieve_user_interaction(
            request,
            self._retrieve_results(variant_ids)
        )[0]

    def retrieve_user_interaction(self, request, variants):
        # get user ratings
        rating_dict = {}
        if self.fetch_user_ratings and request.user.is_authenticated:
            ratings = ProductVariantRating \
                        .objects \
                        .filter(variant__id__in=[pv.id for pv in variants]) \
                        .filter(user=request.user)
            for r in ratings:
                rating_dict[r.variant.id] = r.rating

        # get basket / wishlist flags
        for pv in variants:
            if str(pv.id) in request.session['saleboxbasket']['basket']['lookup']:
                pv.basket_qty = request.session['saleboxbasket']['basket']['lookup'][str(pv.id)]['qty']
            else:
                pv.basket_qty = 0

            pv.in_wishlist = str(pv.id) in request.session['saleboxbasket']['wishlist']['order']

            if pv.id in rating_dict:
                pv.user_rating = get_rating_display(rating_dict[pv.id], 1)
            else:
                pv.user_rating = None

        return variants

    def set_exclude_product_ids(self, id_list):
        if isinstance(id_list, int):
            id_list = [id_list]
        self.exclude_product_ids += id_list

    def set_exclude_productvariant_ids(self, id_list):
        if isinstance(id_list, int):
            id_list = [id_list]
        self.exclude_productvariant_ids += id_list

    def set_minimum_stock_total(self, minimum_stock):
        self.query = self.query.filter(
            Q(stock_total__gte=minimum_stock) |
            Q(product__inventory_flag=False)
        )

    def set_prefetch_product_attributes(self, numbers):
        if isinstance(numbers, int):
            numbers = [numbers]
        self.prefetch_product_attributes = [
            'product__attribute_%s' % i for i in numbers
        ]

    def set_prefetch_variant_attributes(self, numbers):
        if isinstance(numbers, int):
            numbers = [numbers]
        self.prefetch_variant_attributes = [
            'attribute_%s' % i for i in numbers
        ]

    def set_active_status(self):
        # I can think of no reason for this to ever be set to anything
        # other than 'active_only' but include this here so it doesn't
        # bite us later
        if self.active_status == 'active_only':
            self.query = \
                self.query \
                    .filter(active_flag=True) \
                    .filter(available_on_ecom=True) \
                    .filter(product__active_flag=True) \
                    .filter(product__category__active_flag=True)

        elif self.active_status == 'all':
            pass

    def set_category(self, category, include_child_categories=True):
        if include_child_categories:
            id_list = category \
                        .get_descendants(include_self=True) \
                        .values_list('id', flat=True)
        else:
            if isinstance(category, int):
                id_list = [category]
            else:
                id_list = [category.id]

        self.query = self.query.filter(product__category__in=id_list)

    def set_discount_only(self):
        self.query = self.query.filter(sale_price__lt=F('price'))

    def set_fetch_user_ratings(self, value):
        self.fetch_user_ratings = value

    def set_flat_discount(self, percent):
        self.flat_discount = percent

    def set_flat_member_discount(self, percent):
        self.flat_member_discount = percent

    def set_max_price(self, maximun):
        self.query = self.query.filter(sale_price__lte=maximun)

    def set_max_result_count(self, i):
        self.max_result_count = i

    def set_max_sale_percent(self, maximum):
        self.query = self.query.filter(sale_percent__lte=maximun)

    def set_min_price(self, minimun):
        self.query = self.query.filter(sale_price__gte=minimum)

    def set_min_sale_percent(self, minimum):
        self.query = self.query.filter(sale_percent__gte=minimum)

    def set_order_custom(self, order):
        self.order = order
        if isinstance(self.order, str):
            self.order = [self.order]

    def set_order_preset(self, preset):
        # so... it turns out having multiple ORDER BYs with a LIMIT
        # clause slows things down a lot.
        self.order = {
            'bestseller_low_to_high': ['bestseller_rank', 'name_sorted'],
            'bestseller_high_to_low': ['-bestseller_rank', 'name_sorted'],
            'name_low_to_high': ['name_sorted'],
            'name_high_to_low': ['-name_sorted'],
            'price_low_to_high': ['sale_price', 'name_sorted'],
            'price_high_to_low': ['-sale_price', 'name_sorted'],
            'rating_low_to_high': ['rating_score', 'rating_vote_count', 'name_sorted'],
            'rating_high_to_low': ['-rating_score', '-rating_vote_count', 'name_sorted'],
        }[preset]

    def set_pagination(self, page_number, items_per_page, url_prefix):
        self.page_number = page_number
        self.offset = (page_number - 1) * items_per_page
        self.limit = self.offset + items_per_page
        self.items_per_page = items_per_page
        self.pagination_url_prefix = url_prefix

    def set_product_attribute_include(self, attribute_number, value):
        key = 'product__attribute_%s' % attribute_number
        self.query = self.query.filter(**{key: value})

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
        self.query = self.query.filter(**{key: field_value})

    def set_product_attribute_exclude(self, attribute_number, value):
        key = 'product__attribute_%s' % attribute_number
        self.query = self.query.exclude(**{key: value})

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
        self.query = self.query.exclude(**{key: field_value})

    def set_search(self, s):
        # create default list
        qlist = [
            Q(name__icontains=s),
            Q(ecommerce_description__icontains=s),
            Q(product__name__icontains=s),
        ]

        # add config items
        config = settings.SALEBOX.get('SEARCH')
        if config:
            for qstr in config:
                qlist.append(Q((qstr, s)))

        # update query
        self.query = self.query.filter(reduce(operator.or_, qlist))

    def set_variant_attribute_include(self, attribute_number, value):
        key = 'attribute_%s' % attribute_number
        self.query = self.query.filter(**{key: value})

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
        self.query = self.query.filter(**{key: field_value})

    def set_variant_attribute_exclude(self, attribute_number, value):
        key = 'attribute_%s' % attribute_number
        self.query = self.query.exclude(**{key: value})

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
        self.query = self.query.exclude(**{key: field_value})

    def _retrieve_related(self, key, value, category, exclude_ids, limit):
        qs = ProductVariant \
                .objects \
                .distinct('product__id') \
                .filter(active_flag=True) \
                .filter(available_on_ecom=True) \
                .filter(product__active_flag=True) \
                .filter(product__category__active_flag=True) \
                .exclude(product__in=exclude_ids)

        if key is not None:
            qs = qs.filter(**{key: value})

        if category is not None:
            qs = qs.filter(product__category=category)

        return qs.select_related('product') \
                 .order_by('product__id', 'product__name') \
                 .values_list('id', 'product_id')[0:limit]

    def _retrieve_results(self, variant_ids, preserve_order=False):
        qs = []
        if len(variant_ids) > 0:
            qs = ProductVariant \
                    .objects \
                    .filter(id__in=variant_ids) \
                    .select_related('product', 'product__category')

            # prefetch attributes
            if len(self.prefetch_product_attributes) > 0:
                qs = qs.prefetch_related(*self.prefetch_product_attributes)
            if len(self.prefetch_variant_attributes) > 0:
                qs = qs.prefetch_related(*self.prefetch_variant_attributes)

            # price modifier: flat_discount
            if self.flat_discount > 0:
                ratio = 1 - (self.flat_discount / 100)
                qs = qs.annotate(
                    modified_price=F('price') * ratio
                )

            # price modifier: flat_member_discount
            if self.flat_member_discount > 0:
                ratio = 1 - (self.flat_member_discount / 100)
                qs = qs.annotate(modified_price=Case(
                    When(
                        member_discount_applicable=True,
                        then=F('price') * ratio
                    ),
                    default=F('price')
                ))

            # add ordering
            if preserve_order:
                preserved = Case(*[
                    When(pk=pk, then=pos) for pos, pk in enumerate(variant_ids)
                ])
                qs = qs.order_by(preserved)
            elif len(self.order) > 0:
                if (
                    self.flat_discount > 0 or
                    self.flat_member_discount > 0
                ):
                    self.order = [
                        o.replace('sale_price', 'modified_price')
                        for o in self.order
                    ]
                qs = qs.order_by(*self.order)

            # add offset / limit
            if self.max_result_count:
                qs = qs[self.offset:min(self.limit, self.max_result_count)]
            else:
                qs = qs[self.offset:self.limit]

            # modify results
            for o in qs:
                # flat discount modifiers
                try:
                    if o.modified_price:
                        o.sale_price = o.modified_price
                        del o.modified_price
                except:
                    pass

        return qs

    def _retrieve_variant_ids(self, do_exclude=False):
        self.set_active_status()

        if do_exclude:
            # this is complex:
            # if we have two sibling variants and one is sold out and one isn't, we need to
            # make sure we show the in-stock option in the list. Showing 'sold out' for one
            # variant is misleading as there are other options available the customer may
            # want
            sql = """
                SELECT          pv.id
                FROM            saleboxdjango_productvariant AS pv
                INNER JOIN      saleboxdjango_product AS p ON pv.product_id = p.id
                WHERE           p.id IN (
                    SELECT          p.id
                    FROM            saleboxdjango_product AS p
                    INNER JOIN      saleboxdjango_productvariant AS pv ON pv.product_id = p.id
                    WHERE           p.active_flag = true
                    AND             p.inventory_flag = True
                    AND             pv.active_flag = true
                    AND             pv.available_on_ecom = true
                    GROUP BY        p.id
                    HAVING          COUNT(pv) > 1
                    AND             SUM(pv.stock_total) > 0
                )
                AND             stock_total <= 0
                AND             p.inventory_flag = True
                ORDER BY        id
            """
            with connection.cursor() as cursor:
                cursor.execute(sql)
                self.set_exclude_productvariant_ids([row[0] for row in cursor.fetchall()])

        # return variant IDs
        if len(self.exclude_productvariant_ids) > 0:
            self.query = self.query.exclude(id__in=self.exclude_productvariant_ids)
        return list(self.query)


def translate_path(path):
    o = {}
    o['path_list'] = path.strip('/').split('/')

    try:
        o['page_number'] = int(o['path_list'][-1])
        if o['page_number'] < 1:
            raise Http404()
        o['path_list'] = o['path_list'][:-1]
        if len(o['path_list']) == 0:
            o['path_list'].append('')
    except:
        o['page_number'] = 1

    o['path'] = '/'.join(o['path_list'])
    return o
