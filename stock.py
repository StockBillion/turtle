#!/usr/bin/env python
#-*- coding: utf8 -*-
import argparse, sys, numpy, pandas, datetime as dt, time
from turtle import trade, index, data, utils
from turtle.data import StockDataSource


class TurtleList(index.TurtleArgs):
    '列出所有交易品种当前日期的海龟指标'

    def __init__(self):
        index.TurtleArgs.__init__(self)

        sdsr = data.StockData_SQLite( self.files[0] )
        turtle_list = []

        for code in self.codes:
            sdsr.load(code, self.dates[0], self.dates[1], self.params[0])
            if not len(sdsr.stocks):
                continue
            data_list, _dates = sdsr.parse_price()
            _data_vec = numpy.transpose( data_list )

            turtle = index.TurtleIndex()
            index_long = index.LongTurtleIndex(turtle, _data_vec, self.turtle_args[2], 
                        self.turtle_args[3], self.turtle_args[0], self.turtle_args[1])
            Hl = turtle.high_prices[self.turtle_args[2]]
            print( Hl )

            turtle = index.TurtleIndex()
            index_short = index.LongTurtleIndex(turtle, _data_vec, self.turtle_args[3], 
                        self.turtle_args[4], self.turtle_args[0], self.turtle_args[1])
            
            long_list = self.list_info(_data_vec, index_long)
            long_list.tail(30).to_csv('long.csv')
            print( long_list.tail(5) )

            short_list = self.list_info(_data_vec, index_short)
            short_list.tail(30).to_csv('short.csv')
            print( short_list.tail(5) )

            _last = len(_data_vec[0]) - 1
            _price, _wave = index_long['key_price'][_last], index_long['wave'][_last]

            if index_long['state'][_last]:
                _append = _price + _wave
                _stoploss = _price - _wave*self.turtle_args[0]
                _pos_unit = int(1000 / _wave)
            else:
                _append, _stoploss, _pos_unit = 0, 0, 0

            turtle_list.append( [code, _dates[_last], index_long['state'][_last], _price, _append, _stoploss, 
                    _pos_unit, index_long['short'][_last], _wave, _data_vec[4][_last] ])

        print( pandas.DataFrame(turtle_list, columns=[ 'ts_code', 'date', 'state', 'key_price', 
                'append', 'stop_loss', 'pos_unit', 'valley', 'wave', 'close' ]) )

    def list_info(self, stock_data, long_index, count = 0):
        list_len = len(stock_data[0])
        starti = 0
        if count:
            starti = list_len - min(count, list_len)
        info_list = []

        for i in range(starti, list_len):
            if long_index['state'][i]:
                append_price = long_index['key_price'][i] + long_index['wave'][i]
                stop_price = long_index['key_price'][i] - long_index['wave'][i] * self.turtle_args[0]
            else:
                append_price, stop_price = 0, 0
            info_list.append( [ StockDataSource.str_date(stock_data[0][i]), stock_data[4][i], 
                    long_index['state'][i], '%.02f'%long_index['key_price'][i], '%.02f'%append_price, 
                    stop_price, long_index['short'][i], '%.02f'%long_index['wave'][i] ] )

        cols = [ 'trade_date', 'close', 'state', 'key_price', 'append', 'stop', 'profit', 'wave' ]
        return pandas.DataFrame( info_list, columns= cols)
        

