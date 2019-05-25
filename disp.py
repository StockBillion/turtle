#!/usr/bin/env python
#-*- coding: utf8 -*-
import sys, numpy, pandas, datetime as dt, time
from turtle import trade, index, data, utils
from turtle.data import StockDataSource


# colors = ('r', 'y', 'b', 'g', 'c', 'm', 'k', 'w')
colors = ('red', 'yellow', 'blue', 'green', 'cyan', 'magenta', 'black', 'white')

def list_info(stock_data, long_index, stop_loss, count = 0):
    list_len, starti = len(stock_data[0]), 0
    if count:
        starti = list_len - min(count, list_len)
    _close, _high, _low = stock_data[4], stock_data[2], stock_data[3]
    info_list = []

    for i in range(starti, list_len):
        append_price = long_index['key_price'][i] + long_index['wave'][i]
        stop_price = long_index['key_price'][i] - long_index['wave'][i] * stop_loss
        info_list.append( [ StockDataSource.str_date(stock_data[0][i]), _close[i], _high[i], _low[i],
                    long_index['state'][i], '%.02f'%long_index['key_price'][i], '%.02f'%append_price, 
                    '%.02f'%stop_price, '%.02f'%long_index['short'][i], '%.02f'%long_index['wave'][i] ] )

    cols = [ 'trade_date', 'close', 'high', 'low', 'state', 'key_price', 'append', 'stop', 'profit', 'wave' ]
    return pandas.DataFrame( info_list, columns= cols)
        

if __name__ == "__main__":
    # sys.argv = ['./disp.py', '-f', 'data/hs.0525.db', '-d', '20090701', '-c', '600036.sh', '601166.sh', '601288.sh']

    _args = index.TurtleArgs()
    sdsr = data.StockData_SQLite( _args.files[0] )

    title = 'plot['
    for code in _args.codes:
        title = '%s%s-' % (title, code)
    title = '%s]'%title

    sdsr.load('399300.sz', _args.dates[0], _args.dates[1], 'index', _args.params[1])
    if not len(sdsr.stocks):
        exit
    data_list, _dates = sdsr.parse_price()
    _data_vec = numpy.transpose( data_list )

    plot = utils.StockDisp(title, 1)
    plot.LogPlot(plot.ax1, _data_vec[0], _data_vec[4], colors[0])
    cidx = 1
    
    for code in _args.codes:
        sdsr.load(code, _args.dates[0], _args.dates[1], _args.params[0], _args.params[1])
        if not len(sdsr.stocks):
            continue
        data_list, _dates = sdsr.parse_price()
        _data_vec = numpy.transpose( data_list )

        # turtle = index.TurtleIndex()
        # if _args.params[2] == 'long':
        #     long_index = index.LongTurtleIndex(turtle, _data_vec, _args.turtle_args[2], 
        #                 _args.turtle_args[3], _args.turtle_args[0], _args.turtle_args[1])
        # else:
        #     long_index = index.ShortTurtleIndex(turtle, _data_vec, _args.turtle_args[2], 
        #                 _args.turtle_args[3], _args.turtle_args[0], _args.turtle_args[1])

        # info_list = list_info(_data_vec, long_index, _args.turtle_args[0] )
        # print( info_list.tail(20) )
        # info_list.to_csv( '%s/%s.csv'%(_args.files[2], code) )

        plot.LogPlot(plot.ax1, _data_vec[0], _data_vec[4], colors[cidx])
        cidx += 1

    plot.save( title, _args.files[3] )
    plot.show()



        # if _args.params[2] == 'long':
        #     short_index = index.LongTurtleIndex(turtle, _data_vec, _args.turtle_args[4], 
        #                 _args.turtle_args[5], _args.turtle_args[0], _args.turtle_args[1])
        # else:
        #     short_index = index.ShortTurtleIndex(turtle, _data_vec, _args.turtle_args[4], 
        #                 _args.turtle_args[5], _args.turtle_args[0], _args.turtle_args[1])


            # info_list = self.list_info2(_data_vec, long_index, short_index['state'] )
            # print( info_list[-80:-40] )

        # plot.LogKDisp(plot.ax1, data_list)
        # plot.LogPlot(plot.ax1, _data_vec[0], turtle_index['long'], 'r')
        # plot.LogPlot(plot.ax1, _data_vec[0], turtle_index['short'], 'y')
        # plot.Plot(plot.ax1, _data_vec[0], self.stim.data['average'], 'b')
            
        # title = 'plot['
        # for code in _args.codes:
        #     title = '%s%s' % (title, code)
        # title = '%s]'%title
        # plot = utils.StockDisp(title, 1)
        
        # sdsr = data.StockData_SQLite( _args.files[0] )
        # turtle = index.TurtleIndex()

