from django.db import models
from django.conf import settings

from localflavor.us.models import USStateField, USZipCodeField

class Address(models.Model):
    address_line_1 = models.CharField(max_length = 150)
    address_line_2 = models.CharField(max_length = 150, blank = True, null = True)
    city = models.CharField(max_length = 50)
    state = USStateField()
    zip = USZipCodeField()

    def __str__(self):
        return "{} {}, {}, {} {}".format(self.address_line_1,self.address_line_2,self.city,self.state,self.zip)

    class Meta:
        abstract = False
        if hasattr(settings, "ADDRESS_MODEL"):
            abstract = True
