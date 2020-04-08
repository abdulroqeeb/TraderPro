# -*- coding: utf-8 -*-
"""
Demonstrates adding a custom context menu to a GraphicsItem
and extending the context menu of a ViewBox.
 
PyQtGraph implements a system that allows each item in a scene to implement its 
own context menu, and for the menus of its parent items to be automatically 
displayed as well. 
 
"""
#import initExample ## Add path to library (just for examples; you do not need this)
 

from pyqtgraph.Qt import QtGui, QtCore, uic
from PyQt5 import uic
import numpy as np
import pyqtgraph as pg

class TestUI (QtGui.QMainWindow):
    
    def __init__(self):
        super(TestUI, self).__init__()
        
        self.ui = uic.loadUi('random.ui', self)
    

        self.setWindowTitle('pyqtgraph example: PlotWidget')
        self.resize(800,800)

        cw = QtGui.QWidget()
        self.setCentralWidget(cw)
        l = QtGui.QVBoxLayout()
        cw.setLayout(l)
         
        self.pw = pg.PlotWidget(name='Plot1')  ## giving the plots names allows us to link their axes together
        l.addWidget(self.pw)
        self.pw2 = pg.PlotWidget(name='Plot2')
        l.addWidget(self.pw2)
        self.pw3 = pg.PlotWidget()
        l.addWidget(self.pw3)
         
        self.show()
         
        ## Create an empty plot curve to be filled later, set its pen
        self.p1 = self.pw.plot()
        self.p1.setPen((200,200,100))
         
        ## Add in some extra graphics
        rect = QtGui.QGraphicsRectItem(QtCore.QRectF(0, 0, 1, 5e-11))
        rect.setPen(pg.mkPen(100, 200, 100))
        self.pw.addItem(rect)
         
        self.pw.setLabel('left', 'Value', units='V')
        self.pw.setLabel('bottom', 'Time', units='s')
        self.pw.setXRange(0, 2)
        self.pw.setYRange(0, 1e-10)
        
        self.others()
         
    def rand(self, n):
        data = np.random.random(n)
        data[int(n*0.1):int(n*0.13)] += .5
        data[int(n*0.18)] += 2
        data[int(n*0.1):int(n*0.13)] *= 5
        data[int(n*0.18)] *= 20
        data *= 1e-12
        return data, np.arange(n, n+len(data)) / float(n)
         
     
    def updateData(self):
        yd, xd = self.rand(10000)
        self.p1.setData(y=yd, x=xd)

    def others(self):         
        ## Start a timer to rapidly update the plot in pw
        t = QtCore.QTimer()
        t.timeout.connect(self.updateData)
        t.start(50)
        #updateData()
         
        ## Multiple parameterized plots--we can autogenerate averages for these.
        for i in range(0, 5):
            for j in range(0, 3):
                yd, xd = self.rand(10000)
                self.pw2.plot(y=yd*(j+1), x=xd, params={'iter': i, 'val': j})
         
        ## Test large numbers
        curve = self.pw3.plot(np.random.normal(size=100)*1e0, clickable=True)
        curve.curve.setClickable(True)
        curve.setPen('w')  ## white pen
        curve.setShadowPen(pg.mkPen((70,70,30), width=6, cosmetic=True))
        curve.sigClicked.connect(self.clicked) 
        lr = pg.LinearRegionItem([1, 30], bounds=[0,100], movable=True)
        self.pw3.addItem(lr)
        line = pg.InfiniteLine(angle=90, movable=True)
        self.pw3.addItem(line)
        line.setBounds([0,200])
        
    def clicked(self):
        print("curve clicked")
        
         
        
         
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    
    app = QtGui.QApplication([])
    main = TestUI()
    main.show()
    sys.exit(app.exec_())