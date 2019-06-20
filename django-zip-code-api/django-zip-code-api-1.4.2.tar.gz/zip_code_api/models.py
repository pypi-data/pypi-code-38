# -*- coding: utf-8 -*-
from django.db import models
from django.db.utils import IntegrityError
from django.utils.encoding import python_2_unicode_compatible
import csv
import os
import re
import sys

@python_2_unicode_compatible
class Address(models.Model):
    zip_code = models.CharField(u'Kod pocztowy', max_length = 255, help_text = u'np. 96-316')
    city = models.CharField(u'Miasto', max_length = 255, help_text = u'np. Warszawa')
    street = models.CharField(u'Ulica', max_length = 255, help_text = u'np. Wiejska', null = True, blank = True)
    country = models.CharField(u'Kraj', max_length = 2, default = 'PL')

    class Meta:
        verbose_name = u"Adres"
        verbose_name_plural = u"Adresy"
        unique_together = ('zip_code', 'city', 'street')

    def __str__(self):
        if self.street:
            return u"%s, %s %s (%s)" % (self.street, self.zip_code, self.city, self.country)
        else:
            return u"%s %s (%s)" % (self.zip_code, self.city, self.country)

    @classmethod
    def loadFromFile(cls, filename, ignore_rows = None, delete = False, encoding = None):
        def unicode_csv_reader(utf8_data, **kwargs):

            # @OG
            # rozkminić dlaczego źle konwertuje znak "
            # np. "Organizacji ""Wolność i Niezawisłość"""
            # https://docs.python.org/2/library/csv.html#dialects-and-formatting-parameters

            csv_reader = csv.reader(utf8_data, **kwargs)
            for row in csv_reader:
                yield [unicode(cell, encoding) or None for cell in row[0].split(';')]

        if not os.path.exists(filename):
            print >> sys.stderr, u'Plik "%s" nie istnieje' % filename
            return

        if delete:
            cls.objects.all().delete()
            print u"Usunięto istniejące adresy"

        with open(filename, 'rb') as f:
            i = j = 0
            print u"Przetwarzanie rekordów..."

            for row in unicode_csv_reader(open(filename)):
                j += 1
                if ignore_rows and j <= ignore_rows:
                    print u"Pominięto więrsz nr %s" % j
                    continue

                zip_code, city, street = row[:3]
                # https://regex101.com/r/0j1Qj2/2
                regex = u"^([\w\.\-'\" ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+) \(([\w\.\-'\" ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+)\)$"
                city = city.replace('""', '@').replace('"', '').replace('@', '"')
                match = re.match(regex, city)
                if match:
                    city = match.group(1)
                if street:
                    street = street.replace('""', '@').replace('"', '').replace('@', '"')
                    match = re.match(regex, street)
                    if match:
                        street = match.group(1)
                address = Address(zip_code = zip_code, city = city, street = street)
                try:
                    address.save()
                except IntegrityError:
                    print u"Zduplikowany adres: %s..." % address

                i += 1
                if not i % 100:
                    print u"Przetworzono rekordów: %s..." % i

            print u"Przetworzono rekordów: %s..." % i
