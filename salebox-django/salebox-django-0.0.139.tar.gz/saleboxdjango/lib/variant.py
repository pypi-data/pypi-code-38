from django.db.models import Case, BooleanField, Value, When

from saleboxdjango.models import ProductVariant


def get_sibling_variants(variant, order_by=None):
    pv = ProductVariant \
            .objects \
            .filter(active_flag=True) \
            .filter(available_on_ecom=True) \
            .filter(product__active_flag=True) \
            .filter(product__category__active_flag=True) \
            .filter(product=variant.product) \
            .annotate(selected_variant=Case(
                When(id=variant.id, then=True),
                default=Value(False),
                output_field=BooleanField(),
            ))

    if order_by is not None:
        pv = pv.order_by(order_by)

    return pv
