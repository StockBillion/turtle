#!/usr/bin/env python
#-*- coding: utf8 -*-
import numpy, pandas, math, datetime, time 
import sqlite3, pandas.io.sql as pd_sql
from matplotlib.pylab import date2num, num2date
import matplotlib.pyplot as plt, mpl_finance as mpf
import tushare as ts # https://tushare.pro/


class StockDataSource:
    '股票数据源'
    
    def __init__(self):
        self.stocks = pandas.DataFrame()

    def parse_price(self):
        stock_data = self.stocks.sort_index(ascending=False)
        return self._parse_price(stock_data)

    def _parse_price(self, stock_data):
        data_list = stock_data.values.tolist()
        _date, _list = [], []

        for _row in data_list:
            trade_date, _open, _high, _low, _close = _row[1:6]
            _timenum = StockDataSource.float_date(trade_date)
            _list.append( [_timenum, _open, _high, _low, _close, _row[10]] )
            _date.append( trade_date )
        return _list, _date 

    def _parse_period_price(self, stock_data, start_date, end_date):
        _start_date = StockDataSource.float_date(start_date)
        _end_date = StockDataSource.float_date(end_date)

        _list = []
        data_list = stock_data.values.tolist()

        for _row in data_list:
            trade_date, _open, _high, _low, _close = _row[1:6]
            _timenum = StockDataSource.float_date(trade_date)
            if _timenum >= _start_date and _timenum < _end_date:
                _list.append( (_timenum, _open, _high, _low, _close, _row[10]) )

        return _list

    def _daily2weekly(self, daily_datas):
        weekly_datas = pandas.DataFrame()
        kidx = 0
        start = 0
        
        for rnum, row in daily_datas.iterrows():
            ts_code, trade_date, close, open, high, low = row[0:6]
            pre_close,change,pct_chg,vol,amount = row[6:11]
            _date = datetime.strptime(trade_date, '%Y%m%d')
            _weekday = _date.weekday()

            if _weekday == 0:
                if start:
                    _row = {'ts_code': [ts_code], 'trade_date': [_trade_date], 
                        'open': [_open], 'close': [_close], 'high': [_high], 'low': [_low], 
                        'pre_close': [pre_close], 'change': [change], 'pct_chg': [pct_chg], 
                        'vol': [_vol], 'amount': [_amount]}
                    _index = [kidx]
                    weekly_datas = weekly_datas.append(pandas.DataFrame(_row, _index))
                    kidx = kidx+1

                start = 1
                _trade_date = trade_date
                _open = open
                _close = close
                _high = high
                _low = low
                _vol = vol
                _amount = amount

            elif start:
                _close = close
                _high = max(_high, high)
                _low = min(_low, low)
                _vol += vol
                _amount += amount

        return weekly_datas

    @staticmethod
    def float_date(_date):
        if isinstance(_date, numpy.int64) or isinstance(_date, int):
            _date = str(_date)
        if isinstance(_date, str):
            _date = datetime.datetime.strptime(_date, '%Y%m%d')
        if isinstance(_date, datetime.datetime) or isinstance(_date, datetime.date):
            _date = date2num(_date)
        return _date

    @staticmethod
    def str_date(_date):
        if isinstance(_date, float):
            _date = num2date(_date).strftime('%Y%m%d')
        elif isinstance(_date, numpy.int64) or isinstance(_date, int):
            _date = str(_date)
        elif isinstance(_date, datetime.datetime) or isinstance(_date, datetime.date):
            _date = _date.strftime('%Y%m%d')
        return _date

    @staticmethod
    def int_date(_date):
        if isinstance(_date, float):
            _date = num2date(_date).strftime('%Y%m%d')
        if isinstance(_date, datetime.datetime) or isinstance(_date, datetime.date):
            _date = _date.strftime('%Y%m%d')
        return int(_date)

    @staticmethod
    def datetime(_date):
        if isinstance(_date, float):
            _date = num2date(_date)
        elif isinstance(_date, numpy.int64) or isinstance(_date, int):
            _date = str(_date)
        if isinstance(_date, str):
            _date = datetime.datetime.strptime(_date, '%Y%m%d')
        return _date