class TurtleDisp(index.TurtleArgs):
    '显示海龟指标'

    def __init__(self):
        index.TurtleArgs.__init__(self)

        title = 'plot['
        for code in self.codes:
            title = '%s%s' % (title, code)
        title = '%s]'%title
        plot = utils.StockDisp(title, 1)
        
        sdsr = data.StockData_SQLite( self.files[0] )
        turtle = index.TurtleIndex()

        for code in self.codes:
            sdsr.load(code, self.dates[0], self.dates[1], self.params[0], self.params[1])
            if not len(sdsr.stocks):
                continue
            data_list, _dates = sdsr.parse_price()
            _data_vec = numpy.transpose( data_list )
            
            if self.params[2] == 'long':
                long_index = index.LongTurtleIndex(turtle, _data_vec, self.turtle_args[2], 
                        self.turtle_args[3], self.turtle_args[0], self.turtle_args[1])
                # short_index = index.LongTurtleIndex(turtle, _data_vec, self.turtle_args[4], 
                #         self.turtle_args[5], self.turtle_args[0], self.turtle_args[1])
            else:
                long_index = index.ShortTurtleIndex(turtle, _data_vec, self.turtle_args[2], 
                        self.turtle_args[3], self.turtle_args[0], self.turtle_args[1])
                # short_index = index.ShortTurtleIndex(turtle, _data_vec, self.turtle_args[4], 
                #         self.turtle_args[5], self.turtle_args[0], self.turtle_args[1])

            info_list = self.list_info1(_data_vec, long_index )
            # info_list = self.list_info2(_data_vec, long_index, short_index['state'] )
            # print( info_list[-80:-40] )
            print( info_list.tail(40) )
            info_list.to_csv( '%s/%s.csv'%(self.files[2], code) )
            
            plot.LogKDisp(plot.ax1, data_list)
            # plot.LogPlot(plot.ax1, _data_vec[0], turtle_index['long'], 'r')
            # plot.LogPlot(plot.ax1, _data_vec[0], turtle_index['short'], 'y')
            # plot.Plot(plot.ax1, _data_vec[0], self.stim.data['average'], 'b')
            
        plot.save( title, self.files[3] )
        # plot.show()


    def list_info1(self, stock_data, long_index, count = 0):
        list_len = len(stock_data[0])
        starti = 0
        if count:
            starti = list_len - min(count, list_len)

        info_list = []
        _close, _high, _low = stock_data[4], stock_data[2], stock_data[3]

        for i in range(starti, list_len):
            append_price = long_index['key_price'][i] + long_index['wave'][i]
            stop_price = long_index['key_price'][i] - long_index['wave'][i] * self.turtle_args[0]
            info_list.append( [ StockDataSource.str_date(stock_data[0][i]), _close[i], _high[i], _low[i],
                    long_index['state'][i], '%.02f'%long_index['key_price'][i], '%.02f'%append_price, 
                    '%.02f'%stop_price, '%.02f'%long_index['short'][i], '%.02f'%long_index['wave'][i] ] )

        cols = [ 'trade_date', 'close', 'high', 'low', 'state', 'key_price', 'append', 'stop', 'profit', 'wave' ]
        return pandas.DataFrame( info_list, columns= cols)
        
    def list_info2(self, stock_data, long_index, short_state, count = 0):
        list_len = len(stock_data[0])
        starti = 0
        if count:
            starti = list_len - min(count, list_len)

        info_list = []
        _close, _high, _low = stock_data[4], stock_data[2], stock_data[3]

        for i in range(starti, list_len):
            append_price = long_index['key_price'][i] + long_index['wave'][i]
            stop_price = long_index['key_price'][i] - long_index['wave'][i] * self.turtle_args[0]
            info_list.append( [ StockDataSource.str_date(stock_data[0][i]), _close[i], _high[i], _low[i],
                    long_index['state'][i], short_state[i], '%.02f'%long_index['key_price'][i], '%.02f'%append_price, 
                    '%.02f'%stop_price, '%.02f'%long_index['short'][i], '%.02f'%long_index['wave'][i] ] )

        cols = [ 'trade_date', 'close', 'high', 'low', 'long_state', 'short_state', 'key_price', 'append', 'stop', 'profit', 'wave' ]
        return pandas.DataFrame( info_list, columns= cols)
        

