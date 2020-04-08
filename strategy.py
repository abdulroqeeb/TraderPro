#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 08:38:49 2020

@author: abdulroqeeb
"""

from abc import ABCMeta, abstractmethod
import pandas as pd
import time

class Strategy(object):
    """Strategy is an abstract base class providing an interface for
    all subsequent (inherited) trading strategies.

    The goal of a (derived) Strategy object is to output a list of signals,
    which has the form of a time series indexed pandas DataFrame.

    In this instance only a single symbol/instrument is supported."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_signals(self):
        """An implementation is required to return the DataFrame of symbols 
        containing the signals to go long, short or hold (1, -1 or 0)."""
        raise NotImplementedError("Should implement generate_signals()!")



class MovingAverageCrossStrategy(Strategy):
    """    
    Requires:
    symbol - A stock symbol on which to form a strategy on.
    bars - A DataFrame of bars for the above symbol.
    short_window - Lookback period for short moving average.
    long_window - Lookback period for long moving average."""

    def __init__(self, symbol, order_size, broker, short_window=100, long_window=400, name='Unnamed'):
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.position = 0
        self.pnl = 0
        self.cost = 0
        self.trades = 0
        self.order_size = order_size
        self.broker = broker
        self.live = False
        self.name = name
        self.strategy_type = 'MACD'

    def generate_signals(self, bars):
        """Returns the integer indicating whether to go long, short or hold (1, -1 or 0)."""
        print('generate signal called')
        self.bars = bars

        if type(self.bars) == pd.core.frame.DataFrame:

            #print("Bars: ", self.bars)
            
            #print(self.symbol, self.order_size, self.name)
            
            if len(self.bars) > self.long_window:
                try:

                    self.short_mavg = self.bars['Last'][:self.short_window].mean()  
                    self.long_mavg = self.bars['Last'][:self.long_window].mean() 
                    

                    self.market_price = float(self.bars['Last'].tail(1))
                    # Create a 'signal' (invested or not invested) when the short moving average crosses the long
                    # moving average, but only for the period greater than the shortest moving average window
                    

                    if self.short_mavg > self.long_mavg and self.position in [-1, 0]:
                        
                        if self.position == 0:
                            self.position = 1
                            self.broker.orderContract(self.symbol, self.order_size, action='BUY', order_type='MKT', strategy = self.name)
                            self.trades += 1
                            self.cost = self.market_price
                            
                        else:
                            self.position = 0
                            self.broker.orderContract(self.symbol, self.order_size, action='BUY', order_type='MKT', strategy = self.name)
                            if self.position == -1: self.pnl += (self.cost - self.market_price) * self.order_size
                            self.trades += 1
                            self.cost = self.market_price
                            
                        return self.position
                    
                    elif self.short_mavg < self.long_mavg and self.position in [1, 0]:
                        
                        if self.position == 0:
                            self.position = -1
                            self.broker.orderContract(self.symbol, self.order_size, action='SELL', order_type='MKT', strategy = self.name)
                            self.trades += 1
                            self.cost = self.market_price
                            
                        else:
                            self.position = 0
                            self.broker.orderContract(self.symbol, self.order_size, action='SELL', order_type='MKT', strategy = self.name)
                            if self.position == 1: self.pnl += (self.market_price - self.cost) * self.order_size
                            self.trades += 1
                            self.cost = self.market_price
                            
                        return self.position
                    
                    else:
                        if self.position == 1: self.pnl += self.market_price - self.cost
                        else: self.pnl += (self.cost - self.market_price) * self.order_size
                        
                        self.cost = self.market_price
                   
                except Exception as ex:
                    print('Error trading strategy:', ex)
            
                
            else: 
                print('Insufficient Data: {} more ticks needed for {}'.format(len(self.bars) - self.long_window, self.name))
        else:
            print('No data has been collected for ticker')
        return 0

    def run_strategy(self):
        self.live = True
        while (self.live):
            self.generate_signals(self.broker.prices_history.get_price_history_df(self.symbol))
            time.sleep(5)

    def stop_strategy(self):
        self.live = False





if __name__ == "__main__":
    strategy = MovingAverageCrossStrategy(1, 2, 4)
    print(strategy.generate_signals(prices))