class StockData_Tushare(StockDataSource):
    '股票数据源，来自网络数据'
    
    ts.set_token("e2a71ab976c499825f6f48186f24700f70e0f13af933e2f508684cc0")
    ts_api = ts.pro_api()

    def __init__(self):
        StockDataSource.__init__(self)

    def index_daaily(self, code, startdate, enddate):
        time.sleep(0.125)
        df = StockData_Tushare.ts_api.index_dailybasic(ts_code=code, start_date=startdate, 
            end_date=enddate, fields='ts_code,trade_date,pe, pe_ttm')
        return df.sort_index(ascending=False)

    def download_tushare(self, code, startdate, enddate, stype = 'stock', freq = 'daily'):
        time.sleep(0.125)
        startdate = StockDataSource.str_date(startdate)
        enddate = StockDataSource.str_date(enddate)
        print( 'tushare:', code, startdate, enddate )

        if stype in ['index', 'i']:
            stype = 'I'
        elif stype in ['fut', 'ft']:
            stype = 'FT'
        elif stype in ['opt', 'o']:
            stype = 'I'
        elif stype in ['fund', 'fd']:
            stype = 'FD'
        else: #if stype in ['stock', 'e']:
            stype = 'E'
        
        if freq in [ 'weekly', 'w', 'W' ]:
            freq = 'W'
        elif freq in [ 'monthly', 'm', 'M' ]:
            freq = 'M'
        elif freq in [ '60min', '60' ]:
            freq = '60MIN'
        elif freq in [ '15min', '15' ]:
            freq = '15MIN'
        else:
            freq = 'D'

        '''
        stock: ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
        fund : ['ts_code', 'trade_date', 'pre_close', 'open', 'high', 'low', 'close', 'change', 'pct_chg', 'vol', 'amount']
        index: ['ts_code', 'trade_date', 'close', 'open', 'high', 'low', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
        fut  : ['ts_code', 'trade_date', 'pre_close', 'pre_settle', 'open', 'high', 'low', 'close', 'settle', 'change1', 'change2', 'vol', 'amount', 'oi', 'oi_chg']
        '''
        if stype in ['E', 'FD']:
            hist_data = ts.pro_bar(pro_api=StockData_Tushare.ts_api, ts_code=code, adj='qfq', 
                    asset=stype, freq=freq, start_date=startdate, end_date=enddate)
        # elif stype in [ 'FT' ]:
        #     hist_data = StockData_Tushare.ts_api.fut_daily(ts_code=code, freq=freq, 
        #             start_date=startdate, end_date=enddate)
        elif freq in [ 'W' ]:
            hist_data = StockData_Tushare.ts_api.index_weekly(ts_code=code, #adj='qfq', 
                    asset=stype, freq=freq, start_date=startdate, end_date=enddate)
        else:
            hist_data = ts.pro_bar(pro_api=StockData_Tushare.ts_api, ts_code=code, #adj='qfq', 
                    asset=stype, freq=freq, start_date=startdate, end_date=enddate)

        if hist_data is None:
            hist_data = pandas.DataFrame()
        elif len(hist_data):
            hist_data.index = range( len(hist_data) )

            if stype in ['E', 'I', 'FD']:
                hist_data = hist_data[['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close',
                    'change', 'pct_chg', 'vol', 'amount']]
            else:
                hist_data = hist_data[['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close',
                    'change1', 'change2', 'vol', 'amount']]
                hist_data.rename(columns={'change1': 'change', 'change2': 'pct_chg'}, inplace=True) 

        return hist_data


