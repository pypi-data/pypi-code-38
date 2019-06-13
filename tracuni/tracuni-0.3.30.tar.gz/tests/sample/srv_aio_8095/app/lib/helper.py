import hashlib
import hmac
import json
from urllib.parse import parse_qs
from aiohttp.web_request import Request
from app.core.error import Error
from app.core.http_server import SPAN_KEY


class CheckError(Error):
    def __init__(self, code):
        self.code = code


class Helper:
    def __init__(self, config, db_transfer):
        self.config = config
        self.db_transfer = db_transfer

    def get_status_message(self, code):
        return self.config["status_messages"][str(code)]

    def get_response_message(self, code):
        return self.config["errors"][str(code)]

    def gen_response(self, code):
        return {"code": code, "message": self.get_response_message(code)}

    def gen_status(self, code):
        return {"code": code, "message": self.get_status_message(code)}

    @staticmethod
    def check_req(req, method):
        res = False
        if method == "transfer":
            if "from_msisdn" in req and "to_msisdn" in req and "amount" in req:
                res = True
        elif method == "transfer_card":
            if "from_msisdn" in req and "to_card" in req and "amount" in req:
                res = True
        elif method == "transfer_account":
            if "from_msisdn" in req and "account" in req and "amount" in req:
                res = True
        elif method == "transfer_custom":
            if "from_msisdn" in req and "gateway_id" in req and "amount" in req and "fields" in req:
                res = True
        elif method == "status":
            if "transfer_id" in req or "merc_pid" in req:
                res = True
        elif method == "history":
            if "client_id" in req and "from_stamp" in req and "till_stamp" in req:
                res = True
        elif method == "calculate":
            if "client_id" in req and "amount" in req and "target" in req:
                res = True
        elif method == "get_gateway":
            res = True
        elif method == 'get_suggestions':
            if "query" not in req:
                raise CheckError(24)
            if "kind" not in req:
                raise CheckError(25)
            res = True
        elif method == 'create_template':
            if "client_id" not in req:
                raise CheckError(28)
            if "name" not in req:
                raise CheckError(26)
            if "oper_order_id" not in req:
                raise CheckError(27)
            res = True
        elif method == 'get_templates':
            if "client_id" not in req:
                raise CheckError(28)
            res = True
        elif method == 'delete_template':
            if "client_id" not in req:
                raise CheckError(28)
            if "template_uuid" not in req:
                raise CheckError(29)
            res = True
        return res

    async def check_request(self, request: Request, method: str):
        body = await request.text()

        if request.method == 'POST':
            try:
                req = json.loads(body)
            except:
                raise CheckError(4)
        else:
            req = {}
            _req = parse_qs(request.query_string)
            for k, v in _req.items():
                req[k] = v[0]

        return req

    async def authenticate(self, request: Request):
        # Аутентификация мерчанта
        context_span = request[SPAN_KEY]
        body = await request.text()
        params = request.url.query
        if "api_key" in params and "sign" in params:
            # проверка подписи
            secret_key = await self.db_transfer.get_secret(context_span, params["api_key"])
            if secret_key:
                check_sign = hmac.new(secret_key.encode(), body.encode(), hashlib.sha256).hexdigest()
                if params["sign"] == check_sign:
                    merc_data = await self.db_transfer.get_mercdata_by_apikey(context_span, params["api_key"])
                    response = self.gen_response(0)
                else:
                    return self.gen_response(3)
            else:
                return self.gen_response(3)
        else:
            ssl_verified = request.headers.get("Ssl_Verified", None)
            ssl_serial = int(request.headers.get("Ssl_Serial", "0"), 16)
            ssl_idn = request.headers.get("Ssl_Idn", None)

            if ssl_verified != "SUCCESS":
                return self.gen_response(5)

            check_serial = await self.db_transfer.check_serial(context_span, ssl_serial)
            if check_serial:
                merc_data = await self.db_transfer.get_mercdata_by_cert(context_span, ssl_serial)
                response = self.gen_response(0)
            else:
                return self.gen_response(2)

        response = {**response, **merc_data}
        return response
