# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 16:57:54 2020

@author: harry
"""

from PyQt5 import QtWidgets, uic
import os
import sys
from strategy import MovingAverageCrossStrategy
import threading
from ui.ui_assets import resources
from order import OrderUI as BasicOrderUI
from tproutils import get_now

class RunStrategy(QtWidgets.QWidget):

    def __init__(self, broker):
        super(RunStrategy, self).__init__()
        self.ui = uic.loadUi('ui' + os.sep + 'algo.ui', self)
        self.ui.algorithm_combo.currentTextChanged.connect(self.algorithm_combo_changed)
        self.ui.define_algo_button.clicked.connect(self.choose_strategy)
        self.broker = broker
        self.strategy_selected = "Basic Trade"
        self.show()
    
    
    def algorithm_combo_changed(self):
        self.strategy_selected = self.ui.algorithm_combo.currentText()
        print(self.strategy_selected)
    

    def choose_strategy(self):

        if self.strategy_selected == 'Basic Trade':
            self.close()
            BasicOrderUI(self.broker)
        
        elif self.strategy_selected == 'Moving Average Crossover':
            self.close()
            MovingAverageCrossStrategyUI(self.broker)

        else:
            self.window.ui.statusBar().showMessage('Strategy not defined', 5000)

             

class MovingAverageCrossStrategyUI(QtWidgets.QWidget):
    
    def __init__(self, broker):
        super(MovingAverageCrossStrategyUI, self).__init__()
        self.ui = uic.loadUi('ui' + os.sep + 'macd.ui', self)
        self.broker = broker
        self.ui.commence_trading.clicked.connect(self.commence_trading_clicked)
        if broker: self.ui.ticker_combo.addItems(list(self.broker.tracked_names.keys()))
        self.strategies = {}
        self.show()
    
    def trade(self):
        
        print('Starting strategy')
        if self.ticker not in self.broker.tracked_names.keys():
            print('Not tracked')
            return "No data available"
        
        else:
            trader = MovingAverageCrossStrategy(self.ticker, self.size, self.broker, self.short_window_val, self.long_window_val, self.name)
            self.maco_trade_thread = threading.Thread(target = trader.run_strategy)
            self.maco_trade_thread.start()
            self.broker.strategies[trader.name] = trader
            self.broker.window.ui.statusBar().showMessage('Moving Average Strategy Now Running', 5000)
            self.broker.window.update_live_strategies_view()
            self.close()
            
            
    def commence_trading_clicked(self):
        
        

        self.ticker = self.ui.ticker_combo.currentText()
        self.name = self.ui.strategy_name.text() + "-" + get_now()
        self.size = int(self.ui.order_size.text())
        self.short_window_val = int(self.ui.short_window.text())
        self.long_window_val = int(self.ui.long_window.text())
        self.window_val = int(self.ui.window.text())
        print(self.ticker, self.name, self.size, self.short_window_val, self.long_window_val, self.window_val)

        self.trade()
        
    def closeEvent(self, event):
        self.broker.window.freeze_charts = False
        event.accept()
            
            
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = RunStrategy({})
    sys.exit(app.exec_())