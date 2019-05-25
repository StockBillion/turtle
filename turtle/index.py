#!/usr/bin/env python
#-*- coding: utf8 -*-
import argparse, numpy, datetime


class TurtleArgs:
    '海龟交易参数'

    def __init__(self):
        self.turtle_args = [3, 6, 100, 35, 20, 10, 20]
        self.codes = ['399300.SZ']
        self.dates = ['20180101', '20190218']
        self.files = [':memory:', ':memory:', 'records', 'images']
        self.params = [ 'stock', 'daily', 'long' ]

        parser = argparse.ArgumentParser(description="show example")
        parser.add_argument('cmd_name', default='group', nargs='?', 
                help="command name, [dl, data, down, download], [st, sti, index], test")
        parser.add_argument("-a", '--turtle_args', help="turtle arguments", nargs='*')
        parser.add_argument("-c", '--codes', help="stock codes", nargs='*')
        parser.add_argument("-d", "--dates", help="trade date", nargs='*')
        parser.add_argument("-f", "--files", help="stock data path", nargs='*')
        parser.add_argument("-p", '--params', help="data param", nargs='*')

        args = parser.parse_args()
        _today = datetime.date.today()
        _tomor  = _today + datetime.timedelta(days=1)

        _start = datetime.datetime(_today.year-1, _today.month, 1)
        self.dates = [_start.strftime('%Y%m%d'), _tomor.strftime('%Y%m%d')]

        if args.turtle_args:
            for i in range(0, len(args.turtle_args)):
                self.turtle_args[i] = int(args.turtle_args[i])

        if args.codes:
            self.codes = []
            for i in range(0, len(args.codes)):
                self.codes.append( args.codes[i].upper() )

        if args.dates:
            for i in range(0, len(args.dates)):
                self.dates[i] = args.dates[i]

        if args.files:
            for i in range(0, len(args.files)):
                self.files[i] = args.files[i]

        if args.params:
            for i in range(0, len(args.params)):
                self.params[i] = args.params[i]

        print( self.codes, self.turtle_args, self.files, self.dates, self.params )


class MovingAverage:
    '股票的移动平均线'

    def __init__(self, _prices):
        self.ma_indexs = {}
        self.prices = numpy.asarray(_prices)

    def moving_average(self, n):
        mas = []

        if n in self.ma_indexs:
            return self.ma_indexs[n]

        elif n == 1:
            mas.append(self.prices[0])
            for i in range(1, len(self.prices)):
                mas.append(self.prices[i-1])

        elif n == 2:
            mas.append(self.prices[0])
            mas.append(self.prices[0])
            for i in range(2, len(self.prices)):
                mas.append((self.prices[i-1] + self.prices[i-2])/2)

        else: # if n not in self.ma_indexs:
            m1 = int(n/2)
            m2 = n - m1

            if m1 not in self.ma_indexs:
                self.moving_average(m1)
            hs1 = self.ma_indexs[m1]

            if m2 not in self.ma_indexs:
                self.moving_average(m2)
            hs2 = self.ma_indexs[m2]

            len2 = len(self.prices)
            len1 = min(m2, len2)

            for i in range(0, len1):
                mas.append(hs2[i])
            for i in range(len1, len2):
                mas.append((hs2[i]*m2 + hs1[i-m2]*m1)/n)
        
        self.ma_indexs[n] = mas
        return self.ma_indexs[n]

