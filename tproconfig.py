#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 13:11:49 2020

@author: abdulroqeeb
"""

host = "127.0.0.1"
port =  7497


ticktypes = {
        66: "Bid",
        67: "Ask",
        68: "Last",
        69: "Bid Size",
        70: "Ask Size",
        71: "Last Size",
        72: "High",
        73: "Low",
        74: "Volume",
        75: "Prior Close",
        76: "Prior Open",
        88: "Timestamp",
        
        }


account_details_params = [
    'AccountCode',
    'AccountType',
    'AccruedCash',
    'AvailableFunds',
    'BuyingPower',
    'CashBalance',
    'NetLiquidation'
    ]


port_chart_lim = 600 #minutes