from paytmpg.pg.utils.stringUtil import make_string, equals


class UserInfo:

    def __init__(self):
        self.custId = None
        self.mobile = None
        self.email = None
        self.firstName = None
        self.lastName = None
        self.address = None
        self.pincode = None

    def set_cust_id(self, cust_id):
        self.custId = cust_id

    def get_cust_id(self):
        return self.custId

    def set_mobile(self, mobile):
        self.mobile = mobile

    def get_mobile(self):
        return self.mobile

    def set_email(self, email):
        self.email = email

    def get_email(self):
        return self.email

    def set_first_name(self, first_name):
        self.firstName = first_name

    def get_first_name(self):
        return self.firstName

    def set_last_name(self, last_name):
        self.lastName = last_name

    def get_last_name(self):
        return self.lastName

    def set_address(self, address):
        self.address = address

    def get_address(self):
        return self.address

    def set_pincode(self, pincode):
        self.pincode = pincode

    def get_pincode(self):
        return self.pincode

    def __str__(self):
        return make_string(self)

    def __eq__(self, other):
        return equals(self, other)