class PositionCSV(index.TurtleArgs):
    '持仓列表'

    def __init__(self):
        index.TurtleArgs.__init__(self)

        if self.files[1] != ':memory:':
            self.csv_file = self.files[1]
        else:
            self.csv_file = 'fund_pos.csv'
        self.positions = PositionCSV.read_csv(self.csv_file)

        sdsr = data.StockData_SQLite( self.files[0] )
        pos_list = self.positions.values.tolist()
        prev_closes, total_values, profits, may_loss, stop_prices, loss_ratios = [], [], [], [], [], []
        total_invest, total_value, total_profit, total_loss = 0, 0, 0, 0

        for row in pos_list:
            code, volume, cost_price, good_type = row[0:4]

            sdsr.load(code, self.dates[0], self.dates[1], good_type)
            if not len(sdsr.stocks):
                continue
            data_list, _dates = sdsr.parse_price()
            _data_vec = numpy.transpose( data_list )
            
            turtle = index.TurtleIndex()
            turtle_index = index.LongTurtleIndex(turtle, _data_vec, 
                        self.turtle_args[2], self.turtle_args[3], self.turtle_args[0], self.turtle_args[1])
            # info_list = self.list_info(_data_vec, turtle_index )

            list_len = len(turtle_index['key_price'])
            _last = list_len - 1

            _prev_close = _data_vec[4][_last]
            _key_price, _profit_price, _wave = turtle_index['key_price'][_last], turtle_index['short'][_last], turtle_index['wave'][_last]
            _value = volume*_prev_close
            _cost = volume*cost_price
            _stop_price = _key_price - _wave*self.turtle_args[0]
            if cost_price > _key_price:
                _stop_price = cost_price - _wave*self.turtle_args[0]
            _mayloss = volume * (_stop_price - cost_price)
            _stop_price = max(_stop_price, _profit_price)

            total_invest += _cost
            total_value += _value
            total_profit += _value - _cost
            total_loss += _mayloss

            prev_closes.append( _prev_close )
            total_values.append( _value )
            stop_prices.append( _stop_price )
            loss_ratios.append( 100*_stop_price/_prev_close - 100 )
            profits.append( _value - _cost )
            # profit_prices.append( _profit_price )
            may_loss.append( _mayloss )

        self.positions['prev'] = prev_closes
        self.positions['stop'] = stop_prices
        self.positions['ratio'] = loss_ratios
        self.positions['value'] = total_values
        self.positions['profit'] = profits
        # self.positions['profit_price'] = profit_prices
        self.positions['may_loss'] = may_loss

        self.positions.drop('type', axis=1, inplace=True)
        print( self.positions )
        print( 'SUM invest: %.03f, value: %.03f, profit: %.03f, mayloss: %.03f.' %\
            (total_invest*0.0001, total_value*0.0001, total_profit*0.0001, total_loss*.0001) )

    def create(self, path='.'):
        _posis = [ ['510300.SH', '55000', '2.833', 'fund'] ]
        _records = pandas.DataFrame(_posis, columns=['code', 'volume', 'cost', 'type'])
        _records.to_csv( '%s/%s' % (path, self.csv_file) )

    @staticmethod
    def read_csv(data_file):
        try:
            return pandas.read_csv(data_file, index_col = 0) #, dtype = {'trade_date' : str}
        except IOError: 
            return pandas.DataFrame()

    def write_csv(self, path = '.'):
        if len(self.positions):
            self.positions.to_csv('%s/%s' % (path, self.csv_file) )