class StockData_SQLite(StockData_Tushare):
    '本地缓存数据源，使用ＣＳＶ文件存储，没有本地数据时，从网络下载'
    
    def __init__(self, db_file):
        StockData_Tushare.__init__(self)
        self.conn = sqlite3.connect(db_file)
        self.curs = self.conn.cursor()

        self.curs.execute('''
            CREATE TABLE IF NOT EXISTS stocks(
                ts_code char(9), 
                trade_date int, 
                open float, 
                high float, 
                low float,
                close float,
                pre_close float,
                change float,
                pct_chg float,
                vol float,
                amount float,
                primary key (ts_code,trade_date)
            );''' 
        )
        self.conn.commit()

    def __del__(self):
        self.conn.commit()
        self.curs.close()
        self.conn.close()

    def read_stock_code(self, trade_date, stock_code):
        _sql = 'select * from stocks where ts_code = "%s" and trade_date = %d ' % (stock_code, trade_date)
        _cache_data = pd_sql.read_sql(_sql, self.conn)
        if len(_cache_data):
            return _cache_data.iloc[0]
        else:
            return {}

    def read_stocks_codes(self, trade_date, stock_codes):
        _sql = 'select * from stocks where trade_date = %d ' % (trade_date)
        if len(stock_codes):
            _sql += 'and ts_code in ("%s"' % stock_codes[0]
            for i in range(1, len(stock_codes)):
                _sql += ', "' + stock_codes[i] + '"'
            _sql += ');'
        _cache_data = pd_sql.read_sql(_sql, self.conn)

        _stock_datas = {}
        for i in range(0, len(_cache_data)):
            row = _cache_data.iloc[i]
            _stock_datas[row['ts_code']] = row
        return _stock_datas


    def read_stock(self, code, start_date = "", end_date = ""):
        _sql = 'select * from stocks where ts_code = "' + code + '"'

        if not isinstance(start_date, str) or len(start_date):
            start_date = StockDataSource.str_date(start_date)
            _sql += ' and trade_date >= ' + start_date

        if not isinstance(end_date, str) or len(end_date):
            end_date = StockDataSource.str_date(end_date)
            _sql += ' and trade_date < ' + end_date

        _sql += " order by trade_date desc"
        self.stocks = pd_sql.read_sql(_sql, self.conn)

    def write_stock(self, stock_data):
        _len = len(stock_data)
        if not _len:
            return

        _sql = 'INSERT INTO stocks (ts_code, trade_date, open, high, low, close, \
                pre_close, change, pct_chg, vol, amount) \
            VALUES (?,?,?,?,?,?,?,?,?,?,?);'
        _list = stock_data[[ 'ts_code', 'trade_date', 'open', 'high', 'low', 'close', \
                'pre_close', 'change', 'pct_chg', 'vol', 'amount' ]].values.tolist()
        self.curs.executemany( _sql, _list )
        # self.curs.executemany(_sql, stock_data.values.tolist())

    def load(self, code, startdate, enddate, stype = 'stock', time_unit = 'daily'):
        code = code.upper()
        print('load', stype, code, time_unit, 'data, from', StockDataSource.str_date(startdate), 
            'to', StockDataSource.str_date(enddate))

        self.read_stock(code, startdate, enddate)
        _rowcount = len(self.stocks)
        down_data = pandas.DataFrame()

        if _rowcount > 0:
            _startdate = StockDataSource.float_date(startdate)
            _enddate = StockDataSource.float_date(enddate)
            _head = StockDataSource.float_date(self.stocks.at[0, 'trade_date'])
            _tear = StockDataSource.float_date(self.stocks.at[_rowcount-1, 'trade_date'])

            if _enddate - _head > 10:
                down_data = self.download_tushare(code, _head + 1, _enddate, stype, time_unit)
            if _tear - _startdate > 10:
                down_data = self.download_tushare(code, _startdate, _tear - 1, stype, time_unit)
            
        else:
            down_data = self.download_tushare(code, startdate, enddate, stype, time_unit)

        if len(down_data):
            self.write_stock(down_data)
            self.read_stock(code, startdate, enddate)

        return self.stocks
        
    def update_all_stocks(self, stock_codes, index_code, start_date, end_date):
        _start = time.time()
        _idx, _len = 0, len(stock_codes)

        self.curs.execute('PRAGMA synchronous = NORMAL;')
        self.load(index_code, start_date, end_date, 'index')
        self.conn.commit()

        while _idx < _len:
            _lst = min(_idx+25, _len)
            self.curs.execute('begin;')

            for i in range(_idx, _lst):
                _code = stock_codes[i]
                self.load(_code, start_date, end_date)

            self.conn.commit()
            _idx += 25
            print( 'load %d stocks, use time %.02f seconds' %(_idx,  time.time() - _start) )

        print( 'use time %.02f seconds.' % (time.time() - _start) )


