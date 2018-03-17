# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 11:37:34 2018

@author:=
"""

#### Binance API & data retrieval ####

"""

API Key:
Secret: 
"""
############### CODE to transform date to milliseconds
# requires dateparser package
import dateparser
import pytz
from datetime import datetime
import pandas as pd
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt

def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)
    
    
print(date_to_milliseconds("January 01, 2018"))
print(date_to_milliseconds("11 hours ago UTC"))
print(date_to_milliseconds("now UTC"))

############### CODE to transform date to milliseconds
from binance.client import Client

def interval_to_milliseconds(interval):
    """Convert a Binance interval string to milliseconds
    :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str
    :return:
         None if unit not one of m, h, d or w
         None if string not in correct format
         int value of interval in milliseconds
    """
    ms = None
    seconds_per_unit = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60
    }

    unit = interval[-1]
    if unit in seconds_per_unit:
        try:
            ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
        except ValueError:
            pass
    return ms
    
print(interval_to_milliseconds(Client.KLINE_INTERVAL_1MINUTE))
print(interval_to_milliseconds(Client.KLINE_INTERVAL_30MINUTE))
print(interval_to_milliseconds(Client.KLINE_INTERVAL_1WEEK))

################ get Klines 

from binance.client import Client
import time

def get_historical_klines(symbol, interval, start_str, end_str=None):
    """Get Historical Klines from Binance
    See dateparse docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/
    If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    :param symbol: Name of symbol pair e.g BNBBTC
    :type symbol: str
    :param interval: Biannce Kline interval
    :type interval: str
    :param start_str: Start date string in UTC format
    :type start_str: str
    :param end_str: optional - end date string in UTC format
    :type end_str: str
    :return: list of OHLCV values
    """
    # create the Binance client, no need for api key
    client = Client("", "")

    # init our list
    output_data = []

    # setup the max limit
    limit = 500

    # convert interval to useful value in seconds
    timeframe = interval_to_milliseconds(interval)

    # convert our date strings to milliseconds
    start_ts = date_to_milliseconds(start_str)

    # if an end time was passed convert it
    end_ts = None
    if end_str:
        end_ts = date_to_milliseconds(end_str)

    idx = 0
    # it can be difficult to know when a symbol was listed on Binance so allow start time to be before list date
    symbol_existed = False
    while True:
        # fetch the klines from start_ts up to max 500 entries or the end_ts if set
        temp_data = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            startTime=start_ts,
            endTime=end_ts
        )

        # handle the case where our start date is before the symbol pair listed on Binance
        if not symbol_existed and len(temp_data):
            symbol_existed = True

        if symbol_existed:
            # append this loops data to our output data
            output_data += temp_data

            # update our start timestamp using the last value in the array and add the interval timeframe
            start_ts = temp_data[len(temp_data) - 1][0] + timeframe
        else:
            # it wasn't listed yet, increment our start date
            start_ts += timeframe

        idx += 1
        # check if we received less than the required limit and exit the loop
        if len(temp_data) < limit:
            # exit the while loop
            break

        # sleep after every 3rd call to be kind to the API
        if idx % 3 == 0:
            time.sleep(1)

    return output_data
    
### get data

from binance.client import Client

"""
opbouw van een kline

Response:

[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore
  ]
]

