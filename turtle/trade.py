#!/usr/bin/env python
#-*- coding: utf8 -*-
import sys, argparse, numpy, pandas, math, time, datetime
import matplotlib.pyplot as plt, mpl_finance as mpf
from turtle import data, index, utils
from turtle.data import StockDataSource


class DauLTurtleTrade(utils.TradeTest):
    '双级海龟交易'

    def __init__(self):
        utils.TradeTest.__init__(self)
        sdsr = data.StockData_SQLite( self.files[0] )

        self.curr_closes = {}
        self.float_str = StockDataSource.float_date(self.dates[0])
        self.float_end = StockDataSource.float_date(self.dates[1])

        for code in self.codes:
            sdsr.read_stock(code, self.dates[0], self.dates[1] )
            if not len(sdsr.stocks):
                sdsr.load(code, self.dates[0], self.dates[1], self.params[0], self.params[1])
            if not len(sdsr.stocks):
                continue
            data_list, _dates = sdsr.parse_price()
            _data_vec = numpy.transpose( data_list )

            turtle = index.TurtleIndex()
            index_long = index.LongTurtleIndex(turtle, _data_vec, self.turtle_args[2], 
                    self.turtle_args[3], self.turtle_args[0], self.turtle_args[1])
            turtle = index.TurtleIndex()
            index_short = index.LongTurtleIndex(turtle, _data_vec, 
                    self.turtle_args[4], self.turtle_args[5], self.turtle_args[0], self.turtle_args[1])

            self.daul_turtle0(code, _data_vec, index_long, index_short)
            # self.simple_daul_turtle(code, _data_vec, index_long, index_short)

            print( "%s %s, use time %.02f seconds." %('single_turtle', code, time.time() - self.start))
            self.account.save_records(code, self.files[2])
            self.plot(data_list, index_long, code)

    def open_order(self, int_date, stock_data, wave, _open):
        key_price = stock_data['key_price']
        if key_price < _open:
            key_price = _open

        if not len(self.account.stocks):
            self.open_unit = self.account.total_value * self.turtle_args[6] * .001 / wave
            # self.open_unit = int(self.open_unit/300)*300
        _loss_price = key_price - wave *self.turtle_args[0]

        self._order(int_date, stock_data, self.open_unit, key_price, _loss_price)
        self.order_count += 1


    def daul_turtle0(self, code, data_list, index_long, index_short):
        self._start_test(self.turtle_args[2])

        init_max_count = 3
        all_days, long_days, _max_count = len(data_list[0]), 0, init_max_count
        long_state, short_state, max_value, trade_mode, high_price = 0, 0, 0, 0, 0

        opens, highs, lows, closes = data_list[1], data_list[2], data_list[3], data_list[4]
        open_prices, open_dates, max_states = [], [], []

        for _idx in range(self.turtle_args[2], all_days):
            float_date = data_list[0][_idx]
            int_date = StockDataSource.int_date(float_date)
            self.print_progress(int_date)

            if float_date < self.float_str or float_date > self.float_end:
                # self.account.ProfitDaily()
                self.market_values.append(self.account.total_value)
                self.position_ratios.append(self.account.position_value / self.account.total_value)
                continue

            # self.account.ProfitDaily(int_date)
            self.curr_closes[code] = closes[_idx]
            stock_data = { 'ts_code': code, 'key_price': index_long['key_price'][_idx],
                    'open': opens[_idx], 'high': highs[_idx], 'low': lows[_idx], 'close': closes[_idx] }

            if (not index_long['state'][_idx] or self.account.total_value < max_value*.6) and trade_mode:
                if self.account.total_value < max_value*.6:
                    print( int_date, self.account.total_value / max_value )
                    stock_data['key_price'] = closes[_idx]

            # if not index_long['state'][_idx] and trade_mode:

                if len(self.account.stocks):
                    self.single_clear(stock_data['key_price'], stock_data, int_date)
                    max_value = self.account.total_value
                if not index_long['state'][_idx]:
                    long_state, short_state, trade_mode = 0, 0, 0
                    self.order_count, _max_count = 0, init_max_count
                    max_states.append(index_long['state'][_idx-1])

            elif index_long['state'][_idx]:
                long_days += 1
                _wave = index_long['wave'][_idx]

                while trade_mode in [ 0, 1 ] and long_state < index_long['state'][_idx] and long_state < _max_count:
                    # print( int_date, index_long['state'][_idx], index_short['state'][_idx], trade_mode, long_state, short_state )
                    long_state += 1
                    stock_data['key_price'] = index_long['key_price'][_idx] - (index_long['state'][_idx] - long_state)*_wave
                    self.open_order(int_date, stock_data, _wave, opens[_idx])

                if not trade_mode:
                    trade_mode = 1
                    # self.open_value = max(1000*10000, self.account.total_value)
                    max_value = self.open_value = self.account.total_value
                    open_prices.append(index_long['key_price'][_idx])
                    open_dates.append(float_date)

                elif index_long['state'][_idx] >= 4 and trade_mode < 2:
                    trade_mode = 2
                elif not index_short['state'][_idx-1] and index_short['state'][_idx] \
                    and index_long['state'][_idx] > 4 and self.order_count < 10:
                    short_state, trade_mode = 0, 4
                    if len(self.account.stocks):
                        _max_count = init_max_count
                    else:
                        _max_count = 1
                    # print( int_date, self.account.position_value, self.account.total_value )

                if trade_mode == 2 and index_long['state'][_idx] >= 6 and len(open_prices) > 1 and \
                    (open_prices[-1] < open_prices[-2] or open_dates[-1] - open_dates[-2] > 300):
                    trade_mode, high_price = 3, highs[_idx]
                    # print( int_date, self.account.total_value / max_value, index_long['state'][_idx], index_short['state'][_idx] )
                    # print( int_date, self.order_count, long_state, index_long['state'][_idx], short_state, index_short['state'][_idx] )

                if self.account.position_value > self.account.total_value*7:
                    trade_mode = 5
                    
                while trade_mode in [ 4 ] and short_state < index_short['state'][_idx] and short_state < _max_count:
                    short_state += 1
                    stock_data['key_price'] = index_short['key_price'][_idx] - (index_short['state'][_idx] - short_state)*_wave
                    self.open_order(int_date, stock_data, _wave, opens[_idx])

                if trade_mode == 3:
                    if high_price < highs[_idx]:
                        high_price = highs[_idx]
                    if lows[_idx] < high_price - _wave*4:
                        self.single_clear(high_price - _wave*4, stock_data, int_date)
                        self.order_count = 0

            self.account.UpdateValue(self.curr_closes, int_date)
            max_value = max(max_value, self.account.total_value)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        order_list = pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
                'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ])
        out_list = order_list[[ 'date', 'trade_price', 'volume', 'total_value', 'credit', 'lever' ]]
        for i in range(0, len(out_list), 30):
            print( out_list[i:i+30] )
        print( pandas.DataFrame(self.year_values, columns=['year', 'cash', 'ratio']) )

        if len(open_dates) > len(max_states):
            max_states.append(index_long['state'][-1])
        open_dates = list(map(lambda x: StockDataSource.str_date(x), open_dates))
        
        print( pandas.DataFrame( { "date": open_dates, "price": open_prices, "max_state": max_states } ) )
        print( pandas.DataFrame(self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio']) )

        print('all day %d, long day %d.' % (all_days, long_days))
        self.account.status_info()


    def daul_turtle1(self, code, data_list, index_long, index_short):
        self._start_test(self.turtle_args[2])
        self.open_value, _loss_unit, _open_unit = 0, 0, 0

        opens, highs, lows, closes = data_list[1], data_list[2], data_list[3], data_list[4]
        all_days, long_days, long_state, short_state, trade_mode, order_count = len(data_list[0]), 0, 0, 0, 0, 0
        open_prices, open_dates, max_states = [], [], []

        for _idx in range(self.turtle_args[0], all_days):
            float_date = data_list[0][_idx]
            int_date = StockDataSource.int_date(float_date)
            self.print_progress(int_date)

            if float_date < self.float_str or float_date > self.float_end:
                # self.account.ProfitDaily()
                self.market_values.append(self.account.total_value)
                self.position_ratios.append(self.account.position_value / self.account.total_value)
                continue

            self.curr_closes[code] = closes[_idx]
            self.account.ProfitDaily(int_date)
            stock_data = { 'ts_code': code, 'key_price': index_long['key_price'][_idx],
                    'open': opens[_idx], 'high': highs[_idx], 'low': lows[_idx], 'close': closes[_idx] }

            if not index_long['state'][_idx] and order_count:
                if len(self.account.stocks):
                    self.single_clear(stock_data['key_price'], stock_data, int_date)
                long_state, short_state, trade_mode, order_count = 0, 0, 0, 0
                max_states.append(index_long['state'][_idx-1])
            
            else:
                long_days += 1

                if len(self.account.stocks) and index_long['state'][_idx] >= 6 and not trade_mode and len(open_prices) > 1 and \
                    (open_prices[-1] < open_prices[-2] or open_dates[-1] - open_dates[-2] > 300):
                    self.single_clear(stock_data['key_price'], stock_data, int_date)
                    
                if not index_short['state'][_idx] and index_long['state'][_idx] > 4:
                    short_state, trade_mode = 0, 1
                _long_on = long_state < index_long['state'][_idx] and long_state < 2
                _short_on = trade_mode and short_state < index_short['state'][_idx] and short_state < 2

                if (_long_on or _short_on) and order_count < 8: #and self.account.credit < self.account.total_value*2:
                    if not long_state:# or not short_state:
                        self.open_value = max(1000*10000, self.account.total_value)
                        open_prices.append(index_long['key_price'][_idx])
                        open_dates.append(float_date)
                        print( int_date, order_count, long_state, short_state, index_short['state'][_idx] )

                    if _long_on:
                        key_price = index_long['key_price'][_idx]
                    elif _short_on:
                        key_price = index_short['key_price'][_idx]
                    if key_price < opens[_idx]:
                        key_price = opens[_idx]

                    _total_value = max(1000*10000, self.account.total_value)
                    _loss_unit = _total_value * self.turtle_args[6] * .001
                    _open_unit = _loss_unit / index_long['wave'][_idx]
                    _loss_price = key_price - index_long['wave'][_idx] *self.turtle_args[0]
                    self._order(int_date, stock_data, _open_unit, key_price, _loss_price)

                    order_count += 1
                    long_state = index_long['state'][_idx]
                    short_state = index_short['state'][_idx]
                    
            self.account.UpdateValue(self.curr_closes, int_date)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        order_list = pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
                'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ])
        out_list = order_list[[ 'date', 'trade_price', 'volume', 'total_value', 'credit', 'lever' ]]
        for i in range(0, len(out_list), 30):
            print( out_list[i:i+30] )
        print( pandas.DataFrame(self.year_values, columns=['year', 'cash', 'ratio']) )

        if len(open_dates) > len(max_states):
            max_states.append(index_long['state'][-1])
        print( open_dates )
        print( max_states )
        print( pandas.DataFrame( { "date": open_dates, "price": open_prices, "max_state": max_states } ) )
        print( pandas.DataFrame(self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio']) )

        print('all day %d, long day %d.' % (all_days, long_days))
        self.account.status_info()

    def single_turtle(self, code, data_list, index_long):
        self._start_test(self.turtle_args[2])
        self.open_value, _loss_unit, _open_unit = 0, 0, 0

        dates, opens, highs, lows, closes = data_list[0], data_list[1], data_list[2], data_list[3], data_list[4]
        all_days, long_days, long_state = len(dates), 0, 0

        for _idx in range(self.turtle_args[0], all_days):
            float_date = dates[_idx]
            int_date = StockDataSource.int_date(float_date)
            self.print_progress(int_date)

            if float_date < self.float_str or float_date > self.float_end:
                # self.account.ProfitDaily()
                self.market_values.append(self.account.total_value)
                self.position_ratios.append(self.account.position_value / self.account.total_value)
                continue

            self.curr_closes[code] = closes[_idx]
            self.account.ProfitDaily(int_date)
            stock_data = { 'ts_code': code, 'key_price': index_long['key_price'][_idx],
                    'open': opens[_idx], 'high': highs[_idx], 'low': lows[_idx], 'close': closes[_idx] }

            if not index_long['state'][_idx] and len(self.account.stocks): 
                self.single_clear(stock_data['key_price'], stock_data, int_date)
                long_state = 0

            _long_open = long_state < index_long['state'][_idx] and long_state < 2
            if _long_open:
                    # and self.account.credit < self.account.total_value*2:
                if not long_state:
                    self.open_value = self.account.total_value

                key_price = index_long['key_price'][_idx]
                if key_price < opens[_idx]:
                    key_price = opens[_idx]

                _loss_unit = self.account.total_value * self.turtle_args[6] * .001
                _open_unit = _loss_unit / index_long['wave'][_idx]
                _loss_price = key_price - index_long['wave'][_idx] *self.turtle_args[0]

                if self._order(int_date, stock_data, _open_unit, key_price, _loss_price):
                    long_state = index_long['state'][_idx]

            if index_long['state']:
                long_days += 1

            self.account.UpdateValue(self.curr_closes, int_date)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        print( pandas.DataFrame(self.year_values, columns=['year', 'cash']) )
        print( pandas.DataFrame(self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio']) )
        # print( self.account.get_records()[[ 'order_time', 'price', 'volume', 'cash', 'credit' ]] )
        print('all day %d, long day %d.' % (all_days, long_days))
        self.account.status_info()

    def simple_daul_turtle(self, code, data_list, index_long, index_short):
        self._start_test()

        init_max_count = 3
        all_days, long_days, _max_count = len(data_list[0]), 0, init_max_count
        long_state, max_value, trade_mode = 0, 0, 0

        opens, highs, lows, closes = data_list[1], data_list[2], data_list[3], data_list[4]
        open_prices, open_dates, max_states = [], [], []

        for _idx in range(self.turtle_args[0], all_days):
            float_date = data_list[0][_idx]
            int_date = StockDataSource.int_date(float_date)
            self.print_progress(int_date)

            if float_date < self.float_str or float_date > self.float_end:
                # self.account.ProfitDaily()
                self.market_values.append(self.account.total_value)
                self.position_ratios.append(self.account.position_value / self.account.total_value)
                continue

            self.curr_closes[code] = closes[_idx]
            self.account.ProfitDaily(int_date)
            stock_data = { 'ts_code': code, 'key_price': index_short['key_price'][_idx],
                    'open': opens[_idx], 'high': highs[_idx], 'low': lows[_idx], 'close': closes[_idx] }

            if not index_short['state'][_idx] and trade_mode:
                if len(self.account.stocks):
                    self.single_clear(stock_data, int_date)
                long_state, trade_mode = 0, 0
                self.order_count, _max_count = 0, init_max_count
                max_states.append(index_long['state'][_idx-1])

            elif index_short['state'][_idx]:
                long_days += 1

                if not trade_mode:
                    trade_mode = 1
                    # self.open_value = max(1000*10000, self.account.total_value)
                    max_value = self.open_value = self.account.total_value
                    open_prices.append(index_long['key_price'][_idx])
                    open_dates.append(float_date)

                if long_state < index_short['state'][_idx] and long_state < _max_count:
                    self.open_order(int_date, stock_data, index_short['wave'][_idx], stock_data['key_price'], opens[_idx])
                    long_state = index_short['state'][_idx]

            self.account.UpdateValue(self.curr_closes, int_date)
            max_value = max(max_value, self.account.total_value)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        order_list = pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
                'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ])
        out_list = order_list[[ 'date', 'trade_price', 'volume', 'total_value', 'credit', 'lever' ]]
        for i in range(0, len(out_list), 30):
            print( out_list[i:i+30] )
        print( pandas.DataFrame(self.year_values, columns=['year', 'cash', 'ratio']) )

        if len(open_dates) > len(max_states):
            max_states.append(index_long['state'][-1])
        print( pandas.DataFrame( { "date": open_dates, "price": open_prices, "max_state": max_states } ) )
        print( pandas.DataFrame(self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio']) )

        print('all day %d, long day %d.' % (all_days, long_days))
        self.account.status_info()


        # _total_value = max(1000*10000, self.account.total_value)
        # _loss_unit = _total_value * self.turtle_args[6] * .001
        # _open_unit = _loss_unit / wave

        # _open_unit = self.account.total_value * self.turtle_args[6] * .001 / wave
        # _open_unit = int(_open_unit/300)*300

            # self.account.UpdateValue(self.curr_closes, int_date)
            # if int_date == 20190222:
            #     print( int_date, self.account.total_value / max_value, index_long['state'][_idx] )
            #     print( int_date, self.account.total_value, max_value*.6, trade_mode, index_long['state'][_idx] )

                # while trade_mode in [ 3, 4 ] and short_state < index_short['state'][_idx] and short_state < _max_count:
                #     stock_data['key_price'] = index_short['key_price'][_idx]
                #     self.open_order(int_date, stock_data, _wave, opens[_idx])
                #     short_state += 1

                # print( int_date, self.account.position_value, self.account.total_value )
                # if self.order_count > 5: 
                #     trade_mode = 5

                    # print( int_date, index_long['state'][_idx], index_short['state'][_idx], trade_mode, long_state, short_state, _wave )
                    # short_state = index_short['state'][_idx]

                    # self.single_clear(closes[_idx], stock_data, int_date)
                    # self.order_count = 0
                    # print( int_date, high_price, lows[_idx], high_price - _wave*3 )
                        # stock_data['key_price'] = high_price - _wave*2

                # while trade_mode == 1 and long_state < index_long['state'][_idx] and long_state < _max_count:
                #     self.open_order(int_date, stock_data, _wave, opens[_idx])
                #     long_state += 1
                    # long_state = index_long['state'][_idx]
                    # print( int_date, self.order_count, long_state, index_long['state'][_idx], short_state, index_short['state'][_idx] )

                # if trade_mode == 2 and index_long['state'][_idx] >= 6 and len(open_prices) > 1 and \
                #     (open_prices[-1] < open_prices[-2] or open_dates[-1] - open_dates[-2] > 300):
                #     self.single_clear(stock_data, int_date)
                #     self.order_count, trade_mode = 0, 3
                #     # print( int_date, self.order_count, short_state, index_short['state'][_idx] )

    # def open_order(self, int_date, stock_data, wave, key_price, _open):
    #     if key_price < _open:
    #         key_price = _open

    #     # _total_value = max(1000*10000, self.account.total_value)
    #     # _loss_unit = _total_value * self.turtle_args[6] * .001
    #     # _open_unit = _loss_unit / wave

    #     # _open_unit = self.account.total_value * self.turtle_args[6] * .001 / wave
    #     # _open_unit = int(_open_unit/300)*300

    #     if not len(self.account.stocks):
    #         self.open_unit = self.account.total_value * self.turtle_args[6] * .001 / wave
    #         # self.open_unit = int(self.open_unit/300)*300
    #     _loss_price = key_price - wave *self.turtle_args[0]

    #     self._order(int_date, stock_data, self.open_unit, key_price, _loss_price)
    #     self.order_count += 1


            # if (not index_long['state'][_idx] or not index_short['state'][_idx]) and trade_mode:
            #     if not index_long['state'][_idx]:
            #         stock_data['key_price'] = index_long['key_price'][_idx]
            #     if len(self.account.stocks):
            #         self.single_clear(stock_data, int_date)
            #     long_state, trade_mode = 0, 0
            #     self.order_count, _max_count = 0, init_max_count
            #     max_states.append(index_long['state'][_idx-1])

            # elif index_long['state'][_idx] and index_short['state'][_idx]:
            #     long_days += 1

            #     if not trade_mode:
            #         trade_mode = 1
            #         # self.open_value = max(1000*10000, self.account.total_value)
            #         max_value = self.open_value = self.account.total_value
            #         open_prices.append(index_long['key_price'][_idx])
            #         open_dates.append(float_date)

            #     if index_long['state'][_idx] < index_short['state'][_idx]:
            #         stock_data['key_price'] = index_long['key_price'][_idx]
            #     _state = min(index_long['state'][_idx], index_short['state'][_idx])
            #     if long_state < _state and long_state < _max_count:
            #         self.open_order(int_date, stock_data, index_short['wave'][_idx], stock_data['key_price'], opens[_idx])
            #         long_state = _state
