from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)


def execute_trade(contract, order):
    trade = ib.placeOrder(contract, order)
    print(trade)
    return trade