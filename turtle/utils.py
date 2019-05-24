#!/usr/bin/env python
#-*- coding: utf8 -*-
import sys, argparse, numpy, pandas, math, time, datetime
import matplotlib.pyplot as plt, mpl_finance as mpf
from turtle import data, index
from turtle.data import StockDataSource


class StockDisp:
    '股票数据可视化'
    
    def __init__(self, title, subcount = 1, xlabel='date', ylabel='price'):
        if subcount == 1:
            self.fig, self.ax1 = plt.subplots(1, 1, sharex=True)
        else:
            self.fig, [self.ax1, self.ax2] = plt.subplots(2,1,sharex=True)
        self.fig.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)

        plt.xticks(rotation=45)
        plt.yticks()
        plt.xlabel(xlabel)

        self.ax1.xaxis_date()
        self.ax1.set_title(title)
        self.ax1.set_ylabel(ylabel)

    def show(self):
        plt.grid()
        plt.show()

    def save(self, filename, path='./images'):
        plt.grid()
        plt.savefig( path + '/' + filename + '.png', dpi=400 )


    def LogKDisp(self, ax1, data_list, up_color = 'red', down_color = 'green'):
        if len(data_list) > len(data_list[0]):
            data_table = numpy.transpose( data_list )
        else:
            data_table = data_list
        shift = math.log( data_table[1][0] )

        data_table[1] = list(map(lambda x: math.log(x)-shift, data_table[1]))
        data_table[2] = list(map(lambda x: math.log(x)-shift, data_table[2]))
        data_table[3] = list(map(lambda x: math.log(x)-shift, data_table[3]))
        data_table[4] = list(map(lambda x: math.log(x)-shift, data_table[4]))

        data_list = numpy.transpose( data_table )
        mpf.candlestick_ohlc(ax1, data_list, width=1.5, colorup=up_color, colordown=down_color)

    def KDisp(self, ax1, data_list, up_color = 'red', down_color = 'green'):
        if len(data_list) < len(data_list[0]):
            data_table = numpy.transpose( data_list )
        else:
            data_table = data_list
        mpf.candlestick_ohlc(ax1, data_table, width=1.5, colorup=up_color, colordown=down_color)

    def LogPlot(self, ax1, dates, vals, _color='r', _label='label'):
        shift = math.log( vals[0] )
        vals = list(map(lambda x: math.log(x)-shift, vals))
        ax1.plot(dates, vals, color=_color, lw=2, label=_label)
        ax1.axhline(y=vals[-1], linewidth=2, color=_color)

    def Plot(self, ax1, dates, vals, _color='r', shift = 0, _label='label'):
        if shift:
            vals = list(map(lambda x: x-shift, vals))
        ax1.plot(dates, vals, color=_color, lw=2, label=_label)
        ax1.axhline(y=vals[-1], linewidth=2, color=_color)


