#!/usr/bin/env python
#-*- coding: utf8 -*-
import numpy, pandas, datetime as dt, time
from turtle import trade, index, data, utils
from turtle.data import StockDataSource


if __name__ == "__main__":
    args = index.TurtleArgs()
    sdsr = data.StockData_SQLite( args.files[0] )

    for code in args.codes:
        sdsr.load(code, args.dates[0], args.dates[1], args.params[0], args.params[1])
        if not len(sdsr.stocks):
            continue
        data_list, _dates = sdsr.parse_price()
        _data_vec = numpy.transpose( data_list )
        turtle = index.TurtleIndex()
            
        if args.params[2] == 'long':
            long_index = index.LongTurtleIndex(turtle, _data_vec, args.turtle_args[2], 
                        args.turtle_args[3], args.turtle_args[0], args.turtle_args[1])
        else:
            long_index = index.ShortTurtleIndex(turtle, _data_vec, args.turtle_args[2], 
                        args.turtle_args[3], args.turtle_args[0], args.turtle_args[1])

        print( long_index )


