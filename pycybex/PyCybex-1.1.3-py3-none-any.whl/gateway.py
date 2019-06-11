import requests, json

GATEWAY_URL = 'https://gateway.cybex.io/gateway'
def validate_withdraw_address(symbol, address, name):
    headers = { 'Content-Type': 'application/json'}
    payload = {
        "operationName":"VerifyAddress",
        "variables":{
            "asset": symbol,
            "accountName": name,
            "address": address
        },
        "query":"query VerifyAddress($asset: String!, $accountName: String!, $address: String!) {\n  verifyAddress(asset: $asset, accountName: $accountName, address: $address) {\n    valid\n    asset\n    __typename\n  }\n}\n"}

    r = requests.post(url = GATEWAY_URL,
                  data = json.dumps(payload),
                  headers = headers)
    if r.status_code != 200:
        raise Exception('Cannot connect to cybex gateway to verify your withdraw address')

    ret = json.loads(r.text)
    return ret['data']['verifyAddress']['valid']
    
def get_withdraw_info(symbol):
    headers = { 'Content-Type': 'application/json'}
    payload = {
        "operationName":"WithdrawInfo",
        "variables":{"type": symbol},
        "query":"query WithdrawInfo($type: String!) {\n  withdrawInfo(type: $type) {\n    fee\n    minValue\n    precision\n    asset\n    type\n    gatewayAccount\n    __typename\n  }\n}\n"
    }
    r = requests.post(url = GATEWAY_URL,
                  data = json.dumps(payload),
                  headers = headers)
    if r.status_code != 200:
        raise Exception('Cannot connect to cybex gateway to get withdraw info')

    ret = json.loads(r.text)
    return ret['data']['withdrawInfo']

if __name__ == '__main__':
    print(get_withdraw_info('USDT'))
    print(get_withdraw_info('EOS'))
    print(get_withdraw_info('ETH'))
    assert not validate_withdraw_address('ETH', 'invalid_address', 'test-account')
    assert validate_withdraw_address('ETH', '0x4675dc5fe44500eb6af616753c75d39c50be31c8', 'test-account')