class TurtleIndex:
    'Turtle Index, 海龟法则交易指标'

    def __init__(self):
        self.high_prices = {}
        self.low_prices = {}

    def clear(self):
        self.high_prices = {}
        self.low_prices = {}

    def simple_price_wave(self, _price_wave, period):
        wavema = MovingAverage(_price_wave)
        return wavema.moving_average(period)

    def correct_price_wave(self, _price_wave, _open, _close, period):
        _len = len(_price_wave)
        _price_wave[0] = _price_wave[0] / _open[0]
        for i in range(1, _len):
            _price_wave[i] = _price_wave[i] / _close[i-1]

        wavema = MovingAverage(_price_wave)
        _ave_wave = wavema.moving_average(period)

        _ave_wave[0] = _ave_wave[0] * _open[0]
        for i in range(1, _len):
            _ave_wave[i] = _ave_wave[i] * _close[i-1]
        return _ave_wave

    def statis_highest_price(self, x, n):
        ps = []

        if n in self.high_prices:
            return

        if n == 1:
            ps.append(x[0])

            for i in range(1, len(x)):
                ps.append(x[i-1])

        elif n == 2:
            ps.append(x[0])
            ps.append(x[0])

            for i in range(2, len(x)):
                if x[i-1] > x[i-2]:
                    ps.append(x[i-1])
                else:
                    ps.append(x[i-2])

        else:
            m1 = int(n/2)
            m2 = n - m1

            if m1 not in self.high_prices:
                self.statis_highest_price(x, m1)
            ps1 = self.high_prices[m1]

            if m2 not in self.high_prices:
                self.statis_highest_price(x, m2)
            ps2 = self.high_prices[m2]

            len2 = len(x)
            len1 = min(m2, len2)

            for i in range(0, len1):
                ps.append(ps2[i])

            for i in range(len1, len2):
                if ps2[i] > ps1[i-m2]:
                    ps.append(ps2[i])
                else:
                    ps.append(ps1[i-m2])

        self.high_prices[n] = ps

    def statis_lowest_price(self, x, n):
        ps = []

        if n in self.low_prices:
            return
        elif n == 1:
            ps.append(x[0])

            for i in range(1, len(x)):
                ps.append(x[i-1])

        elif n == 2:
            ps.append(x[0])
            ps.append(x[0])

            for i in range(2, len(x)):
                if x[i-1] < x[i-2]:
                    ps.append(x[i-1])
                else:
                    ps.append(x[i-2])

        else:
            m1 = int(n/2)
            m2 = n - m1

            if m1 not in self.low_prices:
                self.statis_lowest_price(x, m1)
            ps1 = self.low_prices[m1]

            if m2 not in self.low_prices:
                self.statis_lowest_price(x, m2)
            ps2 = self.low_prices[m2]

            len2 = len(x)
            len1 = min(m2, len2)

            for i in range(0, len1):
                ps.append(ps2[i])

            for i in range(len1, len2):
                if ps2[i] < ps1[i-m2]:
                    ps.append(ps2[i])
                else:
                    ps.append(ps1[i-m2])

        self.low_prices[n] = ps

def LongTurtleIndex(index, stock_data, long_period, short_period, loss_multiple, max_count = 5):
    'Long Turtle Index, 多头海龟法则交易指标'

    _opens, _highs, _lows, _closes = stock_data[1], stock_data[2], stock_data[3], stock_data[4]
    index.statis_highest_price(_highs, long_period)
    index.statis_lowest_price(_lows, short_period)

    Hl = index.high_prices[long_period]
    Ls = index.low_prices[short_period]
    Nl = index.simple_price_wave(_highs - _lows, long_period)
    
    long_count = 0
    states, key_prices = [], []
    keyP, keyN = _opens[0], 0

    for i in range(0, long_period):
        states.append(long_count)
        key_prices.append(keyP)

    for i in range(long_period, len(_highs)):
        if long_count > 0:
            append_price = keyP + keyN
            stop_price = max(Ls[i], keyP - keyN * loss_multiple)
        else:
            append_price = Hl[i]
            stop_price = Ls[i] 
        # stop_price2 = keyP - keyN*2

        while _highs[i] > append_price and long_count < max_count:
            if not long_count:
                keyN = Nl[i]

            long_count += 1
            if _opens[i] > append_price:
                keyP = _opens[i]
            else:
                keyP = append_price
            append_price = keyP + keyN

        if long_count > 0 and _lows[i] < stop_price:
            long_count = 0
            if _opens[i] < stop_price:
                keyP = _opens[i]
            else:
                keyP = stop_price

        # elif long_count > 0 and long_count < 4 and _highs[i] < stop_price2:
        #     long_count = 0
        #     keyP = _closes[i]

        states.append(long_count)
        key_prices.append(keyP)

    turtle_index = { 'long': Hl, 'short': Ls, 'state': states, 'key_price': key_prices, 'wave': Nl }
    turtle_index['long'][0] = _opens[0]
    turtle_index['short'][0] = _opens[0]

    return turtle_index

