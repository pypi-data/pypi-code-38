from OpenSSL import crypto


class WsaaCertificate(object):

    def __init__(self, key):
        self.key = key
        self.country_code = None
        self.state_name = None
        self.company_name = None
        self.company_vat = None

    def validate_values(self):
        """ Validamos que esten todos los campos necesarios seteados """
        values = vars(self)
        for value in values:
            if not values.get(value):
                raise AttributeError('Falta configurar alguno de los siguientes campos:\n'
                                     'Codigo de pais, Provincia, Nombre de la empresa o CUIT')

    def generate_certificate_request(self, hash_sign='sha256', ou='odoo'):

        self.validate_values()

        # Utilizamos la libreria de crypto para generar el pedido de certificado
        req = crypto.X509Req()
        req.get_subject().C = self.country_code
        req.get_subject().ST = self.state_name
        req.get_subject().O = self.company_name
        req.get_subject().OU = ou
        req.get_subject().CN = self.company_name
        req.get_subject().serialNumber = 'CUIT {}'.format(self.company_vat)

        # Validamos el formato de la key
        key = crypto.load_privatekey(crypto.FILETYPE_PEM, self.key)
        self.key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)

        # Firmamos con la key y el hash el certificado
        req.set_pubkey(key)
        req.sign(key, hash_sign)

        return crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)


class WsaaPrivateKey(object):

    def __init__(self, length=2048):
        self.length = length
        self.key = None

    def generate_rsa_key(self):
        pkey = crypto.PKey()
        pkey.generate_key(crypto.TYPE_RSA, self.length)
        self.key = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey)
