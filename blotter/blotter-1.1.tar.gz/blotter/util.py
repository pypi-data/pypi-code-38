
def calc_pnl(qty1, px1, qty2, px2):
    '''
    @returns float
    '''
    qty = min(abs(qty2), abs(qty1))
    diff = px1 - px2 if qty2 > 0 else px2 - px1
    return qty * diff

def calc_avg_open_price(qty1, px1, qty2, px2):
    '''
    @returns float
    '''
    num = (px1 * qty1) + (px2 * qty2) 
    return num / (qty1 + qty2)

