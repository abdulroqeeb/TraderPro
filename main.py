#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 22:39:27 2020

@author: abdulroqeeb
"""

import sys
import os
from PyQt5 import QtWidgets, QtCore, uic, QtWebEngineWidgets
from base import TraderPro
import threading
import datetime
from tproconfig import host, port, states
from order import OrderUI
from ui.ui_assets import resources
from matplot_qt import MyStaticMplCanvas, MyDynamicMplCanvas
import time
from numpy import exp, random, sqrt
from trade import RunStrategy
from manage_strategy import StrategyManager

class TradeProUI(QtWidgets.QMainWindow):
    """
    @Description:   Program designed as part of the requirement for MSF 597 at the Stuart School 
                    of Business.
    @Term:          Spring 2020
    @Student:       Ariwoola Abdulroqeeb
    
    """
    
    def __init__(self):
        super(TradeProUI, self).__init__()
        self.ui = uic.loadUi('ui' + os.sep + 'main.ui', self)
        self.ui.connect_button.clicked.connect(self.start)
        self.ui.disconnect_button.clicked.connect(self.stop)
        self.init_tick_table()
        self.ui.ticker_lineedit.returnPressed.connect(self.return_pressed_on_ticker)
        self.ui.place_order.clicked.connect(self.place_order_clicked) 
        self.ui.tick_table.cellDoubleClicked.connect(self.tick_table_row_dbl_clicked)
        self.ui.live_strategies.cellDoubleClicked.connect(self.strategy_table_row_dbl_clicked)
        self.portfolio_chart = MyStaticMplCanvas(self.ui.main_widget, width=8.45, height=2.8, dpi=100)                
        self.tick_chart = MyStaticMplCanvas(self.ui.main_chart_widget, width = 12.6, height= 3.1, dpi=100)
        self.ui.start_algos.clicked.connect(self.start_algo)
        self._lock = threading.Lock()
        self.freeze_charts = False
        self.show()
        

    def init_tick_table(self):
        self.ui.tick_table.setColumnWidth(4, 100)
    
    def return_pressed_on_ticker(self):
        self.new_ticker = self.ui.ticker_lineedit.text().upper()
        self.log("Ticker input: {}".format(self.new_ticker.upper()))
        
        self.broker.streamPrice(self.new_ticker)
        self.broker.requestContractDetails(self.new_ticker)
        self.ui.ticker_lineedit.setText('')
        
    
        
    
    def log(self, *args):
        if not self.freeze_charts:
            print(args)
            for s in args:
                self.ui.log_display.addItem(QtWidgets.QListWidgetItem("{} - {}".format(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"), s)))
        
    
    def start(self):
        try: 
            self.broker = TraderPro(self)
            self.broker.connect(host, port, clientId=123)
            self.thread = threading.Thread(target = self.broker.run)
            self.thread.start()
            self.ui.statusBar().showMessage('Broker is now running', 2000)
            self.broker.load_strategies()
            self.ui.connect_button.setEnabled(False)
            self.ui.disconnect_button.setEnabled(True)
            #self.thread_helper = ThreadHelper(self.broker)
        
        except Exception as ex:
            self.ui.statusBar().showMessage('Connection failed, is Traderstation launched yet? {}'.format(ex), 2000)


    def stop(self):
        self.broker.save_strategies()
        if self.thread.is_alive():
            self.broker.disconnect()
            sys.exit()
        self.ui.statusBar().showMessage('Broker is now shutdown', 2000)
        
        self.ui.connect_button.setEnabled(True)
        self.ui.disconnect_button.setEnabled(False)
     
    
    def update_ui(self):
        pass


    def update_tick_table(self, row, column, value, align_center=True):
        if not self.freeze_charts:
        
            item = QtWidgets.QTableWidgetItem(value)
            if align_center: 
                item.setTextAlignment(QtCore.Qt.AlignCenter)
            current_value = self.ui.tick_table.itemAt(row, column).text()
            print(current_value)
            # try:
            #     if float(current_value) > float(value):
            #         item.setBackground(QtCore.Qt.red)
    
            # except Exception as ex:
            #     print('Error: ', ex)
    
            self.ui.tick_table.setItem(row, column, item)
            
            self.ui.tick_table.viewport().update()
            
            try: self.plot_stream()
            except Exception as ex: print('Error plotting data: ', ex)
            self.update_live_strategies_view()

    
    def update_account_table(self, account_details):
        if not self.freeze_charts:
            _keys = sorted(list(account_details.keys()))
            self.ui.account_details_view.setRowCount(0)
            print('Update account table called')
            for _key in _keys:
                print('Updating: ', _key)
                self.ui.account_details_view.insertRow(_keys.index(_key))
                self.ui.account_details_view.setItem(_keys.index(_key), 0, self.make_table_widget_item(_key, False))
                self.ui.account_details_view.setItem(_keys.index(_key), 1, self.make_table_widget_item(account_details.get(_key)))
            self.ui.account_details_view.viewport().update()

    

    def update_positions_table(self, _positions):
        try:
            if not self.freeze_charts:
                self.ui.positions_details_view.setRowCount(0)
                print(_positions)
                positions = list(_positions.keys())
                
                
                for position in positions:
                    self.ui.positions_details_view.insertRow(positions.index(position))
                    self.ui.positions_details_view.setItem(positions.index(position), 0, self.make_table_widget_item(_positions.get(position).get("SecType")))
                    self.ui.positions_details_view.setItem(positions.index(position), 1, self.make_table_widget_item(_positions.get(position).get("Symbol")))
                    self.ui.positions_details_view.setItem(positions.index(position), 2, self.make_table_widget_item(_positions.get(position).get("MarketValue")))
                    self.ui.positions_details_view.setItem(positions.index(position), 3, self.make_table_widget_item(_positions.get(position).get("Position")))
                    self.ui.positions_details_view.setItem(positions.index(position), 4, self.make_table_widget_item(_positions.get(position).get("AverageCost")))
                    self.ui.positions_details_view.setItem(positions.index(position), 5, self.make_table_widget_item(_positions.get(position).get("RealizedPNL")))
                    self.ui.positions_details_view.setItem(positions.index(position), 6, self.make_table_widget_item(_positions.get(position).get("UnrealizedPNL")))
                    
                self.ui.positions_details_view.viewport().update()
                
        except Exception as ex:
            print('Error updating position table: ', ex)
        
    def update_open_orders_table(self, _open_orders):
        try:
            if not self.freeze_charts:
                self.ui.open_orders_view.setRowCount(0)
                print(_open_orders)
                open_orders = list(_open_orders.keys())
                for order in open_orders:
                    self.ui.open_orders_view.insertRow(open_orders.index(order))
                    self.ui.open_orders_view.setItem(open_orders.index(order), 0, self.make_table_widget_item(_open_orders.get(order).get("ticker")))
                    self.ui.open_orders_view.setItem(open_orders.index(order), 1, self.make_table_widget_item(_open_orders.get(order).get("action")))
                    self.ui.open_orders_view.setItem(open_orders.index(order), 2, self.make_table_widget_item(_open_orders.get(order).get("ordertype")))
                    self.ui.open_orders_view.setItem(open_orders.index(order), 3, self.make_table_widget_item(_open_orders.get(order).get("totalqty")))
                    self.ui.open_orders_view.setItem(open_orders.index(order), 4, self.make_table_widget_item(_open_orders.get(order).get("lmtprice")))
                    self.ui.open_orders_view.setItem(open_orders.index(order), 5, self.make_table_widget_item(_open_orders.get(order).get("strategy")))
                    
                self.ui.open_orders_view.viewport().update()

        except Exception as ex:
            print('Error updating open order table: ', ex)
    
    def update_live_strategies_view(self):
        try:
        
            if not self.freeze_charts:
                self.strategies = self.broker.strategies
                
                self.ui.live_strategies.setRowCount(0)
                #print(self.strategies)
                _live_strategies = list(self.strategies.keys())
                
                for strategy in _live_strategies:
                    row = _live_strategies.index(strategy)
                    this_strategy = self.strategies.get(strategy)
                    self.ui.live_strategies.insertRow(row)
                    self.ui.live_strategies.setItem(row, 0, self.make_table_widget_item(this_strategy.name, align_center=False))
                    self.ui.live_strategies.setItem(row, 1, self.make_table_widget_item(this_strategy.strategy_type, align_center=True))
                    self.ui.live_strategies.setItem(row, 2, self.make_table_widget_item(this_strategy.symbol, align_center=True))
                    self.ui.live_strategies.setItem(row, 3, self.make_table_widget_item(states.get(this_strategy.position), align_center=True))
                    self.ui.live_strategies.setItem(row, 4, self.make_table_widget_item(this_strategy.pnl, align_center=True))
                    self.ui.live_strategies.setItem(row, 5, self.make_table_widget_item(this_strategy.trades, align_center=True))
                    state = 'Running ' if this_strategy.live else 'Stopped'
                    self.ui.live_strategies.setItem(row, 6, self.make_table_widget_item(state, align_center=True))
                    
                    #self.ui.live_strategies.setCellWidget(row, 6, QtWidgets.QPushButton('Stop Strategy'))
                self.ui.live_strategies.viewport().update()
                
        except Exception as ex:
            print('Error updating live strategies view')
        
    def make_table_widget_item(self, text, align_center=True):
        _item = QtWidgets.QTableWidgetItem(str(text))
        if align_center:
            _item.setTextAlignment(QtCore.Qt.AlignCenter)
        return _item
    
    
    def update_portfolio_hist_chart(self, port_history):
        if not self.freeze_charts:
            self.portfolio_chart.t = list(port_history.keys())
            self.portfolio_chart.s = list(port_history.values())            
            self.portfolio_chart.plot_new_data() 
                    
    
    def place_order_clicked(self):
        
        self.freeze_charts = True
        order_ui = OrderUI(self.broker)
        
        

    def start_algo(self):
        self.freeze_charts = True
        _run_strategy = RunStrategy(self.broker)

    def open_place_order_thread(self):
        order_ui = OrderUI(self.broker)
        

    def tick_table_row_dbl_clicked(self, row, column):
        
        print(row, column)
        
        print(self.ui.tick_table.item(row, 0).text(), ' clicked')
        
        self._ticker = self.ui.tick_table.item(row, 0).text()
        self.plot_stream()

    def plot_stream(self):
        if not self.freeze_charts:
            _price_stream = self.broker.prices_history.prices_history.get(self._ticker)
            
            if not None:
                self.tick_chart.t = list(_price_stream.keys())
                self.tick_chart.s = list(_price_stream.values())
                self.tick_chart.plot_new_data()

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            print('Window closed')
        else:
            event.ignore()

    def strategy_table_row_dbl_clicked(self, row, column):
        print(row, column)
        strategy_name = self.ui.live_strategies.item(row, 0).text()
        strategy = self.broker.strategies.get(strategy_name)
        if strategy: self.strategy_window = StrategyManager(strategy)
        self.update_live_strategies_view()

class ThreadHelper():
    
    def __init__(self, broker):
        self.broker = broker
        self.order_ui = OrderUI(self.broker)
        self.run_strategy = RunStrategy(self.broker)
    
    def place_order(self):
        self.order_ui.show()
        
    def run_new_strategy(self):
        self.run_new_strategy.show()
    


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = TradeProUI()
    sys.exit(app.exec_())
    
    
    

