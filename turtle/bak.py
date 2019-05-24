


    def fixed_invest(self, code, data_list, index_long):
        self._start_test()
        self.open_value, _loss_unit, _open_unit = 0, 0, 0
    
        all_days, month, long_state = len(data_list[0]), 0, 0
        opens, highs, lows, closes = data_list[1], data_list[2], data_list[3], data_list[4]
    
        for _idx in range(self.arguments[0], all_days):
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
            
            if not index_long['state'][_idx] and index_long['state'][_idx-1] \
                and len(self.account.stocks):
                self.single_clear(stock_data, int_date)
                self.open_value, long_state = 0, 0
            
            if long_state < index_long['state'][_idx] and long_state < 2:
                key_price = index_long['key_price'][_idx]
                if key_price < opens[_idx]:
                    key_price = opens[_idx]
                    
                _cash_unit = self.account.cash * 0.5
                _open_unit = _cash_unit / opens[_idx]
                self.open_value += _cash_unit
                # _loss_price = key_price - index_long['wave'][_idx] *self.arguments[0]

                self._order(int_date, stock_data, _open_unit, key_price, 0)
                long_state = index_long['state'][_idx]
                
            _month = StockDataSource.datetime(int_date).month
            if month != _month:
                month = _month
                self.account.Rechange( 5000*1000 )
                
                _open_unit = 5000 *1000 / opens[_idx]
                self.open_value += 5000 *1000
                self._order(int_date, stock_data, _open_unit, opens[_idx], 0)
    
            self.account.UpdateValue(self.curr_closes, int_date)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        print( pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
                'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ]) )
        print( pandas.DataFrame(self.year_values, columns=['year', 'cash', 'ratio']) )
        print( pandas.DataFrame(self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio']) )
        # print('all day %d, long day %d.' % (all_days, long_days))
        self.account.status_info()

    
    def acc_daul_turtle0(self, code, data_list, index_long, index_short):
        self._start_test()
        self.open_value, _loss_unit, _open_unit = 0, 0, 0

        opens, highs, lows, closes = data_list[1], data_list[2], data_list[3], data_list[4]
        all_days, long_days, month = len(data_list[0]), 0, 0
        long_state, short_state, trade_mode, order_count = 0, 0, 0, 0

        for _idx in range(self.arguments[0], all_days):
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

            if index_long['state'][_idx]:
                long_days += 1
            
            # if not trade_mode and index_long['state'][_idx] > 9 and order_count: # len(self.account.stocks):
            #     self.single_clear(stock_data, int_date)
            #     order_count = 0
                
            # if trade_mode and index_short['state'][_idx] > 9 and order_count: # len(self.account.stocks):
            #     stock_data['key_price'] = index_short['key_price'][_idx]
            #     self.single_clear(stock_data, int_date)
            #     order_count = 0
              
            if not index_long['state'][_idx] and order_count: # len(self.account.stocks):
                self.single_clear(stock_data, int_date)
                long_state, short_state, trade_mode, order_count = 0, 0, 0, 0
            if not index_short['state'][_idx] and index_long['state'][_idx] > 4:
                short_state, trade_mode = 0, 1

            _long_on = long_state < index_long['state'][_idx] and long_state < 2
            _short_on = trade_mode and short_state < index_short['state'][_idx] and short_state < 2

            # if (not index_long['state'][_idx] or not index_short['state'][_idx]) and len(self.account.stocks):
            #     if not index_long['state'][_idx]:
            #         self.single_clear(stock_data, int_date)
            #         long_state, short_state, trade_mode = 0, 0, 0
            #     elif index_long['state'][_idx] > 4:
            #         short_state, trade_mode = 0, 1

            # if int_date == 20150619:
            #     print( index_long['state'][_idx], index_long['key_price'][_idx], index_short['state'][_idx], index_short['key_price'][_idx] )
            #     print( int_date, long_state, short_state, trade_mode, _long_on, _short_on )

            # if int_date == 20180112:
            #     # print( stock_data )
            #     print( index_long['state'][_idx], index_long['key_price'][_idx], index_short['state'][_idx], index_short['key_price'][_idx] )
            #     print( int_date, long_state, short_state, trade_mode, _long_on, _short_on )

            # elif int_date == 20180115:
            #     # print( stock_data )
            #     print( index_long['state'][_idx], index_long['key_price'][_idx], index_short['state'][_idx], index_short['key_price'][_idx] )
            #     print( int_date, long_state, short_state, trade_mode, _long_on, _short_on )

            if index_long['state'][_idx] and order_count < 4 and ( _long_on or _short_on ): #and self.account.credit < self.account.total_value*2:
                if not long_state:# or not short_state:
                    self.open_value = self.account.total_value+1

                if _long_on:
                    key_price = index_long['key_price'][_idx]
                elif _short_on:
                    key_price = index_short['key_price'][_idx]
                if key_price < opens[_idx]:
                    key_price = opens[_idx]

                # _loss_unit = 400000
                # print( int_date, _loss_unit )
                _total_value = max(1000*10000, self.account.total_value)
                _loss_unit = _total_value * self.arguments[6] * .001
                _open_unit = _loss_unit / index_long['wave'][_idx]
                _loss_price = key_price - index_long['wave'][_idx] *self.arguments[0]
                self._order(int_date, stock_data, _open_unit, key_price, _loss_price)

                # _open_unit = self.account.total_value / key_price
                # self._order(int_date, stock_data, _open_unit, key_price, 0)
                order_count += 1
                long_state = index_long['state'][_idx]
                short_state = index_short['state'][_idx]
                
                # if self._order(int_date, stock_data, _open_unit, key_price, _loss_price):
                #     long_state = index_long['state'][_idx]
                #     short_state = index_short['state'][_idx]

            # elif long_state:
            #     long_state, short_state, trade_mode = 0, 0, 0

            self.account.UpdateValue(self.curr_closes, int_date)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        order_list = pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
                'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ])
        print( order_list[[ 'date', 'trade_price', 'volume', 'total_value', 'credit', 'lever' ]] )
        print( pandas.DataFrame(self.year_values, columns=['year', 'cash', 'ratio']) )
        print( pandas.DataFrame(self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio']) )
        print('all day %d, long day %d.' % (all_days, long_days))
        self.account.status_info()


    def acc_daul_turtle1(self, code, data_list, index_long, index_short):
        self._start_test()
        self.open_value, _loss_unit, _open_unit = 0, 0, 0

        opens, highs, lows, closes = data_list[1], data_list[2], data_list[3], data_list[4]
        all_days, long_days, long_state, short_state, trade_mode, prev_key = len(data_list[0]), 0, 0, 0, 0, 1000000

        for _idx in range(self.arguments[0], all_days):
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


            if trade_mode == 0 and short_state < index_short['state'][_idx] and index_short['key_price'][_idx] > prev_key:
                long_state, short_state, trade_mode = 7, 0, 1
                self.open_value = self.account.total_value
                # prev_key = index_short['key_price'][_idx]
            if trade_mode < 2 and long_state < index_long['state'][_idx]:
                if not trade_mode:
                    self.open_value = self.account.total_value
                short_state, trade_mode = 0, 2
                # if not trade_mode:
                #     long_state, short_state, trade_mode = 0, 0, 2
                # else:
                #     long_state, short_state, trade_mode = 0, 0, 2
                # prev_key = index_short['key_price'][_idx]
            elif trade_mode == 2 and not index_short['state'][_idx] and index_long['state'][_idx] > 4:
                short_state, trade_mode = 0, 3
            elif trade_mode == 3 and not index_short['state'][_idx]:
                short_state = 0

            _close_short = trade_mode == 1 and not index_short['state'][_idx]
            _close_long  = trade_mode > 1 and not index_long['state'][_idx]
            if len(self.account.stocks) and (_close_long or _close_short):
                if _close_short:
                    stock_data['key_price'] = index_short['key_price'][_idx]
                self.single_clear(stock_data, int_date)
                long_state, short_state, trade_mode = 0, 0, 0
                print( int_date, long_state, short_state, trade_mode, key_price, prev_key )


            _open_long  = trade_mode == 2 and long_state < index_long['state'][_idx] and long_state < 2
            _open_short = trade_mode in [1, 3] and short_state < index_short['state'][_idx] and short_state < 2

            if _open_long or _open_short:
                if _open_long:
                    key_price = index_long['key_price'][_idx]
                elif _open_short:
                    key_price = index_short['key_price'][_idx]
                if key_price < opens[_idx]:
                    key_price = opens[_idx]

                _loss_unit = self.account.total_value * self.arguments[6] * .001
                _open_unit = _loss_unit / index_long['wave'][_idx]
                _loss_price = key_price - index_long['wave'][_idx] *self.arguments[0]

                if self._order(int_date, stock_data, _open_unit, key_price, _loss_price):
                    long_state = index_long['state'][_idx]
                    short_state = index_short['state'][_idx]
                    print( int_date, long_state, short_state, trade_mode, key_price, prev_key )
                    prev_key = key_price

            if index_long['state'][_idx]:
                long_days += 1

            # if (not index_long['state'][_idx] or not index_short['state'][_idx]) and len(self.account.stocks): 
            #     if (not index_long['state'][_idx] and trade_mode > 1) or not index_short['state'][_idx]:
            #         self.single_clear(stock_data, int_date)
            #         long_state, short_state, trade_mode = 0, 0, 0
            #     elif index_long['state'][_idx] > 4:
            #         short_state, trade_mode = 0, 1

            # _long_on = long_state < index_long['state'][_idx] and long_state < 2
            # _short_on = trade_mode == 3 and short_state < index_short['state'][_idx] and short_state < 2

            # if index_long['state'][_idx] and ( _long_on or _short_on ):
            #     if not long_state:
            #         self.open_value = self.account.total_value

            #     if _long_on:
            #         key_price = index_long['key_price'][_idx]
            #     elif _short_on:
            #         key_price = index_short['key_price'][_idx]
            #     if key_price < opens[_idx]:
            #         key_price = opens[_idx]

            #     _loss_unit = self.account.total_value * self.arguments[5] * .001
            #     _open_unit = _loss_unit / index_long['wave'][_idx]
            #     _loss_price = key_price - index_long['wave'][_idx] *self.arguments[0]

            #     if self._order(int_date, stock_data, _open_unit, key_price, _loss_price):
            #         long_state = index_long['state'][_idx]
            #         short_state = index_short['state'][_idx]

            # elif long_state:
            #     long_state, short_state, trade_mode = 0, 0, 0

            self.account.UpdateValue(self.curr_closes, int_date)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        print( pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
                'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ]) )
        print( pandas.DataFrame(self.year_values, columns=['year', 'cash']) )
        print( pandas.DataFrame(self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio']) )
        print('all day %d, long day %d.' % (all_days, long_days))
        self.account.status_info()


    def acc_daul_turtle3(self, code, data_list, index_long, index_short):
        self._start_test()
        self.open_value, _loss_unit, _open_unit = 0, 0, 0

        dates, opens, highs, lows, closes = data_list[0], data_list[1], data_list[2], data_list[3], data_list[4]
        all_days, long_days, long_state, short_state, short_closed = len(dates), 0, 0, 0, 0

        for _idx in range(self.arguments[0], all_days):
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
                self.single_clear(stock_data, int_date)
                long_state, short_state, short_closed = 0, 0, 0
            if not index_short['state'][_idx] and index_long['state'][_idx] > 4 and not short_closed:
                short_state, short_closed = 0, 1

            _long_on = long_state < index_long['state'][_idx] and long_state < 2
            _short_on = short_closed and short_state < index_short['state'][_idx] and short_state < 2

            # _short_on = short_state < index_short['state'][_idx] and short_state < 2 and index_short['state'][_idx] >= 5
            # if index_long['state'][_idx] > 3 and not index_short['state'][_idx] and not _short_close:
            #     short_close = 1
            #     short_state = 0
            #  #and index_short['state'][_idx] >= 5
            # if int_date > 20160801 and int_date < 20160901:
            #     print( int_date, _short_close, _short_on, index_long['state'][_idx] )

            # if int_date > 20070321 and int_date <= 20070726:
            #     # print( stock_data )
            #     print( index_long['state'][_idx], index_long['key_price'][_idx], index_short['state'][_idx], index_short['key_price'][_idx] )
            #     print( int_date, long_state, short_state, short_closed, _long_on, _short_on )

            if index_long['state'][_idx] and ( _long_on or _short_on ):
                    # and self.account.credit < self.account.total_value*2:
                if not long_state:
                    self.open_value = self.account.total_value

                if _long_on:
                    key_price = index_long['key_price'][_idx]
                elif _short_on:
                    key_price = index_short['key_price'][_idx]
                if key_price < opens[_idx]:
                    key_price = opens[_idx]

                _loss_unit = self.account.total_value * self.arguments[6] * .001
                _open_unit = _loss_unit / index_long['wave'][_idx]
                _loss_price = key_price - index_long['wave'][_idx] *self.arguments[0]

                if self._order(int_date, stock_data, _open_unit, key_price, _loss_price):
                    long_state = index_long['state'][_idx]
                    short_state = index_short['state'][_idx]
                    if short_state > 1:
                        short_closed = 0

            if index_long['state']:
                long_days += 1

            self.account.UpdateValue(self.curr_closes, int_date)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        print( pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
                'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ]) )
        print( pandas.DataFrame(self.year_values, columns=['year', 'cash']) )
        print( pandas.DataFrame(self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio']) )
        # print( self.account.get_records()[[ 'order_time', 'price', 'volume', 'cash', 'credit' ]] )
        print('all day %d, long day %d.' % (all_days, long_days))
        self.account.status_info()


    def simple_daul_turtle(self, code, data_list, index_long, index_short):
        self._start_test()
        self.open_value, _loss_unit, _open_unit = 0, 0, 0

        dates, opens, highs, lows, closes = data_list[0], data_list[1], data_list[2], data_list[3], data_list[4]
        all_days, long_days, long_state, short_state, trade_mode = len(dates), 0, 0, 0, 0

        for _idx in range(self.arguments[0], all_days):
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

            # if int_date == 20090812:
            #     print( stock_data )
            #     print( index_long['state'][_idx], index_long['key_price'][_idx], index_short['state'][_idx], index_short['key_price'][_idx] )
            #     print( long_state, short_state, trade_mode )

            if (not index_long['state'][_idx] or not index_short['state'][_idx]) and len(self.account.stocks): 
                if not index_long['state'][_idx]:
                    self.single_clear(stock_data, int_date)
                    long_state, short_state, trade_mode = 0, 0, 0
                elif index_long['state'][_idx] > 4:
                    # stock_data['key_price'] = index_short['key_price'][_idx]
                    # self.single_clear(stock_data, int_date)
                    short_state, trade_mode = 0, 1

            _long_on = long_state < index_long['state'][_idx] and long_state < 2
            _short_on = trade_mode and short_state < index_short['state'][_idx] and short_state < 2

            if index_long['state'][_idx] and ( _long_on or _short_on ):
                if not long_state:
                # if (not long_state and not trade_mode) or (not short_state and trade_mode):
                    self.open_value = self.account.total_value

                if _long_on:
                    key_price = index_long['key_price'][_idx]
                elif _short_on:
                    key_price = index_short['key_price'][_idx]
                if key_price < opens[_idx]:
                    key_price = opens[_idx]

                _loss_unit = self.account.total_value * self.arguments[6] * .001
                _open_unit = _loss_unit / index_long['wave'][_idx]
                _loss_price = key_price - index_long['wave'][_idx] *self.arguments[0]

                if self._order(int_date, stock_data, _open_unit, key_price, _loss_price):
                    long_state = index_long['state'][_idx]
                    short_state = index_short['state'][_idx]

            if index_long['state']:
                long_days += 1
            elif long_state:
                long_state, short_state, trade_mode = 0, 0, 0

            self.account.UpdateValue(self.curr_closes, int_date)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        print( pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
                'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ]) )
        # print( self.account.get_records()[[ 'order_time', 'price', 'volume', 'cash', 'credit' ]] )
        print( pandas.DataFrame(self.year_values, columns=['year', 'cash']) )
        print( pandas.DataFrame(self.records, columns=['date', 'price', 'total', 'cash', 'profit', 'ratio']) )
        print('all day %d, long day %d.' % (all_days, long_days))
        self.account.status_info()


# class DauLTurtleTrade(TradeTest):
#     '双级海龟交易'

#     def __init__(self):
#         TradeTest.__init__(self)
#         sdsr = data.StockData_SQLite( self.files[0] )

#         self.float_str = StockDataSource.float_date(self.dates[0])
#         self.float_end = StockDataSource.float_date(self.dates[1])

#         for code in self.good_codes:
#             sdsr.read_stock(code, self.dates[0], self.dates[1] )
#             if not len(sdsr.stocks):
#                 sdsr.load(code, self.dates[0], self.dates[1], self.good_type)
#             if not len(sdsr.stocks):
#                 continue
#             data_list, _dates = sdsr.parse_price()
#             _data_vec = numpy.transpose( data_list )

#             turtle = index.TurtleIndex()
#             index_long = index.LongTurtleIndex(turtle, _data_vec, 
#                     self.arguments[2], self.arguments[3], self.arguments[0], self.arguments[1])
#             turtle = index.TurtleIndex()
#             index_short = index.LongTurtleIndex(turtle, _data_vec, 
#                     self.arguments[4], self.arguments[5], self.arguments[0], self.arguments[1])

#             self.daul_turtle0(code, _data_vec, index_long, index_short)

#     def test_turtle(self, code, data_list, index_long, index_short):
#         self._start_test()

#         self.trade_mode, self.order_count, self.open_value, self.max_value = 0, 0, 0, 0
#         self.open_prices, self.open_dates, self.max_states = [], [], []
#         self.curr_closes = {}

#         opens, highs, lows, closes = data_list[1], data_list[2], data_list[3], data_list[4]
#         all_days, long_days, long_state, short_state = len(data_list[0]), 0, 0, 0

#         for _idx in range(self.arguments[0], all_days):
#             float_date = data_list[0][_idx]
#             int_date = StockDataSource.int_date(float_date)
#             self.print_progress(int_date)

#             if float_date < self.float_str or float_date > self.float_end:
#                 # self.account.ProfitDaily()
#                 self.market_values.append(self.account.total_value)
#                 self.position_ratios.append(self.account.position_value / self.account.total_value)
#                 continue

#             self.curr_closes[code] = closes[_idx]
#             self.account.ProfitDaily(int_date)
#             stock_data = { 'ts_code': code, 'key_price': index_long['key_price'][_idx],
#                     'open': opens[_idx], 'high': highs[_idx], 'low': lows[_idx], 'close': closes[_idx] }
#             self.account.UpdateValue(self.curr_closes, int_date)

#     def turtle_core(self):
#         self.account.UpdateValue(self.curr_closes, int_date)
#         if (not index_long['state'][_idx] or self.account.total_value < max_value*.6) and trade_mode:
#             if self.account.total_value < max_value*.6:
#                 stock_data['key_price'] = lows[_idx]

#             # if (not index_long['state'][_idx] or self.account.total_value < max_value*.6) and trade_mode:
#             #     if self.account.total_value < max_value*.6:
#             #         stock_data['key_price'] = opens[_idx]

#             # if (not index_long['state'][_idx] or index_long['long_high'][_idx] *.9 > lows[_idx]) and trade_mode:
#             #     if index_long['long_high'][_idx] *.9 > lows[_idx]:
#             #         stock_data['key_price'] = lows[_idx]
                    
#             # if not index_long['state'][_idx] and trade_mode:

#             if len(self.account.stocks):
#                 self.single_clear(stock_data, int_date)
#                 self.max_value = self.account.total_value
#             if not index_long['state'][_idx]:
#                 self.long_state, self.short_state, self.trade_mode, self.order_count = 0, 0, 0, 0
#                 self.max_states.append(index_long['state'][_idx-1])

#         elif index_long['state'][_idx]:
#             long_days += 1

#             if not self.trade_mode:
#                 self.trade_mode = 1
#                     # self.open_value = max(1000*10000, self.account.total_value)
#                 self.open_value = self.account.total_value
#                 self.max_value = self.open_value
#                 self.open_prices.append(index_long['key_price'][_idx])
#                 self.open_dates.append(float_date)
#             elif index_long['state'][_idx] >= 4 and trade_mode < 2:
#                 self.trade_mode = 2
#             elif not index_short['state'][_idx-1] and index_short['state'][_idx] and index_long['state'][_idx] > 4 and self.order_count < 10:
#                 self.short_state, self.trade_mode = 0, 4
#                     # print( int_date, self.account.position_value, self.account.total_value )

#                 # print( int_date, self.account.position_value, self.account.total_value )
#             if self.account.position_value > self.account.total_value*8:
#                     trade_mode = 5

#             if int_date in [ 20141031, 20141124 ]:
#                     print( int_date, self.order_count, long_state, index_long['state'][_idx], short_state, index_short['state'][_idx] )

#             if trade_mode == 1 and long_state < index_long['state'][_idx] and long_state < 3:
#                     self.open_order(int_date, stock_data, index_long['wave'][_idx], index_long['key_price'][_idx], opens[_idx])
#                     long_state = index_long['state'][_idx]
#                     # print( int_date, self.order_count, long_state, index_long['state'][_idx], short_state, index_short['state'][_idx] )

#             elif trade_mode == 2 and index_long['state'][_idx] >= 6 and len(open_prices) > 1 and \
#                     (open_prices[-1] < open_prices[-2] or open_dates[-1] - open_dates[-2] > 300):
#                     self.single_clear(stock_data, int_date)
#                     self.order_count, trade_mode, state3_low = 0, 3, lows[_idx]
#                     # print( int_date, self.order_count, short_state, index_short['state'][_idx] )

#             elif trade_mode == 4 and short_state < index_short['state'][_idx] and short_state < 2:
#                     self.open_order(int_date, stock_data, index_long['wave'][_idx], index_short['key_price'][_idx], opens[_idx])
#                     short_state = index_short['state'][_idx]

#         self.account.UpdateValue(self.curr_closes, int_date)
#         self.max_value = max(self.max_value, self.account.total_value)
#         self.market_values.append(self.account.total_value)
#         self.position_ratios.append(self.account.position_value / self.account.total_value)


        # volume = self.account.Volume(stock_data['ts_code'])
        
        # trade_price = stock_data['key_price']
        # if trade_price > stock_data['open']:
        #     trade_price = stock_data['open']
            
        # if volume and self._order(int_date, stock_data, -volume, trade_price):
        #     profit = self.account.total_value - self.open_value
        #     self.records.append( [int_date, '%.03f'%trade_price, int(volume), 
        #             '%.02f'%(self.account.total_value*.0001), 
        #             '%.02f'%(profit*.0001), '%.02f'%(profit*100/self.open_value) ] )
                    
        #     new_order = [int_date, '%.3f'%trade_price, 0, int(-volume), 
        #             '%.03f'%(self.account.total_value*0.0001), '%.03f'%(self.account.credit*0.0001), 
        #             '%.03f'%(self.account.credit/self.account.total_value*100), stock_data['ts_code'] ]
        #     self.curr_orders.append ( new_order )
        #     self.hist_orders.append( new_order )
        #     # print( pandas.DataFrame(self.curr_orders, columns=[ 'date', 'trade_price', 
        #     #     'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ]) )

        #     for i in range(len(self.curr_orders)-1, -1, -1):
        #         if self.curr_orders[i][7] == stock_data['ts_code']:
        #             del self.curr_orders[i]
                    
                # if _state > 10000 and self.account.credit < self.account.total_value:
                #     trade_price = index_row['key_price']
                #     if index_row['open'] > trade_price:
                #         trade_price = index_row['open']

                #     _loss_unit = self.account.total_value * self.arguments[4] * .001
                #     _open_unit = _loss_unit  / index_row['wave']
                #     if self._order(int_date, index_row, _open_unit, trade_price, 
                #             trade_price - index_row['wave']*self.arguments[2]):
                #         _state = _state + 1

            # for i in range(len(self.orders)-1, -1, -1):
            #     stop_loss = self.orders[i][3]
            #     if index_row['low'] < stop_loss:
            #         if index_row['open'] < stop_loss:
            #             stop_loss = index_row['open']
            #         if self._order(int_date, index_row, -self.orders[i][4], stop_loss, 0):
            #             del self.orders[i]
            
        # if self.max_back < _back:
        #     self.max_back = _back
        #     print(_date, self.max_back, self.max_value, self.total_value, 
        #             self.cash, self.credit, self.position_value)