class StockAccount:
    '股票交易账户'

    def __init__(self, cash, _max_credit = 0):
        self.max_credit, self.cost, self.position_value = _max_credit, 0, 0
        self.cash, self.total_value, self.credit = cash, cash, 0
        # self.cash, self.total_value, self.credit = 0, 0, cash
        
        self.max_value = self.min_value = cash
        self.max_loss = self.max_back = self.max_lever = 0
        self.long_count = self.short_count = self.succeed = 0

        self.stocks, self.records = pandas.DataFrame(), []

    def status_info(self):
        print('long %d, short %d, success %d.' %(self.long_count, self.short_count, self.succeed))
        print('value %.2f, max %.2f, min %.2f, credit %.2f, cost %.2f' %( self.total_value*0.0001, 
                self.max_value*0.0001, self.min_value*0.0001, self.credit*0.0001, self.cost*0.0001))
        print('back %.2f, max loss %f, lever %.2f' %( self.max_back*100, self.max_loss*100, self.max_lever*100))

    def get_records(self):
        _records = pandas.DataFrame(self.records, columns=['code', 'order_time', 'price', 'volume', 
            'cash', 'credit', 'market value', 'good amount', 'commision', 'total amount', 
            'total volume', 'total value', 'lever', 'back'])
        return _records

    def save_records(self, code, path = './records'):
        _records = self.get_records()
        if( len(_records) > 1 ):
            _records.to_csv(path + '/' + code + '.records.csv')

    def Rechange(self, _cash):
        if self.credit > _cash:
            self.credit -= _cash
        elif self.credit > 0:
            self.cash += _cash - self.credit
            self.credit = 0
        else:
            self.cash += _cash

    def Cash(self, _capital):
        if( self.cash >= _capital ):
            self.cash -= _capital
        else:
            raise ValueError("Insufficient account balance")

    def _update_param(self, _date):
        self.position_value = 0
        for code, row in self.stocks.iterrows():
            self.position_value += row['market_value']

        self.total_value = self.cash - self.credit + self.position_value
        self.max_value = max(self.max_value, self.total_value)
        self.min_value = min(self.min_value, self.total_value)
        _back = 1 - self.total_value/self.max_value

        self.max_back  = max(self.max_back , _back)
        self.max_lever = max(self.max_lever, self.credit/self.total_value)

    def UpdateValue(self, prices, _date):
        for code, row in self.stocks.iterrows():
            if code in prices:
                self.stocks.at[code, 'price'] = prices[code]
                self.stocks.at[code, 'market_value'] = prices[code]*row['volume']
        self._update_param(_date)


    def ProfitDaily(self, _date):
        self.credit *= 1.0002 # 7.2
        # self.credit *= 1.0003 # 10.8
        # self.cash *= 1.00007
        # self._update_param(_date)

    def Format(self, volume, price):
        volume = int(volume/100) * 100
        _value = price*volume
        absv = abs(_value)

        if absv * 0.001 < 5: # 手续费 千一
            _commision = 5
        else:
            _commision = absv * 0.001

        if volume < 0: # 印花税,单边收
            _commision += absv * 0.001
        _commision += absv * 0.00002 # 过户费
        _cost = _value + _commision
        return _cost, _commision, volume

    def Volume(self, code):
        if code in self.stocks.index:
            volume = self.stocks.at[code, 'volume']
        else:
            volume = 0
        return volume

    def Order(self, code, prices, volume, order_time):
        if prices is object:
            if prices['low'] == prices['high']:
                return
            self._Order(code, prices['trade'], volume, order_time)
        elif prices is float:
            self._Order(code, prices, volume, order_time)

    def _Order(self, code, price, volume, order_time):
        _cost, _commision, volume = self.Format(volume, price)
        if not volume: # or (self.max_credit > 100 and self.credit + _cost - self.cash > self.max_credit):
            return 0
        order_time = StockDataSource.str_date( order_time )

        if _cost < 0 and self.credit > 0:
            self.credit += _cost
            if self.credit < 0:
                self.cash -= self.credit
                self.credit = 0
        elif self.cash < _cost:
            _temp = self.total_value*self.max_credit - self.credit + self.cash
            if self.max_credit and _temp < _cost - self.cash:
                _cost, _commision, volume = self.Format(_temp / price, price)
            
            # if self.max_credit > 0 and self.total_value*2 < self.credit + _cost - self.cash:
            #     volume = (self.total_value*2 - self.credit) / price
            #     _cost, _commision, volume = self.Format(volume, price)
            #     print('reset order volume: ', order_time, code, price, volume, _cost, _commision, self.cash, self.credit)

            # if self.max_credit > 0 and self.credit + _cost - self.cash > self.max_credit:
            #     print('reset order volume: ', order_time, code, price, volume, _cost, _commision, self.cash, self.credit)
            #     volume = (self.max_credit - self.credit + self.cash) / price
            #     _cost, _commision, volume = self.Format(volume, price)
            #     print('reset order volume: ', order_time, code, price, volume, _cost, _commision, self.cash, self.credit)

            self.credit += _cost - self.cash
            self.cash = 0
        else:
            self.cash -= _cost
        self.cost += _commision

        if code in self.stocks.index:
            _row = self.stocks.loc[code]
            _volume = _row.volume + volume

            # if _volume < 0:
            #     print(self.stocks.loc[code])
            #     raise ValueError("Don't naked short sale.")

            if _volume == 0:
                _cost_price = _row.cost_price
                _loss = _row.volume*_row.cost_price + _cost
                if _loss < 0: 
                    self.succeed += 1
                else:
                    self.max_loss = max(self.max_loss, _loss/(_row.volume*_row.cost_price))
            else:
                _cost_price = (_row.volume*_row.cost_price + _cost) / _volume
            mkt_value = _volume*price
            self.stocks.loc[code] = [_volume, price, _cost_price, mkt_value, order_time]
            
        else:
            # if volume <= 0:
            #     print(order_time, code, volume, price, self.cash)
            #     raise ValueError("Don't naked short sale.")
            _volume = volume
            _cost_price = _cost / volume
            mkt_value = volume*price

            _row = {'volume': [volume], 'price': [price], 'cost_price': [_cost_price], 
                'market_value': [mkt_value], 'order_time': [order_time]}
            _index = [code]
            self.stocks = self.stocks.append(pandas.DataFrame(_row, _index))
            
        if volume < 0:
            self.short_count+= 1
        else:
            self.long_count += 1

        self._update_param(order_time)
        lever = self.credit/self.total_value
        back_pump = 1 - self.total_value/self.max_value

        _record = (code, order_time, '%.03f'%price, volume, '%.03f'%(self.cash*.0001), 
                '%.03f'%(self.credit*.0001), '%.03f'%(self.total_value*.0001), 
                '%.03f'%(mkt_value*.0001), '%.03f'%(volume*price*.0001), 
                '%.03f'%(_commision*.0001), '%.03f'%(_cost*.0001), _volume, lever, back_pump)
        self.records.append(_record)

        _clear_codes = []
        for _code, row in self.stocks.iterrows():
            if row['volume'] < 10 and row['volume'] > -10:
                _clear_codes.append(_code)
        if len(_clear_codes):
            self.stocks.drop(index = _clear_codes, axis = 0, inplace=True)

        return volume


