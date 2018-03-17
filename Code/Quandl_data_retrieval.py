#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 08:54:35 2018

@author: Robert
"""

import quandl
import datetime
import pandas as pd
import matplotlib.pyplot as plt 
 
quandl.ApiConfig.api_key = 
 
def quandl_stocks(symbol, start_date=(2000, 1, 1), end_date=None):
    
    """
    symbol is a string representing a stock symbol, e.g. 'AAPL'
 
    start_date and end_date are tuples of integers representing the year, month,
    and day
 
    end_date defaults to the current date when None
    """
 
    query_list = ['WIKI' + '/' + symbol + '.' + str(k) for k in range(1, 13)]
 
    
    start_date = datetime.date(*start_date)
 
    if end_date:
        end_date = datetime.date(*end_date)
    else:
        end_date = datetime.date.today()
 
    return quandl.get(query_list, 
            returns='pandas', 
            start_date=start_date,
            end_date=end_date,
            collapse='daily',
            order='asc'
            )
 
 
if __name__ == '__main__':
 
    apple_data = quandl_stocks('AAPL')
    print(apple_data)
    
apple_data = pd.DataFrame(apple_data)   
apple_data.rename(columns= {'WIKI/AAPL - Open': 'Open',\
                            'WIKI/AAPL - High': 'High',\
                            'WIKI/AAPL - Low' : 'Low', \
                            'WIKI/AAPL - Close' : 'Close'}, inplace=True)


#### handmatige query

test = query_list = ['GDAX/LTC_BTC']

quandl.get(query_list, 
            returns='pandas', 
            collapse='weekly',
            order='asc',
            transform='diff'
            )

#### make plots 
apple_data['WIKI/AAPL - Open'].plot(grid = True)


### get cryptocurrency data