class StockData_LocalCSV(StockData_Tushare):
    '本地缓存数据源，使用ＣＳＶ文件存储，没有本地数据时，从网络下载'
    
    def __init__(self, path = './data'):
        StockData_Tushare.__init__(self)
        self.path = path

    def _join(self, local_data, down_data1):
        len1 = len(down_data1)
        len2 = len(local_data)

        if len1 < 1: 
            return local_data
        if len2 < 1: 
            return down_data1

        _head1 = down_data1.at[0, 'trade_date']
        _head2 = local_data.at[0, 'trade_date']
        _tear1 = down_data1.at[len1-1, 'trade_date']
        _tear2 = local_data.at[len2-1, 'trade_date']

        if _head1 < _head2:
            if _tear1 < _tear2:
                temp = local_data.loc[local_data['trade_date'] > _head1]
                data0 = temp.append(down_data1, ignore_index=True)
            else:
                data0 = local_data
        elif _head1 > _head2:
            if _tear1 < _tear2:
                data0 = down_data1
            else:
                temp = down_data1.loc[down_data1['trade_date'] > _head1]
                data0 = temp.append(local_data, ignore_index=True)
        else:
            if _tear1 < _tear2:
                data0 = down_data1
            else:
                data0 = local_data

        return data0

    @staticmethod
    def read_csv(data_file):
        try:
            return pandas.read_csv(data_file, index_col = 0, dtype = {'trade_date' : str})
        except IOError: 
            return pandas.DataFrame()

    def write_csv(self, code, time_unit = 'daily'):
        if len(self.stocks) > 0:
            self.stocks.to_csv(self.path + '/' + code + '.' + time_unit + '.csv')

    def read(self, code, time_unit = 'daily'):
        self.stocks = StockData_LocalCSV.read_csv(self.path + '/' + code + '.' + time_unit + '.csv') 

    def load(self, code, startdate, enddate, stype = 'stock', time_unit = 'daily'):
        print('load', stype, code, time_unit, 'data, from', StockDataSource.str_date(startdate), 
            'to', StockDataSource.str_date(enddate))

        self.stocks = StockData_LocalCSV.read_csv(self.path + '/' + code + '.' + time_unit + '.csv')
        _rowcount = len(self.stocks)
        
        if _rowcount > 0:
            startdate = StockDataSource.float_date(startdate)
            enddate = StockDataSource.float_date(enddate)
            _head = StockDataSource.float_date(self.stocks.at[0, 'trade_date'])
            _tear = StockDataSource.float_date(self.stocks.at[_rowcount-1, 'trade_date'])
            
            if enddate - _head > 10: 
                down_data = self.download_tushare(code, _head + 1, enddate, stype, time_unit)
                self.stocks = self._join(self.stocks, down_data)
            if _tear - startdate > 10:
                down_data = self.download_tushare(code, startdate, _tear-1, stype, time_unit)
                self.stocks = self._join(self.stocks, down_data)
        else:
            self.stocks = self.download_tushare(code, startdate, enddate, stype, time_unit)

        if len(self.stocks) > _rowcount:
            self.write_csv(code)

        return self.stocks
        
