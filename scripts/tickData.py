from ib_insync import *
import redis
import json

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

reqTickerMapper = {}

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, password="p@ss$12E4")

def pendingTickersEvent(tickers):
    for ticker in tickers:
        print("Last: ", ticker.last)

def barUpdateEvent(bars, hasNewBar):
    global reqTickerMapper
    # print(ib.client.getReqId())
    if(hasNewBar):
        pct_change = ((bars[-2].close - bars[-16].close) * 100) / bars[-16].close
        print(f"Last Traded Price of {reqTickerMapper[bars.reqId]}: ", bars[-2].close)
        print(f"Percentage Change: {pct_change}%")
        msg = {"close": bars[-2].close, "pct_change": pct_change}
        redis_client.publish(reqTickerMapper[bars.reqId], json.dumps(msg))
        print("sent!")

tickers = ["GOOG", "AAPL", "MSFT", "AMZN", "META", "TSLA", "NVDA", "PYPL", "ADBE", "NFLX"]

contracts = [Stock(ticker, 'SMART', 'USD') for ticker in tickers]

# ib.pendingTickersEvent += pendingTickersEvent

# ib.reqTickByTickData(contract, 'Last', 0, False)
ib.client._reqIdSeq = 1

for contract in contracts:

    bars = ib.reqHistoricalData(
            contract,
            endDateTime='20240315 09:15:00 US/Eastern',
            durationStr='900 S',
            barSizeSetting='5 secs',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1,
            keepUpToDate=True
            )

    reqTickerMapper[bars.reqId] = contract.symbol

ib.barUpdateEvent += barUpdateEvent

# ticker = ib.reqTickByTickData(contract, 'Last', 0, False)
ib.sleep(30)

# ib.cancelTickByTickData(ticker)

ib.disconnect()