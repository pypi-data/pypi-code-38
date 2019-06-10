# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# available digit patterns for NDCs
NDC_CHOICES = (
    ('4-4-2', '4-4-2'),
    ('5-3-2', '5-3-2'),
    ('5-4-1', '5-4-1'),
)


class Field(models.Model):
    '''
    An abstract name/value pair model
    '''
    name = models.CharField(
        max_length=100,
        null=False,
        db_index=True,
        help_text=_('The name of the field.'),
        verbose_name=_('Name')
    )
    value = models.TextField(
        help_text=_('The value of the field.'),
        verbose_name=_('Value')
    )
    description = models.CharField(
        max_length=500,
        null=True,
        help_text=_('A short description.'),
        verbose_name=_('Description')
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class GenericType(models.Model):
    identifier = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name=_("Identifier"),
        help_text=_("The unique type identifier."),
        null=False
    )
    description = models.CharField(
        max_length=400,
        verbose_name=_("Description"),
        help_text=_("A brief description of the type."),
        null=False
    )

    def __str__(self):
        return self.identifier

    class Meta:
        abstract = True


class GS1Location(models.Model):
    GLN13 = models.CharField(
        max_length=13,
        verbose_name=_("GLN13"),
        help_text=_("The GLN (Global Location Number) provides a standard "
                    "means to identify legal entities, trading parties and "
                    "locations to support the requirements of electronic "
                    "commerce. The GLN-13 is defined by GS1"),
        unique=True,
        db_index=True,
        null=True
    )
    SGLN = models.CharField(
        max_length=150,
        verbose_name=_("SGLN"),
        help_text=_("The SGLN EPC scheme is used to assign a unique identity "
                    "to a physical location or sub-location, such as a "
                    "specific building or "
                    "a specific unit of shelving within a warehouse.  The"
                    "SGLN is expressed as a URN value."),
        null=True,
        unique=True,
        db_index=True
    )

    class Meta:
        abstract = True


