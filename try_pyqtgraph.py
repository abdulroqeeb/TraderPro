from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import threading
import psutil
import time

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('leftButtonPan', False)

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('random.ui', self)
        
        self.x = [1,2,3,4,5,6,7,8,9,10]
        self.y = [30,32,34,32,33,31,29,32,35,45]

        self.plot( self.x, self.y )
        
        self.thread  = threading.Thread(target = self.update)
        self.thread.start()

    def plot(self, hour, temperature):
        self.rnd = self.graphicsView.plot(hour, temperature)
        
        

    def update(self):
        for i in range(20):
            self.x.append(i+11)
            self.y.append(psutil.cpu_percent())
            self.rnd.setData(self.x, self.y)
            time.sleep(5)
        
        

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':      
    main()
    
    
    
    
