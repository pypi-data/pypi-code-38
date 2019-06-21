import json
from urllib.request import urlopen, Request
from urllib import parse
import json
from time import time
from datetime import datetime
import threading


# Debug
from pprint import pprint as pp


class EXTERNAL_API(object):

    _LastLoginDate = 0
    _LastLoginThashold = 60*60*6  # 6h

    # Placeholders
    _token = None
    _totalProducts = None

    _URLs = {
        'login': 'https://www.elektrix.com/rest1/auth/login/elektrixapi',
        'getProducts': 'https://www.elektrix.com/rest1/product/getProducts',
        'getProductTotal': 'https://www.elektrix.com/rest1/product/getProductTotal',
        'setProducts': 'https://www.elektrix.com/rest1/product/setProducts',
        'getOrders': 'https://www.elektrix.com/rest1/order2/getOrders',
        'getCustomers': 'https://www.elektrix.com/rest1/customer/getCustomers',
        'getInvoices': '' 
    }

    def __init__(self, password: str):
        self._pass = password

    def __makeRequest(self, url:str, data:dict) -> dict:
        try:
            req = Request(url, data=data)
            resp = urlopen(req)
            j = json.load(resp)

            if j['success'] == True:
                return j
            else:
                print(j['message'][0]['text'])
                return None
        except:
            #Future ->  Must Debug Here
            return None

    def __login(self):
        url = self._URLs['login']

        data = parse.urlencode({
            "pass": self._pass,
            "language": "en"
        }).encode()

        j = self.__makeRequest(url, data)

        if j is not None:
            self._token = j['data'][0]['token']
            self._LastLoginDate = time()
            print("Logged In")
        else:
            raise Exception("Login Error ...")

    def __checkLogin(self):
        if time() - self._LastLoginDate > self._LastLoginThashold:
            # print('Above Thrashold')
            self.__login()

    #! GetColumnNames ----------------------------------------------------------

    def getColumnNames(self, type:str) ->[str] :
        self.__checkLogin()

        if type == 'product':
            url = self._URLs['getProducts']
        elif  type == 'customer':
            url = self._URLs['getCustomers']
        elif  type == 'orders':
            url = self._URLs['getOrders']
        elif  type == 'invoice':
            url = self._URLs['getInvoices']
        else:
            raise Exception("Invalid Type Entered")
        
        opts = {
            "token": self._token,
            "limit": 1
        }

        data = parse.urlencode(opts).encode()

        j = self.__makeRequest(url, data)

        if j is not None:
            a = j['data'][0]
            return list(a.keys())
        else:
            raise Exception("Connection Error")

    #! Products ----------------------------------------------------------

    def __getTotalProducts(self):
        self.__checkLogin()

        url = self._URLs['getProductTotal']
        data = parse.urlencode({
            "token": self._token
        }).encode()

        j = self.__makeRequest(url, data)

        if j is not None:
            self._totalProducts = j['summary']['totalRecordCount']
        else:
            raise Exception("Could not get Total Product Count")

    def fetchProducts(self, filter:str="", columns:[str]="", onlyActives:bool=False, limit:int=500, custom:dict=None) -> [dict]:
        self.__checkLogin()
        self.__getTotalProducts()

        url = self._URLs['getProducts']
        pagination = (float(self._totalProducts) / limit) + 1

        self._FetchedProducts = []

        page = 0

        def fetch(page):
            opts = {
                "token": self._token,
                "start": page * limit,
                "limit": limit
            }

            if custom is not None:
                opts = {**opts, **custom}

            if filter != "":
                opts['f'] = filter

            if columns != "":
                opts['columns'] = ','.join(columns)

            data = parse.urlencode(opts).encode()

            j = self.__makeRequest(url, data)

            if j is not None:
                try:
                    data = j['data']

                    if len(data) > 0:
                        for prod in data:
                            if onlyActives:
                                if prod['IsActive'] == 'true':
                                    self._FetchedProducts.append(prod)
                            else:
                                self._FetchedProducts.append(prod)

                except:
                    pass
            else:
                pass
                # raise Exception("Product Fetch Error!")

            print(f'{(page + 1) * limit} products out of {self._totalProducts}...')
            return

        threads = []

        for _ in range(int(pagination)):
            # print(f'Fetching {page + 1} page out of {int(pagination)}')

            x = threading.Thread(target=fetch, args=(page,))
            threads.append(x)
            page += 1

            try:
                x.start()
            except:
                pass

        for _, thread in enumerate(threads):
            thread.join()
            # print(f'{i+1} thread Done')

        print("Fetched All Products, in Total: ", len(self._FetchedProducts))
        return self._FetchedProducts

    def setProducts(self, modifiedData:[dict]):
        self.__checkLogin()
        url = self._URLs['setProducts']

        data = parse.urlencode({
            "token": self._token,
            "data": "[" + json.dumps(modifiedData) + "]"
        }).encode()

        j = self.__makeRequest(url, data)

        if j is not None:
            print(f"Successfully Uploaded {len(modifiedData)} !")
        else:
            raise Exception("Could not Upload the modifiedData")

    #! Orders ----------------------------------------------------------

    def __getTotalOrders(self):
        self.__checkLogin()

        url = self._URLs['getOrders']

        data = parse.urlencode({
            "token": self._token
        }).encode()

        j = self.__makeRequest(url, data)

        if j is not None:
            self._totalOrders = j['summary']['totalRecordCount']
        else:
            raise Exception("Could not Get Order Info")

    def fetchOrders(self, filter:str="", columns:[str]="", limit:int=500, custom:dict=None) -> [dict]:
        self.__checkLogin()
        self.__getTotalOrders()

        url = self._URLs['getOrders']

        pagination = (float(self._totalOrders) / limit) + 1

        self._FetchedOrders = []

        page = 0

        def fetch(page):
            opts = {
                "token": self._token,
                "start": page * limit,
                "limit": limit
            }

            if custom is not None:
                opts = {**opts, **custom}

            if filter != "":
                opts['f'] = filter

            if columns != "":
                opts['columns'] = ','.join(columns)

            data = parse.urlencode(opts).encode()

            j = self.__makeRequest(url, data)

            if j is not None:
                try:
                    data = j['data']

                    if len(data) > 0:
                        for order in data:
                            self._FetchedOrders.append(order)

                except:
                    pass
            else:
                raise Exception("Order Fetch Error!")

            print(f'{(page + 1) * limit} Orders out of {self._totalOrders}...')
            return

        threads = []

        for _ in range(int(pagination)):
            # print(f'Fetching {page + 1} page out of {int(pagination)}')

            x = threading.Thread(target=fetch, args=(page,))
            threads.append(x)
            page += 1

            x.start()

        for _, thread in enumerate(threads):
            thread.join()
            # print(f'{i+1} thread Done')

        print("Fetched All Orders, in Total: ", len(self._FetchedOrders))
        return self._FetchedOrders

    #! Customers ----------------------------------------------------------

    def __getTotalCustomers(self):
        self.__checkLogin()

        url = self._URLs['getCustomers']

        data = parse.urlencode({
            "token": self._token
        }).encode()

        j = self.__makeRequest(url, data)

        if j is not None:
            self._totalCustomers = j['summary']['totalRecordCount']
        else:
            raise Exception("Could not Get Order Info")

    def fetchCustomers(self, filter:str="", columns:[str]="", limit:int=500, custom:dict=None) -> [dict]:
        self.__checkLogin()
        self.__getTotalCustomers()

        url = self._URLs['getCustomers']

        pagination = (float(self._totalCustomers) / limit) + 1

        self._FetchedCustomers = []

        page = 0

        def fetch(page):
            opts = {
                "token": self._token,
                "start": page * limit,
                "limit": limit
            }

            if custom is not None:
                opts = {**opts, **custom}

            if filter != "":
                opts['f'] = filter

            if columns != "":
                opts['columns'] = ','.join(columns)

            data = parse.urlencode(opts).encode()

            j = self.__makeRequest(url, data)

            if j is not None:
                try:
                    data = j['data']

                    if len(data) > 0:
                        for order in data:
                            self._FetchedCustomers.append(order)

                except:
                    pass
            else:
                raise Exception("Order Fetch Error!")

            print(f'{(page + 1) * limit} Customers out of {self._totalCustomers}...')
            return

        threads = []

        for _ in range(int(pagination)):
            # print(f'Fetching {page + 1} page out of {int(pagination)}')

            x = threading.Thread(target=fetch, args=(page,))
            threads.append(x)
            page += 1

            x.start()

        for _, thread in enumerate(threads):
            thread.join()
            # print(f'{i+1} thread Done')

        print("Fetched All Customers, in Total: ", len(self._FetchedCustomers))
        return self._FetchedCustomers
