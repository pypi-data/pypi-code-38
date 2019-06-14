from paytmpg.pg.utils.stringUtil import make_string, equals


class ShippingInfo:

    def __init__(self):
        self.merchantShippingId = None
        self.trackingNo = None
        self.carrier = None
        self.chargeAmount = None
        self.countryName = None
        self.stateName = None
        self.cityName = None
        self.address1 = None
        self.address2 = None
        self.firstName = None
        self.lastName = None
        self.mobileNo = None
        self.zipCode = None
        self.email = None

    def set_merchant_shipping_id(self, merchant_shipping_id):
        self.merchantShippingId = merchant_shipping_id

    def get_merchant_shipping_id(self):
        return self.merchantShippingId

    def set_tracking_no(self, tracking_no):
        self.trackingNo = tracking_no

    def get_tracking_no(self):
        return self.trackingNo

    def set_carrier(self, carrier):
        self.carrier = carrier

    def get_carrier(self):
        return self.carrier

    def set_charge_amount(self, charge_amount):
        self.chargeAmount = charge_amount

    def get_charge_amount(self):
        return self.chargeAmount

    def set_country_name(self, country_name):
        self.countryName = country_name

    def get_country_name(self):
        return self.countryName

    def set_state_name(self, state_name):
        self.stateName = state_name

    def get_state_name(self):
        return self.stateName

    def set_city_name(self, city_name):
        self.cityName = city_name

    def get_city_name(self):
        return self.cityName

    def set_address1(self, address1):
        self.address1 = address1

    def get_address1(self):
        return self.address1

    def set_address2(self, address2):
        self.address2 = address2

    def get_address2(self):
        return self.address2

    def set_first_name(self, first_name):
        self.firstName = first_name

    def get_first_name(self):
        return self.firstName

    def set_last_name(self, last_name):
        self.lastName = last_name

    def get_last_name(self):
        return self.lastName

    def set_mobile_no(self, mobile_no):
        self.mobileNo = mobile_no

    def get_mobile_no(self):
        return self.mobileNo

    def set_zip_code(self, zip_code):
        self.zipCode = zip_code

    def get_zip_code(self):
        return self.zipCode

    def set_email(self, email):
        self.email = email

    def get_email(self):
        return self.email

    def __str__(self):
        return make_string(self)

    def __eq__(self, other):
        return equals(self, other)

    def __repr__(self):
        return make_string(self)