class Address(models.Model):
    '''
    Defines a mailing address for a location.
    '''
    name = models.CharField(
        max_length=128,
        verbose_name=_("Name"),
        help_text=_("A unique name for the location or party."),
        db_index=True,
        null=False,
    )
    address1 = models.CharField(
        max_length=1000,
        verbose_name=_("Street Address One"),
        help_text=_("For example, the name of the street and the number "
                    "in the street or the name of a building"),
        null=True
    )
    address2 = models.CharField(
        max_length=1000,
        verbose_name=_("Street Address Two"),
        help_text=_("The second free form line complements the first "
                    "free form line to locate the party or location."),
        null=True
    )
    address3 = models.CharField(
        max_length=1000,
        verbose_name=_("Street Address Three"),
        help_text=_("The third free form line complements the first and "
                    "second free form lines where necessary."),
        null=True
    )
    country = models.CharField(
        max_length=2,
        verbose_name=_("Country Code"),
        help_text=_("Country ISO 3166-1 alpha-2 Code"),
        null=True
    )
    city = models.CharField(
        max_length=50,
        verbose_name=_("city"),
        help_text=_("City"),
        null=True
    )
    state_province = models.CharField(
        max_length=20,
        verbose_name=_("State or Province"),
        help_text=_("One of the constituent units of a nation "
                    "having a federal government."),
        null=True
    )
    postal_code = models.CharField(
        max_length=20,
        verbose_name=_("Postal Code"),
        help_text=_("Postal Code"),
        null=True
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("Latitude"),
        help_text=_(" Latitude of the location, in degrees. Positive "
                    "numbers are northern latitude; negative numbers "
                    "are southern latitude."),
        null=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("Longitude"),
        help_text=_("Longitude of the location, in degrees. Positive "
                    "numbers are eastern longitude; negative numbers "
                    "are western longitude."),
        null=True
    )

    def __str__(self):
        return "%s %s, %s, %s, %s, %s" % (
            self.address1,
            self.address2,
            self.country,
            self.city,
            self.state_province,
            self.postal_code
        )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Location(Address, GS1Location):
    '''
    This model handles a physical location, site or sub-site or party per
    the data and fields outlined in section 10 of the GS1 CBV 1.2
    '''
    company = models.ForeignKey(
        'quartet_masterdata.Company',
        null=True,
        help_text=_('The company, if any, associated with this location.'),
        verbose_name=_('Company'),
        on_delete=models.SET_NULL
    )
    icon = models.FileField(
        upload_to='qu4rtetmasterdataimages/',
        verbose_name=_('Icon'),
        help_text=_('An icon to represent the location in a GUI or report.'),
        null=True
    )
    site = models.ForeignKey(
        'self',
        verbose_name=_("Site"),
        help_text=_("Identifies the site in which this location is contained"
                    "...if at all. "
                    "For a Sub-site location, this is the identifier of "
                    "the parent location."),
        null=True,
        on_delete=models.CASCADE
    )
    sst = models.SmallIntegerField(
        verbose_name=_("Sub-Site Type"),
        help_text=_("Sub-Site Type: describes the primary business function "
                    "of the sub-site location. This master data attribute is "
                    "only applicable to a sub-site location.  This value is "
                    "expressed as a single numerical code."),
        null=True
    )
    ssa = models.CharField(
        max_length=1000,
        verbose_name=_("Sub-Site Attribute"),
        help_text=_("Sub-Site Attribute: further qualifies the business "
                    "function of the sub-site location. This master data "
                    "attribute is only applicable to a sub-site location. "
                    "Sub-site attributes are expressed as a comma- separated "
                    "list of zero or more numerical codes"),
        null=True
    )
    location_type = models.ForeignKey(
        'quartet_masterdata.LocationType',
        verbose_name=_("Location Type"),
        help_text=_("An additional classifier that can be used to identify"
                       "the location outside of the CBV codes.  This "
                       "can be an internal classifier or a human readable "
                       "that lends further clarity to the location record."),
        null=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')


class LocationField(Field):
    '''
    Assignable name-value fields can be added to locations for further clarity
    on their physical or logical attributes.
    '''
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Location Field')
        verbose_name_plural = _('Location Fields')


class LocationIdentifier(models.Model):
    '''
    A location may have one or more unique identifiers aside from those
    defined on the location model (SGLN, GLN13, etc.)
    '''
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE
    )
    identifier = models.CharField(
        max_length=250,
        verbose_name=_("identifier"),
        help_text=_("A unique identifier for a location such as a GLN "
                    "or SGLN."),
        null=False
    )
    identifier_type = models.CharField(
        max_length=50,
        verbose_name=_("identifier_type"),
        help_text=_("The type of location identifier. For example: GLN-13, "
                    "SGLN, etc."),
        null=False
    )
    description = models.CharField(
        max_length=150,
        verbose_name=_("Description"),
        help_text=_("A brief description of what the identifier represents."),
        null=True
    )

    class Meta:
        verbose_name = _('LocationIdentifier')
        verbose_name_plural = _('LocationIdentifiers')


class LocationType(GenericType):
    '''
    Notes the type of location.  For example, Plant, Campus, Customer,
    Warehouse, etc.
    '''

    class Meta:
        verbose_name = _('Location Type')
        verbose_name_plural = _('Location Types')


class Measurement(models.Model):
    '''
    Based on the measurement specifics in the GS1 CBV 1.2 in section
    9.2.4
    '''
    measurement = models.FloatField(
        null=False,
        help_text=_('The numerical value of the measurement'),
        verbose_name=_('Measurement')
    )
    measurement_unit_code = models.CharField(
        max_length=40,
        verbose_name=_("measurement_unit_code"),
        help_text=_("The unit of measure for the measurement. The code list "
                    "for this attribute is UN/ECE Recommendation 20"),
        null=True
    )

    def __str__(self):
        return "%s: %s" % (self.measurement, self.measurement_unit_code)


