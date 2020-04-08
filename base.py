#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 12:11:22 2020

@author: abdulroqeeb
"""
#ibapi imports
from ibapi import wrapper
from ibapi import utils
from ibapi import client
from ibapi.account_summary_tags import AccountSummaryTags
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import threading

#other importants
import logging
import tproutils as my_utils
import datetime
from tproconfig import host, port, ticktypes, account_details_params

from prices import Prices
from strategy import MovingAverageCrossStrategy
import datetime





class TraderPro(wrapper.EWrapper, client.EClient):
        
    """
    @Description:   Program designed as part of the requirement for MSF 597 at the Stuart School 
                    of Business.
    @Term:          Spring 2020
    @Student:       Ariwoola Abdulroqeeb
    
    """
    
    #tick_price_changed = QtCore.pyqtSignal(str)
    
    
    def __init__(self, window=None):
        wrapper.EWrapper.__init__(self)
        client.EClient.__init__(self, wrapper=self)
        #QtWidgets.QThread.__init__(self, None)
        
        self.reqMarketDataType(wrapper.MarketDataTypeEnum.DELAYED) #Use delayed data
        self.nextValidOrderId = 1
        self.permId2ord = {}
        self.req_to_table_row = {}
        self.tracked_names = {}
        self.account_details = {}
        self.positions = {}
        self.open_orders = {}
        if window: self.window = window
        self.prices_history = Prices()
        self.portfolio_value_hist = {}
        self.req_to_strategy = {}
        self.strategies = {}
    
    @utils.iswrapper
    # ! [nextvalidid]
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        logging.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)
        self.window.log("setting nextValidOrderId: {}".format(orderId))
        self.getAccountDetails()
        self.reqManagedAccts()
        self.reqNewsProviders()
        self.register_news()

    def managedAccounts(self, accountsList: str):
        super().managedAccounts(accountsList)
        self.account = accountsList
        self.window.log("Account list:", accountsList) 
        self.reqAccountUpdates(True, self.account)
        

    @utils.iswrapper
    # ! [updateaccountvalue]
    def updateAccountValue(self, key: str, val: str, currency: str,
                           accountName: str):
        super().updateAccountValue(key, val, currency, accountName)
        self.window.log("{} | {} | {} | {}".format("UpdateAccountValue. Key:", key, "Value:", val,
              "Currency:", currency, "AccountName:", accountName))
        
        if key in account_details_params: 
            self.account_details[key] = val
        
        if key == 'NetLiquidation': 
            self.portfolio_value_hist[datetime.datetime.now()] = val
            self.window.update_portfolio_hist_chart(self.portfolio_value_hist)
            
        #self.window.update_account_table(self.account_details)
        
    # ! [updateaccountvalue]
        

    @utils.iswrapper
    # ! [updateportfolio]
    def updatePortfolio(self, contract: wrapper.Contract, position: float,
                        marketPrice: float, marketValue: float,
                        averageCost: float, unrealizedPNL: float,
                        realizedPNL: float, accountName: str):
        super().updatePortfolio(contract, position, marketPrice, marketValue,
                                averageCost, unrealizedPNL, realizedPNL, accountName)
        self.window.log("UpdatePortfolio.", "Symbol:", contract.symbol, "SecType:", contract.secType, "Exchange:",
              contract.exchange, "Position:", position, "MarketPrice:", marketPrice,
              "MarketValue:", marketValue, "AverageCost:", averageCost,
              "UnrealizedPNL:", unrealizedPNL, "RealizedPNL:", realizedPNL,
              "AccountName:", accountName)
        
        self.positions[contract.symbol] = {"Symbol": contract.symbol, 
                               "SecType": contract.secType,
                               "Position": position,
                               "MarketValue": marketValue,
                               "AverageCost": averageCost,
                               "UnrealizedPNL": unrealizedPNL,
                               "RealizedPNL:": realizedPNL}
        self.window.update_positions_table(self.positions)
        
        if contract.symbol not in self.tracked_names:
            self.streamPrice(contract.symbol)
            self.requestContractDetails(contract.symbol)

        
    # ! [updateportfolio]

    @utils.iswrapper
    # ! [updateaccounttime]
    def updateAccountTime(self, timeStamp: str):
        super().updateAccountTime(timeStamp)
        self.window.log("UpdateAccountTime. Time:", timeStamp)
        self.account_details['last_updated'] = timeStamp
    # ! [updateaccounttime]

    @utils.iswrapper
    # ! [accountdownloadend]
    def accountDownloadEnd(self, accountName: str):
        super().accountDownloadEnd(accountName)
        self.window.log("AccountDownloadEnd. Account:", accountName)
        print('Final account details: ', self.account_details)
        
        if self.window: 
            self.window.update_account_table(self.account_details)
            self.window.update_positions_table(self.positions)

        print(self.portfolio_value_hist)
    # ! [accountdownloadend]


    @utils.iswrapper
    # ! [error]
    def error(self, reqId: wrapper.TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        print("Error occured on req: {}-{}. Message: {}".format(reqId, errorCode, errorString))


    """
    Implements API functionalities for fetching
    """
    
    #Processing Contract Details
    @utils.iswrapper
    def contractDetails(self, reqId: int, contractDetails: wrapper.ContractDetails):
        super().contractDetails(reqId, contractDetails)
        #my_utils.printinstance(contractDetails)
        self.window.log(contractDetails.longName)        
        self.window.update_tick_table(self.req_to_table_row.get(reqId), 1, contractDetails.longName, align_center=False)
        
        
    @utils.iswrapper
    def contractDetailsEnd(self, reqId: int):
        super().contractDetailsEnd(reqId)
        self.window.log("ContractDetailsEnd. ReqId: {}".format(reqId))
        


    #Streaming data -- All Last
    @utils.iswrapper
    def tickByTickAllLast(self, reqId: int, tickType: int, time: int, price: float,
                          size: int, tickAtrribLast: wrapper.TickAttribLast, exchange: str,
                          specialConditions: str):
        super().tickByTickAllLast(reqId, tickType, time, price, size, tickAtrribLast,
                                  exchange, specialConditions)
        if tickType == 1:
            print("Last.", end='')
        else:
            print("AllLast.", end='')
        
        print(" ReqId:", reqId,
              "Time:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"),
              "Price:", price, "Size:", size, "Exch:" , exchange,
              "Spec Cond:", specialConditions, "PastLimit:", tickAtrribLast.pastLimit, "Unreported:", tickAtrribLast.unreported)
    

    @utils.iswrapper
    def realtimeBar(self, reqId: wrapper.TickerId, time:int, open_: float, high: float, low: float, close: float,
                        volume: int, wap: float, count: int):
        self.window.log('Realtime bar called')
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        #print("RealTimeBar. TickerId:", reqId, wrapper.RealTimeBar(time, -1, open_, high, low, close, volume, wap, count))


    

    @utils.iswrapper
    def tickPrice(self, reqId: wrapper.TickerId, tickType: wrapper.TickType, price: float,
                  attrib: wrapper.TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        _row = self.req_to_table_row.get(reqId)
        
        
        if (ticktypes.get(int(tickType))) == 'Bid':
            self.window.update_tick_table(_row, 2, str(price))
        
        elif (ticktypes.get(int(tickType))) == 'Ask': 
            self.window.update_tick_table(_row, 3, str(price))
        
        elif (ticktypes.get(int(tickType))) == 'Last': 
            self.window.update_tick_table(_row, 4, str(price))
            _inv_names_key = {v: k for k, v in self.tracked_names.items()}
            
            self.prices_history.update_price_series(_inv_names_key.get(reqId), price)
            print(_inv_names_key)
            
            
        elif (ticktypes.get(int(tickType))) == 'High':
            self.window.update_tick_table(_row, 5, str(price))
        
        elif (ticktypes.get(int(tickType))) == 'Low': 
            self.window.update_tick_table(_row, 6, str(price))
            
        else:
            print('Unknown tickType: {}'.format(tickType))
        
        #self.window.update_ui()

    @utils.iswrapper
    def tickSize(self, reqId: wrapper.TickerId, tickType: wrapper.TickType, size: int):
        super().tickSize(reqId, tickType, size)
        if (ticktypes.get(int(tickType))) == 'Volume':
            self.window.update_tick_table(self.req_to_table_row.get(reqId), 7, str(size))
            self.window.update_tick_table(self.req_to_table_row.get(reqId), 8, str('none'))
        
    @utils.iswrapper
    def tickString(self, reqId:wrapper.TickerId, tickType:wrapper.TickType, value:str):
        pass
    
    
    
    """
    Placing Trades
    """
    
    @utils.iswrapper
    def openOrder(self, orderId: wrapper.OrderId, contract: wrapper.Contract, order: wrapper.Order,
                  orderState: wrapper.OrderState):
        super().openOrder(orderId, contract, order, orderState)
        
        self.open_orders[orderId] = {"ticker": contract.symbol,
                                "action": order.action,
                                "ordertype": order.orderType,
                                "totalqty": order.totalQuantity,
                                "lmtprice": order.lmtPrice,
                                "status": orderState.status,
                                "strategy": self.req_to_strategy.get(orderId)}
        
        order.contract = contract
        self.permId2ord[order.permId] = order
        
        print(self.open_orders)
        self.window.update_open_orders_table(self.open_orders)


    @utils.iswrapper
    def openOrderEnd(self):
        super().openOrderEnd()
        print("OpenOrderEnd")
        print(self.permId2ord)
        logging.debug("Received %d openOrders", len(self.permId2ord))
        self.window.log(self.open_orders)
        
        #app.disconnect()

    @utils.iswrapper
    def orderStatus(self, orderId: wrapper.OrderId, status: str, filled: float,
                    remaining: float, avgFillPrice: float, permId: int,
                    parentId: int, lastFillPrice: float, clientId: int,
                    whyHeld: str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining,
                            avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        print("OrderStatus. Id:", orderId, "Status:", status, "Filled:", filled,
              "Remaining:", remaining, "AvgFillPrice:", avgFillPrice,
              "PermId:", permId, "ParentId:", parentId, "LastFillPrice:",
              lastFillPrice, "ClientId:", clientId, "WhyHeld:",
              whyHeld, "MktCapPrice:", mktCapPrice)
        #app.disconnect()


    

    """
    Account summary operations
    """
    
    @utils.iswrapper
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        self.window.log("{} | {} | {} | {}".format("AccountSummary. ReqId: {}".format(reqId), "Account: {}".format(account),
              "Tag: {}".format(tag), "Value: {}".format(value), "Currency: {}".format(currency)))
    

    @utils.iswrapper
    def accountSummaryEnd(self, reqId: int):
        super().accountSummaryEnd(reqId)
        self.window.log("AccountSummaryEnd. ReqId:", reqId)
        #app.disconnect()



    '''
    News
    '''
    
    def register_news(self):
        contract = wrapper.Contract()
        contract.symbol  = "BRFG:BRFG_ALL"
        contract.secType = "NEWS"
        contract.exchange = "BRFG"
        
        self.reqMktData(1009, contract, "mdoff,292", False, False, [])
    
    @utils.iswrapper
    #! [tickNews]
    def tickNews(self, tickerId: int, timeStamp: int, providerCode: str,
                 articleId: str, headline: str, extraData: str):
        print("TickNews. TickerId:", tickerId, "TimeStamp:", timeStamp,
              "ProviderCode:", providerCode, "ArticleId:", articleId,
              "Headline:", headline, "ExtraData:", extraData)
    #! [tickNews]
    
    @utils.iswrapper
    #! [newsProviders]
    def newsProviders(self, newsProviders: wrapper.ListOfNewsProviders):
        print("NewsProviders: ")
        for provider in newsProviders:
            print("NewsProvider.", provider)
    #! [newsProviders]

    @utils.iswrapper
    #! [newsArticle]
    def newsArticle(self, reqId: int, articleType: int, articleText: str):
        print("NewsArticle. ReqId:", reqId, "ArticleType:", articleType,
              "ArticleText:", articleText)
    #! [newsArticle]




    def streamPrice(self, ticker):

        if ticker not in self.tracked_names.keys():
            
            #Logging and Setting Valid ID
            self.window.log('New ticker submitted', self.tracked_names)
            self.nextValidOrderId = self.nextValidOrderId + 1

            self.tracked_names[ticker] = self.nextValidOrderId
            self.reqMarketDataType(wrapper.MarketDataTypeEnum.DELAYED)
            contract = my_utils.get_USD_stock_contract(ticker)
            
            self.reqMktData(self.nextValidOrderId, contract, "", False, False, [])
            _current_row = self.window.ui.tick_table.rowCount()
            self.window.ui.tick_table.insertRow(_current_row)
            
            self.req_to_table_row[self.nextValidOrderId] = _current_row
            self.window.ui.tick_table.setVerticalHeaderItem(_current_row, QtWidgets.QTableWidgetItem(str(self.req_to_table_row.get(self.nextValidOrderId))))
            self.window.ui.tick_table.setItem(self.req_to_table_row.get(self.nextValidOrderId), 0, QtWidgets.QTableWidgetItem(contract.symbol))
            
        else:
            self.window.ui.statusBar().showMessage('Stream Price: {} is already tracked'.format(ticker), 3000)


    def orderContract(self, ticker, quantity, action='BUY', order_type='MKT', lmt_price=0, strategy='Discretionary'):
        
        self.nextValidOrderId = self.nextValidOrderId + 1
        contract = my_utils.get_USD_stock_contract(ticker)
        order = wrapper.Order()
        order.action = action
        order.orderType = order_type
        if order.orderType == 'LMT': order.lmtPrice = lmt_price
        order.totalQuantity = quantity

        self.placeOrder(self.nextValidOrderId, contract, order)
        self.req_to_strategy[self.nextValidOrderId] = strategy
        
    
    def getAccountDetails(self):
        self.nextValidOrderId = self.nextValidOrderId + 1
        self.reqAccountSummary(self.nextValidOrderId, "All", AccountSummaryTags.AllTags)

    

    def requestContractDetails(self, ticker):
        ticker = ticker.upper()
        contract = my_utils.get_USD_stock_contract(ticker)
        self.reqContractDetails(self.nextValidOrderId, contract)




if __name__ == "_main__":
    my_utils.setup_logger()
    logging.debug("now is %s", datetime.datetime.now())
    logging.getLogger().setLevel(logging.ERROR)


    app = TraderPro()
    
    app.connect(host, port, clientId=0)

    # ! [connect]
    print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),
                                                  app.twsConnectionTime()))
    

    # ! [clientrun]
    app.run()
