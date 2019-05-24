#!/usr/bin/env python
#-*- coding: utf8 -*-
import numpy, pandas, math, datetime as dt, time
from turtle import trade, index, data, utils
from turtle.data import StockDataSource


class DauLTurtleTrade(utils.TradeTest):
    '双级海龟交易'

    def __init__(self):
        utils.TradeTest.__init__(self)

        self.curr_closes = {}
        self.float_str = StockDataSource.float_date(self.dates[0])
        self.float_end = StockDataSource.float_date(self.dates[1])

    def open_long_order(self, int_date, stock_data, wave, _open):

        # if not len(self.account.stocks):
        #     self.open_unit = self.account.total_value * self.turtle_args[6] * .001 / wave
        #     self.open_unit = int(self.open_unit/300)*300

        self.open_unit = self.account.total_value * self.turtle_args[6] * .001 / wave
        _key_price = max(stock_data['key_price'], _open)
        _loss_price = _key_price - wave *self.turtle_args[0]

        self._order(int_date, stock_data, self.open_unit, _key_price, _loss_price)
        self.order_count += 1

    def open_short_order(self, int_date, stock_data, wave, _open):

        # if not len(self.account.stocks):
        #     self.open_unit = self.account.total_value * self.turtle_args[6] * .001 / wave
        #     self.open_unit = int(self.open_unit/300)*300

        self.open_unit = self.account.total_value * self.turtle_args[6] * .001 / wave
        _key_price = min(stock_data['key_price'], _open)
        _loss_price = _key_price - wave *self.turtle_args[0]

        self._order(int_date, stock_data, -self.open_unit, _key_price, _loss_price)
        self.order_count += 1

    def long_turtle(self, code, data_list):
        _data_vec = numpy.transpose( data_list )
        turtle = index.TurtleIndex()
        index_long = index.LongTurtleIndex(turtle, _data_vec, self.turtle_args[2], 
                    self.turtle_args[3], self.turtle_args[0], self.turtle_args[1])
        turtle = index.TurtleIndex()
        index_short = index.LongTurtleIndex(turtle, _data_vec, self.turtle_args[4], 
                    self.turtle_args[5], self.turtle_args[0], self.turtle_args[1])

        # test.daul_turtle(code, _data_vec, index_long, index_short)
        # self.simple_daul_turtle(code, _data_vec, index_long, index_short)
        # self._start_test(self.turtle_args[2])

        init_max_count = 3
        all_days, long_days, _max_count = len(_data_vec[0]), 0, init_max_count
        long_state, short_state, max_value, trade_mode, high_price = 0, 0, 0, 0, 0

        opens, highs, lows, closes = _data_vec[1], _data_vec[2], _data_vec[3], _data_vec[4]
        open_prices, open_dates, max_states = [], [], []

        for _idx in range(self.turtle_args[2], all_days):
            float_date = _data_vec[0][_idx]
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

            self.account.UpdateValue(self.curr_closes, int_date)
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
                    self.open_long_order(int_date, stock_data, _wave, opens[_idx])

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

                if self.account.position_value > self.account.total_value*8:
                    trade_mode = 5
                    
                while trade_mode in [ 4 ] and short_state < index_short['state'][_idx] and short_state < _max_count:
                    short_state += 1
                    stock_data['key_price'] = index_short['key_price'][_idx] - (index_short['state'][_idx] - short_state)*_wave
                    self.open_long_order(int_date, stock_data, _wave, opens[_idx])

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
        print( pandas.DataFrame( self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio'] ) )
        self.account.status_info()

        print('all day %d, long day %d. %s %s, use time %.02f seconds.' % (all_days, long_days, 
                'single_turtle', code, time.time() - self.start))
        # self.account.save_records(code, self.files[2])
        self.plot(data_list, index_long, code)

    def short_turtle(self, code, data_list):
        _data_vec = numpy.transpose( data_list )
        turtle = index.TurtleIndex()
        index_long = index.ShortTurtleIndex(turtle, _data_vec, self.turtle_args[2], 
                    self.turtle_args[3], self.turtle_args[0], self.turtle_args[1])
        turtle = index.TurtleIndex()
        index_short = index.ShortTurtleIndex(turtle, _data_vec, self.turtle_args[4], 
                    self.turtle_args[5], self.turtle_args[0], self.turtle_args[1])

        init_max_count = 3
        all_days, long_days, _max_count = len(_data_vec[0]), 0, init_max_count
        long_state, short_state, max_value, trade_mode, high_price = 0, 0, 0, 0, 0

        opens, highs, lows, closes = _data_vec[1], _data_vec[2], _data_vec[3], _data_vec[4]
        open_prices, open_dates, max_states = [], [], []

        for _idx in range(self.turtle_args[2], all_days):
            float_date = _data_vec[0][_idx]
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
                    stock_data['key_price'] = closes[_idx]
                    print( int_date, self.account.total_value / max_value )

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
                    stock_data['key_price'] = index_long['key_price'][_idx] + (index_long['state'][_idx] - long_state)*_wave
                    self.open_short_order(int_date, stock_data, _wave, opens[_idx])

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

                if self.account.position_value > self.account.total_value*8:
                    trade_mode = 5
                    
                while trade_mode in [ 4 ] and short_state < index_short['state'][_idx] and short_state < _max_count:
                    short_state += 1
                    stock_data['key_price'] = index_short['key_price'][_idx] + (index_short['state'][_idx] - short_state)*_wave
                    self.open_short_order(int_date, stock_data, _wave, opens[_idx])

                # if trade_mode == 3:
                #     if high_price < highs[_idx]:
                #         high_price = highs[_idx]
                #     if lows[_idx] < high_price - _wave*4:
                #         self.single_clear(high_price - _wave*4, stock_data, int_date)
                #         self.order_count = 0

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
        print( pandas.DataFrame( self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio'] ) )
        self.account.status_info()

        print('all day %d, long day %d. %s %s, use time %.02f seconds.' % (all_days, long_days, 
                'single_turtle', code, time.time() - self.start))
        self.account.save_records(code, self.files[2])
        self.plot(data_list, index_long, code)


if __name__ == "__main__":

    test = DauLTurtleTrade()
    sdsr = data.StockData_SQLite( test.files[0] )

    for code in test.codes:
        sdsr.read_stock(code, test.dates[0], test.dates[1] )
        if not len(sdsr.stocks):
            sdsr.load(code, test.dates[0], test.dates[1], test.params[0], test.params[1])
        if not len(sdsr.stocks):
            continue
        data_list, _dates = sdsr.parse_price()

        test.start_test(test.turtle_args[2], 1000*10000)
        test.long_turtle( code, data_list )
        # test.short_turtle( code, data_list )

        # for row in data_list:
        #     row[1] = math.exp( 16 - math.log(row[1]) )
        #     temp = row[2]
        #     row[2] = math.exp( 16 - math.log(row[3]) )
        #     row[3] = math.exp( 16 - math.log( temp ) )
        #     row[4] = math.exp( 16 - math.log(row[4]) )
        # test.long_turtle( code, data_list )

        # len = len(data_list)-1
        # print( data_list[len] )
        # print( data_list[len] )





    # def daul_long(self, code, data_list, index_long, index_short):
    #     self._start_test(self.turtle_args[2])

    #     init_max_count = 3
    #     all_days, long_days, _max_count = len(data_list[0]), 0, init_max_count
    #     long_state, short_state, max_value, trade_mode, high_price = 0, 0, 0, 0, 0

    #     opens, highs, lows, closes = data_list[1], data_list[2], data_list[3], data_list[4]
    #     open_prices, open_dates, max_states = [], [], []

    #     for _idx in range(self.turtle_args[2], all_days):
    #         float_date = data_list[0][_idx]
    #         int_date = StockDataSource.int_date(float_date)
    #         self.print_progress(int_date)

    #         if float_date < self.float_str or float_date > self.float_end:
    #             # self.account.ProfitDaily()
    #             self.market_values.append(self.account.total_value)
    #             self.position_ratios.append(self.account.position_value / self.account.total_value)
    #             continue

    #         # self.account.ProfitDaily(int_date)
    #         self.curr_closes[code] = closes[_idx]
    #         stock_data = { 'ts_code': code, 'key_price': index_long['key_price'][_idx],
    #                 'open': opens[_idx], 'high': highs[_idx], 'low': lows[_idx], 'close': closes[_idx] }

    #         if (not index_long['state'][_idx] or self.account.total_value < max_value*.6) and trade_mode:
    #             if self.account.total_value < max_value*.6:
    #                 print( int_date, self.account.total_value / max_value )
    #                 stock_data['key_price'] = closes[_idx]

    #         # if not index_long['state'][_idx] and trade_mode:

    #             if len(self.account.stocks):
    #                 self.single_clear(stock_data['key_price'], stock_data, int_date)
    #                 max_value = self.account.total_value
    #             if not index_long['state'][_idx]:
    #                 long_state, short_state, trade_mode = 0, 0, 0
    #                 self.order_count, _max_count = 0, init_max_count
    #                 max_states.append(index_long['state'][_idx-1])

    #         elif index_long['state'][_idx]:
    #             long_days += 1
    #             _wave = index_long['wave'][_idx]

    #             while trade_mode in [ 0, 1 ] and long_state < index_long['state'][_idx] and long_state < _max_count:
    #                 # print( int_date, index_long['state'][_idx], index_short['state'][_idx], trade_mode, long_state, short_state )
    #                 long_state += 1
    #                 stock_data['key_price'] = index_long['key_price'][_idx] - (index_long['state'][_idx] - long_state)*_wave
    #                 self.open_order(int_date, stock_data, _wave, opens[_idx])

    #             if not trade_mode:
    #                 trade_mode = 1
    #                 # self.open_value = max(1000*10000, self.account.total_value)
    #                 max_value = self.open_value = self.account.total_value
    #                 open_prices.append(index_long['key_price'][_idx])
    #                 open_dates.append(float_date)

    #             elif index_long['state'][_idx] >= 4 and trade_mode < 2:
    #                 trade_mode = 2
    #             elif not index_short['state'][_idx-1] and index_short['state'][_idx] \
    #                 and index_long['state'][_idx] > 4 and self.order_count < 10:
    #                 short_state, trade_mode = 0, 4
    #                 if len(self.account.stocks):
    #                     _max_count = init_max_count
    #                 else:
    #                     _max_count = 1
    #                 # print( int_date, self.account.position_value, self.account.total_value )

    #             if trade_mode == 2 and index_long['state'][_idx] >= 6 and len(open_prices) > 1 and \
    #                 (open_prices[-1] < open_prices[-2] or open_dates[-1] - open_dates[-2] > 300):
    #                 trade_mode, high_price = 3, highs[_idx]
    #                 # print( int_date, self.account.total_value / max_value, index_long['state'][_idx], index_short['state'][_idx] )
    #                 # print( int_date, self.order_count, long_state, index_long['state'][_idx], short_state, index_short['state'][_idx] )

    #             if self.account.position_value > self.account.total_value*7:
    #                 trade_mode = 5
                    
    #             while trade_mode in [ 4 ] and short_state < index_short['state'][_idx] and short_state < _max_count:
    #                 short_state += 1
    #                 stock_data['key_price'] = index_short['key_price'][_idx] - (index_short['state'][_idx] - short_state)*_wave
    #                 self.open_order(int_date, stock_data, _wave, opens[_idx])

    #             if trade_mode == 3:
    #                 if high_price < highs[_idx]:
    #                     high_price = highs[_idx]
    #                 if lows[_idx] < high_price - _wave*4:
    #                     self.single_clear(high_price - _wave*4, stock_data, int_date)
    #                     self.order_count = 0

    #         self.account.UpdateValue(self.curr_closes, int_date)
    #         max_value = max(max_value, self.account.total_value)
    #         self.market_values.append(self.account.total_value)
    #         self.position_ratios.append(self.account.position_value / self.account.total_value)

    #     order_list = pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
    #             'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ])
    #     out_list = order_list[[ 'date', 'trade_price', 'volume', 'total_value', 'credit', 'lever' ]]
    #     for i in range(0, len(out_list), 30):
    #         print( out_list[i:i+30] )
    #     print( pandas.DataFrame(self.year_values, columns=['year', 'cash', 'ratio']) )

    #     if len(open_dates) > len(max_states):
    #         max_states.append(index_long['state'][-1])
    #     open_dates = list(map(lambda x: StockDataSource.str_date(x), open_dates))
        
    #     print( pandas.DataFrame( { "date": open_dates, "price": open_prices, "max_state": max_states } ) )
    #     print( pandas.DataFrame(self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio']) )

    #     print('all day %d, long day %d.' % (all_days, long_days))
    #     self.account.status_info()


        # _data_vec = numpy.transpose( data_list )

        # turtle = index.TurtleIndex()
        # index_long = index.LongTurtleIndex(turtle, _data_vec, test.turtle_args[2], 
        #             test.turtle_args[3], test.turtle_args[0], test.turtle_args[1])
        # turtle = index.TurtleIndex()
        # index_short = index.LongTurtleIndex(turtle, _data_vec, 
        #             test.turtle_args[4], test.turtle_args[5], test.turtle_args[0], test.turtle_args[1])

        # # test.daul_turtle(code, _data_vec, index_long, index_short)
        # # self.simple_daul_turtle(code, _data_vec, index_long, index_short)

        # print( "%s %s, use time %.02f seconds." %('single_turtle', code, time.time() - test.start))
        # test.account.save_records(code, test.files[2])
        # test.plot(data_list, index_long, code)


    # sys.argv = ['./stock.py', 'test', '-F', 'stock.data.db', '-D', '20090101', '-A', '3',  '6', '100', '30', '15', '20']
    # sys.argv = ['./stock.py', 'fix', '-f', '../data/stock.0414.db', '-d', '20090101'] # , '-c', '600519.sh', '-p', 'stock'
    # sys.argv = ['./stock.py', 'test', '-p', 'index', 'd',  '-d', '20050101']
    # sys.argv = ['./stock.py', 'test', '-f', '../data/stock.data.db', '-d', '20170101']

    # if cmd in ['disp', 'plot']:
    #     TurtleDisp()
    # elif cmd in ['list', 'ls']:
    #     TurtleList()
    # elif cmd in ['posi', 'ps']:
    #     pos = PositionCSV()
    # elif cmd in ['test', 'trade']:
    #     trade.DauLTurtleTrade()
    # elif cmd in ['fix', 'fixed']:
    #     FixedInvestByPE()
    #     # FixedInvestTrade()
    # else:
    #     print( "invalid command." )
