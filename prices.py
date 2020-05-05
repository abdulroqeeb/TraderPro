#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 08:38:49 2020

@author: abdulroqeeb
"""

import datetime as dt
import pandas as pd
import pickle
import atexit
import time
atexit.register(lambda: print('Exiting'))

class Prices:
    
    def __init__(self):
        self.load_price_history()
        
        

    def update_price_series(self, ticker, price):
        print('Saving price stream')
        current_time = dt.datetime.now()
        if ticker not in self.prices_history.keys():
            self.prices_history[ticker] = {}
            
        self.prices_history[ticker][current_time] = price
        #self.save_price_history()

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
    
    
    def load_price_history(self):
        try:
            with open('prices.pk', 'rb') as file:
                self.prices_history = pickle.load(file)
                print('Price history loaded')
        except :
            self.prices_history = {}
            print('Could not load price history')
                
    
    def save_price_history(self):
        print('saving price history on exit')
        with open('prices.pk', 'wb') as file:
            pickle.dump(self.prices_history, file)
    



    
if __name__ == "__main__":
    prices = Prices()
    
    prices.update_price_series(1,2)
    time.sleep(1)
    prices.update_price_series(1,2)
    time.sleep(1)
    prices.update_price_series(1,3)
    time.sleep(1)
    prices.update_price_series(1,4.0)
    time.sleep(1)
    prices.update_price_series(1,3.5)
    time.sleep(1)
    prices.update_price_series(1,2)
    
    
    print(prices.get_price_history_df(1))
    print(prices.get_price_history_df(2))