# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 19:19:56 2020

@author: harry
"""
from PyQt5 import QtWidgets, uic, QtCore
import sys, os
from tproconfig import states
import datetime
from matplot_qt import MyMplCanvas
import threading
import pandas as pd
import numpy as np
import time
timer = QtCore.QTimer()
pd.plotting.register_matplotlib_converters()

class StrategyManager(QtWidgets.QWidget):
    
    
    
    def __init__(self, strategy):
        super(StrategyManager, self).__init__()
        self.ui = uic.loadUi('ui' + os.sep + 'strategy.ui', self)
        self.strategy = strategy
        self.strategy.calc_stats()
        self.ui.name.setText(self.strategy.symbol +" - "+ self.strategy.name)
        self.ui.order_size.setText(str(self.strategy.order_size))
        
        if self.strategy.strategy_type == 'MACD':
            self.ui.short_window.setText(str(self.strategy.short_window))
            self.ui.long_window.setText(str(self.strategy.long_window))
            
        elif self.strategy.strategy_type == 'GAMBLE':
            self.ui.short_window.setText(str(self.strategy.short))
            self.ui.long_window.setText(str(self.strategy.long))
        else:
            pass
            
            
        self.ui.state.setText(states.get(self.strategy.position))
        state = 'Running ' if self.strategy.live else 'Stopped'
        self.ui.status.setText(state)
        self.ui.t_count.setText(str(self.strategy.trades))
        self.ui.pnl.setText(str(round(self.strategy.pnl, 2)))
        dt = datetime.datetime.now() - self.strategy.start_time
        self.ui.time.setText('{} days'.format(dt.days))
        self.ui.halt.clicked.connect(self.halt_strategy)
        self.ui.stop.clicked.connect(self.stop_strategy)
        
        self.ui.positives_disp.setText(str(round(self.strategy.positives * 100,2))+'%')
        self.ui.avg_ret.setText(str(round(self.strategy.average_returns * 100,2)) + "%")
        self.ui.volatility.setText(str(round(self.strategy.vol * 100,2)) + "%")
        self.ui.sharpe.setText(str(round(self.strategy.sharpe_ratio,2)))
        self.ui.sortino.setText(str(round(self.strategy.sortino_ratio,2)))
        self.strategy_plot = MyStaticMplCanvas(self.ui.strategy_plot, width = 5.1, height= 2.7, dpi=100)
        self.vami_vol = MyStaticMplCanvas(self.ui.roll_vol_plot_widget, width = 5.1, height= 2.7, dpi=100)
        self.hist = MyStaticMplCanvas(self.ui.distribution_plot_widget, width = 5.1, height= 2.7, dpi=100)
        #self.thread = threading.Thread(target = self.update_view)
        #self.thread.start()
        
        timer.timeout.connect(self.update_view)
        timer.start(1000)
        #self.update_view()
        self.ui.show()
        
    
    def halt_strategy(self):
        self.strategy.halt_strategy()
        broker = self.strategy.broker
        self.close()
        broker.window.update_live_strategies_view()
        
        
    def stop_strategy(self):
        try:
            broker = self.strategy.broker
            self.strategy.broker.strategies.pop(self.strategy.name)
            self.close()
            broker.window.update_live_strategies_view()
        except Exception as ex:
            print('Strategy does not exist: ', ex)
    
    def update_view(self):
        if not self.strategy.broker.window.freeze_charts:
            #print('Function called')
            self.hist.s = self.strategy.returns
            self.hist.s = self.hist.s[np.isfinite(self.hist.s)]
            self.hist.plot_new_data()
    
            if self.strategy.strategy_type == 'MACD':
                self.strategy_plot.s = pd.concat([self.strategy.prices, self.strategy.short_mavg_prices, self.strategy.long_mavg_prices], axis=1)
                self.strategy_plot.s.columns = ['{} Last Price'.format(self.strategy.symbol),
                                                '{} Ticks MA: {:.2f}'.format(self.strategy.short_window, self.strategy.short_mavg),
                                                '{} Ticks MA: {:.2f}'.format(self.strategy.long_window, self.strategy.long_mavg)]
            else:
                self.strategy_plot.s = self.strategy.prices
                
            self.strategy_plot.plot_new_data(chart='strategy_plot')      
            
            vami = (self.hist.s + 1).cumprod()
            vol = self.hist.s.rolling(10).std()
            self.vami_vol.s = pd.concat([vami, vol], axis=1)
            #print('VAMI-VOL: ', self.vami_vol.s)
            self.vami_vol.plot_new_data(chart='vami_vol')
            
            
            self.ui.state.setText(states.get(self.strategy.position))
            state = 'Running ' if self.strategy.live else 'Stopped'
            self.ui.status.setText(state)
            self.ui.t_count.setText(str(self.strategy.trades))
            self.ui.pnl.setText(str(round(self.strategy.pnl, 2)))
            dt = datetime.datetime.now() - self.strategy.start_time
            self.ui.time.setText('{} days'.format(dt.days))
            
            self.ui.positives_disp.setText(str(round(self.strategy.positives * 100,2))+'%')
            self.ui.avg_ret.setText(str(round(self.strategy.average_returns * 100,2)) + "%")
            self.ui.volatility.setText(str(round(self.strategy.vol * 100,2)) + "%")
            self.ui.sharpe.setText(str(round(self.strategy.sharpe_ratio, 2)))
            self.ui.sortino.setText(str(round(self.strategy.sortino_ratio,2)))
            
        
    def closeEvent(self, event):
        self.strategy.broker.window.freeze_charts = False
        event.accept()
        
        

class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):

        self.s = pd.Series(dtype=np.float64)
        #self.thread = threading.Thread(target=self.plot_new_data)
        #self.axes.invert_yaxis()
        #self.thread.start()
        
        
    def plot_new_data(self, chart='hist', ):
        self.axes.cla()
        self.axes_2.cla()
        #print('Prices for plot: ', self.s)
        if chart =='hist':
            self.axes.hist(self.s, label='Returns')
            self.axes.set_title('Distribution of strategy return')

            self.axes.set_xlabel('Returns')
            self.axes.set_ylabel('Frequency')
            self.axes.legend()
        elif chart == 'vami_vol':
            try:
                #self.axes_2.cla()
                self.axes.plot(self.s.iloc[:,0],label= 'VAMI')
                #self.axes_2 = self.axes.twinx()
                self.axes_2.plot(self.s.iloc[:,1], label='10 event rolling vol', color='r')
                self.axes.set_title('Growth of $1 and it\'s volatility')
                self.axes.set_ylabel('VAMI')
                self.axes_2.set_ylabel('Volatility')
                self.axes.set_xlabel('Time')
                self.axes.legend()
                self.axes_2.legend()
                
            except Exception as ex:
                print(ex)
                print(self.s)
        else:

            self.axes.plot(self.s)
            try: xmin=min(self.s.index[-30:]) if len(self.s.index) >= 30 else min(self.s.index)
            except Exception as ex:
                print('Error occured: ', ex)
                xmin = datetime.datetime.now() - datetime.timedelta(minutes=15)
            self.axes.axis(xmin=xmin, xmax=datetime.datetime.now())
            self.axes.set_title('Strategy Execution Plot')
            self.axes.set_ylabel('Prices')
            self.axes.set_xlabel('Time')
            self.axes.legend(list(self.s.columns))
        
        
        
            

        try:
            self.draw()
        except Exception as ex:
            print('Error occured: ', ex)        




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = StrategyManager({})
    sys.exit(app.exec_())
        