class TradeTest(index.TurtleArgs):
    '证券交易测试基类'

    def __init__(self):
        index.TurtleArgs.__init__(self)

    def start_test(self, long_per, init_cash = 1000*10000):
        funcName = sys._getframe().f_back.f_code.co_name #获取调用函数名
        lineNumber = sys._getframe().f_back.f_lineno     #获取行号
        coname = sys._getframe().f_code.co_name          #获取当前函数名
        print( coname, funcName, lineNumber ) 

        self.account = StockAccount(init_cash, 0)

        self.year, self.start = StockDataSource.datetime(self.dates[0]).year, time.time()
        self.order_count, self.open_value, self.sums = 0, 0, self.account.cash
        
        self.records, self.year_values = [], []
        self.curr_orders, self.hist_orders = [], []
        self.market_values, self.position_ratios = [], []

        for i in range(0, long_per ):
            # self.account.ProfitDaily()
            _total_value = max(1000*10000, self.account.total_value)
            self.market_values.append(self.account.total_value)
            self.position_ratios.append(self.account.position_value / _total_value)

    def print_progress(self, _date):
        _year = StockDataSource.datetime(_date).year
        if self.year != _year:
            # _total_value = max(1000*10000, self.sums)
            _total_value = self.sums
            self.year_values.append( [self.year, '%.02f'%(self.account.total_value*0.0001), \
                '%.02f'%(self.account.total_value*100/_total_value-100)] )
            self.year = _year
            self.sums = self.account.total_value

            # print( "process to %d, market value %.02f, run %.02f seconds." 
            #     % (self.year, self.account.total_value*0.0001, time.time() - self.start) )
            
    def _order(self, _date, stock_data, volume, trade_price, stop_price = 0):
        _volume, _wave = 0, stock_data['high'] - stock_data['low']
        
        if _wave <= 0.002 and ( (volume > 0 and trade_price >= stock_data['high']) \
                or (volume < 0 and trade_price <= stock_data['low']) ):
            print( "%s %s order error: price %.03f can't buy in limit up and sell in limit down."%
                    (_date, stock_data['ts_code'], trade_price) )
        elif trade_price < stock_data['low'] or trade_price > stock_data['high']:
            print( '%s %s order error: trade price %.03f must in [%.03f, %.03f], volume %d.'%
                    (_date, stock_data['ts_code'], trade_price, stock_data['low'], stock_data['high'], volume) )
        else:
            _volume = self.account._Order(stock_data['ts_code'], trade_price, volume, _date)
            
        if _volume:
            new_order = [_date, '%.3f'%trade_price, '%.3f'%stop_price, int(_volume), 
                    '%.03f'%(self.account.total_value*0.0001), '%.03f'%(self.account.credit*0.0001), 
                    '%.03f'%(self.account.credit/self.account.total_value*100), stock_data['ts_code'] ]
            self.curr_orders.append ( new_order )
            self.hist_orders.append( new_order )
        return _volume
        
    def single_clear(self, trade_price, stock_data, int_date):
        if trade_price > stock_data['open']:
            trade_price = stock_data['open']
        volume = self.account.Volume(stock_data['ts_code'])
            
        if volume and self._order(int_date, stock_data, -volume, trade_price):
            profit = self.account.total_value - self.open_value
            self.records.append( [int_date, '%.03f'%trade_price, int(volume), 
                    '%.02f'%(self.account.total_value*.0001), 
                    '%.02f'%(profit*.0001), '%.02f'%(profit*100/self.open_value) ] )
                    
            for i in range(len(self.curr_orders)-1, -1, -1):
                if self.curr_orders[i][7] == stock_data['ts_code']:
                    del self.curr_orders[i]
            
            
    def save_indexs(self, _data_vec, _dates, index_long, _file = 'turtle_index.csv'):
        index_table = pandas.DataFrame()
        index_table['date'] = _dates
        index_table['state'] = index_long['state']
        index_table['key_price'] = index_long['key_price']
        index_table['wave'] = index_long['wave']
        index_table['long_high'] = index_long['long_high']
        index_table['short_low'] = index_long['short_low']
        index_table['high'] = _data_vec[2]
        index_table['low' ] = _data_vec[3]
        index_table['close' ] = _data_vec[4]
        index_table.to_csv('long_turtle_index.csv')
            
    def show(self):
        print( self.account.stocks )
        print( self.account.get_records() )

    def plot(self, data_list, turtle_index, title):
        _dates = numpy.transpose( data_list )[0]
        plot = StockDisp(title, 1)
        plot.LogKDisp(plot.ax1, data_list)
        plot.LogPlot(plot.ax1, _dates, self.market_values, 'r')
        plot.LogPlot(plot.ax1, _dates, turtle_index['long'], 'b')
        plot.LogPlot(plot.ax1, _dates, turtle_index['short'], 'y')
        # plot.LogPlot(plot.ax1, _dates, self.stim.data['average'], 'g')
        # plot.Plot(plot.ax2, _dates, self.position_ratios, 'r')
        # plot.save( title )
        plot.show()


            # new_order = [int_date, '%.3f'%trade_price, 0, int(-volume), 
            #         '%.03f'%(self.account.total_value*0.0001), '%.03f'%(self.account.credit*0.0001), 
            #         '%.03f'%(self.account.credit/self.account.total_value*100), stock_data['ts_code'] ]
            # self.curr_orders.append( new_order )
            # self.hist_orders.append( new_order )

    # def single_clear(self, stock_data, int_date):
    #     self._single_clear(stock_data['key_price'], stock_data, int_date)
    #     self.order_count = 0
