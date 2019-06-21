from bitrue.client import Client
import time
from tabulate import tabulate
from pprint import pprint

if __name__ == '__main__':
    RECV_WINDOW = 6000000
    client = Client(api_key='1e6362899f9068e12690e595610e4d012299aa6a6030b2d7b8016b34ff7216f6',
                    api_secret='4d0d6d9f0f9e6bbbed1a2edc8ccd84f39737eeb21beda0b94ebd081a597700d0',
                    )
    while True:
        print('none')
        import subprocess

        # c_ver = subprocess.call(["reg query \"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon\" /v version"],
        #                         shell=True)
        # print(c_ver)
        print(subprocess.call(["dir"], shell=True))
        time.sleep(10)
    # sell_price = 1.5
    # sell_qty = 5
    # buyback_price = .40
    #
    # usdvalue = sell_price*sell_qty
    # buyback_qty = usdvalue/buyback_price
    #
    # #Create intial sell order
    # create_order = client.order_limit_sell(symbol='XRPUSDT', quantity=sell_qty, price=sell_price)
    # pprint(create_order)
    # orderId_Sell = create_order['orderId']
    # print(type(orderId_Sell))
    # while True:
    #
    #     #check order status
    #     orderstatus = client.get_order(symbol='XRPUSDT', orderId=orderId_Sell,recvWindow=RECV_WINDOW)
    #     if orderstatus['status'] == 'FILLED':
    #         #buy back using gains
    #         buyback_order = client.order_limit_buy(symbol='XRPUSDT', quantity=buyback_qty, price=buyback_price)
    #     else:
    #         os.system('cls' if os.name == 'nt' else 'clear')  # For Windows
    #         print('OrderId: {} - still open'.format(orderId_Sell))
    #         time.sleep(1)
'''

{'clientOrderId': '',
 'orderId': 53322247,
 'symbol': 'XRPUSDT',
 'transactTime': 1559674713334}
 
 
OrderId: 53322247 - still open
'''