import re

from .fill import Fill, _Fill
from .blot import Blotter


def validate_float(string, default=None):
    if not string or not float(string):
        return default
    return float(string)

def consume():
    blotters = {}

    defaults = {'contract_multiplier': 1, 'tick_value': 12.5, 'tick_size': 0.0025}
    buys = ['B', 'b', 'buy', 'Buy', 'BUY']
    sells = ['S', 's', 'sell', 'Sell', 'SELL']
    actions = buys + sells

    order_id = 0
    print(f'> Side OrderFilled ExchangeTicker PriceLevel ')

    while True:
        string = input('> ') 
        tokens = re.split('\s+', string.strip('\n'))

        if not tokens:
            continue
        
        if tokens[0] in actions:
            side, quantity, ticker, price = tokens
            quantity = int(quantity)
            price = float(price)

            if side in sells:
                quantity *= -1

            print(order_id, ticker, price, quantity)
            f = Fill.create_from_attrs(order_id, ticker, price, quantity)
            if not blotters.get(f.ExchangeTicker):
                print(f'> New {f.ExchangeTicker} Blotter ') 
                kwargs = defaults.copy()
                for k,v in defaults.items():
                    tokens = validate_float(input(f"> Enter {k.upper().replace('_',' ')} ({v}): "), 
                                            default=v)
                    kwargs[k] = tokens
                blotters[f.ExchangeTicker] = Blotter(f.ExchangeTicker, **kwargs)
            blotter = blotters.get(f.ExchangeTicker)
            blotter.add_fill(f)

        elif tokens[0] in blotters.keys():
            ticker = tokens[0]
            blotter = blotters.get(ticker)
            print(blotter)

        else:
            print('Unrecognized input.')

