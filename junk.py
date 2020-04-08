import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets

class statusdemo(QtWidgets.QMainWindow):
   def __init__(self, parent = None):
      super(statusdemo, self).__init__(parent)
		
      bar = self.menuBar()
      file = bar.addMenu("File")
      file.addAction("show")
      file.addAction("add")
      file.addAction("remove")
      file.triggered[QtWidgets.QAction].connect(self.processtrigger)
      self.setCentralWidget(QtWidgets.QTextEdit())
		
      self.statusBar = QtWidgets.QStatusBar()
      self.b = QtWidgets.QPushButton("click here")
      self.setWindowTitle("QStatusBar Example")
      self.setStatusBar(self.statusBar)
		
   def processtrigger(self,q):
	
      if (q.text() == "show"):
         self.statusBar.showMessage(q.text()+" is clicked",2000)
			
      if q.text() == "add":
         self.statusBar.addWidget(self.b)
			
      if q.text() == "remove":
         self.statusBar.removeWidget(self.b)
         self.statusBar.show()
			
def main():
   app = QtWidgets.QApplication(sys.argv)
   ex = statusdemo()
   ex.show()
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   main()
   
   
   
   
   
           self.window.log('Tickstring called')
        if tickType == wrapper.TickTypeEnum.RT_VOLUME:
            self.window.log(value)#price,size,time
        self.window.log("{}\t{}:".format(ticktypes.get(tickType, "Unknown: {}".format(tickType)), value)) 
        if (ticktypes.get(int(tickType))) == 'Bid': self.window.ui.tick_table.setItem(self.req_to_table_row.get(reqId, 1), 4, QtWidgets.QTableWidgetItem(value))
        if (ticktypes.get(int(tickType))) == 'Ask': self.window.ui.tick_table.setItem(self.req_to_table_row.get(reqId, 1), 5, QtWidgets.QTableWidgetItem(value))















from PyQt5 import QtGui, QtWidgets, uic  # (the example applies equally well to PySide)
import pyqtgraph as pg
import sys

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class TestUI(QtWidgets.QWidget):
    
    def __init__(self):
        super(TestUI, self).__init__()
        self.ui = uic.loadUi('random.ui', self)
        
        self.btn = QtGui.QPushButton('press me')
        self.text = QtGui.QLineEdit('enter text')
        self.listw = QtGui.QListWidget()
        
        self.x = [1,2,3,4,5,6,7,8,9,10]
        self.y = [30,32,34,32,33,31,29,32,35,45]
        self.plot = pg.PlotWidget()
        self.plot.getPlotItem().plot(self.x, self.y)
        self.widget = self.ui.widget 
        self.lauout = QtGui.QGridLayout()
        self.widget.setLayout(self.layout)
        
        self.layout.addWidget(self.btn, 0, 0)   # button goes in upper-left
        self.layout.addWidget(self.text, 1, 0)   # text edit goes in middle-left
        self.layout.addWidget(self.listw, 2, 0)  # list widget goes in bottom-left
        self.layout.addWidget(self.plot, 0, 1, 3, 1)  # plot goes on right side, spanning 3 rows

        self.show()
## Always start by initializing Qt (only once per application)



if __name__ == "__main__":
    app = QtGui.QApplication([])
    main = TestUI()
    app.exec_()
    
    
    
    
    
    
    
    
    
    
    
            self.trade(self.nextValidOrderId, {})
            
                    #self.reqContractDetails(self.nextValidOrderId, self.requestContractDetails("AAPL"))
        #self.reqMarketDataType(wrapper.MarketDataTypeEnum.DELAYED)
        #self.reqMktData(self.nextValidOrderId, contract, "", False, False, [])
        #self.reqAccountSummary(self.nextValidOrderId, "All", AccountSummaryTags.AllTags)
        #self.placeOrder(self.nextValidOrderId, contract, order)
        
        
        self.t = []
        self.s = []
        
        for i in range(5000):
            #time.sleep(1)
            _s0 = self.s[-1] if self.s else 80
            self.t.append(datetime.datetime.now())
            self.s.append(_s0 * exp(((0.05 - 0.26*0.26*0.5) * 1/(252 * 86400)) + 0.26 * sqrt(1/(252 * 86400)) *  random.normal()))

            self.sc.t = self.t
            self.sc.s = self.s            
            self.sc.plot_new_data() 