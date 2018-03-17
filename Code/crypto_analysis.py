#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 13:00:29 2018

@author: Robert
"""
import quandl
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 



### retrieving data
quandl.ApiConfig.api_key = ''

LTC_EUR = quandl.get("GDAX/LTC_EUR", authtoken=" " )
ETH_EUR = quandl.get("GDAX/ETH_EUR", authtoken=" ")
BTC_EUR = quandl.get("GDAX/EUR", authtoken=" ")

# constructing ohlv datasets
list_opens = [LTC_EUR['Open'] , ETH_EUR['Open'], BTC_EUR['Open']]
list_highs = [LTC_EUR['High'] , ETH_EUR['High'], BTC_EUR['High']]
list_lows = [LTC_EUR['Low'] , ETH_EUR['Low'], BTC_EUR['Low']]
list_volumes = [LTC_EUR['Volume'] , ETH_EUR['Volume'], BTC_EUR['Volume']]

opens = pd.concat(list_opens , axis = 1, join='inner')
highs = pd.concat(list_highs , axis = 1, join='inner')
lows = pd.concat(list_lows , axis = 1, join='inner')
volumes = pd.concat(list_volumes , axis = 1, join='inner')

# renaming the columns in each dataset
opens.columns = ['LTC_Open', 'ETH_Open', 'BTC_Open']
highs.columns = ['LTC_High', 'ETH_High', 'BTC_High']
lows.columns = ['LTC_Low', 'ETH_Low', 'BTC_Low']
volumes.columns = ['LTC_volumes', 'ETH_volumes', 'BTC_volumes']

# plot the graphs
opens.plot(grid = True)
highs.plot(grid = True)
lows.plot(grid= True)
volumes.plot(grid= True)

## calculate returns
open_return = opens.apply(lambda x: x / x[0])
open_return.head()
open_return.plot(grid = True).axhline(y = 1, color = "black", lw = 2)

## calculate the change
open_change = opens.apply(lambda x: np.log(x) - np.log(x.shift(1))) # shift moves dates back by 1.
open_change.head()
open_change.plot(grid = True).axhline(y = 0, color = "black", lw = 2)

## calculating moving average
opens["LTC_20d"] = np.round(opens["LTC_Open"].rolling(window = 20, center = False).mean(), 2)
opens["LTC_50d"] = np.round(opens["LTC_Open"].rolling(window = 50, center = False).mean(), 2)
opens["LTC_200d"] = np.round(opens["LTC_Open"].rolling(window = 200, center = False).mean(), 2)
opens["LTC_diff_20_50"] = opens["LTC_20d"] - opens["LTC_50d"]

opens["ETH_20d"] = np.round(opens["ETH_Open"].rolling(window = 20, center = False).mean(), 2)
opens["ETH_50d"] = np.round(opens["ETH_Open"].rolling(window = 50, center = False).mean(), 2)
opens["ETH_200d"] = np.round(opens["ETH_Open"].rolling(window = 200, center = False).mean(), 2)
opens["ETH_diff_20_50"] = opens["ETH_20d"] - opens["ETH_50d"]

opens["BTC_20d"] = np.round(opens["BTC_Open"].rolling(window = 20, center = False).mean(), 2)
opens["BTC_50d"] = np.round(opens["BTC_Open"].rolling(window = 50, center = False).mean(), 2)
opens["BTC_200d"] = np.round(opens["BTC_Open"].rolling(window = 200, center = False).mean(), 2)
opens["BTC_diff_20_50"] = opens["BTC_20d"] - opens["BTC_50d"]



# plot difference 20 - 50 of all currencies
MA_diff = ['LTC_diff_20_50', 'ETH_diff_20_50', 'BTC_diff_20_50']
opens[MA_diff].plot(grid=True)

# plot the MA of LTC
MAs_LTC = ["LTC_20d", "LTC_50d", "LTC_200d"]
opens[MAs_LTC].plot(grid=True)

# plot the MA of ETH
MAs_ETH = ["ETH_20d", "ETH_50d", "ETH_200d"]
opens[MAs_ETH].plot(grid=True)

# plot the MA of BTC
MAs_BTC = ["BTC_20d", "BTC_50d", "BTC_200d"]
opens[MAs_BTC].plot(grid=True)

## calculate regime 
opens["Regime_LTC"] = np.where(opens['LTC_diff_20_50'] > 0, 1, 0)
opens["Regime_LTC"] = np.where(opens['LTC_diff_20_50'] < 0, -1, opens["Regime_LTC"])

opens["Regime_ETH"] = np.where(opens['ETH_diff_20_50'] > 0, 1, 0)
opens["Regime_ETH"] = np.where(opens['ETH_diff_20_50'] < 0, -1, opens["Regime_ETH"])

opens["Regime_BTC"] = np.where(opens['BTC_diff_20_50'] > 0, 1, 0)
opens["Regime_BTC"] = np.where(opens['BTC_diff_20_50'] < 0, -1, opens["Regime_BTC"])

# plot the regimes
opens["Regime_LTC"].plot(ylim = (-2,2)).axhline(y = 0, color = "black", lw = 2)
regimes = ['Regime_LTC', 'Regime_ETH', 'Regime_BTC']
opens[regimes].plot(ylim = (-2,2)).axhline(y = 0, color = "black", lw = 2, grid=True)

# counts of the values
opens["Regime_LTC"].value_counts()

opens_melted = pd.melt(opens, value_vars=regimes, var_name='regime_type', value_name='value')
opens_melted.groupby(by=['regime_type', 'value'])['value'].count()

## make DataFrame with regime type and signal
#design signal column
opens["Signal_LTC"] = np.sign(opens["Regime_LTC"].iloc[1:] - opens["Regime_LTC"].shift(1).iloc[1:])
opens["Signal_ETH"] = np.sign(opens["Regime_ETH"].iloc[1:] - opens["Regime_ETH"].shift(1).iloc[1:])
opens["Signal_BTC"] = np.sign(opens["Regime_BTC"].iloc[1:] - opens["Regime_BTC"].shift(1).iloc[1:])

opens['Signal_LTC'][0] = float(0)
opens['Signal_ETH'][0] = float(0)
opens['Signal_BTC'][0] = float(0)

signals = ['Signal_LTC', 'Signal_ETH', 'Signal_BTC']

#plot the different signals
opens[signals].plot(ylim = (-2,2)).axhline(y = 0, color = "black", lw = 2, grid=True)

#count the different signal types
opens_melted_signal = pd.melt(opens, value_vars=signals, var_name='signals_type', value_name='value')
opens_melted_signal.groupby(by=['signals_type', 'value'])['value'].count()

#See which prices to buy and which prices to sell
opens.loc[opens["Signal_LTC"] == 1, "LTC_Open"]
opens.loc[opens["Signal_LTC"] == -1, "LTC_Open"]


# Create a DataFrame with trades, including the price at the trade and the regime under which the trade is made.
opens_signals_LTC = pd.concat([
        pd.DataFrame({"Price": opens.loc[opens["Signal_LTC"] == 1, "LTC_Open"],
                     "Regime": opens.loc[opens["Signal_LTC"] == 1, "Regime_LTC"],
                     "Signal": "Buy"}),
        pd.DataFrame({"Price": opens.loc[opens["Signal_LTC"] == -1, "LTC_Open"],
                     "Regime": opens.loc[opens["Signal_LTC"] == -1, "Regime_LTC"],
                     "Signal": "Sell"}),
    ])
opens_signals_LTC.sort_index(inplace = True)
opens_signals_LTC

opens_signals_ETH = pd.concat([
        pd.DataFrame({"Price": opens.loc[opens["Signal_ETH"] == 1, "LTC_Open"],
                     "Regime": opens.loc[opens["Signal_ETH"] == 1, "Regime_ETH"],
                     "Signal": "Buy"}),
        pd.DataFrame({"Price": opens.loc[opens["Signal_ETH"] == -1, "LTC_Open"],
                     "Regime": opens.loc[opens["Signal_ETH"] == -1, "Regime_ETH"],
                     "Signal": "Sell"}),
    ])
opens_signals_ETH.sort_index(inplace = True)
opens_signals_ETH

opens_signals_BTC = pd.concat([
        pd.DataFrame({"Price": opens.loc[opens["Signal_BTC"] == 1, "LTC_Open"],
                     "Regime": opens.loc[opens["Signal_BTC"] == 1, "Regime_BTC"],
                     "Signal": "Buy"}),
        pd.DataFrame({"Price": opens.loc[opens["Signal_BTC"] == -1, "LTC_Open"],
                     "Regime": opens.loc[opens["Signal_BTC"] == -1, "Regime_BTC"],
                     "Signal": "Sell"}),
    ])
opens_signals_BTC.sort_index(inplace = True)
opens_signals_BTC

### Let's see the profitability of long trades
#LTC
LTC_long_profits = pd.DataFrame({
        "Price": opens_signals_LTC.loc[(opens_signals_LTC["Signal"] == "Buy") &
                                  opens_signals_LTC["Regime"] == 1, "Price"],
        "Profit": pd.Series(opens_signals_LTC["Price"] - opens_signals_LTC["Price"].shift(1)).loc[
            opens_signals_LTC.loc[(opens_signals_LTC["Signal"].shift(1) == "Buy") & (opens_signals_LTC["Regime"].shift(1) == 1)].index
        ].tolist(),
        "End Date": opens_signals_LTC["Price"].loc[
            opens_signals_LTC.loc[(opens_signals_LTC["Signal"].shift(1) == "Buy") & (opens_signals_LTC["Regime"].shift(1) == 1)].index
        ].index
    })
LTC_long_profits

#ETH
ETH_long_profits = pd.DataFrame({
        "Price": opens_signals_ETH.loc[(opens_signals_ETH["Signal"] == "Buy") &
                                  opens_signals_ETH["Regime"] == 1, "Price"],
        "Profit": pd.Series(opens_signals_ETH["Price"] - opens_signals_ETH["Price"].shift(1)).loc[
            opens_signals_ETH.loc[(opens_signals_ETH["Signal"].shift(1) == "Buy") & (opens_signals_ETH["Regime"].shift(1) == 1)].index
        ].tolist(),
        "End Date": opens_signals_ETH["Price"].loc[
            opens_signals_ETH.loc[(opens_signals_ETH["Signal"].shift(1) == "Buy") & (opens_signals_ETH["Regime"].shift(1) == 1)].index
        ].index
    })
ETH_long_profits

#BTC
BTC_long_profits = pd.DataFrame({
        "Price": opens_signals_BTC.loc[(opens_signals_BTC["Signal"] == "Buy") &
                                  opens_signals_BTC["Regime"] == 1, "Price"],
        "Profit": pd.Series(opens_signals_BTC["Price"] - opens_signals_BTC["Price"].shift(1)).loc[
            opens_signals_BTC.loc[(opens_signals_BTC["Signal"].shift(1) == "Buy") & (opens_signals_BTC["Regime"].shift(1) == 1)].index
        ].tolist(),
        "End Date": opens_signals_BTC["Price"].loc[
            opens_signals_BTC.loc[(opens_signals_BTC["Signal"].shift(1) == "Buy") & (opens_signals_BTC["Regime"].shift(1) == 1)].index
        ].index
    })
BTC_long_profits




trades = pd.DataFrame({"Price": [], "Regime": [], "Signal": []})