"""


# fetch 1 minute klines for the last day up until now
klines = get_historical_klines("BNBBTC", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

# fetch 30 minute klines for the last month of 2017
klines = get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")

# fetch weekly klines since it listed
klines = get_historical_klines("NEOBTC", KLINE_INTERVAL_1WEEK, "1 Jan, 2017")    


# Get historical data for NANOBTC    
klines_NANOBTC = get_historical_klines("NANOBTC", Client.KLINE_INTERVAL_15MINUTE, "1 day ago UTC")

NANOBTC_data = pd.DataFrame(klines_NANOBTC)    
NANOBTC_data.columns = ['Open_time_NB', 'Open_NB', 'High_NB', 'Low_NB', 'Close_NB', 'Volume_NB', 'Close_time_NB',\
                           'Asset_volume_NB', 'Numb_trades_NB', 'Buy_base_NB', 'Buy_quote_NB', 'Ignore_NB']    
NANOBTC_data['Date_time'] = NANOBTC_data['Open_time_NB'].apply(lambda x: datetime.utcfromtimestamp(x//1000))
numeric_columns = ['Open_NB', 'High_NB', 'Low_NB', 'Close_NB', 'Volume_NB', 'Close_time_NB',\
                           'Asset_volume_NB', 'Numb_trades_NB', 'Buy_base_NB', 'Buy_quote_NB']   
NANOBTC_data[numeric_columns] = NANOBTC_data[numeric_columns].apply(pd.to_numeric)

# Get historical data for BTCUSD
klines_BTCUSD = get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 day ago UTC")
BTCUSDT_data = pd.DataFrame(klines_BTCUSD)  
BTCUSDT_data.columns = ['Open_time_BU', 'Open_BU', 'High_BU', 'Low_BU', 'Close_BU', 'Volume_BU', 'Close_time_BU',\
                           'Asset_volume_BU', 'Numb_trades_BU', 'Buy_base_BU', 'Buy_quote_BU', 'Ignore_BU']    
BTCUSDT_data['Date_time'] = BTCUSDT_data['Open_time_BU'].apply(lambda x: datetime.utcfromtimestamp(x//1000))
numeric_columns_BTCUSD = ['Open_BU', 'High_BU', 'Low_BU', 'Close_BU', 'Volume_BU', 'Close_time_BU',\
                           'Asset_volume_BU', 'Numb_trades_BU', 'Buy_base_BU', 'Buy_quote_BU']    
BTCUSDT_data[numeric_columns_BTCUSD] = BTCUSDT_data[numeric_columns_BTCUSD].apply(pd.to_numeric)

                           
# create NANO/USD dataset
NANOUSD_data = pd.DataFrame([])
NANOUSD_data['Open_NU'] = NANOBTC_data['Open_NB'] * BTCUSDT_data['Open_BU']
NANOUSD_data['Close_NU'] = NANOBTC_data['Close_NB'] * BTCUSDT_data['Close_BU']

## Calculate standard deviations
std_open_NANO = np.std(NANOUSD_data['Open_NU'])
std_close_NANO = np.std(NANOUSD_data['Close_NU'])
std_open_BTC = np.std(BTCUSDT_data['Open_BU'])
std_close_BTC = np.std(BTCUSDT_data['Close_BU'])
std_open_NANOBTC = np.std(NANOBTC_data['Open_NB'])
std_close_NANOBTC = np.std(NANOBTC_data['Close_NB'])

print(tabulate([['Nano_open', std_open_NANO], 
                ['Nano_close', std_close_NANO], 
                ['BTC_open', std_open_BTC], 
                ['BTC_close',  std_close_BTC], 
                ['NANOBTC_open', std_open_NANOBTC], 
                ['NANOBTC_close', std_close_NANOBTC]],              
                headers=['Coin', 'Std']))

## create dataset with all valuable information

Coins_dataset = pd.DataFrame([])
Coins_dataset['Date'] = NANOBTC_data['Date_time']
Coins_dataset['NANOUSD_open'] = NANOUSD_data['Open_NU']
Coins_dataset['NANOUSD_close'] = NANOUSD_data['Close_NU']
Coins_dataset['BTCUSD_open'] = BTCUSDT_data['Open_BU']
Coins_dataset['BTCUSD_close'] = BTCUSDT_data['Close_BU']
Coins_dataset['NANOBTC_open'] = NANOBTC_data['Open_NB']
Coins_dataset['NANOBTC_close'] = NANOBTC_data['Close_NB']



## Calculate returns
coins_return = Coins_dataset.iloc[:, 1:].apply(lambda x: x / x[0])
coins_return['Date'] = NANOBTC_data['Date_time']
coins_return.head()
coins_return_std = coins_return.iloc[:, 0:6].apply(lambda x: np.std(x))
coins_std = Coins_dataset.iloc[:, 1:7].apply(lambda x: np.std(x))
coins_means = Coins_dataset.iloc[:, 1:7].apply(lambda x: np.mean(x))
coins_normalized_std = (Coins_dataset.iloc[:, 1:7] - coins_means).apply(lambda x: np.std(x))

## Calculate percentage returns and binary 
coins_return_percentage = coins_return.iloc[:,0:6] - 1 
plt.hist(coins_return_percentage['NANOBTC_close'])
coins_return_percentage['NANOBTC_10%'] = np.where(apple['20d-50d'] > 0, 1, 0)
coins_return_percentage['NANOBTC_15%'] = 
coins_return_percentage['NANOBTC_20%'] = 
coins_return_percentage['NANOBTC_20%'] =




## Calculate change
coins_change = Coins_dataset.iloc[:, 1:].apply(lambda x: np.log(x) - np.log(x.shift(1))) # shift moves dates back by 1.
coins_change_std = coins_change.iloc[:, 0:6].apply(lambda x: np.std(x))
coins_change.plot(grid = True, x = NANOBTC_data['Date_time']).axhline(y = 0, color = "black", lw = 2)


plt.plot(coins_change['NANOBTC_open'])
plt.axhline(y = 0, color = "black", lw = 2)


## merging of standard deviations
SDs = pd.concat([coins_std, coins_normalized_std, coins_return_std, coins_change_std], axis= 1)
SDs.columns = ['coins_std', 'coins_normalized_std', 'coins_return_std', 'coins_change_std']
SDs

output = [np.float(62)]
for x in range(0, 30):
    result = output[x] * 1.18
    output.append(float(result))
    print(round(output[x], 3))

plt.plot(output)