class ItemInstance(models.Model):
    '''
    Base class for Trade Items and Instance Level models.
    '''
    country_of_origin = models.CharField(
        max_length=2,
        verbose_name=_("Country Of Origin"),
        help_text=_("Country from which the goods are supplied. The code list "
                    "for this attribute is the ISO 3166-1 Alpha-2 list "
                    "of 2-letter country codes"),
        null=True
    )
    drained_weight = models.FloatField(
        verbose_name=_('Drained Weight'),
        help_text=_('The weight of the trade item when drained of its '
                    'liquid. For example 225 grm'),
        null=True,
    )
    drained_weight_uom = models.CharField(
        max_length=5,
        verbose_name=_("Drained Weight UOM"),
        help_text=_("The unit of measure for the drained weight as defined in"
                    "UN/ECE Recommendation 20."),
        null=True
    )
    gross_weight = models.FloatField(
        verbose_name=_('Gross Weight'),
        help_text=_('Used to identify the gross weight of the trade item. '
                    'The gross weight includes all packaging materials '
                    'of the trade item.'),
        null=True,
    )
    gross_weight_uom = models.CharField(
        max_length=5,
        verbose_name=_("Gross Weight UOM"),
        help_text=_("The unit of measure for the gross weight as defined in"
                    "UN/ECE Recommendation 20."),
        null=True
    )
    net_weight = models.FloatField(
        verbose_name=_('Net Weight'),
        help_text=_('Used to identify the net weight of the trade item. '
                    'Net weight excludes any packaging materials and applies '
                    'to all levels but consumer unit level.'),
        null=True
    )
    net_weight_uom = models.CharField(
        max_length=5,
        verbose_name=_("NET Weight UOM"),
        help_text=_("The unit of measure for the net weight as defined in"
                    "UN/ECE Recommendation 20."),
        null=True
    )

    class Meta:
        abstract = True


