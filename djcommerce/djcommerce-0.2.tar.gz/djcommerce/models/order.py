from django.db import models
from django.conf import settings

from django_extensions.db.models import TimeStampedModel

from djcommerce.utils import get_product_in_cart_model

STATUSES = [
    ('cancelled', 'Cancelled'),
    ('complete', 'Complete'),
    ('originated', 'Originated'),
    ('pending', 'Pending'),
    ('shipped', 'Shipped'),
]

ProductInCart = get_product_in_cart_model()

class OrderManager(models.Manager):
    def total_revenue(self, status=None):
        if status:
            orders = self.filter(status=status)
        else:
            orders = self.all()
        return sum([o.get_subtotal() for o in orders])

class Order(TimeStampedModel):
    products = models.ManyToManyField(ProductInCart)
    status = models.CharField(max_length = 50, choices = STATUSES)

    objects = OrderManager()

    def get_subtotal(self):
        return sum([p.get_subtotal for p in self.products.all()])

    class Meta:
        abstract = False
        if hasattr(settings,"ORDER_MODEL"):
            abstract = True
