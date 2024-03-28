from ib_insync import *
import redis
import time
import json

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=4)

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, password="p@ss$12E4")
ticker = "MSFT"

def newOrderEvent(order):
    print("New Order: ", order)

def orderStatusEvent(trade):
    print("Trade: ", trade)

    if((trade.orderStatus.status.lower()=="filled") and (trade.order.orderRef[0] == "f")):
        print("Order Completed")
        allFills = trade.fills
        totalPrice = 0
        totalShares = 0
        avgFillPrice = ''

        for fill in allFills:
            totalPrice += (fill.execution.shares*fill.execution.avgPrice)
            totalShares += fill.execution.shares
        
        if(totalShares>0):
            avgFillPrice = totalPrice/totalShares
            targetPrice = avgFillPrice + (avgFillPrice*0.001)
        
        if(trade.order.orderRef[0] == "f"):
            msg = {
                "signal": "2", 
                "execution_price": avgFillPrice, 
                "quantity": totalShares,
                "target": round(targetPrice, 2)
                }
            redis_client.publish(ticker + "_trade", json.dumps(msg))
        

def execute_trade(contract, order):
    trade = ib.placeOrder(contract, order)
    return trade

contract = Stock(ticker, 'SMART', 'USD')

ib.orderStatusEvent += orderStatusEvent

def first_execution():
    order1 = MarketOrder('BUY', 100, orderRef=f"f_{int(time.time())}")
    order1.algoStrategy = "Adaptive"
    order1.algoParams = []
    order1.algoParams.append(TagValue("adaptivePriority", "Urgent"))
    # adaptive order

    trade = execute_trade(contract, order1)
    ib.sleep(1)
    # trade.execDetailsEvent += execDetailsEvent

def second_execution(data):

    print("Second Execution")
    print(data["quantity"], data["target"])

    order2 = LimitOrder('SELL', data["quantity"], data["target"], orderRef=f"l_{int(time.time())}")
    trade = execute_trade(contract, order2)

# add redis subscription
    
pubsub = redis_client.pubsub()
pubsub.subscribe(ticker + "_trade")

for message in pubsub.listen():
    if message["type"] == "message":
        data = json.loads(message["data"])
        if int(data["signal"]) == 1:
            print("Signal 1")
            first_execution()
        elif int(data["signal"]) == 2:
            print("Signal 2")
            second_execution(data)
        else:
            print("Invalid Signal")
