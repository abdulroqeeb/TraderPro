#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 18:51:55 2020

@author: abdulroqeeb
"""

from PyQt5 import QtGui, QtWidgets, uic  # (the example applies equally well to PySide)
import pyqtgraph as pg
import sys
import psutil
import datetime as dt
import time

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class TestUI(QtWidgets.QWidget):
    
    def __init__(self):
        super(TestUI, self).__init__()
        self.ui = uic.loadUi('random.ui', self)
        
        self.btn = QtGui.QPushButton('press me')
        self.text = QtGui.QLineEdit('enter text')
        self.listw = QtGui.QListWidget()
        
        self.x = []
        self.y = []
        
        self.plot = pg.PlotWidget()
        
        self.plot.getPlotItem().plot(self.x, self.y)
        self.widget = self.ui.widget 
        self.lauout = QtGui.QVBoxLayout()
        self.widget.setLayout(self.layout)
        
        self.layout.addWidget(self.plot)  # plot goes on right side, spanning 3 rows
        self.ui.button.clicked.connect(self.update)
        self.show()
        
        
    def update(self):
        self.x.append(time.time())
        print(self.x[-30:])
        print(self.y[-30:])
        self.y.append(psutil.cpu_percent())
        self.plot.getPlotItem().plot(self.x[-30:], self.y[-30:])
        self.plot.setXRange(min(self.x[-30:]), max(self.x[-30:]), padding=0)
        
        
        
        
        
## Always start by initializing Qt (only once per application)



if __name__ == "__main__":
    app = QtGui.QApplication([])
    main = TestUI()
    app.exec_()