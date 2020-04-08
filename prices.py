#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 08:38:49 2020

@author: abdulroqeeb
"""

import datetime as dt
import pandas as pd

class Prices:
    
    def __init__(self):
        self.prices_history = {}

    def update_price_series(self, ticker, price):
        print('Saving price stream')
        current_time = dt.datetime.now()
        if ticker not in self.prices_history.keys():
            self.prices_history[ticker] = {}
            
        self.prices_history[ticker][current_time] = price

    def get_price_history_df(self, ticker):
        
        data = self.prices_history.get(ticker)
        #print('Ticker: ', ticker)
        #print('Data: ', data)
        #print('All Data: ', self.prices_history)
        if data:
            data_df = pd.DataFrame(index = data.keys())
            data_df['Last'] = data.values()

            return data_df
        return "No price history available for ticker: {}".format(ticker)
    
if __name__ == "__main__":
    prices = Prices()
    
    prices.update_price_series(1,2)
    prices.update_price_series(1,2)
    prices.update_price_series(1,3)
    prices.update_price_series(1,4.0)
    prices.update_price_series(1,3.5)
    prices.update_price_series(1,2)
    
    
    print(prices.get_price_history_df(1))
    print(prices.get_price_history_df(2))