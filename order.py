#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 14:19:10 2020

@author: abdulroqeeb
"""
from PyQt5 import QtWidgets, uic, QtCore
import os
import sys
from ui.ui_assets import resources


class OrderUI(QtWidgets.QWidget):
    
    def __init__(self, broker):
        super(OrderUI, self).__init__()
        self.ui = uic.loadUi('ui' + os.sep + 'order.ui', self)
        self.broker = broker
        self.order_action = 'BUY'
        self.order_type = 'MKT'
        #self.order_
        self.tickers = self.broker.tracked_names if self.broker else []
        if self.tickers: self.ticker_combo.addItems(self.tickers)
        self.order_lmt.toggled.connect(self.lmt_order_toggled)
        self.place_order.clicked.connect(self.order_clicked)
        self.show()
    
    def run(self):
        self.show()
        
    def order_clicked(self):

        self.ticker = self.ticker_combo.currentText()
        self.order_quantity = int(self.order_qty.text())
        if self.order_sell.isChecked(): self.order_action = 'SELL'
        if self.order_lmt.isChecked(): self.order_type = 'LMT'
        if self.lmt_price.text() != '': self.lmt_order_price = float(self.lmt_price.text())
        
        if self.order_type == 'MKT': self.broker.orderContract(self.ticker, self.order_quantity, self.order_action, self.order_type)
        else: self.broker.orderContract(self.ticker, self.order_quantity, self.order_action, self.order_type, self.lmt_order_price)

    def lmt_order_toggled(self):
        self.lmt_price.setEnabled(True)

    def closeEvent(self, event):
        self.broker.window.freeze_charts = False
        event.accept()
        


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = OrderUI({})
    sys.exit(app.exec_())