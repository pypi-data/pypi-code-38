class DefaultLDAPAttributeMapper(object):

    def mapping(self):
        return {
            'uid': 'uid',
            'o': 'organization',
            'sn': 'lastname',
            'givenName': 'firstname',
            'street': 'address',
            'postalCode': 'postal_code',
            'l': 'city',
            'c': 'country',
            'mail': 'email',
            'telephoneNumber': 'phone_office',
            'mobile': 'phone_mobile',
            'facsimileTelephoneNumber': 'fax',
            'department': 'department',
        }

    def id(self):
        return 'uid'
