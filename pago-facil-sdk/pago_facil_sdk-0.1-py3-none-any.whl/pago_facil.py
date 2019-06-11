import hashlib
import hmac

URL = "https://gw-dev.pagofacil.cl/initTransaction"

class Request():

    def __init__(self):
        self.currency = "CLP"
        self.account_id = None
        self.amount = 0
        self.currency = "CLP"
        self.reference = None
        self.customer_email = ""
        self.url_complete = ""
        self.url_cancel = ""
        self.url_callback = ""
        self.shop_country = "CL"
        self.session_id = ""

class Transaction():
    URLS = {
        "DEVELOPMENT" : "https://gw-dev.pagofacil.cl/initTransaction",
        "BETA" : "https://gw-beta.pagofacil.cl/initTransaction",
        "PRODUCTION" : "https://gw.pagofacil.cl/initTransaction"
    }

    def __init__(self, token_secret, env = "DEVELOPMENT"):
        self.token_secret = token_secret
        self.env = env.upper()

    def init_transation(self, request):
        data = {}
        for attr, value in request.__dict__.items():
            data["x_%s" % attr] = str(value)

        data_sorted = sorted(data.items(), key=lambda x:x[0])
        params = ["%s%s" % (k, v) for k, v in data_sorted]

        signature = Transaction.sign(self.token_secret, "".join(params))
        data.update({
            "x_signature" : signature
        })
        return self.generate_html(data)

    @staticmethod
    def sign(secret, data):
        return hmac.new(secret.encode('utf-8'), msg=data.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()


    def generate_html(self, data):
        html = '';
        html += '<html>';
        html += '  <body>';
        html += "    <form id=\"requestForm\" action=\"%s\" method=\"POST\">\n" % Transaction.URLS[self.env];

        for key, value in data.items():
            html += "<input type=\"hidden\" name=\"%s\" value=\"%s\" />\n" % (key, value)

        html += '    </form>';
        html += '    <script>';
        html += '        document.getElementById("requestForm").submit();'
        html += '    </script>';
        html += '  </body>';
        html += '</html>';
        return html