class FixedInvestTrade(utils.TradeTest):
    '定投测试'

    def __init__(self):
        utils.TradeTest.__init__(self)
        sdsr = data.StockData_SQLite( self.files[0] )

        self.curr_closes = {}
        self.float_str = StockDataSource.float_date(self.dates[0])
        self.float_end = StockDataSource.float_date(self.dates[1])

        for code in self.codes:
            sdsr.read_stock(code, self.dates[0], self.dates[1] )
            if not len(sdsr.stocks):
                sdsr.load(code, self.dates[0], self.dates[1], self.params[0])
            if not len(sdsr.stocks):
                continue
            data_list, _dates = sdsr.parse_price()
            _data_vec = numpy.transpose( data_list )

            turtle = index.TurtleIndex()
            index_long = index.LongTurtleIndex(turtle, _data_vec, self.turtle_args[2], 
                    self.turtle_args[3], self.turtle_args[0], self.turtle_args[1])
            self.fixed_invest(code, _data_vec, index_long)

            print( "%s %s, use time %.02f seconds." %('single_turtle', code, time.time() - self.start))
            self.account.save_records(code, self.files[2])
            self.plot(data_list, index_long, code)

    def fixed_invest(self, code, data_list, index_long):
        self._start_test(0, 10*10000)
        all_days, curr_month = len(data_list[0]), -1
        opens, highs, lows, closes = data_list[1], data_list[2], data_list[3], data_list[4]

        for _idx in range(0, all_days):
            float_date = data_list[0][_idx]
            int_date = StockDataSource.int_date(float_date)
            self.print_progress(int_date)

            stock_data = { 'ts_code': code, 'open': opens[_idx], 'high': highs[_idx], 
                    'low': lows[_idx], 'close': closes[_idx] }
            _month = StockDataSource.datetime(int_date).month
            self.account.ProfitDaily(int_date)

            if curr_month != _month:
                curr_month = _month
                self.account.Rechange( 10000 )

                # _open_unit = self.account.cash / opens[_idx]
                # _open_unit = (self.account.cash + 120000 - self.account.credit) / opens[_idx]
                # self._order(int_date, stock_data, _open_unit, opens[_idx], 0)
                # print( int_date, self.account.cash, self.account.credit )

            kp = index_long['short'][_idx] * 1.05
            kp = index_long['long' ][_idx] * 0.95
            _cash = self.account.cash + 120000 - self.account.credit

            if lows[_idx] < kp and _cash > kp*100:
                if kp > opens[_idx]:
                    kp = opens[_idx]
                    
            # if highs[_idx] > kp and _cash > kp*100:
            #     if kp < opens[_idx]:
            #         kp = opens[_idx]

                _open_unit = _cash / kp
                self._order(int_date, stock_data, _open_unit, kp, 0)

            self.curr_closes[code] = closes[_idx]
            self.account.UpdateValue(self.curr_closes, int_date)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        print( pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
                'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ]) )
        print( pandas.DataFrame(self.year_values, columns=['year', 'cash', 'ratio']) )
        self.account.status_info()


class FixedInvestByPE(utils.TradeTest):
    '按照PE定投测试'

    def __init__(self):
        utils.TradeTest.__init__(self)
        sdsr = data.StockData_SQLite( self.files[0] )

        self.curr_closes = {}
        self.float_str = StockDataSource.float_date(self.dates[0])
        self.float_end = StockDataSource.float_date(self.dates[1])

        for code in self.codes:
            sdsr.read_stock(code, self.dates[0], self.dates[1] )
            if not len(sdsr.stocks):
                sdsr.load(code, self.dates[0], self.dates[1], self.params[0])
            if not len(sdsr.stocks):
                continue
            data_list, _dates = sdsr.parse_price()
            _data_vec = numpy.transpose(data_list)

            pe_table = sdsr.index_daaily(code, self.dates[0], self.dates[1] )
            # print( len(data_list), len(pe_table) )
            # print( sdsr.stocks )
            # print( pe_table )

            # pe = pe_table[['pe', 'pe_ttm']].values.tolist()
            # _pe_vec = numpy.transpose( pe )

            # self.fixed_invest(code, _data_vec, _pe_vec[0])
            # print( "%s %s, use time %.02f seconds." %('single_turtle', code, time.time() - self.start))

            # self.account.save_records(code, self.files[2])
            # self.plot(data_list, index_long, code)

    def fixed_invest(self, code, data_list, pe_vec):
        self._start_test(0, 10000)
        all_days, curr_month = len(data_list[0]), -1
        opens, highs, lows, closes = data_list[1], data_list[2], data_list[3], data_list[4]

        for _idx in range(0, all_days):
            float_date = data_list[0][_idx]
            int_date = StockDataSource.int_date(float_date)
            self.print_progress(int_date)

            stock_data = { 'ts_code': code, 'open': opens[_idx], 'high': highs[_idx], 
                    'low': lows[_idx], 'close': closes[_idx] }
            _month = StockDataSource.datetime(int_date).month
            self.account.ProfitDaily(int_date)

            if curr_month != _month:
                curr_month = _month
                self.account.Rechange( 10000 )
                kp = opens[_idx]

                if pe_vec[_idx] > 20.83: # sell 
                    _volume = self.account.credit/kp
                elif pe_vec[_idx] > 13.89:
                    _volume = self.account.cash/kp
                else:
                    _volume = self.account.cash/kp*1.7
                self._order(int_date, stock_data, _volume, kp, 0)

            self.curr_closes[code] = closes[_idx]
            self.account.UpdateValue(self.curr_closes, int_date)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / self.account.total_value)

        print( pandas.DataFrame( self.hist_orders, columns=[ 'date', 'trade_price', 
                'stop_price', 'volume', 'total_value', 'credit', 'lever', 'ts_code' ]) )
        print( pandas.DataFrame(self.year_values, columns=['year', 'cash', 'ratio']) )
        self.account.status_info()


if __name__ == "__main__":
    # sys.argv = ['./stock.py', 'test', '-F', 'stock.data.db', '-D', '20090101', '-A', '3',  '6', '100', '30', '15', '20']
    # sys.argv = ['./stock.py', 'fix', '-f', '../data/stock.0414.db', '-d', '20090101'] # , '-c', '600519.sh', '-p', 'stock'
    # sys.argv = ['./stock.py', 'test', '-p', 'index', 'd',  '-d', '20050101']
    # sys.argv = ['./stock.py', 'test', '-f', '../data/stock.data.db', '-d', '20170101']

    cmd = 'posi'
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

    if cmd in ['disp', 'plot']:
        TurtleDisp()
    elif cmd in ['list', 'ls']:
        TurtleList()
    elif cmd in ['posi', 'ps']:
        pos = PositionCSV()
    elif cmd in ['test', 'trade']:
        trade.DauLTurtleTrade()
    elif cmd in ['fix', 'fixed']:
        FixedInvestByPE()
        # FixedInvestTrade()
    else:
        print( "invalid command." )


            # _len = len(info_list)
            # print( info_list[-40:-0] )

            # print( info_list.head(10) )
            # print( info_list.tail(30) )
            