class TradeItem(ItemInstance):
    '''
    Based on the GS1 CBV 1.2 Trade Item Master Data Attributes in section
    9 of the standard.
    '''
    company = models.ForeignKey(
        'quartet_masterdata.Company',
        null=False,
        help_text=_('The company, associated with this trade item.'),
        verbose_name=_('Company'),
        on_delete=models.CASCADE
    )
    image = models.FileField(
        upload_to='qu4rtetmasterdataimages/',
        verbose_name=_('Icon'),
        help_text=_('An image to represent the product in a GUI or report.'),
        null=True
    )
    GTIN14 = models.CharField(
        max_length=14,
        verbose_name=_("GTIN-14"),
        help_text=_("The GS1 GTIN-14 associated with the Trade Item."),
        null=False,
        unique=True,
        db_index=True
    )
    NDC = models.CharField(
        max_length=12,
        verbose_name=_("NDC"),
        help_text=_("The national drug code for the product. US Only."),
        null=True
    )
    NDC_pattern = models.CharField(
        max_length=5,
        verbose_name=_("NDC_pattern"),
        help_text=_("The pattern of the NDC.  US Only.  Optional."),
        null=True,
        choices=NDC_CHOICES
    )
    additional_id = models.CharField(
        max_length=80,
        verbose_name=_("Additional ID"),
        help_text=_(
            "A trade item identifier that is in addition to the GTIN."),
        null=True
    )
    additional_id_typecode = models.CharField(
        max_length=250,
        verbose_name=_("Additional ID TypeCode"),
        help_text=_(
            "The code list for this attribute is defined in GS1 GDSN."),
        null=True
    )
    description_short = models.CharField(
        max_length=35,
        verbose_name=_("description_short"),
        help_text=_("A free form short length description of the trade item "
                    "that can be used to identify the trade item at "
                    "point of sale."),
        null=True
    )
    dosage_form_type = models.CharField(
        max_length=35,
        verbose_name=_("Dosage Form Type"),
        help_text=_("A dosage form is the physical form of a medication "
                    "that identifies the form of the pharmaceutical item."
                    " For example: PILL"),
        null=True
    )
    functional_name = models.CharField(
        max_length=100,
        verbose_name=_("functional_name"),
        help_text=_("Describes use of the product or service by the consumer. "
                    "Should help clarify the product classification"
                    " associated with the GTIN."),
        null=True
    )
    manufacturer_name = models.CharField(
        max_length=300,
        verbose_name=_("manufacturer_name"),
        help_text=_("Party name information for the manufacturer of the trade "
                    "item. Example: Acme Corporation"),
        null=True
    )
    net_content_description = models.CharField(
        max_length=500,
        verbose_name=_("Net Content Description"),
        help_text=_("Free text describing the amount of the trade item "
                    "contained by a package, usually as claimed on the label. "
                    "Example: 253 grams"),
        null=True
    )
    label_description = models.CharField(
        max_length=500,
        verbose_name=_("Label Description"),
        help_text=_("A literal reproduction of the text featured on a "
                    "product's label in the same word-by-word order in which "
                    "it appears on the front of the product's packaging."),
        null=True
    )
    regulated_product_name = models.CharField(
        max_length=500,
        verbose_name=_("regulated_product_name"),
        help_text=_("The prescribed, regulated or generic product name or "
                    "denomination that describes the true nature of the "
                    "product "
                    "according to country specific regulation."),
        null=True
    )
    strength_description = models.CharField(
        max_length=500,
        verbose_name=_("strength_description"),
        help_text=_("Free text describing the strength of the active "
                    "ingredient(s) of the product. Example: 200mg/100mg"),
        null=True
    )
    trade_item_description = models.CharField(
        max_length=200,
        verbose_name=_("Trade Item Description"),
        help_text=_("An understandable and useable description of a trade "
                    "item using brand and other descriptors."),
        null=True
    )
    serial_number_length = models.PositiveSmallIntegerField(
        verbose_name=_("Serial Number Length"),
        help_text=_("The length of this material's serial number field"),
        null=True
    )
    pack_count = models.PositiveIntegerField(
        verbose_name=_("Pack Count"),
        help_text=_("The number of items packed into this package "
                    "(where appropriate)."),
        null=True
    )
    class Meta:
        verbose_name = _('Trade Item')
        verbose_name_plural = _('Trade Items')


class TradeItemField(Field):
    '''
    The trade item field allows for further classification and description
    of trade items by attaching any number of name-value pair fields to
    a given trade item.
    '''
    trade_item = models.ForeignKey(
        TradeItem,
        on_delete=models.CASCADE,
        verbose_name=_("Trade Item"),
        help_text=_("The Related Trade Item"),
        null=False
    )

    class Meta:
        verbose_name = _('Trade Item Field')
        verbose_name_plural = _('Trade Item Fields')


class Company(Address, GS1Location):
    '''
    Describes top-level company attributes- most importantly the company prefix
    which is required for trade items.  Can be associated with
    locations as well as a mechanism to show ownership, etc.
    '''
    gs1_company_prefix = models.CharField(
        max_length=12,
        verbose_name=_("GS1 Company Prefix"),
        help_text=_("A GS1 Company Prefix is a unique string of four to twelve"
                    " digits used to issue GS1 identification keys."),
        null=False
    )
    company_type = models.ForeignKey(
        'quartet_masterdata.CompanyType',
        null=True,
        verbose_name=_('Type'),
        help_text=_('Describes the type of company.'),
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')


class CompanyType(GenericType):
    '''
    Describes the type of company.  For example, 3PL, CPO, Trading Partner,
    etc.
    '''

    class Meta:
        verbose_name = _('CompanyType')
        verbose_name_plural = _('CompanyTypes')