def LongTurtleIndex1(index, stock_data, long_period, short_period, loss_multiple, max_count = 5):
    'Long Turtle Index, 多头海龟法则交易指标'

    _opens, _highs, _lows, _closes = stock_data[1], stock_data[2], stock_data[3], stock_data[4]
    index.statis_highest_price(_highs, long_period)
    index.statis_lowest_price(_lows, short_period)

    Hl = index.high_prices[long_period]
    Ls = index.low_prices[short_period]
    Nl = index.simple_price_wave(_highs - _lows, long_period)
    
    long_count = 0
    states, key_prices = [], []
    keyP, keyN = _opens[0], 0

    for i in range(0, long_period):
        states.append(long_count)
        key_prices.append(keyP)

    for i in range(long_period, len(_highs)):
        if long_count > 0:
            append_price = keyP + keyN
            stop_price = max(Ls[i], keyP - keyN * loss_multiple)
        else:
            append_price = Hl[i]
            stop_price = Ls[i] 
        # stop_price2 = keyP - keyN*2

        if _highs[i] > append_price and long_count < max_count:
            if not long_count:
                keyN = Nl[i]

            long_count += 1
            if _opens[i] > append_price:
                keyP = _opens[i]
            else:
                keyP = append_price

        elif long_count > 0 and _lows[i] < stop_price:
            long_count = 0
            if _opens[i] < stop_price:
                keyP = _opens[i]
            else:
                keyP = stop_price

        # elif long_count > 0 and long_count < 4 and _highs[i] < stop_price2:
        #     long_count = 0
        #     keyP = _closes[i]

        states.append(long_count)
        key_prices.append(keyP)

    turtle_index = { 'long': Hl, 'short': Ls, 'state': states, 'key_price': key_prices, 'wave': Nl }
    turtle_index['long'][0] = _opens[0]
    turtle_index['short'][0] = _opens[0]

    return turtle_index

def ShortTurtleIndex(index, stock_data, long_period, short_period, loss_multiple, max_count = 5):
    'Short Turtle Index, 空头海龟法则交易指标'

    _opens, _highs, _lows, _closes = stock_data[1], stock_data[2], stock_data[3], stock_data[4]
    index.statis_highest_price(_highs, short_period)
    index.statis_lowest_price(_lows, long_period)

    Hs = index.high_prices[short_period]
    Ll = index.low_prices[long_period]
    Nl = index.simple_price_wave(_highs - _lows, long_period)
    
    short_count = 0
    states, key_prices = [], []
    keyP, keyN = _opens[0], 0

    for i in range(0, long_period):
        states.append(short_count)
        key_prices.append(keyP)

    for i in range(long_period, len(_highs)):
        if short_count > 0:
            append_price = keyP - keyN
            stop_price = min(Hs[i], keyP + keyN * loss_multiple)
        else:
            append_price = Ll[i]
            stop_price = Hs[i] 
        stop_price2 = keyP + keyN*2

        if _lows[i] < append_price and short_count < max_count:
            if not short_count:
                keyN = Nl[i]
            short_count += 1

            if _opens[i] < append_price:
                keyP = _opens[i]
            else:
                keyP = append_price

        elif short_count > 0 and _highs[i] > stop_price:
            short_count = 0

            if _opens[i] > stop_price:
                keyP = _opens[i]
            else:
                keyP = stop_price

        elif short_count > 0 and short_count < 4 and _lows[i] > stop_price2:
            short_count = 0
            keyP = _closes[i]

        states.append(short_count)
        key_prices.append(keyP)

    turtle_index = { 'short': Ll, 'long': Hs, 'state': states, 'key_price': key_prices, 'wave': Nl }
    turtle_index['short'][0] = _opens[0]
    turtle_index['long'][0] = _opens[0]

    return turtle_index

def LongTurtleIndex2(index, stock_data, long_period, short_period, loss_multiple, max_count = 5):
    'Long Turtle Index, 多头海龟法则交易指标'

    _open, _high, _low, _close = stock_data[1], stock_data[2], stock_data[3], stock_data[4]
    index.statis_highest_price(_high, long_period)
    index.statis_lowest_price(_low, short_period)

    Hl = index.high_prices[long_period]
    Ls = index.low_prices[short_period]
    Nl = index.simple_price_wave(_high - _low, long_period)
    
    long_count = 0
    states, key_prices = [], []
    keyP, keyN = _open[0], 0

    for i in range(0, long_period):
        states.append(long_count)
        key_prices.append(keyP)

    for i in range(long_period, len(_high)):
        _stop_frofit = Ls[i]
        if long_count > 0:
            append_price = keyP + keyN
            stop_price = max(_stop_frofit, keyP - keyN * loss_multiple)
        else:
            append_price = Hl[i]
            stop_price = _stop_frofit

        if long_count > 0 and _low[i] < stop_price:
            long_count = 0
            if _open[i] < stop_price:
                keyP = _open[i]
            else:
                keyP = stop_price

        elif _high[i] > append_price and long_count < max_count:
            if not long_count:
                keyN = Nl[i]

            long_count += 1
            if _open[i] > append_price:
                keyP = _open[i]
            else:
                keyP = append_price

        states.append(long_count)
        key_prices.append(keyP)

    turtle_index = { 'long_high': Hl, 'short_low': Ls, 'state': states, 'key_price': key_prices, 'wave': Nl }
    turtle_index['long_high'][0] = _open[0]
    turtle_index['short_low'][0] = _open[0]
    return turtle_index
    
    