from django.db import models
from django.conf import settings

from django_extensions.db.models import TimeStampedModel

from djcommerce.utils import get_product_model

Product = get_product_model()

class Cart(TimeStampedModel):
    products_in_cart = models.ManyToManyField(Product)

    def __str__(self):
        return "{} items in cart".format(self.products_in_cart.all().count())

    def get_subtotal(self):
        subtotal = 0
        for p in self.products_in_cart.all():
            subtotal += p.get_subtotal()
        return subtotal

    class Meta:
        abstract = False
        if hasattr(settings,"CART_MODEL"):
            abstract = True
