#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 08:38:49 2020

@author: abdulroqeeb
"""

from abc import ABCMeta, abstractmethod
import pandas as pd
import time
import pickle
import sys
import datetime
import numpy as np
from performanceanalytics import statistics
import random

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
        self.start_time = datetime.datetime.now()
        self.returns = pd.Series([0],index=[datetime.datetime.now()], dtype=np.float64)
        self.positives = 0
        self.average_returns = 0
        self.vol = 1
        self.sharpe_ratio = self.average_returns/ self.vol
        self.sortino_ratio = 0
        self.benchmark_return = 0
        self.max_drawdown = 0
        self.VAMI = pd.Series([1], index=[datetime.datetime.now()], dtype=np.float64)
        self.roll_vol = pd.Series([0], index=[datetime.datetime.now()], dtype=np.float64)
        self.prices = self.broker.prices_history.get_price_history_df(self.symbol)
        #self.returns = self.prices.pct_change()
        self.short_mavg_prices = pd.Series([0],index=[datetime.datetime.now()], dtype=np.float64)
        self.long_mavg_prices = pd.Series([0],index=[datetime.datetime.now()], dtype=np.float64)
        self.short_mavg = 0
        self.long_mavg = 0
        self.calc_stats()


    def generate_signals(self, bars):
        """Returns the integer indicating whether to go long, short or hold (1, -1 or 0)."""
        print('generate signal called')
        self.bars = bars

        if type(self.bars) == pd.core.frame.DataFrame:

            #print("Bars: ", self.bars)
            
            #print(self.symbol, self.order_size, self.name)
            
            if len(self.bars) > self.long_window:
                try:

                    self.short_mavg = self.bars['Last'][-self.short_window:].mean()  
                    self.long_mavg = self.bars['Last'][-self.long_window:].mean() 
                    print('Short MA: {:2f}, Long MA: {:2f}, Position: {}'.format(self.short_mavg, self.long_mavg, self.position))
                    
                    self.market_price = float(self.bars['Last'].tail(1))
                    # Create a 'signal' (invested or not invested) when the short moving average crosses the long
                    # moving average, but only for the period greater than the shortest moving average window
                    
                    print('Market price:', self.market_price)

                    if self.short_mavg > self.long_mavg and self.position in [-1, 0]:
                        
                        if self.position == 0:
                            print('Short above long and we are flat', self.short_mavg, self.long_mavg)
                            self.position = 1
                            self.broker.orderContract(self.symbol, self.order_size, action='BUY', order_type='MKT', strategy = self.name)
                            self.trades += 1
                            self.cost = self.market_price
                            
                        else:
                            
                            self.broker.orderContract(self.symbol, self.order_size, action='BUY', order_type='MKT', strategy = self.name)
                            print('Short above long and we are short', self.short_mavg, self.long_mavg)
                            if self.position == -1: 
                                self.position = 0
                                self.pnl += (self.cost - self.market_price) * self.order_size
                                self.returns = self.returns.append(pd.Series([self.pnl/self.cost], index=[datetime.datetime.now()]))
                            self.trades += 1
                            self.cost = self.market_price
                            
                        return self.position
                    
                    elif self.short_mavg < self.long_mavg and self.position in [1, 0]:
                        
                        if self.position == 0:
                            print('Short below long and we are flat', self.short_mavg, self.long_mavg)
                            self.position = -1
                            self.broker.orderContract(self.symbol, self.order_size, action='SELL', order_type='MKT', strategy = self.name)
                            self.trades += 1
                            self.cost = self.market_price
                            
                        else:
                            print('Short below long and we are long', self.short_mavg, self.long_mavg)
                            self.broker.orderContract(self.symbol, self.order_size, action='SELL', order_type='MKT', strategy = self.name)
                            if self.position == 1: 
                                self.position = 0
                                self.pnl += (self.market_price - self.cost) * self.order_size
                                self.returns = self.returns.append(pd.Series([self.pnl/self.cost], index=[datetime.datetime.now()]))
                            self.trades += 1
                            self.cost = self.market_price
                            
                        return self.position
                    
                    else:
                        self.cost = self.market_price
                   
                except Exception as ex:
                    print('Error trading strategy:', ex)
            
                
            else: 
                print('Insufficient Data: {} more ticks needed for {}'.format(len(self.bars) - self.long_window, self.name))
        else:
            print('No data has been collected for ticker')
        
        print('Generate signal completed')
        return 0

    def calc_stats(self):
        try:
            if not self.returns.empty:
                self.positives = len(self.returns[self.returns>0])/len(self.returns) if len(self.returns) != 0 else 0 
                self.average_returns = self.returns.mean()
                self.vol = self.returns.std()
                self.sharpe_ratio = self.average_returns/ self.vol
                #self.sharpe_ratio = statistics.sharpe_ratio(self.returns, self.benchmark_return)
                #self.sortino_ratio = statistics.sortino_ratio(self.returns, 0, self.benchmark_return)
                #self.max_drawdown = statistics.max_dd(self.returns)
                self.VAMI = (1 + self.returns).cumprod()
                self.roll_vol = self.returns.rolling(window=1).std()
                self.prices = self.broker.prices_history.get_price_history_df(self.symbol)
                #print('Prices from strategy: ', self.prices)
                self.short_mavg_prices = self.prices.rolling(window=self.short_window).mean()
                self.long_mavg_prices = self.prices.rolling(window=self.long_window).mean()
                
            else:
                print('Not enough returns data to calculate stats: ', self.name)
        except  Exception as ex:
            print('Error calculating statistics: ', self.symbol, ' Error: ', ex)


    def run_strategy(self):
        self.live = True
        while (self.live):
            try:
                self.generate_signals(self.broker.prices_history.get_price_history_df(self.symbol))
            except Exception as ex:
                print('Error in generate signals: ', ex)
            print('Before Calculate stats')
            self.calc_stats()
            time.sleep(1)
            print('After Calculate stats')
            self.broker.window.update_live_strategies_view()

    def halt_strategy(self):
        self.live = False
        

class LetGamble(Strategy):
    """    
    Requires:
    symbol - A stock symbol on which to form a strategy on.
    bars - A DataFrame of bars for the above symbol.
    short_window - Lookback period for short moving average.
    long_window - Lookback period for long moving average."""

    def __init__(self, symbol, order_size, broker, short=0, long=6, length = 3, name='Unnamed'):
        self.symbol = symbol
        self.short = short
        self.long = long
        self.length = length
        self.position = 0
        self.pnl = 0
        self.cost = 0
        self.trades = 0
        self.order_size = order_size
        self.broker = broker
        self.live = False
        self.name = name
        self.strategy_type = 'GAMBLE'
        self.start_time = datetime.datetime.now()
        self.returns = pd.Series([], dtype=np.float64)
        self.positives = 0
        self.average_returns = 0
        self.vol = 1
        self.sharpe_ratio = self.average_returns/ self.vol
        self.sortino_ratio = 0
        self.benchmark_return = 0
        self.max_drawdown = 0
        self.VAMI = pd.Series(dtype=np.float64)
        self.roll_vol = pd.Series(dtype=np.float64)
        self.prices = self.broker.prices_history.get_price_history_df(self.symbol)

        


    def generate_signals(self, bars):
        """Returns the integer indicating whether to go long, short or hold (1, -1 or 0)."""
        print('generate signal called')
        self.bars = bars

        if type(self.bars) == pd.core.frame.DataFrame:


            if len(self.bars) > 0:
                die = [1,2,3,4,5,6]
                pick = random.sample(die, self.length)
                print('Gamble Pick: ', pick)
                
                
                try:

                    self.market_price = float(self.bars['Last'].tail(1))
                    # Create a 'signal' (invested or not invested) when the short moving average crosses the long
                    # moving average, but only for the period greater than the shortest moving average window
                    
                    if pick.count(self.long) == self.length  and self.position in [-1, 0]:
                        
                        if self.position == 0: #Opening Trade
                            self.position = 1
                            #self.broker.orderContract(self.symbol, self.order_size, action='BUY', order_type='MKT', strategy = self.name)
                            self.trades += 1
                            self.cost = self.market_price
                            
                        else: #Closing Trade
                            
                            #self.broker.orderContract(self.symbol, self.order_size, action='BUY', order_type='MKT', strategy = self.name)
                            if self.position == -1:
                                self.position = 0
                                self.pnl += (self.cost - self.market_price) * self.order_size
                                #self.returns = self.returns.append(pd.Series([self.pnl/self.cost], index=datetime.datetime.now()))
                                self.returns = self.returns.append(pd.Series([random.normalvariate(0.1, 1)], index=[datetime.datetime.now()]))
                                #print(self.returns)
                            self.trades += 1
                            self.cost = self.market_price
                            
                        return self.position
                    
                    elif pick.count(self.short) == self.length and self.position in [1, 0]:
                        
                        if self.position == 0:
                            self.position = -1
                            #self.broker.orderContract(self.symbol, self.order_size, action='SELL', order_type='MKT', strategy = self.name)
                            self.trades += 1
                            self.cost = self.market_price
                            
                        else:
                            
                            #self.broker.orderContract(self.symbol, self.order_size, action='SELL', order_type='MKT', strategy = self.name)
                            if self.position == 1:
                                self.position = 0
                                self.pnl += (self.market_price - self.cost) * self.order_size
                                #self.returns = self.returns.append(pd.Series([self.pnl/self.cost], index=datetime.datetime.now()))
                                self.returns = self.returns.append(pd.Series([random.normalvariate(-0.05, 1)], index=[datetime.datetime.now()]))
                                #print(self.returns)
                            self.trades += 1
                            self.cost = self.market_price
                            
                        return self.position
                    
                    else:
                        print('Sorry, try again: ', pick)
                        self.cost = self.market_price
                   
                except Exception as ex:
                    print('Error trading strategy:', ex)
            
                
            else: 
                print('Insufficient Data: {} more ticks needed for {}'.format(len(self.bars) - self.long_window, self.name))
        else:
            print('No data has been collected for ticker')
        
        return 0

    def calc_stats(self):
        try:
            if not self.returns.empty:
                self.positives = round(len(self.returns[self.returns>0])/len(self.returns) if len(self.returns) != 0 else 0, 2) 
                self.average_returns = round(self.returns.mean(), 2)
                self.vol = round(self.returns.std(), 2)
                self.sharpe_ratio = self.average_returns/ self.vol
                #print('Returns: ', self.returns)
                #self.sharpe_ratio = round(statistics.sharpe_ratio(self.returns, self.benchmark_return), 2)
                #self.sortino_ratio = round(statistics.sortino_ratio(self.returns, 0, self.benchmark_return), 2)
                #self.max_drawdown = round(statistics.max_dd(self.returns), 2)
                self.VAMI = (1 + self.returns).cumprod()
                self.roll_vol = self.returns.rolling(window=1).std()
                self.prices = self.broker.prices_history.get_price_history_df(self.symbol)
                #print('Prices from strategy: ', self.prices)
        except  Exception as ex:
            print('Error calculating statistics: ', self.symbol, ' Error: ', ex)

    def run_strategy(self):
        try:
            
            self.live = True
            while (self.live):
                self.generate_signals(self.broker.prices_history.get_price_history_df(self.symbol))
                self.calc_stats()
                time.sleep(10)
                self.broker.window.update_live_strategies_view()
        
        except  Exception as ex:
            print('Error encountered at: ', self.symbol, ' Error: ', ex)
        
    def halt_strategy(self):
        self.live = False




if __name__ == "__main__":
    strategy = MovingAverageCrossStrategy(1, 2, 4)
    #print(strategy.generate_signals(prices))
