from .log import Logger
from .fill import Fill
from .directions import DIRECTIONS
from .util import calc_pnl, calc_avg_open_price

class Blotter:
    def __init__(self, 
                 ticker, 
                 contract_multiplier=1, 
                 tick_value=12.5, 
                 tick_size=0.0025
                 ):
        self.ticker = ticker
        self.net_position = 0
        self.avg_open_price = 0
        self.realized_pnl = 0
        self.unrealized_pnl = 0
        self.total_pnl = 0
        #
        self.trades = []
        self.positions = []
        #
        self.contract_multiplier = contract_multiplier
        self.tick_value = tick_value
        self.tick_size = tick_size
        self.logger = self.get_logger()

    def get_logger(self):
        logger = Logger(self.__class__.__name__)
        logger.debug(self.headers)
        logger.info(self)
        return logger

    @property
    def headers(self):
        return '>EVENT|SIDE|QTY|TICKER|PX|PNL|MISC|'

    @property
    def net_direction(self):
        '''
        @returns type(DIRECTIONS)
        '''
        if not self.net_position:
            return DIRECTIONS.FLAT
        return DIRECTIONS.LONG if self.net_position > 0 else DIRECTIONS.SHORT

    def __str__(self):
        if self.avg_open_price:
            avg_open_price = round(self.avg_open_price, 6)
        else:
            avg_open_price = 'None'
        return f'>{self.__class__.__name__.upper()}|' + \
               f'{self.net_direction.name}|'+ \
               f'{abs(self.net_position)}|' + \
               f'{self.ticker}|' + \
               f'{avg_open_price}|' + \
               f'{round(self.total_pnl, 2)}|' + \
               f'|'

    def __repr__(self):
        return self.__str__()

    def add_fill(self, fill):
        '''
        fill -> Fill
        '''
        if fill.ExchangeTicker != self.ticker:
            msg = f'Warning: attempt to add fill to blotter with incorrect ExchangeTicker ({fill.ExchangeTicker != self.ticker})'
            self.logger.error(msg)
            raise ValueError(msg)
        self.update(fill)

    def get_closed_positions(self):
        booked = [t for t in self.trades if t.Booked]
        return booked

    def get_open_positions(self):
        '''
        @returns List
        '''
        positions = {}
        not_booked = [t for t in self.trades if not t.Booked]
        for t in not_booked:
            position = positions.get(t.OrderID)
            if not position:
                positions[t.OrderID] = t
            else:
                price = ((position.PriceLevel * abs(position.OpenQuantity)) + (t.PriceLevel * abs(t.OpenQuantity))) \
                            / (abs(position.OpenQuantity) + abs(t.OpenQuantity))
                position.PriceLevel = price
                position.OrderFilled += t.OrderFilled
                position.OpenQuantity += t.OpenQuantity
                position.BookedPartial = t.BookedPartial
                position.Offsets += t.Offsets
                position.UnrealPnl += t.UnrealPnl
                position.RealPnl += t.RealPnl
                # store the most recent ExecID, ClOrderID
                position.ExecID = t.ExecID
                position.ClOrderID = t.ClOrderID
        return sorted(positions.values(), key=lambda x: x.TransactionTime)

    def get_fifo_trade_by_direction(self, direction):
        '''
        direction -> type(DIRECTIONS)
        @returns Fill or None  
        '''
        for t in self.trades:
            if t.Direction.value == direction and not t.Booked:
                return t

    def close_existing_positions(self, trade):
        '''
        trade -> Fill
        @returns Blotter
        '''
        closing_trade = self.get_fifo_trade_by_direction(-1*trade.Direction.value)
        if trade.Booked or not closing_trade:
            return

        pnl = calc_pnl(closing_trade.OpenQuantity, 
                       closing_trade.PriceLevel, 
                       trade.OpenQuantity, 
                       trade.PriceLevel
        )  * self.contract_multiplier / self.tick_size * self.tick_value
        self.realized_pnl += pnl

        closing_trade.book(pnl, trade)
        return self.close_existing_positions(trade)

    def update(self, fill):
        '''
        trade -> Fill
        @returns Blotter
        '''
        fill.logger.info(f'{fill}')
        is_closing_trade = self.net_position and self.net_direction != fill.Direction

        if is_closing_trade:
            self.close_existing_positions(fill)
                                
        elif self.net_position:
            self.avg_open_price = calc_avg_open_price(self.net_position, self.avg_open_price, fill.OpenQuantity, fill.PriceLevel)
        else:
            self.avg_open_price = fill.PriceLevel

        if is_closing_trade and abs(self.net_position) < abs(fill.OpenQuantity):
            self.avg_open_price = fill.PriceLevel

        self.total_pnl = self.realized_pnl + self.unrealized_pnl
        self.net_position += fill.OrderFilled

        if not self.net_position:
            self.avg_open_price = None

        self.trades.append(fill)
        self.logger.info(self)
        return self

    def update_from_marketdata(self, last_price):
        '''
        last_price -> float
        @returns Blotter
        '''
        self.unrealized_pnl = (last_price - self.avg_open_price) * self.net_position
        self.total_pnl = self.realized_pnl + self.unrealized_pnl
        return self

    def initialize_from_list(self, fills:list):
        '''
        fills -> List
        @returns Blotter
        '''
        for f in fills:
            self.add_fill(f)
        return self

