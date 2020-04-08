#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 12:30:41 2020

@author: abdulroqeeb
"""

import os
import time
import logging
from ibapi import wrapper
import datetime

def setup_logger():
    if not os.path.exists("log"):
        os.makedirs("log")

    time.strftime("trade_pro.%Y%m%d_%H%M%S.log")

    recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'

    timefmt = '%y%m%d_%H:%M:%S'

    logging.basicConfig(filename=time.strftime("log/trade_pro.%y%m%d_%H%M%S.log"),
                        filemode="w",
                        level=logging.INFO,
                        format=recfmt, datefmt=timefmt)
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    logger.addHandler(console)
    
    

def printinstance(inst: wrapper.Object):
    attrs = vars(inst)
    print(', '.join("%s: %s" % item for item in attrs.items()))
    
    
    
def get_USD_stock_contract(ticker):
    
    contract = wrapper.Contract()
    contract.symbol = ticker
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    
    return contract  


def get_now():
    return datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")