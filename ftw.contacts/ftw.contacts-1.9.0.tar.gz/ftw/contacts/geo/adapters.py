class ContactLocationAdapter(object):
    """Adapter that is able to represent the location of Contact in
    a geocodable string form.
    """

    def __init__(self, context):
        self.context = context

    def getLocationString(self):
        """Build a geocodable location string from the Contact address
        related fields.
        """
        street = u' '.join(self.context.address.strip().split())
        # Remove Postfach from street, otherwise Google geocoder API will
        # return wrong results
        street = street.replace(u'Postfach', u'').replace(u'\r', u'').strip()
        zip_code = self.context.postal_code.strip()
        city = self.context.city.strip()
        country = self.context.country.strip()

        # We need at least something other than country to be defined,
        # otherwise we can't do a meaningful geocode lookup
        if not (street or zip_code or city):
            return None

        # Concatenate only the fields with a value into the location string
        return u', '.join(filter(None, [street, zip_code, city, country]))
